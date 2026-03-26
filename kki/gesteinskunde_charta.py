from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .kristallographie_register import KristallographieRegister, build_kristallographie_register


class GesteinskundeChartaGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_MINERALOGISCH = auto()
    MINERALOGISCH = auto()
    MINERALOGISCH_AKTIV = auto()
    MINERALOGIE_SOUVERAEN = auto()


class GesteinskundeChartaTyp(Enum):
    GESTEINSKUNDE_CHARTA = auto()
    GESTEINSKUNDE_SYSTEM = auto()
    GESTEINSKUNDE_KOMPONENTE = auto()


class GesteinskundeChartaProzedur(Enum):
    GESTEINSKUNDEANALYSE = auto()
    GESTEINSKUNDE_SYNTHESE = auto()
    GESTEINSKUNDE_BEWERTUNG = auto()


_WEIGHT_DELTA: dict[GesteinskundeChartaGeltung, float] = {
    GesteinskundeChartaGeltung.GESPERRT: 0.0,
    GesteinskundeChartaGeltung.GRUNDLEGEND_MINERALOGISCH: 1.4,
    GesteinskundeChartaGeltung.MINERALOGISCH: 2.8,
    GesteinskundeChartaGeltung.MINERALOGISCH_AKTIV: 4.2,
    GesteinskundeChartaGeltung.MINERALOGIE_SOUVERAEN: 5.6,
}

_TYP_MAP = {
    GesteinskundeChartaGeltung.GESPERRT: GesteinskundeChartaTyp.GESTEINSKUNDE_CHARTA,
    GesteinskundeChartaGeltung.GRUNDLEGEND_MINERALOGISCH: GesteinskundeChartaTyp.GESTEINSKUNDE_KOMPONENTE,
    GesteinskundeChartaGeltung.MINERALOGISCH: GesteinskundeChartaTyp.GESTEINSKUNDE_KOMPONENTE,
    GesteinskundeChartaGeltung.MINERALOGISCH_AKTIV: GesteinskundeChartaTyp.GESTEINSKUNDE_SYSTEM,
    GesteinskundeChartaGeltung.MINERALOGIE_SOUVERAEN: GesteinskundeChartaTyp.GESTEINSKUNDE_SYSTEM,
}

_PROZEDUR_MAP = {
    GesteinskundeChartaGeltung.GESPERRT: GesteinskundeChartaProzedur.GESTEINSKUNDEANALYSE,
    GesteinskundeChartaGeltung.GRUNDLEGEND_MINERALOGISCH: GesteinskundeChartaProzedur.GESTEINSKUNDEANALYSE,
    GesteinskundeChartaGeltung.MINERALOGISCH: GesteinskundeChartaProzedur.GESTEINSKUNDE_SYNTHESE,
    GesteinskundeChartaGeltung.MINERALOGISCH_AKTIV: GesteinskundeChartaProzedur.GESTEINSKUNDE_SYNTHESE,
    GesteinskundeChartaGeltung.MINERALOGIE_SOUVERAEN: GesteinskundeChartaProzedur.GESTEINSKUNDE_BEWERTUNG,
}


@dataclass(frozen=True)
class GesteinskundeChartaNorm:
    geltung: GesteinskundeChartaGeltung
    mineralogie_weight: float
    mineralogie_tier: int
    mineralogie_ids: tuple[str, ...]
    mineralogie_tags: tuple[str, ...]
    typ: GesteinskundeChartaTyp
    prozedur: GesteinskundeChartaProzedur
    canonical: bool = True


@dataclass(frozen=True)
class GesteinskundeCharta:
    normen: tuple[GesteinskundeChartaNorm, ...]
    parent: Optional[KristallographieRegister] = None


def build_gesteinskunde_charta(parent: Optional[KristallographieRegister] = None) -> GesteinskundeCharta:
    if parent is None:
        parent = build_kristallographie_register()
    base = sum(e.mineralogie_weight for e in parent.eintraege)
    normen = tuple(
        GesteinskundeChartaNorm(
            geltung=g,
            mineralogie_weight=round(base + _WEIGHT_DELTA[g], 4),
            mineralogie_tier=i + 1,
            mineralogie_ids=(f"gesteinskunde-charta-{g.name.lower()}-001",),
            mineralogie_tags=("mineralogie", "gesteinskunde", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(GesteinskundeChartaGeltung)
    )
    return GesteinskundeCharta(normen=normen, parent=parent)
