"""Mars-Senat #987 — Senat der Marsforschung und -kolonisierung im KKI-Schwarm."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

from .mondmission_pakt import MondmissionPakt, build_mondmission_pakt


class MarsTyp(Enum):
    TERRAFORMING = "TERRAFORMING"
    KOLONIE = "KOLONIE"
    TRANSPORT = "TRANSPORT"
    LEBENSERHALTUNG = "LEBENSERHALTUNG"
    WISSENSCHAFT = "WISSENSCHAFT"


class MarsProzedur(Enum):
    VORBEREITUNG = "VORBEREITUNG"
    TRANSIT = "TRANSIT"
    LANDUNG = "LANDUNG"
    AUFBAU = "AUFBAU"
    DAUERBETRIEB = "DAUERBETRIEB"


_WEIGHT_DELTA: dict[MarsTyp, float] = {
    MarsTyp.TERRAFORMING: 0.28,
    MarsTyp.KOLONIE: 0.24,
    MarsTyp.TRANSPORT: 0.2,
    MarsTyp.LEBENSERHALTUNG: 0.22,
    MarsTyp.WISSENSCHAFT: 0.18,
}

_TYP_MAP: dict[MarsTyp, str] = {
    MarsTyp.TERRAFORMING: "Mars-Terraforming",
    MarsTyp.KOLONIE: "Mars-Kolonie",
    MarsTyp.TRANSPORT: "Mars-Transport",
    MarsTyp.LEBENSERHALTUNG: "Mars-Lebenserhaltung",
    MarsTyp.WISSENSCHAFT: "Mars-Wissenschaft",
}

_PROZEDUR_MAP: dict[MarsProzedur, str] = {
    MarsProzedur.VORBEREITUNG: "Vorbereitung",
    MarsProzedur.TRANSIT: "Transit",
    MarsProzedur.LANDUNG: "Landung",
    MarsProzedur.AUFBAU: "Aufbau",
    MarsProzedur.DAUERBETRIEB: "Dauerbetrieb",
}


@dataclass(frozen=True)
class MarsNorm:
    name: str
    raumfahrt_weight: float
    raumfahrt_tier: int


@dataclass(frozen=True)
class Mars:
    normen: tuple[MarsNorm, ...]


def build_mars(parent=None) -> Mars:
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
    for i, t in enumerate(MarsTyp):
        delta = _WEIGHT_DELTA.get(t, 0.0)
        items.append(MarsNorm(name=_TYP_MAP[t], raumfahrt_weight=round(basis + delta, 4), raumfahrt_tier=tier_base + i + 1))
    return Mars(normen=tuple(items))
