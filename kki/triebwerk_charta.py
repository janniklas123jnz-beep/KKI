"""Triebwerk-Charta #983 — Charta der Raumfahrtantriebe im KKI-Schwarm."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

from .satellit_register import SatellitRegister, build_satellit_register


class TriebwerkTyp(Enum):
    CHEMISCH = "CHEMISCH"
    IONENANTRIEB = "IONENANTRIEB"
    NUKLEAR = "NUKLEAR"
    SOLAR_SEGEL = "SOLAR_SEGEL"
    FUSIONSANTRIEB = "FUSIONSANTRIEB"


class TriebwerkProzedur(Enum):
    VERBRENNUNG = "VERBRENNUNG"
    BESCHLEUNIGUNG = "BESCHLEUNIGUNG"
    STEUERUNG = "STEUERUNG"
    KALIBRIERUNG = "KALIBRIERUNG"
    OPTIMIERUNG = "OPTIMIERUNG"


_WEIGHT_DELTA: dict[TriebwerkTyp, float] = {
    TriebwerkTyp.CHEMISCH: 0.12,
    TriebwerkTyp.IONENANTRIEB: 0.18,
    TriebwerkTyp.NUKLEAR: 0.22,
    TriebwerkTyp.SOLAR_SEGEL: 0.16,
    TriebwerkTyp.FUSIONSANTRIEB: 0.25,
}

_TYP_MAP: dict[TriebwerkTyp, str] = {
    TriebwerkTyp.CHEMISCH: "Chemisches Triebwerk",
    TriebwerkTyp.IONENANTRIEB: "Ionentriebwerk",
    TriebwerkTyp.NUKLEAR: "Nukleares Triebwerk",
    TriebwerkTyp.SOLAR_SEGEL: "Sonnensegel",
    TriebwerkTyp.FUSIONSANTRIEB: "Fusionsantrieb",
}

_PROZEDUR_MAP: dict[TriebwerkProzedur, str] = {
    TriebwerkProzedur.VERBRENNUNG: "Verbrennung",
    TriebwerkProzedur.BESCHLEUNIGUNG: "Beschleunigung",
    TriebwerkProzedur.STEUERUNG: "Steuerung",
    TriebwerkProzedur.KALIBRIERUNG: "Kalibrierung",
    TriebwerkProzedur.OPTIMIERUNG: "Optimierung",
}


@dataclass(frozen=True)
class TriebwerkNorm:
    name: str
    raumfahrt_weight: float
    raumfahrt_tier: int


@dataclass(frozen=True)
class Triebwerk:
    normen: tuple[TriebwerkNorm, ...]


def build_triebwerk(parent=None) -> Triebwerk:
    if parent and hasattr(parent, 'normen'):
        basis = parent.normen[-1].raumfahrt_weight
        tier_base = max(n.raumfahrt_tier for n in parent.normen)
    elif parent and hasattr(parent, 'eintraege'):
        basis = parent.eintraege[-1].raumfahrt_weight
        tier_base = max(e.raumfahrt_tier for e in parent.eintraege)
    else:
        basis = 0.0
        tier_base = 0
    items = []
    for i, t in enumerate(TriebwerkTyp):
        delta = _WEIGHT_DELTA.get(t, 0.0)
        items.append(TriebwerkNorm(name=_TYP_MAP[t], raumfahrt_weight=round(basis + delta, 4), raumfahrt_tier=tier_base + i + 1))
    return Triebwerk(normen=tuple(items))
