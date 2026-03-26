from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .glaziologie_senat import GlaziologieSenat, build_glaziologie_senat


class GlaziologieNormTyp(Enum):
    MESS_STANDARD = auto()
    KLASSIFIKATIONS_NORM = auto()
    INVENTAR_PROTOKOLL = auto()
    MONITORING_RICHTLINIE = auto()
    DATEN_STANDARD = auto()


class GlaziologieNormProzedur(Enum):
    NORMIERUNG = auto()
    STANDARDISIERUNG = auto()
    VALIDIERUNG = auto()
    ZERTIFIZIERUNG = auto()
    AKKREDITIERUNG = auto()


_WEIGHT_DELTA = {
    "MESS_STANDARD": 0.0,
    "KLASSIFIKATIONS_NORM": 1.9,
    "INVENTAR_PROTOKOLL": 3.8,
    "MONITORING_RICHTLINIE": 5.7,
    "DATEN_STANDARD": 7.6,
}
_TYP_MAP = {
    "MESS_STANDARD": "mess_standard",
    "KLASSIFIKATIONS_NORM": "klassifikations_norm",
    "INVENTAR_PROTOKOLL": "inventar_protokoll",
    "MONITORING_RICHTLINIE": "monitoring_richtlinie",
    "DATEN_STANDARD": "daten_standard",
}
_PROZEDUR_MAP = {
    "NORMIERUNG": "normierung",
    "STANDARDISIERUNG": "standardisierung",
    "VALIDIERUNG": "validierung",
    "ZERTIFIZIERUNG": "zertifizierung",
    "AKKREDITIERUNG": "akkreditierung",
}


@dataclass(frozen=True)
class GlaziologieNormEintrag:
    typ: GlaziologieNormTyp
    prozedur: GlaziologieNormProzedur
    glaziologie_norm_weight: float
    glaziologie_norm_tier: int
    canonical: bool = True


@dataclass(frozen=True)
class GlaziologieNorm:
    normen: tuple[GlaziologieNormEintrag, ...]
    canonical: bool = True

    def aggregates_norm_signal(self) -> dict:
        return {
            "norm_id": "glaziologie-norm-898",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_glaziologie_norm(parent: Optional[GlaziologieSenat] = None) -> GlaziologieNorm:
    if parent is None:
        parent = build_glaziologie_senat()
    base = sum(n.glaziologie_weight for n in parent.normen)
    normen = tuple(
        GlaziologieNormEintrag(
            typ=t,
            prozedur=list(GlaziologieNormProzedur)[i],
            glaziologie_norm_weight=base + _WEIGHT_DELTA[t.name],
            glaziologie_norm_tier=i + 1,
        )
        for i, t in enumerate(GlaziologieNormTyp)
    )
    return GlaziologieNorm(normen=normen)
