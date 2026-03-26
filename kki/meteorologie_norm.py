from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .meteorologie_senat import MeteorologieSenat, build_meteorologie_senat


class MeteorologieNormGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_METEOROLOGIE_NORMATIV = auto()
    METEOROLOGIE_NORMATIV = auto()
    METEOROLOGIE_NORMATIV_AKTIV = auto()
    METEOROLOGIE_NORMATIV_SOUVERAEN = auto()


class MeteorologieNormTyp(Enum):
    METEOROLOGIENORM = auto()
    METEOROLOGIESTANDARD = auto()
    METEOROLOGIERICHTLINIE = auto()


class MeteorologieNormProzedur(Enum):
    METEOROLOGIENORMIERUNG = auto()
    METEOROLOGIESTANDARDISIERUNG = auto()
    METEOROLOGIEZERTIFIZIERUNG = auto()


_WEIGHT_DELTA: dict[str, float] = {
    "GESPERRT": 0.0,
    "GRUNDLEGEND_METEOROLOGIE_NORMATIV": 1.9,
    "METEOROLOGIE_NORMATIV": 3.8,
    "METEOROLOGIE_NORMATIV_AKTIV": 5.7,
    "METEOROLOGIE_NORMATIV_SOUVERAEN": 7.6,
}

_TYP_MAP: dict[str, MeteorologieNormTyp] = {
    "GESPERRT": MeteorologieNormTyp.METEOROLOGIENORM,
    "GRUNDLEGEND_METEOROLOGIE_NORMATIV": MeteorologieNormTyp.METEOROLOGIERICHTLINIE,
    "METEOROLOGIE_NORMATIV": MeteorologieNormTyp.METEOROLOGIERICHTLINIE,
    "METEOROLOGIE_NORMATIV_AKTIV": MeteorologieNormTyp.METEOROLOGIESTANDARD,
    "METEOROLOGIE_NORMATIV_SOUVERAEN": MeteorologieNormTyp.METEOROLOGIESTANDARD,
}

_PROZEDUR_MAP: dict[str, MeteorologieNormProzedur] = {
    "GESPERRT": MeteorologieNormProzedur.METEOROLOGIENORMIERUNG,
    "GRUNDLEGEND_METEOROLOGIE_NORMATIV": MeteorologieNormProzedur.METEOROLOGIENORMIERUNG,
    "METEOROLOGIE_NORMATIV": MeteorologieNormProzedur.METEOROLOGIESTANDARDISIERUNG,
    "METEOROLOGIE_NORMATIV_AKTIV": MeteorologieNormProzedur.METEOROLOGIESTANDARDISIERUNG,
    "METEOROLOGIE_NORMATIV_SOUVERAEN": MeteorologieNormProzedur.METEOROLOGIEZERTIFIZIERUNG,
}

_GELTUNG_KEY_MAP: dict[MeteorologieNormGeltung, str] = {g: g.name for g in MeteorologieNormGeltung}


@dataclass(frozen=True)
class MeteorologieNormEintrag:
    geltung: MeteorologieNormGeltung
    meteorologie_norm_weight: float
    meteorologie_norm_tier: int
    meteorologie_norm_ids: tuple[str, ...]
    meteorologie_norm_tags: tuple[str, ...]
    typ: MeteorologieNormTyp
    prozedur: MeteorologieNormProzedur
    canonical: bool = True


@dataclass(frozen=True)
class MeteorologieNormSatz:
    normen: tuple[MeteorologieNormEintrag, ...]
    parent: Optional[MeteorologieSenat] = None


def build_meteorologie_norm(parent: Optional[MeteorologieSenat] = None) -> MeteorologieNormSatz:
    if parent is None:
        parent = build_meteorologie_senat()
    base = sum(n.meteorologie_weight for n in parent.normen)
    eintraege = []
    for i, g in enumerate(MeteorologieNormGeltung):
        key = _GELTUNG_KEY_MAP[g]
        eintraege.append(MeteorologieNormEintrag(
            geltung=g,
            meteorologie_norm_weight=round(base + _WEIGHT_DELTA[key], 4),
            meteorologie_norm_tier=i + 1,
            meteorologie_norm_ids=(f"meteorologie-norm-{key.lower()}-001",),
            meteorologie_norm_tags=("meteorologie", "norm", key.lower()),
            typ=_TYP_MAP[key],
            prozedur=_PROZEDUR_MAP[key],
        ))
    return MeteorologieNormSatz(normen=tuple(eintraege), parent=parent)
