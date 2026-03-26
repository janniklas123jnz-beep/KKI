from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .altersbestimmung_charta import AltersbestimmungCharta, build_altersbestimmung_charta


class GeochronologieVerfassungTyp(Enum):
    GRUNDGESETZ = auto()
    FORSCHUNGSAUFTRAG = auto()
    BILDUNGSMANDAT = auto()
    ETHIKPRINZIP = auto()
    NACHHALTIGKEITSGEBOT = auto()


class GeochronologieVerfassungProzedur(Enum):
    RATIFIZIERUNG = auto()
    REVISION = auto()
    INKRAFTTRETEN = auto()
    AUSLEGUNG = auto()
    DURCHSETZUNG = auto()


_WEIGHT_DELTA = {
    GeochronologieVerfassungTyp.GRUNDGESETZ: 0.0,
    GeochronologieVerfassungTyp.FORSCHUNGSAUFTRAG: 2.1,
    GeochronologieVerfassungTyp.BILDUNGSMANDAT: 4.2,
    GeochronologieVerfassungTyp.ETHIKPRINZIP: 6.3,
    GeochronologieVerfassungTyp.NACHHALTIGKEITSGEBOT: 8.4,
}
_TYP_MAP = {
    GeochronologieVerfassungTyp.GRUNDGESETZ: "grundgesetz",
    GeochronologieVerfassungTyp.FORSCHUNGSAUFTRAG: "forschungsauftrag",
    GeochronologieVerfassungTyp.BILDUNGSMANDAT: "bildungsmandat",
    GeochronologieVerfassungTyp.ETHIKPRINZIP: "ethikprinzip",
    GeochronologieVerfassungTyp.NACHHALTIGKEITSGEBOT: "nachhaltigkeitsgebot",
}
_PROZEDUR_MAP = {
    GeochronologieVerfassungProzedur.RATIFIZIERUNG: "ratifizierung",
    GeochronologieVerfassungProzedur.REVISION: "revision",
    GeochronologieVerfassungProzedur.INKRAFTTRETEN: "inkrafttreten",
    GeochronologieVerfassungProzedur.AUSLEGUNG: "auslegung",
    GeochronologieVerfassungProzedur.DURCHSETZUNG: "durchsetzung",
}


@dataclass(frozen=True)
class GeochronologieVerfassungNorm:
    typ: GeochronologieVerfassungTyp
    prozedur: GeochronologieVerfassungProzedur
    geochronologie_weight: float
    geochronologie_tier: int
    canonical: bool = True


@dataclass(frozen=True)
class GeochronologieVerfassung:
    normen: tuple[GeochronologieVerfassungNorm, ...]
    canonical: bool = True

    def aggregates_verfassung_signal(self) -> dict:
        return {
            "verfassung_id": "geochronologie-verfassung-880",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_geochronologie_verfassung(parent: Optional[AltersbestimmungCharta] = None) -> GeochronologieVerfassung:
    if parent is None:
        parent = build_altersbestimmung_charta()
    base = sum(n.geochronologie_weight for n in parent.normen)
    tier_base = max(n.tier for n in parent.normen)
    normen = tuple(
        GeochronologieVerfassungNorm(
            typ=t,
            prozedur=list(GeochronologieVerfassungProzedur)[i],
            geochronologie_weight=base + _WEIGHT_DELTA[t],
            geochronologie_tier=tier_base + i + 1,
        )
        for i, t in enumerate(GeochronologieVerfassungTyp)
    )
    return GeochronologieVerfassung(normen=normen)
