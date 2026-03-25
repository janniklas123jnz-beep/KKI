from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .biomechanik_register import BiomechanikRegister, build_biomechanik_register


class TrainingslehreChartaGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_TRAININGSWISSENSCHAFTLICH = auto()
    TRAININGSWISSENSCHAFTLICH = auto()
    TRAININGSWISSENSCHAFTLICH_AKTIV = auto()
    TRAININGSLEHRE_SOUVERAEN = auto()


class TrainingslehreChartaTyp(Enum):
    TRAININGSLEHRER_CHARTA = auto()
    PERIODISIERUNGSPLAN = auto()
    BELASTUNGSSTEUERUNG = auto()


class TrainingslehreChartaProzedur(Enum):
    TRAININGSPLANUNG = auto()
    BELASTUNGSANALYSE = auto()
    ADAPTATIONSBEWERTUNG = auto()


_WEIGHT_DELTA: dict[TrainingslehreChartaGeltung, float] = {
    TrainingslehreChartaGeltung.GESPERRT: 0.0,
    TrainingslehreChartaGeltung.GRUNDLEGEND_TRAININGSWISSENSCHAFTLICH: 1.4,
    TrainingslehreChartaGeltung.TRAININGSWISSENSCHAFTLICH: 2.8,
    TrainingslehreChartaGeltung.TRAININGSWISSENSCHAFTLICH_AKTIV: 4.2,
    TrainingslehreChartaGeltung.TRAININGSLEHRE_SOUVERAEN: 5.6,
}

_TYP_MAP = {
    TrainingslehreChartaGeltung.GESPERRT: TrainingslehreChartaTyp.TRAININGSLEHRER_CHARTA,
    TrainingslehreChartaGeltung.GRUNDLEGEND_TRAININGSWISSENSCHAFTLICH: TrainingslehreChartaTyp.PERIODISIERUNGSPLAN,
    TrainingslehreChartaGeltung.TRAININGSWISSENSCHAFTLICH: TrainingslehreChartaTyp.PERIODISIERUNGSPLAN,
    TrainingslehreChartaGeltung.TRAININGSWISSENSCHAFTLICH_AKTIV: TrainingslehreChartaTyp.BELASTUNGSSTEUERUNG,
    TrainingslehreChartaGeltung.TRAININGSLEHRE_SOUVERAEN: TrainingslehreChartaTyp.BELASTUNGSSTEUERUNG,
}

_PROZEDUR_MAP = {
    TrainingslehreChartaGeltung.GESPERRT: TrainingslehreChartaProzedur.TRAININGSPLANUNG,
    TrainingslehreChartaGeltung.GRUNDLEGEND_TRAININGSWISSENSCHAFTLICH: TrainingslehreChartaProzedur.TRAININGSPLANUNG,
    TrainingslehreChartaGeltung.TRAININGSWISSENSCHAFTLICH: TrainingslehreChartaProzedur.BELASTUNGSANALYSE,
    TrainingslehreChartaGeltung.TRAININGSWISSENSCHAFTLICH_AKTIV: TrainingslehreChartaProzedur.BELASTUNGSANALYSE,
    TrainingslehreChartaGeltung.TRAININGSLEHRE_SOUVERAEN: TrainingslehreChartaProzedur.ADAPTATIONSBEWERTUNG,
}


@dataclass(frozen=True)
class TrainingslehreChartaNorm:
    geltung: TrainingslehreChartaGeltung
    sport_weight: float
    sport_tier: int
    sport_ids: tuple[str, ...]
    sport_tags: tuple[str, ...]
    typ: TrainingslehreChartaTyp
    prozedur: TrainingslehreChartaProzedur
    canonical: bool = True


@dataclass(frozen=True)
class TrainingslehreCharta:
    normen: tuple[TrainingslehreChartaNorm, ...]
    parent: Optional[BiomechanikRegister] = None


def build_trainingslehre_charta(parent: Optional[BiomechanikRegister] = None) -> TrainingslehreCharta:
    if parent is None:
        parent = build_biomechanik_register()
    base = sum(e.sport_weight for e in parent.eintraege)
    normen = tuple(
        TrainingslehreChartaNorm(
            geltung=g,
            sport_weight=round(base + _WEIGHT_DELTA[g], 4),
            sport_tier=i + 1,
            sport_ids=(f"trainingslehre-{g.name.lower()}-001",),
            sport_tags=("trainingslehre", "charta", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(TrainingslehreChartaGeltung)
    )
    return TrainingslehreCharta(normen=normen, parent=parent)
