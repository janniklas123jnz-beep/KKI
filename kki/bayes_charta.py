from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .wahrscheinlichkeit_register import WahrscheinlichkeitRegister, build_wahrscheinlichkeit_register


class BayesChartaGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_BAYESIANISCH = auto()
    BAYESIANISCH = auto()
    BAYESIANISCH_AKTIV = auto()
    BAYES_SOUVERAEN = auto()


class BayesChartaTyp(Enum):
    BAYESCHARTA = auto()
    POSTERIORVERTEILUNG = auto()
    PRIORWISSEN = auto()


class BayesChartaProzedur(Enum):
    BAYESANALYSE = auto()
    POSTERIORBERECHNUNG = auto()
    BAYESBEWERTUNG = auto()


_WEIGHT_DELTA: dict[BayesChartaGeltung, float] = {
    BayesChartaGeltung.GESPERRT: 0.0,
    BayesChartaGeltung.GRUNDLEGEND_BAYESIANISCH: 1.4,
    BayesChartaGeltung.BAYESIANISCH: 2.8,
    BayesChartaGeltung.BAYESIANISCH_AKTIV: 4.2,
    BayesChartaGeltung.BAYES_SOUVERAEN: 5.6,
}

_TYP_MAP = {
    BayesChartaGeltung.GESPERRT: BayesChartaTyp.BAYESCHARTA,
    BayesChartaGeltung.GRUNDLEGEND_BAYESIANISCH: BayesChartaTyp.PRIORWISSEN,
    BayesChartaGeltung.BAYESIANISCH: BayesChartaTyp.PRIORWISSEN,
    BayesChartaGeltung.BAYESIANISCH_AKTIV: BayesChartaTyp.POSTERIORVERTEILUNG,
    BayesChartaGeltung.BAYES_SOUVERAEN: BayesChartaTyp.POSTERIORVERTEILUNG,
}

_PROZEDUR_MAP = {
    BayesChartaGeltung.GESPERRT: BayesChartaProzedur.BAYESANALYSE,
    BayesChartaGeltung.GRUNDLEGEND_BAYESIANISCH: BayesChartaProzedur.BAYESANALYSE,
    BayesChartaGeltung.BAYESIANISCH: BayesChartaProzedur.POSTERIORBERECHNUNG,
    BayesChartaGeltung.BAYESIANISCH_AKTIV: BayesChartaProzedur.POSTERIORBERECHNUNG,
    BayesChartaGeltung.BAYES_SOUVERAEN: BayesChartaProzedur.BAYESBEWERTUNG,
}


@dataclass(frozen=True)
class BayesChartaNorm:
    geltung: BayesChartaGeltung
    stat_weight: float
    stat_tier: int
    stat_ids: tuple[str, ...]
    stat_tags: tuple[str, ...]
    typ: BayesChartaTyp
    prozedur: BayesChartaProzedur
    canonical: bool = True


@dataclass(frozen=True)
class BayesCharta:
    normen: tuple[BayesChartaNorm, ...]
    parent: Optional[WahrscheinlichkeitRegister] = None


def build_bayes_charta(parent: Optional[WahrscheinlichkeitRegister] = None) -> BayesCharta:
    if parent is None:
        parent = build_wahrscheinlichkeit_register()
    base = sum(e.stat_weight for e in parent.eintraege)
    normen = tuple(
        BayesChartaNorm(
            geltung=g,
            stat_weight=round(base + _WEIGHT_DELTA[g], 4),
            stat_tier=i + 1,
            stat_ids=(f"bayes-charta-{g.name.lower()}-001",),
            stat_tags=("bayes", "charta", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(BayesChartaGeltung)
    )
    return BayesCharta(normen=normen, parent=parent)
