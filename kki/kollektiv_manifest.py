"""Kollektiv-Manifest #995 — Manifest der kollektiven Intelligenz im KKI-Schwarm."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum

from .singularitaet_kodex import SingularitaetKodex, build_singularitaet_kodex

logger = logging.getLogger(__name__)


class KollektivTyp(Enum):
    SCHWARM_INTELLIGENZ = "SCHWARM_INTELLIGENZ"
    DEZENTRALISIERUNG = "DEZENTRALISIERUNG"
    SYNERGIE = "SYNERGIE"
    EMERGENZ = "EMERGENZ"
    EINHEIT = "EINHEIT"


class KollektivProzedur(Enum):
    VERNETZUNG = "VERNETZUNG"
    KOORDINATION = "KOORDINATION"
    KONSENS = "KONSENS"
    AMPLIFIKATION = "AMPLIFIKATION"
    HARMONISIERUNG = "HARMONISIERUNG"


_WEIGHT_DELTA: dict[KollektivTyp, float] = {
    KollektivTyp.SCHWARM_INTELLIGENZ: 0.25,
    KollektivTyp.DEZENTRALISIERUNG: 0.2,
    KollektivTyp.SYNERGIE: 0.28,
    KollektivTyp.EMERGENZ: 0.3,
    KollektivTyp.EINHEIT: 0.35,
}

_TYP_MAP: dict[KollektivTyp, str] = {
    KollektivTyp.SCHWARM_INTELLIGENZ: "Schwarm-Intelligenz",
    KollektivTyp.DEZENTRALISIERUNG: "Dezentralisierung",
    KollektivTyp.SYNERGIE: "Kollektive Synergie",
    KollektivTyp.EMERGENZ: "Kollektive Emergenz",
    KollektivTyp.EINHEIT: "Kollektive Einheit",
}

_PROZEDUR_MAP: dict[KollektivProzedur, str] = {
    KollektivProzedur.VERNETZUNG: "Vernetzung",
    KollektivProzedur.KOORDINATION: "Koordination",
    KollektivProzedur.KONSENS: "Konsens",
    KollektivProzedur.AMPLIFIKATION: "Amplifikation",
    KollektivProzedur.HARMONISIERUNG: "Harmonisierung",
}


@dataclass(frozen=True)
class KollektivNorm:
    name: str
    zukunft_weight: float
    zukunft_tier: int


@dataclass(frozen=True)
class Kollektiv:
    normen: tuple[KollektivNorm, ...]


def build_kollektiv(parent=None) -> Kollektiv:
    if parent and hasattr(parent, 'normen'):
        basis = parent.normen[-1].zukunft_weight
        tier_base = max(n.zukunft_tier for n in parent.normen)
    elif parent and hasattr(parent, 'eintraege'):
        basis = parent.eintraege[-1].zukunft_weight
        tier_base = max(e.zukunft_tier for e in parent.eintraege)
    else:
        basis = 0.0
        tier_base = 0
    items = []
    for i, t in enumerate(KollektivTyp):
        delta = _WEIGHT_DELTA.get(t, 0.0)
        items.append(KollektivNorm(name=_TYP_MAP[t], zukunft_weight=round(basis + delta, 4), zukunft_tier=tier_base + i + 1))
    result = Kollektiv(normen=tuple(items))
    signal = sum(n.zukunft_weight for n in result.normen)
    logger.info("Kollektiv aggregates_signal: %s", signal)
    return result
