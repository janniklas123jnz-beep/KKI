from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .petrographie_senat import PetrographieSenat, build_petrographie_senat


class PetrographieNormTyp(Enum):
    ANALYSE_STANDARD = auto()
    KLASSIFIKATIONS_NORM = auto()
    NOMENKLATUR_RICHTLINIE = auto()
    BESCHREIBUNGS_PROTOKOLL = auto()
    PUBLIKATIONS_STANDARD = auto()


class PetrographieNormProzedur(Enum):
    NORMIERUNG = auto()
    STANDARDISIERUNG = auto()
    VALIDIERUNG = auto()
    ZERTIFIZIERUNG = auto()
    AKKREDITIERUNG = auto()


_WEIGHT_DELTA = {
    "ANALYSE_STANDARD": 0.0,
    "KLASSIFIKATIONS_NORM": 1.9,
    "NOMENKLATUR_RICHTLINIE": 3.8,
    "BESCHREIBUNGS_PROTOKOLL": 5.7,
    "PUBLIKATIONS_STANDARD": 7.6,
}
_TYP_MAP = {
    "ANALYSE_STANDARD": "analyse_standard",
    "KLASSIFIKATIONS_NORM": "klassifikations_norm",
    "NOMENKLATUR_RICHTLINIE": "nomenklatur_richtlinie",
    "BESCHREIBUNGS_PROTOKOLL": "beschreibungs_protokoll",
    "PUBLIKATIONS_STANDARD": "publikations_standard",
}
_PROZEDUR_MAP = {
    "NORMIERUNG": "normierung",
    "STANDARDISIERUNG": "standardisierung",
    "VALIDIERUNG": "validierung",
    "ZERTIFIZIERUNG": "zertifizierung",
    "AKKREDITIERUNG": "akkreditierung",
}


@dataclass(frozen=True)
class PetrographieNormEintrag:
    typ: PetrographieNormTyp
    prozedur: PetrographieNormProzedur
    petrographie_norm_weight: float
    petrographie_norm_tier: int
    canonical: bool = True


@dataclass(frozen=True)
class PetrographieNorm:
    normen: tuple[PetrographieNormEintrag, ...]
    canonical: bool = True

    def aggregates_norm_signal(self) -> dict:
        return {
            "norm_id": "petrographie-norm-888",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_petrographie_norm(parent: Optional[PetrographieSenat] = None) -> PetrographieNorm:
    if parent is None:
        parent = build_petrographie_senat()
    base = sum(n.petrographie_weight for n in parent.normen)
    normen = tuple(
        PetrographieNormEintrag(
            typ=t,
            prozedur=list(PetrographieNormProzedur)[i],
            petrographie_norm_weight=base + _WEIGHT_DELTA[t.name],
            petrographie_norm_tier=i + 1,
        )
        for i, t in enumerate(PetrographieNormTyp)
    )
    return PetrographieNorm(normen=normen)
