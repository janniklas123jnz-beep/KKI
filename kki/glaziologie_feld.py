from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .petrographie_verfassung import PetrographieVerfassung, build_petrographie_verfassung


class GlaziologieFeldTyp(Enum):
    GEBIRGSGLETSCHER = auto()
    EISDECKE = auto()
    EISSCHILD = auto()
    TALGLETSCHER = auto()
    PIEDMONTGLETSCHER = auto()


class GlaziologieFeldProzedur(Enum):
    KARTIERUNG = auto()
    MESSUNG = auto()
    MODELLIERUNG = auto()
    MONITORING = auto()
    ANALYSE = auto()


_WEIGHT_DELTA = {
    GlaziologieFeldTyp.GEBIRGSGLETSCHER: 0.0,
    GlaziologieFeldTyp.EISDECKE: 1.2,
    GlaziologieFeldTyp.EISSCHILD: 2.4,
    GlaziologieFeldTyp.TALGLETSCHER: 3.6,
    GlaziologieFeldTyp.PIEDMONTGLETSCHER: 5.0,
}
_TYP_MAP = {
    GlaziologieFeldTyp.GEBIRGSGLETSCHER: "gebirgsgletscher",
    GlaziologieFeldTyp.EISDECKE: "eisdecke",
    GlaziologieFeldTyp.EISSCHILD: "eisschild",
    GlaziologieFeldTyp.TALGLETSCHER: "talgletscher",
    GlaziologieFeldTyp.PIEDMONTGLETSCHER: "piedmontgletscher",
}
_PROZEDUR_MAP = {
    GlaziologieFeldProzedur.KARTIERUNG: "kartierung",
    GlaziologieFeldProzedur.MESSUNG: "messung",
    GlaziologieFeldProzedur.MODELLIERUNG: "modellierung",
    GlaziologieFeldProzedur.MONITORING: "monitoring",
    GlaziologieFeldProzedur.ANALYSE: "analyse",
}


@dataclass(frozen=True)
class GlaziologieFeldNorm:
    typ: GlaziologieFeldTyp
    prozedur: GlaziologieFeldProzedur
    glaziologie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class GlaziologieFeld:
    normen: tuple[GlaziologieFeldNorm, ...]
    canonical: bool = True

    def aggregates_feld_signal(self) -> dict:
        return {
            "feld_id": "glaziologie-feld-891",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_glaziologie_feld(parent: Optional[PetrographieVerfassung] = None) -> GlaziologieFeld:
    if parent is None:
        parent = build_petrographie_verfassung()
    base = sum(n.petrographie_weight for n in parent.normen)
    normen = tuple(
        GlaziologieFeldNorm(
            typ=t,
            prozedur=list(GlaziologieFeldProzedur)[i],
            glaziologie_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(GlaziologieFeldTyp)
    )
    return GlaziologieFeld(normen=normen)
