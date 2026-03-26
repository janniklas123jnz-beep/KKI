from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .geochronologie_senat import GeochronologieSenat, build_geochronologie_senat


class GeochronologieNormTyp(Enum):
    DATIERUNGS_STANDARD = auto()
    MESS_PROTOKOLL = auto()
    KALIBRIERUNGS_NORM = auto()
    FEHLER_RICHTLINIE = auto()
    PUBLIKATIONS_STANDARD = auto()


class GeochronologieNormProzedur(Enum):
    NORMIERUNG = auto()
    STANDARDISIERUNG = auto()
    VALIDIERUNG = auto()
    ZERTIFIZIERUNG = auto()
    AKKREDITIERUNG = auto()


_WEIGHT_DELTA = {
    "DATIERUNGS_STANDARD": 0.0,
    "MESS_PROTOKOLL": 1.9,
    "KALIBRIERUNGS_NORM": 3.8,
    "FEHLER_RICHTLINIE": 5.7,
    "PUBLIKATIONS_STANDARD": 7.6,
}
_TYP_MAP = {
    "DATIERUNGS_STANDARD": "datierungs_standard",
    "MESS_PROTOKOLL": "mess_protokoll",
    "KALIBRIERUNGS_NORM": "kalibrierungs_norm",
    "FEHLER_RICHTLINIE": "fehler_richtlinie",
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
class GeochronologieNormEintrag:
    typ: GeochronologieNormTyp
    prozedur: GeochronologieNormProzedur
    geochronologie_norm_weight: float
    geochronologie_norm_tier: int
    canonical: bool = True


@dataclass(frozen=True)
class GeochronologieNorm:
    normen: tuple[GeochronologieNormEintrag, ...]
    canonical: bool = True

    def aggregates_norm_signal(self) -> dict:
        return {
            "norm_id": "geochronologie-norm-878",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_geochronologie_norm(parent: Optional[GeochronologieSenat] = None) -> GeochronologieNorm:
    if parent is None:
        parent = build_geochronologie_senat()
    base = sum(n.geochronologie_weight for n in parent.normen)
    normen = tuple(
        GeochronologieNormEintrag(
            typ=t,
            prozedur=list(GeochronologieNormProzedur)[i],
            geochronologie_norm_weight=base + _WEIGHT_DELTA[t.name],
            geochronologie_norm_tier=i + 1,
        )
        for i, t in enumerate(GeochronologieNormTyp)
    )
    return GeochronologieNorm(normen=normen)
