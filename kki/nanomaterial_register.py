"""Nanomaterial-Register #972 — Katalog der Nanomaterialien im KKI-Schwarm."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from .matwiss_feld import Matwiss, build_matwiss


class NanomaterialTyp(Enum):
    KOHLENSTOFFNANOROEHREN = auto()
    GRAPHEN = auto()
    QUANTENPUNKTE = auto()
    NANOPARTIKEL = auto()
    NANODRAEHTE = auto()


class NanomaterialProzedur(Enum):
    SYNTHESE = auto()
    FUNKTIONALISIERUNG = auto()
    CHARAKTERISIERUNG = auto()
    INTEGRATION = auto()
    SKALIERUNG = auto()


_WEIGHT_DELTA = {
    "KOHLENSTOFFNANOROEHREN": 0.12,
    "GRAPHEN": 0.18,
    "QUANTENPUNKTE": 0.15,
    "NANOPARTIKEL": 0.1,
    "NANODRAEHTE": 0.13,
}
_TYP_MAP = {
    NanomaterialTyp.KOHLENSTOFFNANOROEHREN: "Kohlenstoffnanoröhren",
    NanomaterialTyp.GRAPHEN: "Graphen",
    NanomaterialTyp.QUANTENPUNKTE: "Quantenpunkte",
    NanomaterialTyp.NANOPARTIKEL: "Nanopartikel",
    NanomaterialTyp.NANODRAEHTE: "Nanodrähte",
}
_PROZEDUR_MAP = {
    NanomaterialProzedur.SYNTHESE: "Synthese",
    NanomaterialProzedur.FUNKTIONALISIERUNG: "Funktionalisierung",
    NanomaterialProzedur.CHARAKTERISIERUNG: "Charakterisierung",
    NanomaterialProzedur.INTEGRATION: "Integration",
    NanomaterialProzedur.SKALIERUNG: "Skalierung",
}


@dataclass(frozen=True)
class NanomaterialEintrag:
    name: str
    material_weight: float
    material_tier: int


@dataclass(frozen=True)
class NanomaterialRegister:
    eintraege: tuple[NanomaterialEintrag, ...]


def build_nanomaterial_register(parent=None) -> NanomaterialRegister:
    basis = parent.normen[-1].material_weight if parent and hasattr(parent, 'normen') else 0.0
    tier_base = (max(n.material_tier for n in parent.normen) if parent and hasattr(parent, 'normen') else 0)
    items = []
    for i, t in enumerate(NanomaterialTyp):
        delta = _WEIGHT_DELTA.get(t.name, 0.0)
        items.append(NanomaterialEintrag(name=_TYP_MAP[t], material_weight=round(basis + delta, 4), material_tier=tier_base + i + 1))
    return NanomaterialRegister(eintraege=tuple(items))
