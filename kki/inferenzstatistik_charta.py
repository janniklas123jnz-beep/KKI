from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .statistik_norm import StatistikNormSatz, build_statistik_norm


class InferenzstatistikChartaGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_INFERENZIELL = auto()
    INFERENZIELL = auto()
    INFERENZIELL_AKTIV = auto()
    INFERENZ_SOUVERAEN = auto()


class InferenzstatistikChartaTyp(Enum):
    INFERENZSTATISTIKCHARTA = auto()
    KONFIDENZINTERVALL = auto()
    SCHAETZVERFAHREN = auto()


class InferenzstatistikChartaProzedur(Enum):
    INFERENZANALYSE = auto()
    SCHAETZBERECHNUNG = auto()
    INFERENZBEWERTUNG = auto()


_WEIGHT_DELTA: dict[InferenzstatistikChartaGeltung, float] = {
    InferenzstatistikChartaGeltung.GESPERRT: 0.0,
    InferenzstatistikChartaGeltung.GRUNDLEGEND_INFERENZIELL: 2.0,
    InferenzstatistikChartaGeltung.INFERENZIELL: 4.0,
    InferenzstatistikChartaGeltung.INFERENZIELL_AKTIV: 6.0,
    InferenzstatistikChartaGeltung.INFERENZ_SOUVERAEN: 8.0,
}

_TYP_MAP = {
    InferenzstatistikChartaGeltung.GESPERRT: InferenzstatistikChartaTyp.INFERENZSTATISTIKCHARTA,
    InferenzstatistikChartaGeltung.GRUNDLEGEND_INFERENZIELL: InferenzstatistikChartaTyp.SCHAETZVERFAHREN,
    InferenzstatistikChartaGeltung.INFERENZIELL: InferenzstatistikChartaTyp.SCHAETZVERFAHREN,
    InferenzstatistikChartaGeltung.INFERENZIELL_AKTIV: InferenzstatistikChartaTyp.KONFIDENZINTERVALL,
    InferenzstatistikChartaGeltung.INFERENZ_SOUVERAEN: InferenzstatistikChartaTyp.KONFIDENZINTERVALL,
}

_PROZEDUR_MAP = {
    InferenzstatistikChartaGeltung.GESPERRT: InferenzstatistikChartaProzedur.INFERENZANALYSE,
    InferenzstatistikChartaGeltung.GRUNDLEGEND_INFERENZIELL: InferenzstatistikChartaProzedur.INFERENZANALYSE,
    InferenzstatistikChartaGeltung.INFERENZIELL: InferenzstatistikChartaProzedur.SCHAETZBERECHNUNG,
    InferenzstatistikChartaGeltung.INFERENZIELL_AKTIV: InferenzstatistikChartaProzedur.SCHAETZBERECHNUNG,
    InferenzstatistikChartaGeltung.INFERENZ_SOUVERAEN: InferenzstatistikChartaProzedur.INFERENZBEWERTUNG,
}


@dataclass(frozen=True)
class InferenzstatistikChartaNorm:
    geltung: InferenzstatistikChartaGeltung
    stat_weight: float
    stat_tier: int
    stat_ids: tuple[str, ...]
    stat_tags: tuple[str, ...]
    typ: InferenzstatistikChartaTyp
    prozedur: InferenzstatistikChartaProzedur
    canonical: bool = True


@dataclass(frozen=True)
class InferenzstatistikCharta:
    normen: tuple[InferenzstatistikChartaNorm, ...]
    parent: Optional[StatistikNormSatz] = None


def build_inferenzstatistik_charta(parent: Optional[StatistikNormSatz] = None) -> InferenzstatistikCharta:
    if parent is None:
        parent = build_statistik_norm()
    base = sum(e.stat_norm_weight for e in parent.normen)
    tier_base = max(e.stat_norm_tier for e in parent.normen)
    normen = tuple(
        InferenzstatistikChartaNorm(
            geltung=g,
            stat_weight=round(base + _WEIGHT_DELTA[g], 4),
            stat_tier=tier_base + i + 1,
            stat_ids=(f"inferenzstatistik-charta-{g.name.lower()}-001",),
            stat_tags=("inferenzstatistik", "charta", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(InferenzstatistikChartaGeltung)
    )
    return InferenzstatistikCharta(normen=normen, parent=parent)
