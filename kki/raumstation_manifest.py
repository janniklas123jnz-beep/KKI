"""Raumstation-Manifest #985 — Manifest der Raumstationstechnologie im KKI-Schwarm."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

from .orbit_kodex import OrbitKodex, build_orbit_kodex


class RaumstationTyp(Enum):
    FORSCHUNGSMODUL = "FORSCHUNGSMODUL"
    WOHNMODUL = "WOHNMODUL"
    ANTRIEBSMODUL = "ANTRIEBSMODUL"
    SOLAR_ARRAY = "SOLAR_ARRAY"
    ANDOCKSYSTEM = "ANDOCKSYSTEM"


class RaumstationProzedur(Enum):
    MONTAGE = "MONTAGE"
    WARTUNG = "WARTUNG"
    EXPERIMENT = "EXPERIMENT"
    VERSORGUNG = "VERSORGUNG"
    EVAKUIERUNG = "EVAKUIERUNG"


_WEIGHT_DELTA: dict[RaumstationTyp, float] = {
    RaumstationTyp.FORSCHUNGSMODUL: 0.14,
    RaumstationTyp.WOHNMODUL: 0.12,
    RaumstationTyp.ANTRIEBSMODUL: 0.16,
    RaumstationTyp.SOLAR_ARRAY: 0.13,
    RaumstationTyp.ANDOCKSYSTEM: 0.15,
}

_TYP_MAP: dict[RaumstationTyp, str] = {
    RaumstationTyp.FORSCHUNGSMODUL: "Forschungsmodul",
    RaumstationTyp.WOHNMODUL: "Wohnmodul",
    RaumstationTyp.ANTRIEBSMODUL: "Antriebsmodul",
    RaumstationTyp.SOLAR_ARRAY: "Solaranlage",
    RaumstationTyp.ANDOCKSYSTEM: "Andocksystem",
}

_PROZEDUR_MAP: dict[RaumstationProzedur, str] = {
    RaumstationProzedur.MONTAGE: "Montage",
    RaumstationProzedur.WARTUNG: "Wartung",
    RaumstationProzedur.EXPERIMENT: "Experiment",
    RaumstationProzedur.VERSORGUNG: "Versorgung",
    RaumstationProzedur.EVAKUIERUNG: "Evakuierung",
}


@dataclass(frozen=True)
class RaumstationNorm:
    name: str
    raumfahrt_weight: float
    raumfahrt_tier: int


@dataclass(frozen=True)
class Raumstation:
    normen: tuple[RaumstationNorm, ...]


def build_raumstation(parent=None) -> Raumstation:
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
    for i, t in enumerate(RaumstationTyp):
        delta = _WEIGHT_DELTA.get(t, 0.0)
        items.append(RaumstationNorm(name=_TYP_MAP[t], raumfahrt_weight=round(basis + delta, 4), raumfahrt_tier=tier_base + i + 1))
    return Raumstation(normen=tuple(items))
