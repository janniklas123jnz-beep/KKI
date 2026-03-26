from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .sedimentit_pakt import SedimentitPakt, build_sedimentit_pakt


class PetrographieSenatTyp(Enum):
    GESTEINSKLASSIFIKATION = auto()
    MINERALBESTAND = auto()
    TEXTUR = auto()
    STRUKTUR = auto()
    GENESE = auto()


class PetrographieSenatProzedur(Enum):
    BERATUNG = auto()
    BEWERTUNG = auto()
    STANDARDISIERUNG = auto()
    FORSCHUNG = auto()
    KOORDINATION = auto()


_WEIGHT_DELTA = {
    PetrographieSenatTyp.GESTEINSKLASSIFIKATION: 0.0,
    PetrographieSenatTyp.MINERALBESTAND: 1.8,
    PetrographieSenatTyp.TEXTUR: 3.6,
    PetrographieSenatTyp.STRUKTUR: 5.4,
    PetrographieSenatTyp.GENESE: 7.2,
}
_TYP_MAP = {
    PetrographieSenatTyp.GESTEINSKLASSIFIKATION: "gesteinsklassifikation",
    PetrographieSenatTyp.MINERALBESTAND: "mineralbestand",
    PetrographieSenatTyp.TEXTUR: "textur",
    PetrographieSenatTyp.STRUKTUR: "struktur",
    PetrographieSenatTyp.GENESE: "genese",
}
_PROZEDUR_MAP = {
    PetrographieSenatProzedur.BERATUNG: "beratung",
    PetrographieSenatProzedur.BEWERTUNG: "bewertung",
    PetrographieSenatProzedur.STANDARDISIERUNG: "standardisierung",
    PetrographieSenatProzedur.FORSCHUNG: "forschung",
    PetrographieSenatProzedur.KOORDINATION: "koordination",
}


@dataclass(frozen=True)
class PetrographieSenatNorm:
    typ: PetrographieSenatTyp
    prozedur: PetrographieSenatProzedur
    petrographie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class PetrographieSenat:
    normen: tuple[PetrographieSenatNorm, ...]
    canonical: bool = True

    def aggregates_senat_signal(self) -> dict:
        return {
            "senat_id": "petrographie-senat-887",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_petrographie_senat(parent: Optional[SedimentitPakt] = None) -> PetrographieSenat:
    if parent is None:
        parent = build_sedimentit_pakt()
    base = sum(e.petrographie_weight for e in parent.eintraege)
    normen = tuple(
        PetrographieSenatNorm(
            typ=t,
            prozedur=list(PetrographieSenatProzedur)[i],
            petrographie_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(PetrographieSenatTyp)
    )
    return PetrographieSenat(normen=normen)
