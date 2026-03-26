from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .sedimentologie_norm import SedimentologieNorm, build_sedimentologie_norm


class AlluvialChartaTyp(Enum):
    SCHWEMMFAECHER = auto()
    FLUSSAUE = auto()
    TERRASSEN = auto()
    MAEANDER = auto()
    GERINNE = auto()


class AlluvialChartaProzedur(Enum):
    ABLAGERUNG = auto()
    UEBERFLUTUNG = auto()
    EROSION = auto()
    TRANSPORT = auto()
    AKKUMULATION = auto()


_WEIGHT_DELTA = {
    AlluvialChartaTyp.SCHWEMMFAECHER: 0.0,
    AlluvialChartaTyp.FLUSSAUE: 2.0,
    AlluvialChartaTyp.TERRASSEN: 4.0,
    AlluvialChartaTyp.MAEANDER: 6.0,
    AlluvialChartaTyp.GERINNE: 8.0,
}
_TYP_MAP = {
    AlluvialChartaTyp.SCHWEMMFAECHER: "schwemmfaecher",
    AlluvialChartaTyp.FLUSSAUE: "flussaue",
    AlluvialChartaTyp.TERRASSEN: "terrassen",
    AlluvialChartaTyp.MAEANDER: "maeander",
    AlluvialChartaTyp.GERINNE: "gerinne",
}
_PROZEDUR_MAP = {
    AlluvialChartaProzedur.ABLAGERUNG: "ablagerung",
    AlluvialChartaProzedur.UEBERFLUTUNG: "ueberflutung",
    AlluvialChartaProzedur.EROSION: "erosion",
    AlluvialChartaProzedur.TRANSPORT: "transport",
    AlluvialChartaProzedur.AKKUMULATION: "akkumulation",
}


@dataclass(frozen=True)
class AlluvialChartaNorm:
    typ: AlluvialChartaTyp
    prozedur: AlluvialChartaProzedur
    sedimentologie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class AlluvialCharta:
    normen: tuple[AlluvialChartaNorm, ...]
    canonical: bool = True

    def aggregates_charta_signal(self) -> dict:
        return {
            "charta_id": "alluvial-charta-869",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_alluvial_charta(parent: Optional[SedimentologieNorm] = None) -> AlluvialCharta:
    if parent is None:
        parent = build_sedimentologie_norm()
    base = sum(e.sedimentologie_norm_weight for e in parent.normen)
    tier_base = max(e.sedimentologie_norm_tier for e in parent.normen)
    normen = tuple(
        AlluvialChartaNorm(
            typ=t,
            prozedur=list(AlluvialChartaProzedur)[i],
            sedimentologie_weight=base + _WEIGHT_DELTA[t],
            tier=tier_base + i + 1,
        )
        for i, t in enumerate(AlluvialChartaTyp)
    )
    return AlluvialCharta(normen=normen)
