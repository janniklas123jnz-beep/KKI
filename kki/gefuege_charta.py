from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .mineral_register import MineralRegister, build_mineral_register


class GefuegeChartaTyp(Enum):
    KRISTALLIN = auto()
    KLASTISCH = auto()
    AMORPH = auto()
    FOLIIERT = auto()
    GRANOBLASTISCH = auto()


class GefuegeChartaProzedur(Enum):
    ANALYSE = auto()
    BESCHREIBUNG = auto()
    KLASSIFIKATION = auto()
    INTERPRETATION = auto()
    DOKUMENTATION = auto()


_WEIGHT_DELTA = {
    GefuegeChartaTyp.KRISTALLIN: 0.0,
    GefuegeChartaTyp.KLASTISCH: 1.4,
    GefuegeChartaTyp.AMORPH: 2.8,
    GefuegeChartaTyp.FOLIIERT: 4.2,
    GefuegeChartaTyp.GRANOBLASTISCH: 5.6,
}
_TYP_MAP = {
    GefuegeChartaTyp.KRISTALLIN: "kristallin",
    GefuegeChartaTyp.KLASTISCH: "klastisch",
    GefuegeChartaTyp.AMORPH: "amorph",
    GefuegeChartaTyp.FOLIIERT: "foliiert",
    GefuegeChartaTyp.GRANOBLASTISCH: "granoblastisch",
}
_PROZEDUR_MAP = {
    GefuegeChartaProzedur.ANALYSE: "analyse",
    GefuegeChartaProzedur.BESCHREIBUNG: "beschreibung",
    GefuegeChartaProzedur.KLASSIFIKATION: "klassifikation",
    GefuegeChartaProzedur.INTERPRETATION: "interpretation",
    GefuegeChartaProzedur.DOKUMENTATION: "dokumentation",
}


@dataclass(frozen=True)
class GefuegeChartaNorm:
    typ: GefuegeChartaTyp
    prozedur: GefuegeChartaProzedur
    petrographie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class GefuegeCharta:
    normen: tuple[GefuegeChartaNorm, ...]
    canonical: bool = True

    def aggregates_charta_signal(self) -> dict:
        return {
            "charta_id": "gefuege-charta-883",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_gefuege_charta(parent: Optional[MineralRegister] = None) -> GefuegeCharta:
    if parent is None:
        parent = build_mineral_register()
    base = sum(e.petrographie_weight for e in parent.eintraege)
    normen = tuple(
        GefuegeChartaNorm(
            typ=t,
            prozedur=list(GefuegeChartaProzedur)[i],
            petrographie_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(GefuegeChartaTyp)
    )
    return GefuegeCharta(normen=normen)
