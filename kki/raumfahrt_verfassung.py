"""Raumfahrt-Verfassung #990 — Verfassung der Luft- und Raumfahrt im KKI-Schwarm ⭐."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import logging

from .weltraum_charta import Weltraum, build_weltraum

logger = logging.getLogger(__name__)


class RaumfahrtVerfassungTyp(Enum):
    VISION = "VISION"
    MISSION = "MISSION"
    ETHIK = "ETHIK"
    KOOPERATION = "KOOPERATION"
    ZUKUNFT = "ZUKUNFT"


class RaumfahrtVerfassungProzedur(Enum):
    INSPIRATION = "INSPIRATION"
    PLANUNG = "PLANUNG"
    UMSETZUNG = "UMSETZUNG"
    EVALUATION = "EVALUATION"
    EVOLUTION = "EVOLUTION"


_WEIGHT_DELTA: dict[RaumfahrtVerfassungTyp, float] = {
    RaumfahrtVerfassungTyp.VISION: 0.15,
    RaumfahrtVerfassungTyp.MISSION: 0.2,
    RaumfahrtVerfassungTyp.ETHIK: 0.18,
    RaumfahrtVerfassungTyp.KOOPERATION: 0.22,
    RaumfahrtVerfassungTyp.ZUKUNFT: 0.3,
}

_TYP_MAP: dict[RaumfahrtVerfassungTyp, str] = {
    RaumfahrtVerfassungTyp.VISION: "Raumfahrtvision",
    RaumfahrtVerfassungTyp.MISSION: "Raumfahrtmission",
    RaumfahrtVerfassungTyp.ETHIK: "Raumfahrtethik",
    RaumfahrtVerfassungTyp.KOOPERATION: "Internationale Kooperation",
    RaumfahrtVerfassungTyp.ZUKUNFT: "Zukunft der Menschheit im All",
}

_PROZEDUR_MAP: dict[RaumfahrtVerfassungProzedur, str] = {
    RaumfahrtVerfassungProzedur.INSPIRATION: "Inspiration",
    RaumfahrtVerfassungProzedur.PLANUNG: "Planung",
    RaumfahrtVerfassungProzedur.UMSETZUNG: "Umsetzung",
    RaumfahrtVerfassungProzedur.EVALUATION: "Evaluation",
    RaumfahrtVerfassungProzedur.EVOLUTION: "Evolution",
}


@dataclass(frozen=True)
class RaumfahrtVerfassungNorm:
    name: str
    raumfahrt_weight: float
    raumfahrt_tier: int


@dataclass(frozen=True)
class RaumfahrtVerfassung:
    normen: tuple[RaumfahrtVerfassungNorm, ...]


def build_raumfahrt_verfassung(parent=None) -> RaumfahrtVerfassung:
    if parent and hasattr(parent, 'normen'):
        basis = parent.normen[-1].raumfahrt_weight
        tier_base = max(n.raumfahrt_tier for n in parent.normen)
    elif parent and hasattr(parent, 'eintraege'):
        basis = parent.eintraege[-1].raumfahrt_weight
        tier_base = max(e.raumfahrt_tier for e in parent.eintraege)
    else:
        basis = 0.0
        tier_base = 0
    items = []
    for i, t in enumerate(RaumfahrtVerfassungTyp):
        delta = _WEIGHT_DELTA.get(t, 0.0)
        items.append(RaumfahrtVerfassungNorm(name=_TYP_MAP[t], raumfahrt_weight=round(basis + delta, 4), raumfahrt_tier=tier_base + i + 1))
    result = RaumfahrtVerfassung(normen=tuple(items))
    signal = sum(n.raumfahrt_weight for n in result.normen)
    logger.info("RaumfahrtVerfassung aggregates_signal: %s", signal)
    return result
