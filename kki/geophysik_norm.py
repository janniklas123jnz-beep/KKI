from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .geophysik_senat import GeophysikSenat, build_geophysik_senat


class GeophysikNormGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_GEOPHYSIK_NORMATIV = auto()
    GEOPHYSIK_NORMATIV = auto()
    GEOPHYSIK_NORMATIV_AKTIV = auto()
    GEOPHYSIK_NORMATIV_SOUVERAEN = auto()


class GeophysikNormTyp(Enum):
    GEOPHYSIKNORM = auto()
    GEOPHYSIKSTANDARD = auto()
    GEOPHYSIKRICHTLINIE = auto()


class GeophysikNormProzedur(Enum):
    GEOPHYSIKNORMIERUNG = auto()
    GEOPHYSIKSTANDARDISIERUNG = auto()
    GEOPHYSIKZERTIFIZIERUNG = auto()


_WEIGHT_DELTA: dict[str, float] = {
    "GESPERRT": 0.0,
    "GRUNDLEGEND_GEOPHYSIK_NORMATIV": 1.9,
    "GEOPHYSIK_NORMATIV": 3.8,
    "GEOPHYSIK_NORMATIV_AKTIV": 5.7,
    "GEOPHYSIK_NORMATIV_SOUVERAEN": 7.6,
}

_TYP_MAP: dict[str, GeophysikNormTyp] = {
    "GESPERRT": GeophysikNormTyp.GEOPHYSIKNORM,
    "GRUNDLEGEND_GEOPHYSIK_NORMATIV": GeophysikNormTyp.GEOPHYSIKRICHTLINIE,
    "GEOPHYSIK_NORMATIV": GeophysikNormTyp.GEOPHYSIKRICHTLINIE,
    "GEOPHYSIK_NORMATIV_AKTIV": GeophysikNormTyp.GEOPHYSIKSTANDARD,
    "GEOPHYSIK_NORMATIV_SOUVERAEN": GeophysikNormTyp.GEOPHYSIKSTANDARD,
}

_PROZEDUR_MAP: dict[str, GeophysikNormProzedur] = {
    "GESPERRT": GeophysikNormProzedur.GEOPHYSIKNORMIERUNG,
    "GRUNDLEGEND_GEOPHYSIK_NORMATIV": GeophysikNormProzedur.GEOPHYSIKNORMIERUNG,
    "GEOPHYSIK_NORMATIV": GeophysikNormProzedur.GEOPHYSIKSTANDARDISIERUNG,
    "GEOPHYSIK_NORMATIV_AKTIV": GeophysikNormProzedur.GEOPHYSIKSTANDARDISIERUNG,
    "GEOPHYSIK_NORMATIV_SOUVERAEN": GeophysikNormProzedur.GEOPHYSIKZERTIFIZIERUNG,
}

_GELTUNG_KEY_MAP: dict[GeophysikNormGeltung, str] = {g: g.name for g in GeophysikNormGeltung}


@dataclass(frozen=True)
class GeophysikNormEintrag:
    geltung: GeophysikNormGeltung
    geophysik_norm_weight: float
    geophysik_norm_tier: int
    geophysik_norm_ids: tuple[str, ...]
    geophysik_norm_tags: tuple[str, ...]
    typ: GeophysikNormTyp
    prozedur: GeophysikNormProzedur
    canonical: bool = True


@dataclass(frozen=True)
class GeophysikNormSatz:
    normen: tuple[GeophysikNormEintrag, ...]
    parent: Optional[GeophysikSenat] = None


def build_geophysik_norm(parent: Optional[GeophysikSenat] = None) -> GeophysikNormSatz:
    if parent is None:
        parent = build_geophysik_senat()
    base = sum(n.geophysik_weight for n in parent.normen)
    eintraege = []
    for i, g in enumerate(GeophysikNormGeltung):
        key = _GELTUNG_KEY_MAP[g]
        eintraege.append(GeophysikNormEintrag(
            geltung=g,
            geophysik_norm_weight=round(base + _WEIGHT_DELTA[key], 4),
            geophysik_norm_tier=i + 1,
            geophysik_norm_ids=(f"geophysik-norm-{key.lower()}-001",),
            geophysik_norm_tags=("geophysik", "norm", key.lower()),
            typ=_TYP_MAP[key],
            prozedur=_PROZEDUR_MAP[key],
        ))
    return GeophysikNormSatz(normen=tuple(eintraege), parent=parent)
