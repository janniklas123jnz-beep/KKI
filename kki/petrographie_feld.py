from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .geochronologie_verfassung import GeochronologieVerfassung, build_geochronologie_verfassung


class PetrographieFeldTyp(Enum):
    MAGMATISCH = auto()
    SEDIMENTAER = auto()
    METAMORPH = auto()
    PLUTONISCH = auto()
    VULKANISCH = auto()


class PetrographieFeldProzedur(Enum):
    ANALYSE = auto()
    KLASSIFIKATION = auto()
    BESCHREIBUNG = auto()
    KARTIERUNG = auto()
    INTERPRETATION = auto()


_WEIGHT_DELTA = {
    PetrographieFeldTyp.MAGMATISCH: 0.0,
    PetrographieFeldTyp.SEDIMENTAER: 1.2,
    PetrographieFeldTyp.METAMORPH: 2.4,
    PetrographieFeldTyp.PLUTONISCH: 3.6,
    PetrographieFeldTyp.VULKANISCH: 5.0,
}
_TYP_MAP = {
    PetrographieFeldTyp.MAGMATISCH: "magmatisch",
    PetrographieFeldTyp.SEDIMENTAER: "sedimentaer",
    PetrographieFeldTyp.METAMORPH: "metamorph",
    PetrographieFeldTyp.PLUTONISCH: "plutonisch",
    PetrographieFeldTyp.VULKANISCH: "vulkanisch",
}
_PROZEDUR_MAP = {
    PetrographieFeldProzedur.ANALYSE: "analyse",
    PetrographieFeldProzedur.KLASSIFIKATION: "klassifikation",
    PetrographieFeldProzedur.BESCHREIBUNG: "beschreibung",
    PetrographieFeldProzedur.KARTIERUNG: "kartierung",
    PetrographieFeldProzedur.INTERPRETATION: "interpretation",
}


@dataclass(frozen=True)
class PetrographieFeldNorm:
    typ: PetrographieFeldTyp
    prozedur: PetrographieFeldProzedur
    petrographie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class PetrographieFeld:
    normen: tuple[PetrographieFeldNorm, ...]
    canonical: bool = True

    def aggregates_feld_signal(self) -> dict:
        return {
            "feld_id": "petrographie-feld-881",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_petrographie_feld(parent: Optional[GeochronologieVerfassung] = None) -> PetrographieFeld:
    if parent is None:
        parent = build_geochronologie_verfassung()
    base = sum(n.geochronologie_weight for n in parent.normen)
    normen = tuple(
        PetrographieFeldNorm(
            typ=t,
            prozedur=list(PetrographieFeldProzedur)[i],
            petrographie_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(PetrographieFeldTyp)
    )
    return PetrographieFeld(normen=normen)
