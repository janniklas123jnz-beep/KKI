"""
#453 SeletkionsCharta — Natürliche Selektion: Fitness, Anpassung und sexuelle Selektion.
Fisher (1930): Fundamentales Theorem der natürlichen Selektion — Fitnesszunahme = genetische Varianz.
Wright (1932): Adaptive Landschaft (Fitness Landscape) — Gipfel, Täler und evolutionäre Pfade.
Darwin (1871): Sexuelle Selektion — intrasexueller Wettbewerb und intersexuelle Wahl.
Leitsterns Agenten navigieren adaptive Landschaften: lokale Optima, Mutation als Exploration.
Geltungsstufen: GESPERRT / SELEKTIV / GRUNDLEGEND_SELEKTIV
Parent: GenetikRegister (#452)
Block #451–#460: Evolutionsbiologie & Genetik
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .genetik_register import (
    GenetikRegister,
    GenetikRegisterGeltung,
    build_genetik_register,
)

_GELTUNG_MAP: dict[GenetikRegisterGeltung, "SeletkionsChartaGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[GenetikRegisterGeltung.GESPERRT] = SeletkionsChartaGeltung.GESPERRT
    _GELTUNG_MAP[GenetikRegisterGeltung.GENETISCH] = SeletkionsChartaGeltung.SELEKTIV
    _GELTUNG_MAP[GenetikRegisterGeltung.GRUNDLEGEND_GENETISCH] = SeletkionsChartaGeltung.GRUNDLEGEND_SELEKTIV


class SeletkionsChartaTyp(Enum):
    SCHUTZ_SELEKTION = "schutz-selektion"
    ORDNUNGS_SELEKTION = "ordnungs-selektion"
    SOUVERAENITAETS_SELEKTION = "souveraenitaets-selektion"


class SeletkionsChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class SeletkionsChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    SELEKTIV = "selektiv"
    GRUNDLEGEND_SELEKTIV = "grundlegend-selektiv"


_init_map()

_TYP_MAP: dict[SeletkionsChartaGeltung, SeletkionsChartaTyp] = {
    SeletkionsChartaGeltung.GESPERRT: SeletkionsChartaTyp.SCHUTZ_SELEKTION,
    SeletkionsChartaGeltung.SELEKTIV: SeletkionsChartaTyp.ORDNUNGS_SELEKTION,
    SeletkionsChartaGeltung.GRUNDLEGEND_SELEKTIV: SeletkionsChartaTyp.SOUVERAENITAETS_SELEKTION,
}

_PROZEDUR_MAP: dict[SeletkionsChartaGeltung, SeletkionsChartaProzedur] = {
    SeletkionsChartaGeltung.GESPERRT: SeletkionsChartaProzedur.NOTPROZEDUR,
    SeletkionsChartaGeltung.SELEKTIV: SeletkionsChartaProzedur.REGELPROTOKOLL,
    SeletkionsChartaGeltung.GRUNDLEGEND_SELEKTIV: SeletkionsChartaProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[SeletkionsChartaGeltung, float] = {
    SeletkionsChartaGeltung.GESPERRT: 0.0,
    SeletkionsChartaGeltung.SELEKTIV: 0.04,
    SeletkionsChartaGeltung.GRUNDLEGEND_SELEKTIV: 0.08,
}

_TIER_DELTA: dict[SeletkionsChartaGeltung, int] = {
    SeletkionsChartaGeltung.GESPERRT: 0,
    SeletkionsChartaGeltung.SELEKTIV: 1,
    SeletkionsChartaGeltung.GRUNDLEGEND_SELEKTIV: 2,
}


@dataclass(frozen=True)
class SeletkionsChartaNorm:
    selektions_charta_id: str
    selektions_charta_typ: SeletkionsChartaTyp
    prozedur: SeletkionsChartaProzedur
    geltung: SeletkionsChartaGeltung
    selektions_weight: float
    selektions_tier: int
    canonical: bool
    selektions_ids: tuple[str, ...]
    selektions_tags: tuple[str, ...]


@dataclass(frozen=True)
class SeletkionsCharta:
    charta_id: str
    genetik_register: GenetikRegister
    normen: tuple[SeletkionsChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.selektions_charta_id for n in self.normen if n.geltung is SeletkionsChartaGeltung.GESPERRT)

    @property
    def selektiv_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.selektions_charta_id for n in self.normen if n.geltung is SeletkionsChartaGeltung.SELEKTIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.selektions_charta_id for n in self.normen if n.geltung is SeletkionsChartaGeltung.GRUNDLEGEND_SELEKTIV)

    @property
    def charta_signal(self):
        if any(n.geltung is SeletkionsChartaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is SeletkionsChartaGeltung.SELEKTIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-selektiv")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-selektiv")


def build_selektions_charta(
    genetik_register: GenetikRegister | None = None,
    *,
    charta_id: str = "selektions-charta",
) -> SeletkionsCharta:
    if genetik_register is None:
        genetik_register = build_genetik_register(register_id=f"{charta_id}-register")

    normen: list[SeletkionsChartaNorm] = []
    for parent_norm in genetik_register.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.genetik_register_id.removeprefix(f'{genetik_register.register_id}-')}"
        raw_weight = min(1.0, parent_norm.genetik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.genetik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SeletkionsChartaGeltung.GRUNDLEGEND_SELEKTIV)
        normen.append(
            SeletkionsChartaNorm(
                selektions_charta_id=new_id,
                selektions_charta_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                selektions_weight=new_weight,
                selektions_tier=new_tier,
                canonical=is_canonical,
                selektions_ids=parent_norm.genetik_ids + (new_id,),
                selektions_tags=parent_norm.genetik_tags + (f"selektions-charta:{new_geltung.value}",),
            )
        )
    return SeletkionsCharta(
        charta_id=charta_id,
        genetik_register=genetik_register,
        normen=tuple(normen),
    )
