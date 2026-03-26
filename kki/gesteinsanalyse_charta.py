from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .petrographie_norm import PetrographieNorm, build_petrographie_norm


class GesteinsanalyseChartaTyp(Enum):
    DUENNSCHLIFF = auto()
    ROENTGENDIFFRAKTION = auto()
    RASTERELEKTRONIK = auto()
    ELEKTRONENSTRAHL = auto()
    MASSENSPEKTROMETRIE = auto()


class GesteinsanalyseChartaProzedur(Enum):
    PROBENAHME = auto()
    VORBEREITUNG = auto()
    MESSUNG = auto()
    AUSWERTUNG = auto()
    INTERPRETATION = auto()


_WEIGHT_DELTA = {
    GesteinsanalyseChartaTyp.DUENNSCHLIFF: 0.0,
    GesteinsanalyseChartaTyp.ROENTGENDIFFRAKTION: 2.0,
    GesteinsanalyseChartaTyp.RASTERELEKTRONIK: 4.0,
    GesteinsanalyseChartaTyp.ELEKTRONENSTRAHL: 6.0,
    GesteinsanalyseChartaTyp.MASSENSPEKTROMETRIE: 8.0,
}
_TYP_MAP = {
    GesteinsanalyseChartaTyp.DUENNSCHLIFF: "duennschliff",
    GesteinsanalyseChartaTyp.ROENTGENDIFFRAKTION: "roentgendiffraktion",
    GesteinsanalyseChartaTyp.RASTERELEKTRONIK: "rasterelektronik",
    GesteinsanalyseChartaTyp.ELEKTRONENSTRAHL: "elektronenstrahl",
    GesteinsanalyseChartaTyp.MASSENSPEKTROMETRIE: "massenspektrometrie",
}
_PROZEDUR_MAP = {
    GesteinsanalyseChartaProzedur.PROBENAHME: "probenahme",
    GesteinsanalyseChartaProzedur.VORBEREITUNG: "vorbereitung",
    GesteinsanalyseChartaProzedur.MESSUNG: "messung",
    GesteinsanalyseChartaProzedur.AUSWERTUNG: "auswertung",
    GesteinsanalyseChartaProzedur.INTERPRETATION: "interpretation",
}


@dataclass(frozen=True)
class GesteinsanalyseChartaNorm:
    typ: GesteinsanalyseChartaTyp
    prozedur: GesteinsanalyseChartaProzedur
    petrographie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class GesteinsanalyseCharta:
    normen: tuple[GesteinsanalyseChartaNorm, ...]
    canonical: bool = True

    def aggregates_charta_signal(self) -> dict:
        return {
            "charta_id": "gesteinsanalyse-charta-889",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_gesteinsanalyse_charta(parent: Optional[PetrographieNorm] = None) -> GesteinsanalyseCharta:
    if parent is None:
        parent = build_petrographie_norm()
    base = sum(e.petrographie_norm_weight for e in parent.normen)
    tier_base = max(e.petrographie_norm_tier for e in parent.normen)
    normen = tuple(
        GesteinsanalyseChartaNorm(
            typ=t,
            prozedur=list(GesteinsanalyseChartaProzedur)[i],
            petrographie_weight=base + _WEIGHT_DELTA[t],
            tier=tier_base + i + 1,
        )
        for i, t in enumerate(GesteinsanalyseChartaTyp)
    )
    return GesteinsanalyseCharta(normen=normen)
