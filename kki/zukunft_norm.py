"""Zukunft-Norm #998 — Normenwerk der Zukunftswerte im KKI-Schwarm."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .omega_senat import Omega, build_omega


class ZukunftNormTyp(Enum):
    NACHHALTIGKEIT = "Nachhaltigkeit"
    GERECHTIGKEIT = "Gerechtigkeit"
    FREIHEIT = "Freiheit"
    HARMONIE = "Harmonie"
    EVOLUTION = "Evolution"


class ZukunftNormProzedur(Enum):
    DEFINIEREN = "Definieren"
    MESSEN = "Messen"
    ANWENDEN = "Anwenden"
    UEBERWACHEN = "Ueberwachen"
    WEITERENTWICKELN = "Weiterentwickeln"


_WEIGHT_DELTA: dict[str, float] = {
    "NACHHALTIGKEIT": 0.3,
    "GERECHTIGKEIT": 0.35,
    "FREIHEIT": 0.32,
    "HARMONIE": 0.38,
    "EVOLUTION": 0.4,
}

_TYP_MAP: dict[ZukunftNormTyp, str] = {
    ZukunftNormTyp.NACHHALTIGKEIT: "Nachhaltigkeitsnorm",
    ZukunftNormTyp.GERECHTIGKEIT: "Gerechtigkeitsnorm",
    ZukunftNormTyp.FREIHEIT: "Freiheitsnorm",
    ZukunftNormTyp.HARMONIE: "Harmonienorm",
    ZukunftNormTyp.EVOLUTION: "Evolutionsnorm",
}


@dataclass(frozen=True)
class ZukunftNormEintrag:
    name: str
    zukunft_norm_weight: float
    zukunft_norm_tier: int


@dataclass(frozen=True)
class ZukunftNorm:
    eintraege: tuple[ZukunftNormEintrag, ...]


def build_zukunft_norm(parent=None) -> ZukunftNorm:
    if parent and hasattr(parent, "normen"):
        basis = parent.normen[-1].zukunft_weight
        tier_base = max(n.zukunft_tier for n in parent.normen)
    elif parent and hasattr(parent, "eintraege"):
        basis = parent.eintraege[-1].zukunft_weight
        tier_base = max(e.zukunft_tier for e in parent.eintraege)
    else:
        basis = 0.0
        tier_base = 0
    items = []
    for i, t in enumerate(ZukunftNormTyp):
        delta = _WEIGHT_DELTA.get(t.name, 0.0)
        items.append(ZukunftNormEintrag(
            name=_TYP_MAP[t],
            zukunft_norm_weight=round(basis + delta, 4),
            zukunft_norm_tier=tier_base + i + 1,
        ))
    return ZukunftNorm(eintraege=tuple(items))
