"""Bewusstsein-Register #992 — Katalog der Bewusstseinszustände im KKI-Schwarm."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum

from .ki_feld import KI, build_ki

logger = logging.getLogger(__name__)


class BewusstseinTyp(Enum):
    QUALIA = "QUALIA"
    SELBSTWAHRNEHMUNG = "SELBSTWAHRNEHMUNG"
    EMPATHIE = "EMPATHIE"
    METAKOGNITION = "METAKOGNITION"
    KOLLEKTIVBEWUSSTSEIN = "KOLLEKTIVBEWUSSTSEIN"


class BewusstseinProzedur(Enum):
    INTROSPEKTION = "INTROSPEKTION"
    MEDITATION = "MEDITATION"
    NEUROFEEDBACK = "NEUROFEEDBACK"
    INTEGRATION = "INTEGRATION"
    EXPANSION = "EXPANSION"


_WEIGHT_DELTA: dict[str, float] = {
    "QUALIA": 0.18,
    "SELBSTWAHRNEHMUNG": 0.2,
    "EMPATHIE": 0.15,
    "METAKOGNITION": 0.22,
    "KOLLEKTIVBEWUSSTSEIN": 0.28,
}

_TYP_MAP: dict[BewusstseinTyp, str] = {
    BewusstseinTyp.QUALIA: "Qualia-Bewusstsein",
    BewusstseinTyp.SELBSTWAHRNEHMUNG: "Selbstwahrnehmung",
    BewusstseinTyp.EMPATHIE: "Empathisches Bewusstsein",
    BewusstseinTyp.METAKOGNITION: "Metakognition",
    BewusstseinTyp.KOLLEKTIVBEWUSSTSEIN: "Kollektivbewusstsein",
}

_PROZEDUR_MAP: dict[BewusstseinProzedur, str] = {
    BewusstseinProzedur.INTROSPEKTION: "Introspektion",
    BewusstseinProzedur.MEDITATION: "Meditation",
    BewusstseinProzedur.NEUROFEEDBACK: "Neurofeedback",
    BewusstseinProzedur.INTEGRATION: "Integration",
    BewusstseinProzedur.EXPANSION: "Expansion",
}


@dataclass(frozen=True)
class BewusstseinEintrag:
    name: str
    zukunft_weight: float
    zukunft_tier: int


@dataclass(frozen=True)
class BewusstseinRegister:
    eintraege: tuple[BewusstseinEintrag, ...]


def build_bewusstsein_register(parent=None) -> BewusstseinRegister:
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
    for i, t in enumerate(BewusstseinTyp):
        delta = _WEIGHT_DELTA.get(t.name, 0.0)
        items.append(BewusstseinEintrag(name=_TYP_MAP[t], zukunft_weight=round(basis + delta, 4), zukunft_tier=tier_base + i + 1))
    result = BewusstseinRegister(eintraege=tuple(items))
    signal = sum(e.zukunft_weight for e in result.eintraege)
    logger.info("BewusstseinRegister aggregates_signal: %s", signal)
    return result
