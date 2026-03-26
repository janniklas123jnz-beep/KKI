from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .ablagerungs_register import AblagerungsRegister, build_ablagerungs_register


class FaziesChartaTyp(Enum):
    DELTAISCH = auto()
    RIFFKALK = auto()
    TIEFSEETON = auto()
    SANDSTEIN = auto()
    KONGLOMERAT = auto()


class FaziesChartaProzedur(Enum):
    ANALYSE = auto()
    INTERPRETATION = auto()
    KORRELATION = auto()
    KARTIERUNG = auto()
    MODELLIERUNG = auto()


_WEIGHT_DELTA = {
    FaziesChartaTyp.DELTAISCH: 0.0,
    FaziesChartaTyp.RIFFKALK: 1.4,
    FaziesChartaTyp.TIEFSEETON: 2.8,
    FaziesChartaTyp.SANDSTEIN: 4.2,
    FaziesChartaTyp.KONGLOMERAT: 5.6,
}
_TYP_MAP = {
    FaziesChartaTyp.DELTAISCH: "deltaisch",
    FaziesChartaTyp.RIFFKALK: "riffkalk",
    FaziesChartaTyp.TIEFSEETON: "tiefseeton",
    FaziesChartaTyp.SANDSTEIN: "sandstein",
    FaziesChartaTyp.KONGLOMERAT: "konglomerat",
}
_PROZEDUR_MAP = {
    FaziesChartaProzedur.ANALYSE: "analyse",
    FaziesChartaProzedur.INTERPRETATION: "interpretation",
    FaziesChartaProzedur.KORRELATION: "korrelation",
    FaziesChartaProzedur.KARTIERUNG: "kartierung",
    FaziesChartaProzedur.MODELLIERUNG: "modellierung",
}


@dataclass(frozen=True)
class FaziesChartaNorm:
    typ: FaziesChartaTyp
    prozedur: FaziesChartaProzedur
    sedimentologie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class FaziesCharta:
    normen: tuple[FaziesChartaNorm, ...]
    canonical: bool = True

    def aggregates_charta_signal(self) -> dict:
        return {
            "charta_id": "fazies-charta-863",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_fazies_charta(parent: Optional[AblagerungsRegister] = None) -> FaziesCharta:
    if parent is None:
        parent = build_ablagerungs_register()
    base = sum(e.sedimentologie_weight for e in parent.eintraege)
    normen = tuple(
        FaziesChartaNorm(
            typ=t,
            prozedur=list(FaziesChartaProzedur)[i],
            sedimentologie_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(FaziesChartaTyp)
    )
    return FaziesCharta(normen=normen)
