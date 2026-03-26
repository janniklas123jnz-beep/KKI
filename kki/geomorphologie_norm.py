from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .geomorphologie_senat import GeomorphologieSenat, build_geomorphologie_senat


class GeomorphologieNormGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_GEOMORPHOLOGIE_NORMATIV = auto()
    GEOMORPHOLOGIE_NORMATIV = auto()
    GEOMORPHOLOGIE_NORMATIV_AKTIV = auto()
    GEOMORPHOLOGIE_NORMATIV_SOUVERAEN = auto()


class GeomorphologieNormTyp(Enum):
    GEOMORPHOLOGIENORM = auto()
    GEOMORPHOLOGIESTANDARD = auto()
    GEOMORPHOLOGIERICHTLINIE = auto()


class GeomorphologieNormProzedur(Enum):
    GEOMORPHOLOGIENORMIERUNG = auto()
    GEOMORPHOLOGIESTANDARDISIERUNG = auto()
    GEOMORPHOLOGIEZERTIFIZIERUNG = auto()


_WEIGHT_DELTA: dict[str, float] = {
    "GESPERRT": 0.0,
    "GRUNDLEGEND_GEOMORPHOLOGIE_NORMATIV": 1.9,
    "GEOMORPHOLOGIE_NORMATIV": 3.8,
    "GEOMORPHOLOGIE_NORMATIV_AKTIV": 5.7,
    "GEOMORPHOLOGIE_NORMATIV_SOUVERAEN": 7.6,
}

_TYP_MAP: dict[str, GeomorphologieNormTyp] = {
    "GESPERRT": GeomorphologieNormTyp.GEOMORPHOLOGIENORM,
    "GRUNDLEGEND_GEOMORPHOLOGIE_NORMATIV": GeomorphologieNormTyp.GEOMORPHOLOGIERICHTLINIE,
    "GEOMORPHOLOGIE_NORMATIV": GeomorphologieNormTyp.GEOMORPHOLOGIERICHTLINIE,
    "GEOMORPHOLOGIE_NORMATIV_AKTIV": GeomorphologieNormTyp.GEOMORPHOLOGIESTANDARD,
    "GEOMORPHOLOGIE_NORMATIV_SOUVERAEN": GeomorphologieNormTyp.GEOMORPHOLOGIESTANDARD,
}

_PROZEDUR_MAP: dict[str, GeomorphologieNormProzedur] = {
    "GESPERRT": GeomorphologieNormProzedur.GEOMORPHOLOGIENORMIERUNG,
    "GRUNDLEGEND_GEOMORPHOLOGIE_NORMATIV": GeomorphologieNormProzedur.GEOMORPHOLOGIENORMIERUNG,
    "GEOMORPHOLOGIE_NORMATIV": GeomorphologieNormProzedur.GEOMORPHOLOGIESTANDARDISIERUNG,
    "GEOMORPHOLOGIE_NORMATIV_AKTIV": GeomorphologieNormProzedur.GEOMORPHOLOGIESTANDARDISIERUNG,
    "GEOMORPHOLOGIE_NORMATIV_SOUVERAEN": GeomorphologieNormProzedur.GEOMORPHOLOGIEZERTIFIZIERUNG,
}

_GELTUNG_KEY_MAP: dict[GeomorphologieNormGeltung, str] = {g: g.name for g in GeomorphologieNormGeltung}


@dataclass(frozen=True)
class GeomorphologieNormEintrag:
    geltung: GeomorphologieNormGeltung
    geomorphologie_norm_weight: float
    geomorphologie_norm_tier: int
    geomorphologie_norm_ids: tuple[str, ...]
    geomorphologie_norm_tags: tuple[str, ...]
    typ: GeomorphologieNormTyp
    prozedur: GeomorphologieNormProzedur
    canonical: bool = True


@dataclass(frozen=True)
class GeomorphologieNormSatz:
    normen: tuple[GeomorphologieNormEintrag, ...]
    parent: Optional[GeomorphologieSenat] = None


def build_geomorphologie_norm(parent: Optional[GeomorphologieSenat] = None) -> GeomorphologieNormSatz:
    if parent is None:
        parent = build_geomorphologie_senat()
    base = sum(n.geomorphologie_weight for n in parent.normen)
    eintraege = []
    for i, g in enumerate(GeomorphologieNormGeltung):
        key = _GELTUNG_KEY_MAP[g]
        eintraege.append(GeomorphologieNormEintrag(
            geltung=g,
            geomorphologie_norm_weight=round(base + _WEIGHT_DELTA[key], 4),
            geomorphologie_norm_tier=i + 1,
            geomorphologie_norm_ids=(f"geomorphologie-norm-{key.lower()}-001",),
            geomorphologie_norm_tags=("geomorphologie", "norm", key.lower()),
            typ=_TYP_MAP[key],
            prozedur=_PROZEDUR_MAP[key],
        ))
    return GeomorphologieNormSatz(normen=tuple(eintraege), parent=parent)
