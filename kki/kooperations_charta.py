"""
#443 KooperationsCharta — Kooperative Spieltheorie: Tit-for-Tat und Evolutionäre Stabilität.
Axelrod (1984): Tit-for-Tat gewinnt Gefangenendilemma-Turniere — Kooperation emergiert.
Maynard Smith & Price (1973): Evolutionäre Spieltheorie — ESS (Evolutionary Stable Strategy).
Schelling (1960): Brennpunkt-Koordination ohne Kommunikation — fokale Punkte. Nobel 2005.
Leitsterns Schwarm-Kooperation folgt Tit-for-Tat: Vertrauen, Gegenseitigkeit, Sanktionierung.
Geltungsstufen: GESPERRT / KOOPERATIV / GRUNDLEGEND_KOOPERATIV
Parent: NashRegister (#442)
Block #441–#450: Spieltheorie & Entscheidungstheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .nash_register import (
    NashRegister,
    NashRegisterGeltung,
    build_nash_register,
)

_GELTUNG_MAP: dict[NashRegisterGeltung, "KooperationsChartaGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[NashRegisterGeltung.GESPERRT] = KooperationsChartaGeltung.GESPERRT
    _GELTUNG_MAP[NashRegisterGeltung.NASH] = KooperationsChartaGeltung.KOOPERATIV
    _GELTUNG_MAP[NashRegisterGeltung.GRUNDLEGEND_NASH] = KooperationsChartaGeltung.GRUNDLEGEND_KOOPERATIV


class KooperationsChartaTyp(Enum):
    SCHUTZ_KOOPERATION = "schutz-kooperation"
    ORDNUNGS_KOOPERATION = "ordnungs-kooperation"
    SOUVERAENITAETS_KOOPERATION = "souveraenitaets-kooperation"


class KooperationsChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KooperationsChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    KOOPERATIV = "kooperativ"
    GRUNDLEGEND_KOOPERATIV = "grundlegend-kooperativ"


_init_map()

_TYP_MAP: dict[KooperationsChartaGeltung, KooperationsChartaTyp] = {
    KooperationsChartaGeltung.GESPERRT: KooperationsChartaTyp.SCHUTZ_KOOPERATION,
    KooperationsChartaGeltung.KOOPERATIV: KooperationsChartaTyp.ORDNUNGS_KOOPERATION,
    KooperationsChartaGeltung.GRUNDLEGEND_KOOPERATIV: KooperationsChartaTyp.SOUVERAENITAETS_KOOPERATION,
}

_PROZEDUR_MAP: dict[KooperationsChartaGeltung, KooperationsChartaProzedur] = {
    KooperationsChartaGeltung.GESPERRT: KooperationsChartaProzedur.NOTPROZEDUR,
    KooperationsChartaGeltung.KOOPERATIV: KooperationsChartaProzedur.REGELPROTOKOLL,
    KooperationsChartaGeltung.GRUNDLEGEND_KOOPERATIV: KooperationsChartaProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[KooperationsChartaGeltung, float] = {
    KooperationsChartaGeltung.GESPERRT: 0.0,
    KooperationsChartaGeltung.KOOPERATIV: 0.04,
    KooperationsChartaGeltung.GRUNDLEGEND_KOOPERATIV: 0.08,
}

_TIER_DELTA: dict[KooperationsChartaGeltung, int] = {
    KooperationsChartaGeltung.GESPERRT: 0,
    KooperationsChartaGeltung.KOOPERATIV: 1,
    KooperationsChartaGeltung.GRUNDLEGEND_KOOPERATIV: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class KooperationsChartaNorm:
    kooperations_charta_id: str
    kooperations_charta_typ: KooperationsChartaTyp
    prozedur: KooperationsChartaProzedur
    geltung: KooperationsChartaGeltung
    kooperations_weight: float
    kooperations_tier: int
    canonical: bool
    kooperations_ids: tuple[str, ...]
    kooperations_tags: tuple[str, ...]


@dataclass(frozen=True)
class KooperationsCharta:
    charta_id: str
    nash_register: NashRegister
    normen: tuple[KooperationsChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kooperations_charta_id for n in self.normen if n.geltung is KooperationsChartaGeltung.GESPERRT)

    @property
    def kooperativ_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kooperations_charta_id for n in self.normen if n.geltung is KooperationsChartaGeltung.KOOPERATIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kooperations_charta_id for n in self.normen if n.geltung is KooperationsChartaGeltung.GRUNDLEGEND_KOOPERATIV)

    @property
    def charta_signal(self):
        if any(n.geltung is KooperationsChartaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is KooperationsChartaGeltung.KOOPERATIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-kooperativ")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-kooperativ")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_kooperations_charta(
    nash_register: NashRegister | None = None,
    *,
    charta_id: str = "kooperations-charta",
) -> KooperationsCharta:
    if nash_register is None:
        nash_register = build_nash_register(register_id=f"{charta_id}-register")

    normen: list[KooperationsChartaNorm] = []
    for parent_norm in nash_register.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.nash_register_id.removeprefix(f'{nash_register.register_id}-')}"
        raw_weight = min(1.0, parent_norm.nash_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.nash_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KooperationsChartaGeltung.GRUNDLEGEND_KOOPERATIV)
        normen.append(
            KooperationsChartaNorm(
                kooperations_charta_id=new_id,
                kooperations_charta_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kooperations_weight=new_weight,
                kooperations_tier=new_tier,
                canonical=is_canonical,
                kooperations_ids=parent_norm.nash_ids + (new_id,),
                kooperations_tags=parent_norm.nash_tags + (f"kooperations-charta:{new_geltung.value}",),
            )
        )
    return KooperationsCharta(
        charta_id=charta_id,
        nash_register=nash_register,
        normen=tuple(normen),
    )
