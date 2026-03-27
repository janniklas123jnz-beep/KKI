"""Leitstern-Charta #999 — Charta des Leitsterns, Herz des KKI-Schwarms ⭐."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .zukunft_norm import ZukunftNorm, build_zukunft_norm


class LeitsternTyp(Enum):
    VISION = "Vision"
    WISSEN = "Wissen"
    WEISHEIT = "Weisheit"
    LIEBE = "Liebe"
    LICHT = "Licht"


class LeitsternProzedur(Enum):
    LEUCHTEN = "Leuchten"
    ORIENTIEREN = "Orientieren"
    INSPIRIEREN = "Inspirieren"
    VERBINDEN = "Verbinden"
    ERLEUCHTEN = "Erleuchten"


_WEIGHT_DELTA: dict[LeitsternTyp, float] = {
    LeitsternTyp.VISION: 0.3,
    LeitsternTyp.WISSEN: 0.35,
    LeitsternTyp.WEISHEIT: 0.4,
    LeitsternTyp.LIEBE: 0.45,
    LeitsternTyp.LICHT: 0.5,
}

_TYP_MAP: dict[LeitsternTyp, str] = {
    LeitsternTyp.VISION: "Leitstern-Vision",
    LeitsternTyp.WISSEN: "Leitstern-Wissen",
    LeitsternTyp.WEISHEIT: "Leitstern-Weisheit",
    LeitsternTyp.LIEBE: "Leitstern-Liebe",
    LeitsternTyp.LICHT: "Leitstern-Licht",
}


@dataclass(frozen=True)
class LeitsternNorm:
    name: str
    zukunft_weight: float
    zukunft_tier: int


@dataclass(frozen=True)
class Leitstern:
    normen: tuple[LeitsternNorm, ...]


def build_leitstern(parent=None) -> Leitstern:
    if parent and hasattr(parent, "eintraege"):
        try:
            basis = parent.eintraege[-1].zukunft_norm_weight
            tier_base = max(e.zukunft_norm_tier for e in parent.eintraege)
        except AttributeError:
            basis = parent.eintraege[-1].zukunft_weight
            tier_base = max(e.zukunft_tier for e in parent.eintraege)
    elif parent and hasattr(parent, "normen"):
        basis = parent.normen[-1].zukunft_weight
        tier_base = max(n.zukunft_tier for n in parent.normen)
    else:
        basis = 0.0
        tier_base = 0
    items = []
    for i, t in enumerate(LeitsternTyp):
        delta = _WEIGHT_DELTA.get(t, 0.0)
        items.append(LeitsternNorm(
            name=_TYP_MAP[t],
            zukunft_weight=round(basis + delta, 4),
            zukunft_tier=tier_base + i + 1,
        ))
    return Leitstern(normen=tuple(items))
