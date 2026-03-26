from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .erosions_register import ErosionsRegister, build_erosions_register


class ReliefentwicklungChartaGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_GEOMORPHOLOGISCH = auto()
    GEOMORPHOLOGISCH = auto()
    GEOMORPHOLOGISCH_AKTIV = auto()
    GEOMORPHOLOGIE_SOUVERAEN = auto()


class ReliefentwicklungChartaTyp(Enum):
    RELIEFENTWICKLUNGCHARTA = auto()
    RELIEFENTWICKLUNGSYSTEM = auto()
    RELIEFENTWICKLUNGKOMPONENTE = auto()


class ReliefentwicklungChartaProzedur(Enum):
    RELIEFENTWICKLUNGANALYSE = auto()
    RELIEFENTWICKLUNGSYNTHESE = auto()
    RELIEFENTWICKLUNGBEWERTUNG = auto()


_WEIGHT_DELTA: dict[ReliefentwicklungChartaGeltung, float] = {
    ReliefentwicklungChartaGeltung.GESPERRT: 0.0,
    ReliefentwicklungChartaGeltung.GRUNDLEGEND_GEOMORPHOLOGISCH: 1.4,
    ReliefentwicklungChartaGeltung.GEOMORPHOLOGISCH: 2.8,
    ReliefentwicklungChartaGeltung.GEOMORPHOLOGISCH_AKTIV: 4.2,
    ReliefentwicklungChartaGeltung.GEOMORPHOLOGIE_SOUVERAEN: 5.6,
}

_TYP_MAP = {
    ReliefentwicklungChartaGeltung.GESPERRT: ReliefentwicklungChartaTyp.RELIEFENTWICKLUNGCHARTA,
    ReliefentwicklungChartaGeltung.GRUNDLEGEND_GEOMORPHOLOGISCH: ReliefentwicklungChartaTyp.RELIEFENTWICKLUNGKOMPONENTE,
    ReliefentwicklungChartaGeltung.GEOMORPHOLOGISCH: ReliefentwicklungChartaTyp.RELIEFENTWICKLUNGKOMPONENTE,
    ReliefentwicklungChartaGeltung.GEOMORPHOLOGISCH_AKTIV: ReliefentwicklungChartaTyp.RELIEFENTWICKLUNGSYSTEM,
    ReliefentwicklungChartaGeltung.GEOMORPHOLOGIE_SOUVERAEN: ReliefentwicklungChartaTyp.RELIEFENTWICKLUNGSYSTEM,
}

_PROZEDUR_MAP = {
    ReliefentwicklungChartaGeltung.GESPERRT: ReliefentwicklungChartaProzedur.RELIEFENTWICKLUNGANALYSE,
    ReliefentwicklungChartaGeltung.GRUNDLEGEND_GEOMORPHOLOGISCH: ReliefentwicklungChartaProzedur.RELIEFENTWICKLUNGANALYSE,
    ReliefentwicklungChartaGeltung.GEOMORPHOLOGISCH: ReliefentwicklungChartaProzedur.RELIEFENTWICKLUNGSYNTHESE,
    ReliefentwicklungChartaGeltung.GEOMORPHOLOGISCH_AKTIV: ReliefentwicklungChartaProzedur.RELIEFENTWICKLUNGSYNTHESE,
    ReliefentwicklungChartaGeltung.GEOMORPHOLOGIE_SOUVERAEN: ReliefentwicklungChartaProzedur.RELIEFENTWICKLUNGBEWERTUNG,
}


@dataclass(frozen=True)
class ReliefentwicklungChartaNorm:
    geltung: ReliefentwicklungChartaGeltung
    geomorphologie_weight: float
    geomorphologie_tier: int
    geomorphologie_ids: tuple[str, ...]
    geomorphologie_tags: tuple[str, ...]
    typ: ReliefentwicklungChartaTyp
    prozedur: ReliefentwicklungChartaProzedur
    canonical: bool = True


@dataclass(frozen=True)
class ReliefentwicklungCharta:
    normen: tuple[ReliefentwicklungChartaNorm, ...]
    parent: Optional[ErosionsRegister] = None


def build_reliefentwicklung_charta(parent: Optional[ErosionsRegister] = None) -> ReliefentwicklungCharta:
    if parent is None:
        parent = build_erosions_register()
    base = sum(e.geomorphologie_weight for e in parent.eintraege)
    normen = tuple(
        ReliefentwicklungChartaNorm(
            geltung=g,
            geomorphologie_weight=round(base + _WEIGHT_DELTA[g], 4),
            geomorphologie_tier=i + 1,
            geomorphologie_ids=(f"reliefentwicklung-charta-{g.name.lower()}-001",),
            geomorphologie_tags=("geomorphologie", "reliefentwicklung", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(ReliefentwicklungChartaGeltung)
    )
    return ReliefentwicklungCharta(normen=normen, parent=parent)
