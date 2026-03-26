"""Nanofabrik-Charta #979 — Charta der Nanofabrikation im KKI-Schwarm."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

from .material_norm import MaterialNorm, build_material_norm


class NanofabrikTyp(Enum):
    LITHOGRAPHIE = "LITHOGRAPHIE"
    SELBSTORGANISATION = "SELBSTORGANISATION"
    ATOMMONTAGE = "ATOMMONTAGE"
    DRUCKTECHNIK = "DRUCKTECHNIK"
    BIOASSEMBLIERUNG = "BIOASSEMBLIERUNG"


class NanofabrikProzedur(Enum):
    REINRAUM = "REINRAUM"
    KONTROLLE = "KONTROLLE"
    QUALITAET = "QUALITAET"
    SKALIERUNG = "SKALIERUNG"
    INTEGRATION = "INTEGRATION"


_WEIGHT_DELTA: dict[NanofabrikTyp, float] = {
    NanofabrikTyp.LITHOGRAPHIE: 0.17,
    NanofabrikTyp.SELBSTORGANISATION: 0.19,
    NanofabrikTyp.ATOMMONTAGE: 0.24,
    NanofabrikTyp.DRUCKTECHNIK: 0.15,
    NanofabrikTyp.BIOASSEMBLIERUNG: 0.21,
}

_TYP_MAP: dict[NanofabrikTyp, str] = {
    NanofabrikTyp.LITHOGRAPHIE: "Nanolithographie",
    NanofabrikTyp.SELBSTORGANISATION: "Molekulare Selbstorganisation",
    NanofabrikTyp.ATOMMONTAGE: "Atommontage",
    NanofabrikTyp.DRUCKTECHNIK: "Nano-Drucktechnik",
    NanofabrikTyp.BIOASSEMBLIERUNG: "Bio-Assemblierung",
}

_PROZEDUR_MAP: dict[NanofabrikProzedur, str] = {
    NanofabrikProzedur.REINRAUM: "Reinraum",
    NanofabrikProzedur.KONTROLLE: "Kontrolle",
    NanofabrikProzedur.QUALITAET: "Qualität",
    NanofabrikProzedur.SKALIERUNG: "Skalierung",
    NanofabrikProzedur.INTEGRATION: "Integration",
}


@dataclass(frozen=True)
class NanofabrikNorm:
    name: str
    material_weight: float
    material_tier: int


@dataclass(frozen=True)
class Nanofabrik:
    normen: tuple[NanofabrikNorm, ...]


def build_nanofabrik(parent=None) -> Nanofabrik:
    if parent and hasattr(parent, 'eintraege'):
        basis = parent.eintraege[-1].material_norm_weight
        tier_base = max(e.material_norm_tier for e in parent.eintraege)
    elif parent and hasattr(parent, 'normen'):
        basis = parent.normen[-1].material_weight
        tier_base = max(n.material_tier for n in parent.normen)
    else:
        basis = 0.0
        tier_base = 0
    items = []
    for i, t in enumerate(NanofabrikTyp):
        delta = _WEIGHT_DELTA.get(t, 0.0)
        items.append(NanofabrikNorm(name=_TYP_MAP[t], material_weight=round(basis + delta, 4), material_tier=tier_base + i + 1))
    return Nanofabrik(normen=tuple(items))
