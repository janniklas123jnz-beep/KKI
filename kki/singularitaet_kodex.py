"""Singularität-Kodex #994 — Kodex der Technologischen Singularität im KKI-Schwarm."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum

from .transhumanismus_charta import Transhumanismus, build_transhumanismus

logger = logging.getLogger(__name__)


class SingularitaetTyp(Enum):
    TECHNOLOGISCHE_SINGULARITAET = "TECHNOLOGISCHE_SINGULARITAET"
    AGI = "AGI"
    ASI = "ASI"
    INTELLIGENZEXPLOSION = "INTELLIGENZEXPLOSION"
    EMERGENZ = "EMERGENZ"


class SingularitaetProzedur(Enum):
    ANALYSE = "ANALYSE"
    MODELLIERUNG = "MODELLIERUNG"
    VORBEREITUNG = "VORBEREITUNG"
    ALIGNMENT = "ALIGNMENT"
    STEUERUNG = "STEUERUNG"


_WEIGHT_DELTA: dict[str, float] = {
    "TECHNOLOGISCHE_SINGULARITAET": 0.3,
    "AGI": 0.35,
    "ASI": 0.4,
    "INTELLIGENZEXPLOSION": 0.38,
    "EMERGENZ": 0.28,
}

_TYP_MAP: dict[SingularitaetTyp, str] = {
    SingularitaetTyp.TECHNOLOGISCHE_SINGULARITAET: "Technologische Singularität",
    SingularitaetTyp.AGI: "Artificial General Intelligence",
    SingularitaetTyp.ASI: "Artificial Superintelligence",
    SingularitaetTyp.INTELLIGENZEXPLOSION: "Intelligenzexplosion",
    SingularitaetTyp.EMERGENZ: "Emergente Superintelligenz",
}

_PROZEDUR_MAP: dict[SingularitaetProzedur, str] = {
    SingularitaetProzedur.ANALYSE: "Analyse",
    SingularitaetProzedur.MODELLIERUNG: "Modellierung",
    SingularitaetProzedur.VORBEREITUNG: "Vorbereitung",
    SingularitaetProzedur.ALIGNMENT: "Alignment",
    SingularitaetProzedur.STEUERUNG: "Steuerung",
}


@dataclass(frozen=True)
class SingularitaetEintrag:
    name: str
    zukunft_weight: float
    zukunft_tier: int


@dataclass(frozen=True)
class SingularitaetKodex:
    eintraege: tuple[SingularitaetEintrag, ...]


def build_singularitaet_kodex(parent=None) -> SingularitaetKodex:
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
    for i, t in enumerate(SingularitaetTyp):
        delta = _WEIGHT_DELTA.get(t.name, 0.0)
        items.append(SingularitaetEintrag(name=_TYP_MAP[t], zukunft_weight=round(basis + delta, 4), zukunft_tier=tier_base + i + 1))
    result = SingularitaetKodex(eintraege=tuple(items))
    signal = sum(e.zukunft_weight for e in result.eintraege)
    logger.info("SingularitaetKodex aggregates_signal: %s", signal)
    return result
