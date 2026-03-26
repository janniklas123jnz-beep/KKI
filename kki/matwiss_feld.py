"""Materialwissenschaften-Feld #971 — Grundlagen der Materialkunde im KKI-Schwarm."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from .finanz_verfassung import FinanzVerfassung, build_finanz_verfassung


class MatwissTyp(Enum):
    GRUNDLAGEN = auto()
    KRISTALLOGRAPHIE = auto()
    THERMODYNAMIK = auto()
    MECHANIK = auto()
    ELEKTRONIK = auto()


class MatwissProzedur(Enum):
    SYNTHESE = auto()
    ANALYSE = auto()
    SIMULATION = auto()
    CHARAKTERISIERUNG = auto()
    OPTIMIERUNG = auto()


_WEIGHT_DELTA = {
    MatwissTyp.GRUNDLAGEN: 0.1,
    MatwissTyp.KRISTALLOGRAPHIE: 0.15,
    MatwissTyp.THERMODYNAMIK: 0.2,
    MatwissTyp.MECHANIK: 0.18,
    MatwissTyp.ELEKTRONIK: 0.22,
}
_TYP_MAP = {
    MatwissTyp.GRUNDLAGEN: "Materialgrundlagen",
    MatwissTyp.KRISTALLOGRAPHIE: "Kristallographie",
    MatwissTyp.THERMODYNAMIK: "Thermodynamik",
    MatwissTyp.MECHANIK: "Materialmechanik",
    MatwissTyp.ELEKTRONIK: "Materialelektronik",
}
_PROZEDUR_MAP = {
    MatwissProzedur.SYNTHESE: "Synthese",
    MatwissProzedur.ANALYSE: "Analyse",
    MatwissProzedur.SIMULATION: "Simulation",
    MatwissProzedur.CHARAKTERISIERUNG: "Charakterisierung",
    MatwissProzedur.OPTIMIERUNG: "Optimierung",
}


@dataclass(frozen=True)
class MatwissNorm:
    name: str
    material_weight: float
    material_tier: int


@dataclass(frozen=True)
class Matwiss:
    normen: tuple[MatwissNorm, ...]


def build_matwiss(parent=None) -> Matwiss:
    basis = parent.normen[-1].material_weight if parent and hasattr(parent, 'normen') else 0.0
    tier_base = (max(n.material_tier for n in parent.normen) if parent and hasattr(parent, 'normen') else 0)
    items = []
    for i, t in enumerate(MatwissTyp):
        delta = _WEIGHT_DELTA.get(t, 0.0)
        items.append(MatwissNorm(name=_TYP_MAP[t], material_weight=round(basis + delta, 4), material_tier=tier_base + i + 1))
    return Matwiss(normen=tuple(items))
