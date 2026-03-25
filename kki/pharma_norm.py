from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .pharmakologie_senat import PharmakologieSenat, build_pharmakologie_senat


class PharmaNormGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_PHARMA_NORMATIV = auto()
    PHARMA_NORMATIV = auto()
    PHARMA_NORMATIV_AKTIV = auto()
    PHARMA_NORMATIV_SOUVERAEN = auto()


class PharmaNormTyp(Enum):
    PHARMANORM = auto()
    PHARMASTANDARD = auto()
    PHARMARICHTLINIE = auto()


class PharmaNormProzedur(Enum):
    PHARMANORMIERUNG = auto()
    PHARMASTANDARDISIERUNG = auto()
    PHARMAKODIFIZIERUNG = auto()


_WEIGHT_DELTA: dict[str, float] = {
    "GESPERRT": 0.0,
    "GRUNDLEGEND_PHARMA_NORMATIV": 2.0,
    "PHARMA_NORMATIV": 4.0,
    "PHARMA_NORMATIV_AKTIV": 6.0,
    "PHARMA_NORMATIV_SOUVERAEN": 8.0,
}

_TYP_MAP: dict[str, PharmaNormTyp] = {
    "GESPERRT": PharmaNormTyp.PHARMANORM,
    "GRUNDLEGEND_PHARMA_NORMATIV": PharmaNormTyp.PHARMARICHTLINIE,
    "PHARMA_NORMATIV": PharmaNormTyp.PHARMARICHTLINIE,
    "PHARMA_NORMATIV_AKTIV": PharmaNormTyp.PHARMASTANDARD,
    "PHARMA_NORMATIV_SOUVERAEN": PharmaNormTyp.PHARMASTANDARD,
}

_PROZEDUR_MAP: dict[str, PharmaNormProzedur] = {
    "GESPERRT": PharmaNormProzedur.PHARMANORMIERUNG,
    "GRUNDLEGEND_PHARMA_NORMATIV": PharmaNormProzedur.PHARMANORMIERUNG,
    "PHARMA_NORMATIV": PharmaNormProzedur.PHARMASTANDARDISIERUNG,
    "PHARMA_NORMATIV_AKTIV": PharmaNormProzedur.PHARMASTANDARDISIERUNG,
    "PHARMA_NORMATIV_SOUVERAEN": PharmaNormProzedur.PHARMAKODIFIZIERUNG,
}

_GELTUNG_KEY_MAP: dict[PharmaNormGeltung, str] = {g: g.name for g in PharmaNormGeltung}

_GELTUNG_MAP: dict[str, PharmaNormGeltung] = {
    "gesperrt": PharmaNormGeltung.GESPERRT,
    "grundlegend_pharmakologisch": PharmaNormGeltung.GRUNDLEGEND_PHARMA_NORMATIV,
    "pharmakologisch": PharmaNormGeltung.PHARMA_NORMATIV,
    "pharmakologisch_aktiv": PharmaNormGeltung.PHARMA_NORMATIV_AKTIV,
    "pharmakologie_souveraen": PharmaNormGeltung.PHARMA_NORMATIV_SOUVERAEN,
}


@dataclass(frozen=True)
class PharmaNormEintrag:
    geltung: PharmaNormGeltung
    pharma_norm_weight: float
    pharma_norm_tier: int
    pharma_norm_ids: tuple[str, ...]
    pharma_norm_tags: tuple[str, ...]
    typ: PharmaNormTyp
    prozedur: PharmaNormProzedur
    canonical: bool = True


@dataclass(frozen=True)
class PharmaNormSatz:
    normen: tuple[PharmaNormEintrag, ...]
    parent: Optional[PharmakologieSenat] = None


def build_pharma_norm(parent: Optional[PharmakologieSenat] = None) -> PharmaNormSatz:
    if parent is None:
        parent = build_pharmakologie_senat()
    base = sum(n.pharma_weight for n in parent.normen)
    eintraege = []
    for i, g in enumerate(PharmaNormGeltung):
        key = _GELTUNG_KEY_MAP[g]
        eintraege.append(PharmaNormEintrag(
            geltung=g,
            pharma_norm_weight=round(base + _WEIGHT_DELTA[key], 4),
            pharma_norm_tier=i + 1,
            pharma_norm_ids=(f"pharma-norm-{key.lower()}-001",),
            pharma_norm_tags=("pharma", "norm", key.lower()),
            typ=_TYP_MAP[key],
            prozedur=_PROZEDUR_MAP[key],
        ))
    return PharmaNormSatz(normen=tuple(eintraege), parent=parent)
