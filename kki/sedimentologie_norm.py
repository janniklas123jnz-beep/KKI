from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .sedimentologie_senat import SedimentologieSenat, build_sedimentologie_senat


class SedimentologieNormTyp(Enum):
    ABLAGERUNGS_STANDARD = auto()
    ANALYSE_PROTOKOLL = auto()
    KLASSIFIKATIONS_NORM = auto()
    BEWERTUNGS_RICHTLINIE = auto()
    DOKUMENTATIONS_STANDARD = auto()


class SedimentologieNormProzedur(Enum):
    NORMIERUNG = auto()
    STANDARDISIERUNG = auto()
    VALIDIERUNG = auto()
    ZERTIFIZIERUNG = auto()
    AKKREDITIERUNG = auto()


_WEIGHT_DELTA = {
    "ABLAGERUNGS_STANDARD": 0.0,
    "ANALYSE_PROTOKOLL": 1.9,
    "KLASSIFIKATIONS_NORM": 3.8,
    "BEWERTUNGS_RICHTLINIE": 5.7,
    "DOKUMENTATIONS_STANDARD": 7.6,
}
_TYP_MAP = {
    "ABLAGERUNGS_STANDARD": "ablagerungs_standard",
    "ANALYSE_PROTOKOLL": "analyse_protokoll",
    "KLASSIFIKATIONS_NORM": "klassifikations_norm",
    "BEWERTUNGS_RICHTLINIE": "bewertungs_richtlinie",
    "DOKUMENTATIONS_STANDARD": "dokumentations_standard",
}
_PROZEDUR_MAP = {
    "NORMIERUNG": "normierung",
    "STANDARDISIERUNG": "standardisierung",
    "VALIDIERUNG": "validierung",
    "ZERTIFIZIERUNG": "zertifizierung",
    "AKKREDITIERUNG": "akkreditierung",
}


@dataclass(frozen=True)
class SedimentologieNormEintrag:
    typ: SedimentologieNormTyp
    prozedur: SedimentologieNormProzedur
    sedimentologie_norm_weight: float
    sedimentologie_norm_tier: int
    canonical: bool = True


@dataclass(frozen=True)
class SedimentologieNorm:
    normen: tuple[SedimentologieNormEintrag, ...]
    canonical: bool = True

    def aggregates_norm_signal(self) -> dict:
        return {
            "norm_id": "sedimentologie-norm-868",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_sedimentologie_norm(parent: Optional[SedimentologieSenat] = None) -> SedimentologieNorm:
    if parent is None:
        parent = build_sedimentologie_senat()
    base = sum(n.sedimentologie_weight for n in parent.normen)
    normen = tuple(
        SedimentologieNormEintrag(
            typ=t,
            prozedur=list(SedimentologieNormProzedur)[i],
            sedimentologie_norm_weight=base + _WEIGHT_DELTA[t.name],
            sedimentologie_norm_tier=i + 1,
        )
        for i, t in enumerate(SedimentologieNormTyp)
    )
    return SedimentologieNorm(normen=normen)
