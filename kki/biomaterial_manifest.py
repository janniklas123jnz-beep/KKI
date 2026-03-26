"""Biomaterial-Manifest #975 — Manifest der Biomaterialien im KKI-Schwarm."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from .komposit_kodex import KompositKodex, build_komposit_kodex


class BiomaterialTyp(Enum):
    HYDROXYLAPATIT = auto()
    KOLLAGEN = auto()
    HYDROGEL = auto()
    BIOPOLYMER = auto()
    BIOKERAMIK = auto()


class BiomaterialProzedur(Enum):
    BIOFUNKTIONALISIERUNG = auto()
    STERILISATION = auto()
    DEGRADATION = auto()
    ZELLKULTUR = auto()
    IMPLANTATION = auto()


_WEIGHT_DELTA = {
    BiomaterialTyp.HYDROXYLAPATIT: 0.15,
    BiomaterialTyp.KOLLAGEN: 0.12,
    BiomaterialTyp.HYDROGEL: 0.17,
    BiomaterialTyp.BIOPOLYMER: 0.13,
    BiomaterialTyp.BIOKERAMIK: 0.16,
}

_TYP_MAP = {
    BiomaterialTyp.HYDROXYLAPATIT: "Hydroxylapatit",
    BiomaterialTyp.KOLLAGEN: "Kollagen-Biomaterial",
    BiomaterialTyp.HYDROGEL: "Hydrogel",
    BiomaterialTyp.BIOPOLYMER: "Biopolymer",
    BiomaterialTyp.BIOKERAMIK: "Biokeramik",
}

_PROZEDUR_MAP = {
    BiomaterialProzedur.BIOFUNKTIONALISIERUNG: "Biofunktionalisierung",
    BiomaterialProzedur.STERILISATION: "Sterilisation",
    BiomaterialProzedur.DEGRADATION: "Degradation",
    BiomaterialProzedur.ZELLKULTUR: "Zellkultur",
    BiomaterialProzedur.IMPLANTATION: "Implantation",
}


@dataclass(frozen=True)
class BiomaterialNorm:
    name: str
    material_weight: float
    material_tier: int


@dataclass(frozen=True)
class Biomaterial:
    normen: tuple[BiomaterialNorm, ...]


def build_biomaterial(parent=None) -> Biomaterial:
    basis = parent.normen[-1].material_weight if parent and hasattr(parent, 'normen') else 0.0
    tier_base = max(n.material_tier for n in parent.normen) if parent and hasattr(parent, 'normen') else 0
    items = []
    for i, t in enumerate(BiomaterialTyp):
        delta = _WEIGHT_DELTA.get(t, 0.0)
        items.append(BiomaterialNorm(name=_TYP_MAP[t], material_weight=round(basis + delta, 4), material_tier=tier_base + i + 1))
    return Biomaterial(normen=tuple(items))
