from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .palaeontologie_senat import PalaeontologieSenat, build_palaeontologie_senat


class PalaeontologieNormGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_PALAEONTOLOGIE_NORMATIV = auto()
    PALAEONTOLOGIE_NORMATIV = auto()
    PALAEONTOLOGIE_NORMATIV_AKTIV = auto()
    PALAEONTOLOGIE_NORMATIV_SOUVERAEN = auto()


class PalaeontologieNormTyp(Enum):
    PALAEONTOLOGIENORM = auto()
    PALAEONTOLOGIESTANDARD = auto()
    PALAEONTOLOGIERICHTLINIE = auto()


class PalaeontologieNormProzedur(Enum):
    PALAEONTOLOGIENORMIERUNG = auto()
    PALAEONTOLOGIESTANDARDISIERUNG = auto()
    PALAEONTOLOGIEZERTIFIZIERUNG = auto()


_WEIGHT_DELTA: dict[str, float] = {
    "GESPERRT": 0.0,
    "GRUNDLEGEND_PALAEONTOLOGIE_NORMATIV": 1.9,
    "PALAEONTOLOGIE_NORMATIV": 3.8,
    "PALAEONTOLOGIE_NORMATIV_AKTIV": 5.7,
    "PALAEONTOLOGIE_NORMATIV_SOUVERAEN": 7.6,
}

_TYP_MAP: dict[str, PalaeontologieNormTyp] = {
    "GESPERRT": PalaeontologieNormTyp.PALAEONTOLOGIENORM,
    "GRUNDLEGEND_PALAEONTOLOGIE_NORMATIV": PalaeontologieNormTyp.PALAEONTOLOGIERICHTLINIE,
    "PALAEONTOLOGIE_NORMATIV": PalaeontologieNormTyp.PALAEONTOLOGIERICHTLINIE,
    "PALAEONTOLOGIE_NORMATIV_AKTIV": PalaeontologieNormTyp.PALAEONTOLOGIESTANDARD,
    "PALAEONTOLOGIE_NORMATIV_SOUVERAEN": PalaeontologieNormTyp.PALAEONTOLOGIESTANDARD,
}

_PROZEDUR_MAP: dict[str, PalaeontologieNormProzedur] = {
    "GESPERRT": PalaeontologieNormProzedur.PALAEONTOLOGIENORMIERUNG,
    "GRUNDLEGEND_PALAEONTOLOGIE_NORMATIV": PalaeontologieNormProzedur.PALAEONTOLOGIENORMIERUNG,
    "PALAEONTOLOGIE_NORMATIV": PalaeontologieNormProzedur.PALAEONTOLOGIESTANDARDISIERUNG,
    "PALAEONTOLOGIE_NORMATIV_AKTIV": PalaeontologieNormProzedur.PALAEONTOLOGIESTANDARDISIERUNG,
    "PALAEONTOLOGIE_NORMATIV_SOUVERAEN": PalaeontologieNormProzedur.PALAEONTOLOGIEZERTIFIZIERUNG,
}

_GELTUNG_KEY_MAP: dict[PalaeontologieNormGeltung, str] = {g: g.name for g in PalaeontologieNormGeltung}


@dataclass(frozen=True)
class PalaeontologieNormEintrag:
    geltung: PalaeontologieNormGeltung
    palaeontologie_norm_weight: float
    palaeontologie_norm_tier: int
    palaeontologie_norm_ids: tuple[str, ...]
    palaeontologie_norm_tags: tuple[str, ...]
    typ: PalaeontologieNormTyp
    prozedur: PalaeontologieNormProzedur
    canonical: bool = True


@dataclass(frozen=True)
class PalaeontologieNormSatz:
    normen: tuple[PalaeontologieNormEintrag, ...]
    parent: Optional[PalaeontologieSenat] = None


def build_palaeontologie_norm(parent: Optional[PalaeontologieSenat] = None) -> PalaeontologieNormSatz:
    if parent is None:
        parent = build_palaeontologie_senat()
    base = sum(n.palaeontologie_weight for n in parent.normen)
    eintraege = []
    for i, g in enumerate(PalaeontologieNormGeltung):
        key = _GELTUNG_KEY_MAP[g]
        eintraege.append(PalaeontologieNormEintrag(
            geltung=g,
            palaeontologie_norm_weight=round(base + _WEIGHT_DELTA[key], 4),
            palaeontologie_norm_tier=i + 1,
            palaeontologie_norm_ids=(f"palaeontologie-norm-{key.lower()}-001",),
            palaeontologie_norm_tags=("palaeontologie", "norm", key.lower()),
            typ=_TYP_MAP[key],
            prozedur=_PROZEDUR_MAP[key],
        ))
    return PalaeontologieNormSatz(normen=tuple(eintraege), parent=parent)
