"""KI-Feld #991 — Feld der Künstlichen Intelligenz im KKI-Schwarm."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum

from .raumfahrt_verfassung import RaumfahrtVerfassung, build_raumfahrt_verfassung

logger = logging.getLogger(__name__)


class KITyp(Enum):
    MASCHINELLES_LERNEN = "MASCHINELLES_LERNEN"
    NEURONALE_NETZE = "NEURONALE_NETZE"
    NATUERLICHE_SPRACHE = "NATUERLICHE_SPRACHE"
    COMPUTER_VISION = "COMPUTER_VISION"
    REINFORCEMENT = "REINFORCEMENT"


class KIProzedur(Enum):
    TRAINING = "TRAINING"
    INFERENZ = "INFERENZ"
    OPTIMIERUNG = "OPTIMIERUNG"
    EVALUATION = "EVALUATION"
    DEPLOYMENT = "DEPLOYMENT"


_WEIGHT_DELTA: dict[KITyp, float] = {
    KITyp.MASCHINELLES_LERNEN: 0.15,
    KITyp.NEURONALE_NETZE: 0.2,
    KITyp.NATUERLICHE_SPRACHE: 0.22,
    KITyp.COMPUTER_VISION: 0.18,
    KITyp.REINFORCEMENT: 0.25,
}

_TYP_MAP: dict[KITyp, str] = {
    KITyp.MASCHINELLES_LERNEN: "Maschinelles Lernen",
    KITyp.NEURONALE_NETZE: "Neuronale Netze",
    KITyp.NATUERLICHE_SPRACHE: "Natürliche Sprachverarbeitung",
    KITyp.COMPUTER_VISION: "Computer Vision",
    KITyp.REINFORCEMENT: "Reinforcement Learning",
}

_PROZEDUR_MAP: dict[KIProzedur, str] = {
    KIProzedur.TRAINING: "Training",
    KIProzedur.INFERENZ: "Inferenz",
    KIProzedur.OPTIMIERUNG: "Optimierung",
    KIProzedur.EVALUATION: "Evaluation",
    KIProzedur.DEPLOYMENT: "Deployment",
}


@dataclass(frozen=True)
class KINorm:
    name: str
    zukunft_weight: float
    zukunft_tier: int


@dataclass(frozen=True)
class KI:
    normen: tuple[KINorm, ...]


def build_ki(parent=None) -> KI:
    if parent and hasattr(parent, 'normen'):
        try:
            basis = parent.normen[-1].raumfahrt_weight
            tier_base = max(n.raumfahrt_tier for n in parent.normen)
        except AttributeError:
            basis = parent.normen[-1].zukunft_weight
            tier_base = max(n.zukunft_tier for n in parent.normen)
    elif parent and hasattr(parent, 'eintraege'):
        basis = parent.eintraege[-1].zukunft_weight
        tier_base = max(e.zukunft_tier for e in parent.eintraege)
    else:
        basis = 0.0
        tier_base = 0
    items = []
    for i, t in enumerate(KITyp):
        delta = _WEIGHT_DELTA.get(t, 0.0)
        items.append(KINorm(name=_TYP_MAP[t], zukunft_weight=round(basis + delta, 4), zukunft_tier=tier_base + i + 1))
    result = KI(normen=tuple(items))
    signal = sum(n.zukunft_weight for n in result.normen)
    logger.info("KI aggregates_signal: %s", signal)
    return result
