from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .sedimentologie_verfassung import SedimentologieVerfassung, build_sedimentologie_verfassung


class GeochronologieFeldTyp(Enum):
    ABSOLUT = auto()
    RELATIV = auto()
    RADIOMETRISCH = auto()
    BIOSTRATIGRAPHISCH = auto()
    MAGNETOSTRATIGRAPHISCH = auto()


class GeochronologieFeldProzedur(Enum):
    DATIERUNG = auto()
    KALIBRIERUNG = auto()
    KORRELATION = auto()
    VALIDIERUNG = auto()
    INTERPRETATION = auto()


_WEIGHT_DELTA = {
    GeochronologieFeldTyp.ABSOLUT: 0.0,
    GeochronologieFeldTyp.RELATIV: 1.2,
    GeochronologieFeldTyp.RADIOMETRISCH: 2.4,
    GeochronologieFeldTyp.BIOSTRATIGRAPHISCH: 3.6,
    GeochronologieFeldTyp.MAGNETOSTRATIGRAPHISCH: 5.0,
}
_TYP_MAP = {
    GeochronologieFeldTyp.ABSOLUT: "absolut",
    GeochronologieFeldTyp.RELATIV: "relativ",
    GeochronologieFeldTyp.RADIOMETRISCH: "radiometrisch",
    GeochronologieFeldTyp.BIOSTRATIGRAPHISCH: "biostratigraphisch",
    GeochronologieFeldTyp.MAGNETOSTRATIGRAPHISCH: "magnetostratigraphisch",
}
_PROZEDUR_MAP = {
    GeochronologieFeldProzedur.DATIERUNG: "datierung",
    GeochronologieFeldProzedur.KALIBRIERUNG: "kalibrierung",
    GeochronologieFeldProzedur.KORRELATION: "korrelation",
    GeochronologieFeldProzedur.VALIDIERUNG: "validierung",
    GeochronologieFeldProzedur.INTERPRETATION: "interpretation",
}


@dataclass(frozen=True)
class GeochronologieFeldNorm:
    typ: GeochronologieFeldTyp
    prozedur: GeochronologieFeldProzedur
    geochronologie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class GeochronologieFeld:
    normen: tuple[GeochronologieFeldNorm, ...]
    canonical: bool = True

    def aggregates_feld_signal(self) -> dict:
        return {
            "feld_id": "geochronologie-feld-871",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_geochronologie_feld(parent: Optional[SedimentologieVerfassung] = None) -> GeochronologieFeld:
    if parent is None:
        parent = build_sedimentologie_verfassung()
    base = sum(n.sedimentologie_weight for n in parent.normen)
    normen = tuple(
        GeochronologieFeldNorm(
            typ=t,
            prozedur=list(GeochronologieFeldProzedur)[i],
            geochronologie_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(GeochronologieFeldTyp)
    )
    return GeochronologieFeld(normen=normen)
