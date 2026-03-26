from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .hydrologie_senat import HydrologieSenat, build_hydrologie_senat


class HydrologieNormGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_HYDROLOGIE_NORMATIV = auto()
    HYDROLOGIE_NORMATIV = auto()
    HYDROLOGIE_NORMATIV_AKTIV = auto()
    HYDROLOGIE_NORMATIV_SOUVERAEN = auto()


class HydrologieNormTyp(Enum):
    HYDROLOGIENORM = auto()
    HYDROLOGIESTANDARD = auto()
    HYDROLOGIERICHTLINIE = auto()


class HydrologieNormProzedur(Enum):
    HYDROLOGIENORMIERUNG = auto()
    HYDROLOGIESTANDARDISIERUNG = auto()
    HYDROLOGIEZERTIFIZIERUNG = auto()


_WEIGHT_DELTA: dict[str, float] = {
    "GESPERRT": 0.0,
    "GRUNDLEGEND_HYDROLOGIE_NORMATIV": 1.9,
    "HYDROLOGIE_NORMATIV": 3.8,
    "HYDROLOGIE_NORMATIV_AKTIV": 5.7,
    "HYDROLOGIE_NORMATIV_SOUVERAEN": 7.6,
}

_TYP_MAP: dict[str, HydrologieNormTyp] = {
    "GESPERRT": HydrologieNormTyp.HYDROLOGIENORM,
    "GRUNDLEGEND_HYDROLOGIE_NORMATIV": HydrologieNormTyp.HYDROLOGIERICHTLINIE,
    "HYDROLOGIE_NORMATIV": HydrologieNormTyp.HYDROLOGIERICHTLINIE,
    "HYDROLOGIE_NORMATIV_AKTIV": HydrologieNormTyp.HYDROLOGIESTANDARD,
    "HYDROLOGIE_NORMATIV_SOUVERAEN": HydrologieNormTyp.HYDROLOGIESTANDARD,
}

_PROZEDUR_MAP: dict[str, HydrologieNormProzedur] = {
    "GESPERRT": HydrologieNormProzedur.HYDROLOGIENORMIERUNG,
    "GRUNDLEGEND_HYDROLOGIE_NORMATIV": HydrologieNormProzedur.HYDROLOGIENORMIERUNG,
    "HYDROLOGIE_NORMATIV": HydrologieNormProzedur.HYDROLOGIESTANDARDISIERUNG,
    "HYDROLOGIE_NORMATIV_AKTIV": HydrologieNormProzedur.HYDROLOGIESTANDARDISIERUNG,
    "HYDROLOGIE_NORMATIV_SOUVERAEN": HydrologieNormProzedur.HYDROLOGIEZERTIFIZIERUNG,
}

_GELTUNG_KEY_MAP: dict[HydrologieNormGeltung, str] = {g: g.name for g in HydrologieNormGeltung}


@dataclass(frozen=True)
class HydrologieNormEintrag:
    geltung: HydrologieNormGeltung
    hydrologie_norm_weight: float
    hydrologie_norm_tier: int
    hydrologie_norm_ids: tuple[str, ...]
    hydrologie_norm_tags: tuple[str, ...]
    typ: HydrologieNormTyp
    prozedur: HydrologieNormProzedur
    canonical: bool = True


@dataclass(frozen=True)
class HydrologieNormSatz:
    normen: tuple[HydrologieNormEintrag, ...]
    parent: Optional[HydrologieSenat] = None


def build_hydrologie_norm(parent: Optional[HydrologieSenat] = None) -> HydrologieNormSatz:
    if parent is None:
        parent = build_hydrologie_senat()
    base = sum(n.hydrologie_weight for n in parent.normen)
    eintraege = []
    for i, g in enumerate(HydrologieNormGeltung):
        key = _GELTUNG_KEY_MAP[g]
        eintraege.append(HydrologieNormEintrag(
            geltung=g,
            hydrologie_norm_weight=round(base + _WEIGHT_DELTA[key], 4),
            hydrologie_norm_tier=i + 1,
            hydrologie_norm_ids=(f"hydrologie-norm-{key.lower()}-001",),
            hydrologie_norm_tags=("hydrologie", "norm", key.lower()),
            typ=_TYP_MAP[key],
            prozedur=_PROZEDUR_MAP[key],
        ))
    return HydrologieNormSatz(normen=tuple(eintraege), parent=parent)
