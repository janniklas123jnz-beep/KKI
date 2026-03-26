from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .gletscher_register import GletscherRegister, build_gletscher_register


class EisdeckenChartaTyp(Enum):
    ANTARKTIS = auto()
    GROENLAND = auto()
    ARKTIS = auto()
    KONTINENTAL = auto()
    SUBARKTISCH = auto()


class EisdeckenChartaProzedur(Enum):
    MASSENHAUSHALT = auto()
    DYNAMIK = auto()
    SCHMELZE = auto()
    AKKUMULATION = auto()
    MODELLIERUNG = auto()


_WEIGHT_DELTA = {
    EisdeckenChartaTyp.ANTARKTIS: 0.0,
    EisdeckenChartaTyp.GROENLAND: 1.4,
    EisdeckenChartaTyp.ARKTIS: 2.8,
    EisdeckenChartaTyp.KONTINENTAL: 4.2,
    EisdeckenChartaTyp.SUBARKTISCH: 5.6,
}
_TYP_MAP = {
    EisdeckenChartaTyp.ANTARKTIS: "antarktis",
    EisdeckenChartaTyp.GROENLAND: "groenland",
    EisdeckenChartaTyp.ARKTIS: "arktis",
    EisdeckenChartaTyp.KONTINENTAL: "kontinental",
    EisdeckenChartaTyp.SUBARKTISCH: "subarktisch",
}
_PROZEDUR_MAP = {
    EisdeckenChartaProzedur.MASSENHAUSHALT: "massenhaushalt",
    EisdeckenChartaProzedur.DYNAMIK: "dynamik",
    EisdeckenChartaProzedur.SCHMELZE: "schmelze",
    EisdeckenChartaProzedur.AKKUMULATION: "akkumulation",
    EisdeckenChartaProzedur.MODELLIERUNG: "modellierung",
}


@dataclass(frozen=True)
class EisdeckenChartaNorm:
    typ: EisdeckenChartaTyp
    prozedur: EisdeckenChartaProzedur
    glaziologie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class EisdeckenCharta:
    normen: tuple[EisdeckenChartaNorm, ...]
    canonical: bool = True

    def aggregates_charta_signal(self) -> dict:
        return {
            "charta_id": "eisdecken-charta-893",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_eisdecken_charta(parent: Optional[GletscherRegister] = None) -> EisdeckenCharta:
    if parent is None:
        parent = build_gletscher_register()
    base = sum(e.glaziologie_weight for e in parent.eintraege)
    normen = tuple(
        EisdeckenChartaNorm(
            typ=t,
            prozedur=list(EisdeckenChartaProzedur)[i],
            glaziologie_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(EisdeckenChartaTyp)
    )
    return EisdeckenCharta(normen=normen)
