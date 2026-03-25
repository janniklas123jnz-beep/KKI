from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .bewegungslehre_senat import BewegungslehreSenat, build_bewegungslehre_senat


class SportNormGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_SPORT_NORMATIV = auto()
    SPORT_NORMATIV = auto()
    SPORT_NORMATIV_AKTIV = auto()
    SPORT_NORMATIV_SOUVERAEN = auto()


class SportNormTyp(Enum):
    SPORTNORM = auto()
    SPORTSTANDARD = auto()
    SPORTRICHTLINIE = auto()


class SportNormProzedur(Enum):
    SPORTNORMIERUNG = auto()
    SPORTSTANDARDISIERUNG = auto()
    SPORTZERTIFIZIERUNG = auto()


_WEIGHT_DELTA: dict[str, float] = {
    "GESPERRT": 0.0,
    "GRUNDLEGEND_SPORT_NORMATIV": 1.9,
    "SPORT_NORMATIV": 3.8,
    "SPORT_NORMATIV_AKTIV": 5.7,
    "SPORT_NORMATIV_SOUVERAEN": 7.6,
}

_TYP_MAP: dict[str, SportNormTyp] = {
    "GESPERRT": SportNormTyp.SPORTNORM,
    "GRUNDLEGEND_SPORT_NORMATIV": SportNormTyp.SPORTRICHTLINIE,
    "SPORT_NORMATIV": SportNormTyp.SPORTRICHTLINIE,
    "SPORT_NORMATIV_AKTIV": SportNormTyp.SPORTSTANDARD,
    "SPORT_NORMATIV_SOUVERAEN": SportNormTyp.SPORTSTANDARD,
}

_PROZEDUR_MAP: dict[str, SportNormProzedur] = {
    "GESPERRT": SportNormProzedur.SPORTNORMIERUNG,
    "GRUNDLEGEND_SPORT_NORMATIV": SportNormProzedur.SPORTNORMIERUNG,
    "SPORT_NORMATIV": SportNormProzedur.SPORTSTANDARDISIERUNG,
    "SPORT_NORMATIV_AKTIV": SportNormProzedur.SPORTSTANDARDISIERUNG,
    "SPORT_NORMATIV_SOUVERAEN": SportNormProzedur.SPORTZERTIFIZIERUNG,
}

_GELTUNG_KEY_MAP: dict[SportNormGeltung, str] = {g: g.name for g in SportNormGeltung}

_GELTUNG_MAP: dict[str, SportNormGeltung] = {
    "gesperrt": SportNormGeltung.GESPERRT,
    "grundlegend_bewegungswissenschaftlich": SportNormGeltung.GRUNDLEGEND_SPORT_NORMATIV,
    "bewegungswissenschaftlich": SportNormGeltung.SPORT_NORMATIV,
    "bewegungswissenschaftlich_aktiv": SportNormGeltung.SPORT_NORMATIV_AKTIV,
    "bewegungslehre_souveraen": SportNormGeltung.SPORT_NORMATIV_SOUVERAEN,
}


@dataclass(frozen=True)
class SportNormEintrag:
    geltung: SportNormGeltung
    sport_norm_weight: float
    sport_norm_tier: int
    sport_norm_ids: tuple[str, ...]
    sport_norm_tags: tuple[str, ...]
    typ: SportNormTyp
    prozedur: SportNormProzedur
    canonical: bool = True


@dataclass(frozen=True)
class SportNormSatz:
    normen: tuple[SportNormEintrag, ...]
    parent: Optional[BewegungslehreSenat] = None


def build_sport_norm(parent: Optional[BewegungslehreSenat] = None) -> SportNormSatz:
    if parent is None:
        parent = build_bewegungslehre_senat()
    base = sum(n.sport_weight for n in parent.normen)
    eintraege = []
    for i, g in enumerate(SportNormGeltung):
        key = _GELTUNG_KEY_MAP[g]
        eintraege.append(SportNormEintrag(
            geltung=g,
            sport_norm_weight=round(base + _WEIGHT_DELTA[key], 4),
            sport_norm_tier=i + 1,
            sport_norm_ids=(f"sport-norm-{key.lower()}-001",),
            sport_norm_tags=("sport", "norm", key.lower()),
            typ=_TYP_MAP[key],
            prozedur=_PROZEDUR_MAP[key],
        ))
    return SportNormSatz(normen=tuple(eintraege), parent=parent)
