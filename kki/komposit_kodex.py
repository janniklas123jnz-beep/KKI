"""Komposit-Kodex #974 — Kodex der Verbundwerkstoffe im KKI-Schwarm."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from .halbleiter_charta import Halbleiter, build_halbleiter


class KompositTyp(Enum):
    FASERVERSTAERKT = auto()
    PARTIKELVERSTAERKT = auto()
    SCHICHTKOMPOSIT = auto()
    NANOKOMPOSIT = auto()
    BIOMIMETISCH = auto()


class KompositProzedur(Enum):
    LAMINIERUNG = auto()
    INFILTRATION = auto()
    SPRITZGUSS = auto()
    PULVERSINTERN = auto()
    ADDITIVE_FERTIGUNG = auto()


_WEIGHT_DELTA = {
    "FASERVERSTAERKT": 0.16,
    "PARTIKELVERSTAERKT": 0.12,
    "SCHICHTKOMPOSIT": 0.14,
    "NANOKOMPOSIT": 0.2,
    "BIOMIMETISCH": 0.18,
}
_TYP_MAP = {
    KompositTyp.FASERVERSTAERKT: "Faserverstärkter Komposit",
    KompositTyp.PARTIKELVERSTAERKT: "Partikelverstärkter Komposit",
    KompositTyp.SCHICHTKOMPOSIT: "Schichtkomposit",
    KompositTyp.NANOKOMPOSIT: "Nanokomposit",
    KompositTyp.BIOMIMETISCH: "Biomimetischer Komposit",
}
_PROZEDUR_MAP = {
    KompositProzedur.LAMINIERUNG: "Laminierung",
    KompositProzedur.INFILTRATION: "Infiltration",
    KompositProzedur.SPRITZGUSS: "Spritzguss",
    KompositProzedur.PULVERSINTERN: "Pulversintern",
    KompositProzedur.ADDITIVE_FERTIGUNG: "Additive Fertigung",
}


@dataclass(frozen=True)
class KompositEintrag:
    name: str
    material_weight: float
    material_tier: int


@dataclass(frozen=True)
class KompositKodex:
    eintraege: tuple[KompositEintrag, ...]


def build_komposit_kodex(parent=None) -> KompositKodex:
    basis = parent.normen[-1].material_weight if parent and hasattr(parent, 'normen') else 0.0
    tier_base = (max(n.material_tier for n in parent.normen) if parent and hasattr(parent, 'normen') else 0)
    items = []
    for i, t in enumerate(KompositTyp):
        delta = _WEIGHT_DELTA.get(t.name, 0.0)
        items.append(KompositEintrag(name=_TYP_MAP[t], material_weight=round(basis + delta, 4), material_tier=tier_base + i + 1))
    return KompositKodex(eintraege=tuple(items))
