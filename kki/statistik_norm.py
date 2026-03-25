from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .stochastik_senat import StochastikSenat, build_stochastik_senat


class StatistikNormGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_STAT_NORMATIV = auto()
    STAT_NORMATIV = auto()
    STAT_NORMATIV_AKTIV = auto()
    STAT_NORMATIV_SOUVERAEN = auto()


class StatistikNormTyp(Enum):
    STATISTIKNORM = auto()
    STATISTIKSTANDARD = auto()
    STATISTIKRICHTLINIE = auto()


class StatistikNormProzedur(Enum):
    STATISTIKNORMIERUNG = auto()
    STATISTIKSTANDARDISIERUNG = auto()
    STATISTIKZERTIFIZIERUNG = auto()


_WEIGHT_DELTA: dict[str, float] = {
    "GESPERRT": 0.0,
    "GRUNDLEGEND_STAT_NORMATIV": 1.9,
    "STAT_NORMATIV": 3.8,
    "STAT_NORMATIV_AKTIV": 5.7,
    "STAT_NORMATIV_SOUVERAEN": 7.6,
}

_TYP_MAP: dict[str, StatistikNormTyp] = {
    "GESPERRT": StatistikNormTyp.STATISTIKNORM,
    "GRUNDLEGEND_STAT_NORMATIV": StatistikNormTyp.STATISTIKRICHTLINIE,
    "STAT_NORMATIV": StatistikNormTyp.STATISTIKRICHTLINIE,
    "STAT_NORMATIV_AKTIV": StatistikNormTyp.STATISTIKSTANDARD,
    "STAT_NORMATIV_SOUVERAEN": StatistikNormTyp.STATISTIKSTANDARD,
}

_PROZEDUR_MAP: dict[str, StatistikNormProzedur] = {
    "GESPERRT": StatistikNormProzedur.STATISTIKNORMIERUNG,
    "GRUNDLEGEND_STAT_NORMATIV": StatistikNormProzedur.STATISTIKNORMIERUNG,
    "STAT_NORMATIV": StatistikNormProzedur.STATISTIKSTANDARDISIERUNG,
    "STAT_NORMATIV_AKTIV": StatistikNormProzedur.STATISTIKSTANDARDISIERUNG,
    "STAT_NORMATIV_SOUVERAEN": StatistikNormProzedur.STATISTIKZERTIFIZIERUNG,
}

_GELTUNG_KEY_MAP: dict[StatistikNormGeltung, str] = {g: g.name for g in StatistikNormGeltung}

_GELTUNG_MAP: dict[str, StatistikNormGeltung] = {
    "gesperrt": StatistikNormGeltung.GESPERRT,
    "grundlegend_stochastisch": StatistikNormGeltung.GRUNDLEGEND_STAT_NORMATIV,
    "stochastisch": StatistikNormGeltung.STAT_NORMATIV,
    "stochastisch_aktiv": StatistikNormGeltung.STAT_NORMATIV_AKTIV,
    "stochastik_souveraen": StatistikNormGeltung.STAT_NORMATIV_SOUVERAEN,
}


@dataclass(frozen=True)
class StatistikNormEintrag:
    geltung: StatistikNormGeltung
    stat_norm_weight: float
    stat_norm_tier: int
    stat_norm_ids: tuple[str, ...]
    stat_norm_tags: tuple[str, ...]
    typ: StatistikNormTyp
    prozedur: StatistikNormProzedur
    canonical: bool = True


@dataclass(frozen=True)
class StatistikNormSatz:
    normen: tuple[StatistikNormEintrag, ...]
    parent: Optional[StochastikSenat] = None


def build_statistik_norm(parent: Optional[StochastikSenat] = None) -> StatistikNormSatz:
    if parent is None:
        parent = build_stochastik_senat()
    base = sum(n.stat_weight for n in parent.normen)
    eintraege = []
    for i, g in enumerate(StatistikNormGeltung):
        key = _GELTUNG_KEY_MAP[g]
        eintraege.append(StatistikNormEintrag(
            geltung=g,
            stat_norm_weight=round(base + _WEIGHT_DELTA[key], 4),
            stat_norm_tier=i + 1,
            stat_norm_ids=(f"statistik-norm-{key.lower()}-001",),
            stat_norm_tags=("statistik", "norm", key.lower()),
            typ=_TYP_MAP[key],
            prozedur=_PROZEDUR_MAP[key],
        ))
    return StatistikNormSatz(normen=tuple(eintraege), parent=parent)
