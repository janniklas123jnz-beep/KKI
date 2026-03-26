from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .geomorphologie_verfassung import GeomorphologieVerfassung, build_geomorphologie_verfassung


class SedimentologieFeldTyp(Enum):
    KLASTISCH = auto()
    CHEMISCH = auto()
    BIOGEN = auto()
    EVAPORITISCH = auto()
    VULKANOGEN = auto()


class SedimentologieFeldProzedur(Enum):
    SEDIMENTATION = auto()
    TRANSPORT = auto()
    EROSION = auto()
    DIAGENESE = auto()
    LITHIFIKATION = auto()


_WEIGHT_DELTA = {
    SedimentologieFeldTyp.KLASTISCH: 0.0,
    SedimentologieFeldTyp.CHEMISCH: 1.2,
    SedimentologieFeldTyp.BIOGEN: 2.4,
    SedimentologieFeldTyp.EVAPORITISCH: 3.6,
    SedimentologieFeldTyp.VULKANOGEN: 5.0,
}
_TYP_MAP = {
    SedimentologieFeldTyp.KLASTISCH: "klastisch",
    SedimentologieFeldTyp.CHEMISCH: "chemisch",
    SedimentologieFeldTyp.BIOGEN: "biogen",
    SedimentologieFeldTyp.EVAPORITISCH: "evaporitisch",
    SedimentologieFeldTyp.VULKANOGEN: "vulkanogen",
}
_PROZEDUR_MAP = {
    SedimentologieFeldProzedur.SEDIMENTATION: "sedimentation",
    SedimentologieFeldProzedur.TRANSPORT: "transport",
    SedimentologieFeldProzedur.EROSION: "erosion",
    SedimentologieFeldProzedur.DIAGENESE: "diagenese",
    SedimentologieFeldProzedur.LITHIFIKATION: "lithifikation",
}


@dataclass(frozen=True)
class SedimentologieFeldNorm:
    typ: SedimentologieFeldTyp
    prozedur: SedimentologieFeldProzedur
    sedimentologie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class SedimentologieFeld:
    normen: tuple[SedimentologieFeldNorm, ...]
    canonical: bool = True

    def aggregates_feld_signal(self) -> dict:
        return {
            "feld_id": "sedimentologie-feld-861",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_sedimentologie_feld(parent: Optional[GeomorphologieVerfassung] = None) -> SedimentologieFeld:
    if parent is None:
        parent = build_geomorphologie_verfassung()
    base = sum(n.geomorphologie_weight for n in parent.normen)
    normen = tuple(
        SedimentologieFeldNorm(
            typ=t,
            prozedur=list(SedimentologieFeldProzedur)[i],
            sedimentologie_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(SedimentologieFeldTyp)
    )
    return SedimentologieFeld(normen=normen)
