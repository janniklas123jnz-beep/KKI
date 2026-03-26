"""Supraleiter-Pakt #976 — Pakt der Supraleiter-Materialien im KKI-Schwarm."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

from .biomaterial_manifest import Biomaterial, build_biomaterial


class SupraleiterTyp(Enum):
    HOCHTEMPERATUR = "HOCHTEMPERATUR"
    TIEFTEMPERATUR = "TIEFTEMPERATUR"
    RAUMTEMPERATUR_KANDIDAT = "RAUMTEMPERATUR_KANDIDAT"
    TOPOLOGISCH = "TOPOLOGISCH"
    MAGNETISCH = "MAGNETISCH"


class SupraleiterProzedur(Enum):
    KUEHLUNG = "KUEHLUNG"
    ABSCHIRMUNG = "ABSCHIRMUNG"
    STROMLEITUNG = "STROMLEITUNG"
    MAGNETFELDANWENDUNG = "MAGNETFELDANWENDUNG"
    FEHLERKORREKTUR = "FEHLERKORREKTUR"


_WEIGHT_DELTA: dict[str, float] = {
    "HOCHTEMPERATUR": 0.2,
    "TIEFTEMPERATUR": 0.14,
    "RAUMTEMPERATUR_KANDIDAT": 0.25,
    "TOPOLOGISCH": 0.22,
    "MAGNETISCH": 0.17,
}

_TYP_MAP: dict[SupraleiterTyp, str] = {
    SupraleiterTyp.HOCHTEMPERATUR: "Hochtemperatur-Supraleiter",
    SupraleiterTyp.TIEFTEMPERATUR: "Tieftemperatur-Supraleiter",
    SupraleiterTyp.RAUMTEMPERATUR_KANDIDAT: "Raumtemperatur-Kandidat",
    SupraleiterTyp.TOPOLOGISCH: "Topologischer Supraleiter",
    SupraleiterTyp.MAGNETISCH: "Magnetischer Supraleiter",
}

_PROZEDUR_MAP: dict[SupraleiterProzedur, str] = {
    SupraleiterProzedur.KUEHLUNG: "Kühlung",
    SupraleiterProzedur.ABSCHIRMUNG: "Abschirmung",
    SupraleiterProzedur.STROMLEITUNG: "Stromleitung",
    SupraleiterProzedur.MAGNETFELDANWENDUNG: "Magnetfeldanwendung",
    SupraleiterProzedur.FEHLERKORREKTUR: "Fehlerkorrektur",
}


@dataclass(frozen=True)
class SupraleiterEintrag:
    name: str
    material_weight: float
    material_tier: int


@dataclass(frozen=True)
class SupraleiterPakt:
    eintraege: tuple[SupraleiterEintrag, ...]


def build_supraleiter_pakt(parent=None) -> SupraleiterPakt:
    basis = parent.normen[-1].material_weight if parent and hasattr(parent, 'normen') else 0.0
    tier_base = max(n.material_tier for n in parent.normen) if parent and hasattr(parent, 'normen') else 0
    items = []
    for i, t in enumerate(SupraleiterTyp):
        delta = _WEIGHT_DELTA.get(t.name, 0.0)
        items.append(SupraleiterEintrag(name=_TYP_MAP[t], material_weight=round(basis + delta, 4), material_tier=tier_base + i + 1))
    return SupraleiterPakt(eintraege=tuple(items))
