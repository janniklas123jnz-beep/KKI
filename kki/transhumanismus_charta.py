"""Transhumanismus-Charta #993 — Charta des Transhumanismus im KKI-Schwarm."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum

from .bewusstsein_register import BewusstseinRegister, build_bewusstsein_register

logger = logging.getLogger(__name__)


class TranshumanismusTyp(Enum):
    GEHIRN_COMPUTER = "GEHIRN_COMPUTER"
    GENETISCHE_VERBESSERUNG = "GENETISCHE_VERBESSERUNG"
    LONGEVITY = "LONGEVITY"
    MIND_UPLOAD = "MIND_UPLOAD"
    CYBORG = "CYBORG"


class TranshumanismusProzedur(Enum):
    AUGMENTATION = "AUGMENTATION"
    INTEGRATION = "INTEGRATION"
    OPTIMIERUNG = "OPTIMIERUNG"
    EVOLUTION = "EVOLUTION"
    TRANSZENDENZ = "TRANSZENDENZ"


_WEIGHT_DELTA: dict[TranshumanismusTyp, float] = {
    TranshumanismusTyp.GEHIRN_COMPUTER: 0.25,
    TranshumanismusTyp.GENETISCHE_VERBESSERUNG: 0.2,
    TranshumanismusTyp.LONGEVITY: 0.18,
    TranshumanismusTyp.MIND_UPLOAD: 0.3,
    TranshumanismusTyp.CYBORG: 0.22,
}

_TYP_MAP: dict[TranshumanismusTyp, str] = {
    TranshumanismusTyp.GEHIRN_COMPUTER: "Gehirn-Computer-Interface",
    TranshumanismusTyp.GENETISCHE_VERBESSERUNG: "Genetische Verbesserung",
    TranshumanismusTyp.LONGEVITY: "Lebensverlängerung",
    TranshumanismusTyp.MIND_UPLOAD: "Mind-Upload",
    TranshumanismusTyp.CYBORG: "Cyborg-Technologie",
}

_PROZEDUR_MAP: dict[TranshumanismusProzedur, str] = {
    TranshumanismusProzedur.AUGMENTATION: "Augmentation",
    TranshumanismusProzedur.INTEGRATION: "Integration",
    TranshumanismusProzedur.OPTIMIERUNG: "Optimierung",
    TranshumanismusProzedur.EVOLUTION: "Evolution",
    TranshumanismusProzedur.TRANSZENDENZ: "Transzendenz",
}


@dataclass(frozen=True)
class TranshumanismusNorm:
    name: str
    zukunft_weight: float
    zukunft_tier: int


@dataclass(frozen=True)
class Transhumanismus:
    normen: tuple[TranshumanismusNorm, ...]


def build_transhumanismus(parent=None) -> Transhumanismus:
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
    for i, t in enumerate(TranshumanismusTyp):
        delta = _WEIGHT_DELTA.get(t, 0.0)
        items.append(TranshumanismusNorm(name=_TYP_MAP[t], zukunft_weight=round(basis + delta, 4), zukunft_tier=tier_base + i + 1))
    result = Transhumanismus(normen=tuple(items))
    signal = sum(n.zukunft_weight for n in result.normen)
    logger.info("Transhumanismus aggregates_signal: %s", signal)
    return result
