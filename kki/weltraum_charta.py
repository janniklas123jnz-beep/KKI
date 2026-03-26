"""Weltraum-Charta #989 — Charta der Weltraumforschung im KKI-Schwarm."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

from .raumfahrt_norm import RaumfahrtNorm, build_raumfahrt_norm


class WeltraumTyp(Enum):
    INTERSTELLAR = "INTERSTELLAR"
    EXOPLANETEN = "EXOPLANETEN"
    DUNKLE_MATERIE = "DUNKLE_MATERIE"
    GRAVITATIONSWELLEN = "GRAVITATIONSWELLEN"
    KOSMOLOGIE = "KOSMOLOGIE"


class WeltraumProzedur(Enum):
    BEOBACHTUNG = "BEOBACHTUNG"
    ANALYSE = "ANALYSE"
    MODELLIERUNG = "MODELLIERUNG"
    HYPOTHESE = "HYPOTHESE"
    THEORIE = "THEORIE"


_WEIGHT_DELTA: dict[WeltraumTyp, float] = {
    WeltraumTyp.INTERSTELLAR: 0.2,
    WeltraumTyp.EXOPLANETEN: 0.18,
    WeltraumTyp.DUNKLE_MATERIE: 0.25,
    WeltraumTyp.GRAVITATIONSWELLEN: 0.22,
    WeltraumTyp.KOSMOLOGIE: 0.28,
}

_TYP_MAP: dict[WeltraumTyp, str] = {
    WeltraumTyp.INTERSTELLAR: "Interstellare Raumfahrt",
    WeltraumTyp.EXOPLANETEN: "Exoplanetenforschung",
    WeltraumTyp.DUNKLE_MATERIE: "Dunkle Materie",
    WeltraumTyp.GRAVITATIONSWELLEN: "Gravitationswellen",
    WeltraumTyp.KOSMOLOGIE: "Kosmologie",
}

_PROZEDUR_MAP: dict[WeltraumProzedur, str] = {
    WeltraumProzedur.BEOBACHTUNG: "Beobachtung",
    WeltraumProzedur.ANALYSE: "Analyse",
    WeltraumProzedur.MODELLIERUNG: "Modellierung",
    WeltraumProzedur.HYPOTHESE: "Hypothese",
    WeltraumProzedur.THEORIE: "Theorie",
}


@dataclass(frozen=True)
class WeltraumNorm:
    name: str
    raumfahrt_weight: float
    raumfahrt_tier: int


@dataclass(frozen=True)
class Weltraum:
    normen: tuple[WeltraumNorm, ...]


def build_weltraum(parent=None) -> Weltraum:
    if parent and hasattr(parent, 'eintraege'):
        basis = parent.eintraege[-1].raumfahrt_norm_weight
        tier_base = max(e.raumfahrt_norm_tier for e in parent.eintraege)
    elif parent and hasattr(parent, 'normen'):
        basis = parent.normen[-1].raumfahrt_weight
        tier_base = max(n.raumfahrt_tier for n in parent.normen)
    else:
        basis = 0.0
        tier_base = 0
    items = []
    for i, t in enumerate(WeltraumTyp):
        delta = _WEIGHT_DELTA.get(t, 0.0)
        items.append(WeltraumNorm(name=_TYP_MAP[t], raumfahrt_weight=round(basis + delta, 4), raumfahrt_tier=tier_base + i + 1))
    return Weltraum(normen=tuple(items))
