"""Raumfahrt-Norm #988 — Normenwerk der Raumfahrtstandards im KKI-Schwarm."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

from .mars_senat import Mars, build_mars


class RaumfahrtNormTyp(Enum):
    SICHERHEIT = "SICHERHEIT"
    ZUVERLAESSIGKEIT = "ZUVERLAESSIGKEIT"
    KOMPATIBILITAET = "KOMPATIBILITAET"
    UMWELT = "UMWELT"
    ETHIK = "ETHIK"


class RaumfahrtNormProzedur(Enum):
    PRUEFEN = "PRUEFEN"
    ZERTIFIZIEREN = "ZERTIFIZIEREN"
    UEBERWACHEN = "UEBERWACHEN"
    AKTUALISIEREN = "AKTUALISIEREN"
    DURCHSETZEN = "DURCHSETZEN"


_WEIGHT_DELTA: dict[str, float] = {
    "SICHERHEIT": 0.15,
    "ZUVERLAESSIGKEIT": 0.18,
    "KOMPATIBILITAET": 0.13,
    "UMWELT": 0.16,
    "ETHIK": 0.14,
}

_TYP_MAP: dict[RaumfahrtNormTyp, str] = {
    RaumfahrtNormTyp.SICHERHEIT: "Raumfahrt-Sicherheitsnorm",
    RaumfahrtNormTyp.ZUVERLAESSIGKEIT: "Zuverlässigkeitsnorm",
    RaumfahrtNormTyp.KOMPATIBILITAET: "Kompatibilitätsnorm",
    RaumfahrtNormTyp.UMWELT: "Raumfahrt-Umweltnorm",
    RaumfahrtNormTyp.ETHIK: "Raumfahrt-Ethiknorm",
}

_PROZEDUR_MAP: dict[RaumfahrtNormProzedur, str] = {
    RaumfahrtNormProzedur.PRUEFEN: "Prüfen",
    RaumfahrtNormProzedur.ZERTIFIZIEREN: "Zertifizieren",
    RaumfahrtNormProzedur.UEBERWACHEN: "Überwachen",
    RaumfahrtNormProzedur.AKTUALISIEREN: "Aktualisieren",
    RaumfahrtNormProzedur.DURCHSETZEN: "Durchsetzen",
}


@dataclass(frozen=True)
class RaumfahrtNormEintrag:
    name: str
    raumfahrt_norm_weight: float
    raumfahrt_norm_tier: int


@dataclass(frozen=True)
class RaumfahrtNorm:
    eintraege: tuple[RaumfahrtNormEintrag, ...]


def build_raumfahrt_norm(parent=None) -> RaumfahrtNorm:
    if parent and hasattr(parent, 'normen'):
        basis = parent.normen[-1].raumfahrt_weight
        tier_base = max(n.raumfahrt_tier for n in parent.normen)
    elif parent and hasattr(parent, 'eintraege') and hasattr(list(parent.eintraege)[0], 'raumfahrt_weight'):
        basis = parent.eintraege[-1].raumfahrt_weight
        tier_base = max(e.raumfahrt_tier for e in parent.eintraege)
    else:
        basis = 0.0
        tier_base = 0
    items = []
    for i, t in enumerate(RaumfahrtNormTyp):
        delta = _WEIGHT_DELTA.get(t.name, 0.0)
        items.append(RaumfahrtNormEintrag(name=_TYP_MAP[t], raumfahrt_norm_weight=round(basis + delta, 4), raumfahrt_norm_tier=tier_base + i + 1))
    return RaumfahrtNorm(eintraege=tuple(items))
