"""Orbit-Kodex #984 — Kodex der Umlaufbahnen und Orbitalmanöver im KKI-Schwarm."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

from .triebwerk_charta import Triebwerk, build_triebwerk


class OrbitTyp(Enum):
    LEO = "LEO"
    MEO = "MEO"
    GEO = "GEO"
    HEO = "HEO"
    INTERPLANETAER = "INTERPLANETAER"


class OrbitProzedur(Enum):
    TRANSFER = "TRANSFER"
    RENDEZVOUS = "RENDEZVOUS"
    ANDOCKEN = "ANDOCKEN"
    DEORBIT = "DEORBIT"
    ENTSORGUNG = "ENTSORGUNG"


_WEIGHT_DELTA: dict[str, float] = {
    "LEO": 0.11,
    "MEO": 0.13,
    "GEO": 0.15,
    "HEO": 0.17,
    "INTERPLANETAER": 0.22,
}

_TYP_MAP: dict[OrbitTyp, str] = {
    OrbitTyp.LEO: "Niedrige Erdumlaufbahn (LEO)",
    OrbitTyp.MEO: "Mittlere Erdumlaufbahn (MEO)",
    OrbitTyp.GEO: "Geostationäre Umlaufbahn (GEO)",
    OrbitTyp.HEO: "Hochelliptische Umlaufbahn (HEO)",
    OrbitTyp.INTERPLANETAER: "Interplanetarer Orbit",
}

_PROZEDUR_MAP: dict[OrbitProzedur, str] = {
    OrbitProzedur.TRANSFER: "Transfer",
    OrbitProzedur.RENDEZVOUS: "Rendezvous",
    OrbitProzedur.ANDOCKEN: "Andocken",
    OrbitProzedur.DEORBIT: "Deorbit",
    OrbitProzedur.ENTSORGUNG: "Entsorgung",
}


@dataclass(frozen=True)
class OrbitEintrag:
    name: str
    raumfahrt_weight: float
    raumfahrt_tier: int


@dataclass(frozen=True)
class OrbitKodex:
    eintraege: tuple[OrbitEintrag, ...]


def build_orbit_kodex(parent=None) -> OrbitKodex:
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
    for i, t in enumerate(OrbitTyp):
        delta = _WEIGHT_DELTA.get(t.name, 0.0)
        items.append(OrbitEintrag(name=_TYP_MAP[t], raumfahrt_weight=round(basis + delta, 4), raumfahrt_tier=tier_base + i + 1))
    return OrbitKodex(eintraege=tuple(items))
