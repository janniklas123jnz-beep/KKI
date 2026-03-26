"""
#959 KreislaufwirtschaftCharta — Kreislaufwirtschaft: Ellen MacArthur, Cradle-to-Cradle & Doughnut.
Ellen MacArthur Foundation (2013): Towards the Circular Economy — Kreislaufwirtschaft
  als Alternative zur Linearwirtschaft; Reduce, Reuse, Recycle als Grundprinzip;
  biologischer und technischer Kreislauf.
Braungart & McDonough (2002): Cradle to Cradle — Abfall als Nährstoff; vollständige
  Materialkreisläufe ohne Downcycling; Design für Demontage und Wiederverwendung.
Raworth (2017): Doughnut Economics — planetare Grenzen und soziales Fundament;
  Doughnut-Modell als Kompass für nachhaltige Wirtschaft im 21. Jahrhundert.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .energie_norm import EnergieNorm, build_energie_norm


class KreislaufwirtschaftChartaTyp(Enum):
    BIOLOGISCHER_KREISLAUF = auto()
    TECHNISCHER_KREISLAUF = auto()
    CRADLE_TO_CRADLE = auto()
    URBAN_MINING = auto()
    INDUSTRIELLE_OEKOLOGIE = auto()


class KreislaufwirtschaftChartaProzedur(Enum):
    DESIGN_FOR_DISASSEMBLY = auto()
    MATERIALRUECKFUEHRUNG = auto()
    WIEDERVERWENDUNG = auto()
    UPCYCLING = auto()
    SCHLIESSEN_KREISLAEUFE = auto()


_WEIGHT_DELTA = {
    KreislaufwirtschaftChartaTyp.BIOLOGISCHER_KREISLAUF: 0.0,
    KreislaufwirtschaftChartaTyp.TECHNISCHER_KREISLAUF: 2.0,
    KreislaufwirtschaftChartaTyp.CRADLE_TO_CRADLE: 4.0,
    KreislaufwirtschaftChartaTyp.URBAN_MINING: 6.0,
    KreislaufwirtschaftChartaTyp.INDUSTRIELLE_OEKOLOGIE: 8.0,
}
_TYP_MAP = {
    KreislaufwirtschaftChartaTyp.BIOLOGISCHER_KREISLAUF: "biologischer_kreislauf",
    KreislaufwirtschaftChartaTyp.TECHNISCHER_KREISLAUF: "technischer_kreislauf",
    KreislaufwirtschaftChartaTyp.CRADLE_TO_CRADLE: "cradle_to_cradle",
    KreislaufwirtschaftChartaTyp.URBAN_MINING: "urban_mining",
    KreislaufwirtschaftChartaTyp.INDUSTRIELLE_OEKOLOGIE: "industrielle_oekologie",
}
_PROZEDUR_MAP = {
    KreislaufwirtschaftChartaProzedur.DESIGN_FOR_DISASSEMBLY: "design_for_disassembly",
    KreislaufwirtschaftChartaProzedur.MATERIALRUECKFUEHRUNG: "materialrueckfuehrung",
    KreislaufwirtschaftChartaProzedur.WIEDERVERWENDUNG: "wiederverwendung",
    KreislaufwirtschaftChartaProzedur.UPCYCLING: "upcycling",
    KreislaufwirtschaftChartaProzedur.SCHLIESSEN_KREISLAEUFE: "schliessen_kreislaeufe",
}


@dataclass(frozen=True)
class KreislaufwirtschaftChartaNorm:
    typ: KreislaufwirtschaftChartaTyp
    prozedur: KreislaufwirtschaftChartaProzedur
    energie_weight: float
    energie_tier: int
    canonical: bool = True


@dataclass(frozen=True)
class KreislaufwirtschaftCharta:
    normen: tuple[KreislaufwirtschaftChartaNorm, ...]
    canonical: bool = True

    def aggregates_charta_signal(self) -> dict:
        return {
            "charta_id": "kreislaufwirtschaft-charta-959",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_kreislaufwirtschaft_charta(parent: Optional[EnergieNorm] = None) -> KreislaufwirtschaftCharta:
    if parent is None:
        parent = build_energie_norm()
    base = sum(e.energie_norm_weight for e in parent.normen)
    normen = tuple(
        KreislaufwirtschaftChartaNorm(
            typ=t,
            prozedur=list(KreislaufwirtschaftChartaProzedur)[i],
            energie_weight=base + _WEIGHT_DELTA[t],
            energie_tier=i + 1,
        )
        for i, t in enumerate(KreislaufwirtschaftChartaTyp)
    )
    return KreislaufwirtschaftCharta(normen=normen)
