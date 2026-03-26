from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .magnetostratigraphie_pakt import MagnetostratigraphiePakt, build_magnetostratigraphie_pakt


class GeochronologieSenatTyp(Enum):
    ZEITSKALA = auto()
    EPOCHENGRENZE = auto()
    EONGRENZE = auto()
    PERIODGRENZE = auto()
    STUFENGRENZE = auto()


class GeochronologieSenatProzedur(Enum):
    BERATUNG = auto()
    STANDARDISIERUNG = auto()
    RATIFIZIERUNG = auto()
    REVISION = auto()
    KOORDINATION = auto()


_WEIGHT_DELTA = {
    GeochronologieSenatTyp.ZEITSKALA: 0.0,
    GeochronologieSenatTyp.EPOCHENGRENZE: 1.8,
    GeochronologieSenatTyp.EONGRENZE: 3.6,
    GeochronologieSenatTyp.PERIODGRENZE: 5.4,
    GeochronologieSenatTyp.STUFENGRENZE: 7.2,
}
_TYP_MAP = {
    GeochronologieSenatTyp.ZEITSKALA: "zeitskala",
    GeochronologieSenatTyp.EPOCHENGRENZE: "epochengrenze",
    GeochronologieSenatTyp.EONGRENZE: "eongrenze",
    GeochronologieSenatTyp.PERIODGRENZE: "periodgrenze",
    GeochronologieSenatTyp.STUFENGRENZE: "stufengrenze",
}
_PROZEDUR_MAP = {
    GeochronologieSenatProzedur.BERATUNG: "beratung",
    GeochronologieSenatProzedur.STANDARDISIERUNG: "standardisierung",
    GeochronologieSenatProzedur.RATIFIZIERUNG: "ratifizierung",
    GeochronologieSenatProzedur.REVISION: "revision",
    GeochronologieSenatProzedur.KOORDINATION: "koordination",
}


@dataclass(frozen=True)
class GeochronologieSenatNorm:
    typ: GeochronologieSenatTyp
    prozedur: GeochronologieSenatProzedur
    geochronologie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class GeochronologieSenat:
    normen: tuple[GeochronologieSenatNorm, ...]
    canonical: bool = True

    def aggregates_senat_signal(self) -> dict:
        return {
            "senat_id": "geochronologie-senat-877",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_geochronologie_senat(parent: Optional[MagnetostratigraphiePakt] = None) -> GeochronologieSenat:
    if parent is None:
        parent = build_magnetostratigraphie_pakt()
    base = sum(e.geochronologie_weight for e in parent.eintraege)
    normen = tuple(
        GeochronologieSenatNorm(
            typ=t,
            prozedur=list(GeochronologieSenatProzedur)[i],
            geochronologie_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(GeochronologieSenatTyp)
    )
    return GeochronologieSenat(normen=normen)
