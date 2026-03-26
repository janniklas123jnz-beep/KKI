"""
#907 MaschinenlernenSenat — ML-Governance: Ensemble, Federated & AutoML.
Breiman (2001): Random Forests — Ensemble-Methoden als robuste ML-Lösung.
Freund & Schapire (1997): AdaBoost — Boosting kombiniert schwache Lerner zu starken.
McMahan et al. (2017): Federated Learning — datenschutzfreundliches verteiltes Lernen.
Zoph & Le (2017): Neural Architecture Search — AutoML findet optimale Netzarchitekturen.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .computer_vision_pakt import ComputerVisionPakt, build_computer_vision_pakt


class MaschinenlernenSenatTyp(Enum):
    ENSEMBLE = auto()
    FEDERATED = auto()
    AUTO_ML = auto()
    TRANSFER = auto()
    META_LERNEN = auto()


class MaschinenlernenSenatProzedur(Enum):
    KOORDINATION = auto()
    STANDARDISIERUNG = auto()
    FORSCHUNG = auto()
    GOVERNANCE = auto()
    EVALUATION = auto()


_WEIGHT_DELTA = {
    MaschinenlernenSenatTyp.ENSEMBLE: 0.0,
    MaschinenlernenSenatTyp.FEDERATED: 1.9,
    MaschinenlernenSenatTyp.AUTO_ML: 3.8,
    MaschinenlernenSenatTyp.TRANSFER: 5.7,
    MaschinenlernenSenatTyp.META_LERNEN: 7.6,
}
_TYP_MAP = {
    MaschinenlernenSenatTyp.ENSEMBLE: "ensemble",
    MaschinenlernenSenatTyp.FEDERATED: "federated",
    MaschinenlernenSenatTyp.AUTO_ML: "auto_ml",
    MaschinenlernenSenatTyp.TRANSFER: "transfer",
    MaschinenlernenSenatTyp.META_LERNEN: "meta_lernen",
}
_PROZEDUR_MAP = {
    MaschinenlernenSenatProzedur.KOORDINATION: "koordination",
    MaschinenlernenSenatProzedur.STANDARDISIERUNG: "standardisierung",
    MaschinenlernenSenatProzedur.FORSCHUNG: "forschung",
    MaschinenlernenSenatProzedur.GOVERNANCE: "governance",
    MaschinenlernenSenatProzedur.EVALUATION: "evaluation",
}


@dataclass(frozen=True)
class MaschinenlernenSenatNorm:
    typ: MaschinenlernenSenatTyp
    prozedur: MaschinenlernenSenatProzedur
    maschinenlernen_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class MaschinenlernenSenat:
    normen: tuple[MaschinenlernenSenatNorm, ...]
    canonical: bool = True

    def aggregates_senat_signal(self) -> dict:
        return {
            "senat_id": "maschinenlernen-senat-907",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_maschinenlernen_senat(parent: Optional[ComputerVisionPakt] = None) -> MaschinenlernenSenat:
    if parent is None:
        parent = build_computer_vision_pakt()
    base = sum(e.maschinenlernen_weight for e in parent.eintraege)
    normen = tuple(
        MaschinenlernenSenatNorm(
            typ=t,
            prozedur=list(MaschinenlernenSenatProzedur)[i],
            maschinenlernen_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(MaschinenlernenSenatTyp)
    )
    return MaschinenlernenSenat(normen=normen)
