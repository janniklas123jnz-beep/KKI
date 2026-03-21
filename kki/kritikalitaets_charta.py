"""
#413 KritikalitaetsCharta — Selbstorganisierte Kritikalität (SOC).
Per Bak (1987): Selbstorganisierte Kritikalität (SOC) — komplexe Systeme
entwickeln sich spontan zum kritischen Punkt ohne externe Steuerung. Sandpile-Modell.
Potenzgesetz P(s) ∝ s^(-τ): Lawinen aller Größen. 1/f-Rauschen als universelle Signatur.
Kritischer Exponent τ als Governance-Parameter.
Skalenfreiheit: keine charakteristische Größe. Universalitätsklassen:
verschiedene Systeme, gleiche kritische Exponenten. Leitsterns Schwarm: am kritischen Punkt.
Geltungsstufen: GESPERRT / KRITISCH / GRUNDLEGEND_KRITISCH
Parent: DissipativeStrukturenRegister (#412)
Block #411–#420 Komplexe Systeme & Emergenz
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .dissipative_strukturen_register import (
    DissipativeStrukturenRegister,
    DissipativeStrukturenRegisterGeltung,
    build_dissipative_strukturen_register,
)

_GELTUNG_MAP: dict[DissipativeStrukturenRegisterGeltung, "KritikalitaetsChartaGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[DissipativeStrukturenRegisterGeltung.GESPERRT] = KritikalitaetsChartaGeltung.GESPERRT
    _GELTUNG_MAP[DissipativeStrukturenRegisterGeltung.DISSIPATIV] = KritikalitaetsChartaGeltung.KRITISCH
    _GELTUNG_MAP[DissipativeStrukturenRegisterGeltung.GRUNDLEGEND_DISSIPATIV] = KritikalitaetsChartaGeltung.GRUNDLEGEND_KRITISCH


class KritikalitaetsChartaTyp(Enum):
    SCHUTZ_KRITIKALITAET = "schutz-kritikalitaet"
    ORDNUNGS_KRITIKALITAET = "ordnungs-kritikalitaet"
    SOUVERAENITAETS_KRITIKALITAET = "souveraenitaets-kritikalitaet"


class KritikalitaetsChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KritikalitaetsChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    KRITISCH = "kritisch"
    GRUNDLEGEND_KRITISCH = "grundlegend-kritisch"


_init_map()

_TYP_MAP: dict[KritikalitaetsChartaGeltung, KritikalitaetsChartaTyp] = {
    KritikalitaetsChartaGeltung.GESPERRT: KritikalitaetsChartaTyp.SCHUTZ_KRITIKALITAET,
    KritikalitaetsChartaGeltung.KRITISCH: KritikalitaetsChartaTyp.ORDNUNGS_KRITIKALITAET,
    KritikalitaetsChartaGeltung.GRUNDLEGEND_KRITISCH: KritikalitaetsChartaTyp.SOUVERAENITAETS_KRITIKALITAET,
}

_PROZEDUR_MAP: dict[KritikalitaetsChartaGeltung, KritikalitaetsChartaProzedur] = {
    KritikalitaetsChartaGeltung.GESPERRT: KritikalitaetsChartaProzedur.NOTPROZEDUR,
    KritikalitaetsChartaGeltung.KRITISCH: KritikalitaetsChartaProzedur.REGELPROTOKOLL,
    KritikalitaetsChartaGeltung.GRUNDLEGEND_KRITISCH: KritikalitaetsChartaProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[KritikalitaetsChartaGeltung, float] = {
    KritikalitaetsChartaGeltung.GESPERRT: 0.0,
    KritikalitaetsChartaGeltung.KRITISCH: 0.04,
    KritikalitaetsChartaGeltung.GRUNDLEGEND_KRITISCH: 0.08,
}

_TIER_DELTA: dict[KritikalitaetsChartaGeltung, int] = {
    KritikalitaetsChartaGeltung.GESPERRT: 0,
    KritikalitaetsChartaGeltung.KRITISCH: 1,
    KritikalitaetsChartaGeltung.GRUNDLEGEND_KRITISCH: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class KritikalitaetsChartaNorm:
    kritikalitaets_charta_id: str
    kritikalitaet_typ: KritikalitaetsChartaTyp
    prozedur: KritikalitaetsChartaProzedur
    geltung: KritikalitaetsChartaGeltung
    kritikalitaet_weight: float
    kritikalitaet_tier: int
    canonical: bool
    kritikalitaet_ids: tuple[str, ...]
    kritikalitaet_tags: tuple[str, ...]


@dataclass(frozen=True)
class KritikalitaetsCharta:
    charta_id: str
    dissipative_strukturen_register: DissipativeStrukturenRegister
    normen: tuple[KritikalitaetsChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kritikalitaets_charta_id for n in self.normen if n.geltung is KritikalitaetsChartaGeltung.GESPERRT)

    @property
    def kritisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kritikalitaets_charta_id for n in self.normen if n.geltung is KritikalitaetsChartaGeltung.KRITISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kritikalitaets_charta_id for n in self.normen if n.geltung is KritikalitaetsChartaGeltung.GRUNDLEGEND_KRITISCH)

    @property
    def charta_signal(self):
        if any(n.geltung is KritikalitaetsChartaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is KritikalitaetsChartaGeltung.KRITISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-kritisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-kritisch")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_kritikalitaets_charta(
    dissipative_strukturen_register: DissipativeStrukturenRegister | None = None,
    *,
    charta_id: str = "kritikalitaets-charta",
) -> KritikalitaetsCharta:
    if dissipative_strukturen_register is None:
        dissipative_strukturen_register = build_dissipative_strukturen_register(register_id=f"{charta_id}-register")

    normen: list[KritikalitaetsChartaNorm] = []
    for parent_norm in dissipative_strukturen_register.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.dissipative_strukturen_register_id.removeprefix(f'{dissipative_strukturen_register.register_id}-')}"
        raw_weight = min(1.0, parent_norm.dissipation_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.dissipation_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KritikalitaetsChartaGeltung.GRUNDLEGEND_KRITISCH)
        normen.append(
            KritikalitaetsChartaNorm(
                kritikalitaets_charta_id=new_id,
                kritikalitaet_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kritikalitaet_weight=new_weight,
                kritikalitaet_tier=new_tier,
                canonical=is_canonical,
                kritikalitaet_ids=parent_norm.dissipation_ids + (new_id,),
                kritikalitaet_tags=parent_norm.dissipation_tags + (f"kritikalitaet:{new_geltung.value}",),
            )
        )
    return KritikalitaetsCharta(
        charta_id=charta_id,
        dissipative_strukturen_register=dissipative_strukturen_register,
        normen=tuple(normen),
    )
