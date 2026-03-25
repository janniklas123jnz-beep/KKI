from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .ozeanographie_senat import OzeanographieSenat, build_ozeanographie_senat


class OzeanNormGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_OZEAN_NORMATIV = auto()
    OZEAN_NORMATIV = auto()
    OZEAN_NORMATIV_AKTIV = auto()
    OZEAN_NORMATIV_SOUVERAEN = auto()


class OzeanNormTyp(Enum):
    OZEANNORM = auto()
    OZEANSTANDARD = auto()
    OZEANRICHTLINIE = auto()


class OzeanNormProzedur(Enum):
    OZEANNORMIERUNG = auto()
    OZEANSTANDARDISIERUNG = auto()
    OZEANZERTIFIZIERUNG = auto()


_WEIGHT_DELTA: dict[str, float] = {
    "GESPERRT": 0.0,
    "GRUNDLEGEND_OZEAN_NORMATIV": 1.9,
    "OZEAN_NORMATIV": 3.8,
    "OZEAN_NORMATIV_AKTIV": 5.7,
    "OZEAN_NORMATIV_SOUVERAEN": 7.6,
}

_TYP_MAP: dict[str, OzeanNormTyp] = {
    "GESPERRT": OzeanNormTyp.OZEANNORM,
    "GRUNDLEGEND_OZEAN_NORMATIV": OzeanNormTyp.OZEANRICHTLINIE,
    "OZEAN_NORMATIV": OzeanNormTyp.OZEANRICHTLINIE,
    "OZEAN_NORMATIV_AKTIV": OzeanNormTyp.OZEANSTANDARD,
    "OZEAN_NORMATIV_SOUVERAEN": OzeanNormTyp.OZEANSTANDARD,
}

_PROZEDUR_MAP: dict[str, OzeanNormProzedur] = {
    "GESPERRT": OzeanNormProzedur.OZEANNORMIERUNG,
    "GRUNDLEGEND_OZEAN_NORMATIV": OzeanNormProzedur.OZEANNORMIERUNG,
    "OZEAN_NORMATIV": OzeanNormProzedur.OZEANSTANDARDISIERUNG,
    "OZEAN_NORMATIV_AKTIV": OzeanNormProzedur.OZEANSTANDARDISIERUNG,
    "OZEAN_NORMATIV_SOUVERAEN": OzeanNormProzedur.OZEANZERTIFIZIERUNG,
}

_GELTUNG_KEY_MAP: dict[OzeanNormGeltung, str] = {g: g.name for g in OzeanNormGeltung}


@dataclass(frozen=True)
class OzeanNormEintrag:
    geltung: OzeanNormGeltung
    ozean_norm_weight: float
    ozean_norm_tier: int
    ozean_norm_ids: tuple[str, ...]
    ozean_norm_tags: tuple[str, ...]
    typ: OzeanNormTyp
    prozedur: OzeanNormProzedur
    canonical: bool = True


@dataclass(frozen=True)
class OzeanNormSatz:
    normen: tuple[OzeanNormEintrag, ...]
    parent: Optional[OzeanographieSenat] = None


def build_ozean_norm(parent: Optional[OzeanographieSenat] = None) -> OzeanNormSatz:
    if parent is None:
        parent = build_ozeanographie_senat()
    base = sum(n.ozean_weight for n in parent.normen)
    eintraege = []
    for i, g in enumerate(OzeanNormGeltung):
        key = _GELTUNG_KEY_MAP[g]
        eintraege.append(OzeanNormEintrag(
            geltung=g,
            ozean_norm_weight=round(base + _WEIGHT_DELTA[key], 4),
            ozean_norm_tier=i + 1,
            ozean_norm_ids=(f"ozean-norm-{key.lower()}-001",),
            ozean_norm_tags=("ozean", "norm", key.lower()),
            typ=_TYP_MAP[key],
            prozedur=_PROZEDUR_MAP[key],
        ))
    return OzeanNormSatz(normen=tuple(eintraege), parent=parent)
