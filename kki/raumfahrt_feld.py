"""Raumfahrt-Feld #981 — Grundlagen der Luft- und Raumfahrt im KKI-Schwarm."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

from .matwiss_verfassung import MatwissVerfassung, build_matwiss_verfassung


class RaumfahrtTyp(Enum):
    GRUNDLAGEN = "GRUNDLAGEN"
    ORBITAL_MECHANIK = "ORBITAL_MECHANIK"
    ANTRIEB = "ANTRIEB"
    NUTZLAST = "NUTZLAST"
    MISSION = "MISSION"


class RaumfahrtProzedur(Enum):
    PLANUNG = "PLANUNG"
    DESIGN = "DESIGN"
    TEST = "TEST"
    START = "START"
    BETRIEB = "BETRIEB"


_WEIGHT_DELTA: dict[RaumfahrtTyp, float] = {
    RaumfahrtTyp.GRUNDLAGEN: 0.1,
    RaumfahrtTyp.ORBITAL_MECHANIK: 0.15,
    RaumfahrtTyp.ANTRIEB: 0.2,
    RaumfahrtTyp.NUTZLAST: 0.17,
    RaumfahrtTyp.MISSION: 0.22,
}

_TYP_MAP: dict[RaumfahrtTyp, str] = {
    RaumfahrtTyp.GRUNDLAGEN: "Raumfahrtgrundlagen",
    RaumfahrtTyp.ORBITAL_MECHANIK: "Orbitalmechanik",
    RaumfahrtTyp.ANTRIEB: "Raumfahrtantrieb",
    RaumfahrtTyp.NUTZLAST: "Raumfahrt-Nutzlast",
    RaumfahrtTyp.MISSION: "Raumfahrtmission",
}

_PROZEDUR_MAP: dict[RaumfahrtProzedur, str] = {
    RaumfahrtProzedur.PLANUNG: "Planung",
    RaumfahrtProzedur.DESIGN: "Design",
    RaumfahrtProzedur.TEST: "Test",
    RaumfahrtProzedur.START: "Start",
    RaumfahrtProzedur.BETRIEB: "Betrieb",
}


@dataclass(frozen=True)
class RaumfahrtNorm:
    name: str
    raumfahrt_weight: float
    raumfahrt_tier: int


@dataclass(frozen=True)
class Raumfahrt:
    normen: tuple[RaumfahrtNorm, ...]


def build_raumfahrt(parent=None) -> Raumfahrt:
    basis = parent.normen[-1].material_weight if parent and hasattr(parent, 'normen') else 0.0
    tier_base = max(n.material_tier for n in parent.normen) if parent and hasattr(parent, 'normen') else 0
    items = []
    for i, t in enumerate(RaumfahrtTyp):
        delta = _WEIGHT_DELTA.get(t, 0.0)
        items.append(RaumfahrtNorm(name=_TYP_MAP[t], raumfahrt_weight=round(basis + delta, 4), raumfahrt_tier=tier_base + i + 1))
    return Raumfahrt(normen=tuple(items))
