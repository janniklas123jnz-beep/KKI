from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .mineralogie_senat import MineralogieSenat, build_mineralogie_senat


class MineralogieNormGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_MINERALOGIE_NORMATIV = auto()
    MINERALOGIE_NORMATIV = auto()
    MINERALOGIE_NORMATIV_AKTIV = auto()
    MINERALOGIE_NORMATIV_SOUVERAEN = auto()


class MineralogieNormTyp(Enum):
    MINERALOGIENORM = auto()
    MINERALOGIESTANDARD = auto()
    MINERALOGIERICHTLINIE = auto()


class MineralogieNormProzedur(Enum):
    MINERALOGIENORMIERUNG = auto()
    MINERALOGIESTANDARDISIERUNG = auto()
    MINERALOGIEZERTIFIZIERUNG = auto()


_WEIGHT_DELTA: dict[str, float] = {
    "GESPERRT": 0.0,
    "GRUNDLEGEND_MINERALOGIE_NORMATIV": 1.9,
    "MINERALOGIE_NORMATIV": 3.8,
    "MINERALOGIE_NORMATIV_AKTIV": 5.7,
    "MINERALOGIE_NORMATIV_SOUVERAEN": 7.6,
}

_TYP_MAP: dict[str, MineralogieNormTyp] = {
    "GESPERRT": MineralogieNormTyp.MINERALOGIENORM,
    "GRUNDLEGEND_MINERALOGIE_NORMATIV": MineralogieNormTyp.MINERALOGIERICHTLINIE,
    "MINERALOGIE_NORMATIV": MineralogieNormTyp.MINERALOGIERICHTLINIE,
    "MINERALOGIE_NORMATIV_AKTIV": MineralogieNormTyp.MINERALOGIESTANDARD,
    "MINERALOGIE_NORMATIV_SOUVERAEN": MineralogieNormTyp.MINERALOGIESTANDARD,
}

_PROZEDUR_MAP: dict[str, MineralogieNormProzedur] = {
    "GESPERRT": MineralogieNormProzedur.MINERALOGIENORMIERUNG,
    "GRUNDLEGEND_MINERALOGIE_NORMATIV": MineralogieNormProzedur.MINERALOGIENORMIERUNG,
    "MINERALOGIE_NORMATIV": MineralogieNormProzedur.MINERALOGIESTANDARDISIERUNG,
    "MINERALOGIE_NORMATIV_AKTIV": MineralogieNormProzedur.MINERALOGIESTANDARDISIERUNG,
    "MINERALOGIE_NORMATIV_SOUVERAEN": MineralogieNormProzedur.MINERALOGIEZERTIFIZIERUNG,
}

_GELTUNG_KEY_MAP: dict[MineralogieNormGeltung, str] = {g: g.name for g in MineralogieNormGeltung}


@dataclass(frozen=True)
class MineralogieNormEintrag:
    geltung: MineralogieNormGeltung
    mineralogie_norm_weight: float
    mineralogie_norm_tier: int
    mineralogie_norm_ids: tuple[str, ...]
    mineralogie_norm_tags: tuple[str, ...]
    typ: MineralogieNormTyp
    prozedur: MineralogieNormProzedur
    canonical: bool = True


@dataclass(frozen=True)
class MineralogieNormSatz:
    normen: tuple[MineralogieNormEintrag, ...]
    parent: Optional[MineralogieSenat] = None


def build_mineralogie_norm(parent: Optional[MineralogieSenat] = None) -> MineralogieNormSatz:
    if parent is None:
        parent = build_mineralogie_senat()
    base = sum(n.mineralogie_weight for n in parent.normen)
    eintraege = []
    for i, g in enumerate(MineralogieNormGeltung):
        key = _GELTUNG_KEY_MAP[g]
        eintraege.append(MineralogieNormEintrag(
            geltung=g,
            mineralogie_norm_weight=round(base + _WEIGHT_DELTA[key], 4),
            mineralogie_norm_tier=i + 1,
            mineralogie_norm_ids=(f"mineralogie-norm-{key.lower()}-001",),
            mineralogie_norm_tags=("mineralogie", "norm", key.lower()),
            typ=_TYP_MAP[key],
            prozedur=_PROZEDUR_MAP[key],
        ))
    return MineralogieNormSatz(normen=tuple(eintraege), parent=parent)
