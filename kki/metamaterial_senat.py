"""Metamaterial-Senat #977 — Senat der Metamaterialien im KKI-Schwarm."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

from .supraleiter_pakt import SupraleiterPakt, build_supraleiter_pakt


class MetamaterialTyp(Enum):
    NEGATIVBRECHUNG = "NEGATIVBRECHUNG"
    AKUSTISCH = "AKUSTISCH"
    MECHANISCH = "MECHANISCH"
    ELEKTROMAGNETISCH = "ELEKTROMAGNETISCH"
    THERMISCH = "THERMISCH"


class MetamaterialProzedur(Enum):
    DESIGN = "DESIGN"
    FABRIKATION = "FABRIKATION"
    CHARAKTERISIERUNG = "CHARAKTERISIERUNG"
    SIMULATION = "SIMULATION"
    ANWENDUNG = "ANWENDUNG"


_WEIGHT_DELTA: dict[MetamaterialTyp, float] = {
    MetamaterialTyp.NEGATIVBRECHUNG: 0.18,
    MetamaterialTyp.AKUSTISCH: 0.14,
    MetamaterialTyp.MECHANISCH: 0.16,
    MetamaterialTyp.ELEKTROMAGNETISCH: 0.2,
    MetamaterialTyp.THERMISCH: 0.15,
}

_TYP_MAP: dict[MetamaterialTyp, str] = {
    MetamaterialTyp.NEGATIVBRECHUNG: "Negativ-Brechungsindex-Material",
    MetamaterialTyp.AKUSTISCH: "Akustisches Metamaterial",
    MetamaterialTyp.MECHANISCH: "Mechanisches Metamaterial",
    MetamaterialTyp.ELEKTROMAGNETISCH: "Elektromagnetisches Metamaterial",
    MetamaterialTyp.THERMISCH: "Thermisches Metamaterial",
}

_PROZEDUR_MAP: dict[MetamaterialProzedur, str] = {
    MetamaterialProzedur.DESIGN: "Design",
    MetamaterialProzedur.FABRIKATION: "Fabrikation",
    MetamaterialProzedur.CHARAKTERISIERUNG: "Charakterisierung",
    MetamaterialProzedur.SIMULATION: "Simulation",
    MetamaterialProzedur.ANWENDUNG: "Anwendung",
}


@dataclass(frozen=True)
class MetamaterialNorm:
    name: str
    material_weight: float
    material_tier: int


@dataclass(frozen=True)
class Metamaterial:
    normen: tuple[MetamaterialNorm, ...]


def build_metamaterial(parent=None) -> Metamaterial:
    basis = parent.eintraege[-1].material_weight if parent and hasattr(parent, 'eintraege') else 0.0
    tier_base = max(e.material_tier for e in parent.eintraege) if parent and hasattr(parent, 'eintraege') else 0
    items = []
    for i, t in enumerate(MetamaterialTyp):
        delta = _WEIGHT_DELTA.get(t, 0.0)
        items.append(MetamaterialNorm(name=_TYP_MAP[t], material_weight=round(basis + delta, 4), material_tier=tier_base + i + 1))
    return Metamaterial(normen=tuple(items))
