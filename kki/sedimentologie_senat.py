from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .delta_pakt import DeltaPakt, build_delta_pakt


class SedimentologieSenatTyp(Enum):
    GESTEINSANALYSE = auto()
    KORNGROESSEN = auto()
    MINERALBESTAND = auto()
    SCHICHTFOLGE = auto()
    GEFUEGE = auto()


class SedimentologieSenatProzedur(Enum):
    BERATUNG = auto()
    BEWERTUNG = auto()
    KOORDINATION = auto()
    FORSCHUNG = auto()
    DOKUMENTATION = auto()


_WEIGHT_DELTA = {
    SedimentologieSenatTyp.GESTEINSANALYSE: 0.0,
    SedimentologieSenatTyp.KORNGROESSEN: 1.8,
    SedimentologieSenatTyp.MINERALBESTAND: 3.6,
    SedimentologieSenatTyp.SCHICHTFOLGE: 5.4,
    SedimentologieSenatTyp.GEFUEGE: 7.2,
}
_TYP_MAP = {
    SedimentologieSenatTyp.GESTEINSANALYSE: "gesteinsanalyse",
    SedimentologieSenatTyp.KORNGROESSEN: "korngroessen",
    SedimentologieSenatTyp.MINERALBESTAND: "mineralbestand",
    SedimentologieSenatTyp.SCHICHTFOLGE: "schichtfolge",
    SedimentologieSenatTyp.GEFUEGE: "gefuege",
}
_PROZEDUR_MAP = {
    SedimentologieSenatProzedur.BERATUNG: "beratung",
    SedimentologieSenatProzedur.BEWERTUNG: "bewertung",
    SedimentologieSenatProzedur.KOORDINATION: "koordination",
    SedimentologieSenatProzedur.FORSCHUNG: "forschung",
    SedimentologieSenatProzedur.DOKUMENTATION: "dokumentation",
}


@dataclass(frozen=True)
class SedimentologieSenatNorm:
    typ: SedimentologieSenatTyp
    prozedur: SedimentologieSenatProzedur
    sedimentologie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class SedimentologieSenat:
    normen: tuple[SedimentologieSenatNorm, ...]
    canonical: bool = True

    def aggregates_senat_signal(self) -> dict:
        return {
            "senat_id": "sedimentologie-senat-867",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_sedimentologie_senat(parent: Optional[DeltaPakt] = None) -> SedimentologieSenat:
    if parent is None:
        parent = build_delta_pakt()
    base = sum(e.sedimentologie_weight for e in parent.eintraege)
    normen = tuple(
        SedimentologieSenatNorm(
            typ=t,
            prozedur=list(SedimentologieSenatProzedur)[i],
            sedimentologie_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(SedimentologieSenatTyp)
    )
    return SedimentologieSenat(normen=normen)
