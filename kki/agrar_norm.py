from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .agraroekologie_senat import AgraroekologieSenat, build_agraoekologie_senat


class AgrarNormGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_AGRAR_NORMATIV = auto()
    AGRAR_NORMATIV = auto()
    AGRAR_NORMATIV_AKTIV = auto()
    AGRAR_NORMATIV_SOUVERAEN = auto()


class AgrarNormTyp(Enum):
    AGRARNORM = auto()
    AGRARSTANDARD = auto()
    AGRARRICHTLINIE = auto()


class AgrarNormProzedur(Enum):
    AGRARNORMIERUNG = auto()
    AGRARSTANDARTISIERUNG = auto()
    AGRARZERTIFIZIERUNG = auto()


_WEIGHT_DELTA: dict[str, float] = {
    "GESPERRT": 0.0,
    "GRUNDLEGEND_AGRAR_NORMATIV": 1.9,
    "AGRAR_NORMATIV": 3.8,
    "AGRAR_NORMATIV_AKTIV": 5.7,
    "AGRAR_NORMATIV_SOUVERAEN": 7.6,
}

_TYP_MAP: dict[str, AgrarNormTyp] = {
    "GESPERRT": AgrarNormTyp.AGRARNORM,
    "GRUNDLEGEND_AGRAR_NORMATIV": AgrarNormTyp.AGRARRICHTLINIE,
    "AGRAR_NORMATIV": AgrarNormTyp.AGRARRICHTLINIE,
    "AGRAR_NORMATIV_AKTIV": AgrarNormTyp.AGRARSTANDARD,
    "AGRAR_NORMATIV_SOUVERAEN": AgrarNormTyp.AGRARSTANDARD,
}

_PROZEDUR_MAP: dict[str, AgrarNormProzedur] = {
    "GESPERRT": AgrarNormProzedur.AGRARNORMIERUNG,
    "GRUNDLEGEND_AGRAR_NORMATIV": AgrarNormProzedur.AGRARNORMIERUNG,
    "AGRAR_NORMATIV": AgrarNormProzedur.AGRARSTANDARTISIERUNG,
    "AGRAR_NORMATIV_AKTIV": AgrarNormProzedur.AGRARSTANDARTISIERUNG,
    "AGRAR_NORMATIV_SOUVERAEN": AgrarNormProzedur.AGRARZERTIFIZIERUNG,
}

_GELTUNG_KEY_MAP: dict[AgrarNormGeltung, str] = {g: g.name for g in AgrarNormGeltung}

_GELTUNG_MAP: dict[str, AgrarNormGeltung] = {
    "gesperrt": AgrarNormGeltung.GESPERRT,
    "grundlegend_agraroekologisch": AgrarNormGeltung.GRUNDLEGEND_AGRAR_NORMATIV,
    "agraroekologisch": AgrarNormGeltung.AGRAR_NORMATIV,
    "agraroekologisch_aktiv": AgrarNormGeltung.AGRAR_NORMATIV_AKTIV,
    "agraoekologie_souveraen": AgrarNormGeltung.AGRAR_NORMATIV_SOUVERAEN,
}


@dataclass(frozen=True)
class AgrarNormEintrag:
    geltung: AgrarNormGeltung
    agrar_norm_weight: float
    agrar_norm_tier: int
    agrar_norm_ids: tuple[str, ...]
    agrar_norm_tags: tuple[str, ...]
    typ: AgrarNormTyp
    prozedur: AgrarNormProzedur
    canonical: bool = True


@dataclass(frozen=True)
class AgrarNormSatz:
    normen: tuple[AgrarNormEintrag, ...]
    parent: Optional[AgraroekologieSenat] = None


def build_agrar_norm(parent: Optional[AgraroekologieSenat] = None) -> AgrarNormSatz:
    if parent is None:
        parent = build_agraoekologie_senat()
    base = sum(n.agrar_weight for n in parent.normen)
    eintraege = []
    for i, g in enumerate(AgrarNormGeltung):
        key = _GELTUNG_KEY_MAP[g]
        eintraege.append(AgrarNormEintrag(
            geltung=g,
            agrar_norm_weight=round(base + _WEIGHT_DELTA[key], 4),
            agrar_norm_tier=i + 1,
            agrar_norm_ids=(f"agrar-norm-{key.lower()}-001",),
            agrar_norm_tags=("agrar", "norm", key.lower()),
            typ=_TYP_MAP[key],
            prozedur=_PROZEDUR_MAP[key],
        ))
    return AgrarNormSatz(normen=tuple(eintraege), parent=parent)
