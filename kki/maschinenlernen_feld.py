"""
#901 MaschinenlernenFeld — Maschinelles Lernen: Grundlagen & Paradigmen.
Alan Turing (1950): Computing Machinery and Intelligence — Turing-Test als Operationalisierung von Intelligenz.
Arthur Samuel (1959): ML als "Fähigkeit zu lernen ohne explizit programmiert zu sein" — Grunddefinition.
Tom Mitchell (1997): Formale ML-Definition: Erfahrung E, Aufgabe T, Leistungsmaß P.
Leitsterns ML-Fundament: Supervised, Unsupervised und Reinforcement Learning als drei Säulen.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .glaziologie_verfassung import GlaziologieVerfassung, build_glaziologie_verfassung


class MaschinenlernenFeldTyp(Enum):
    SUPERVISED = auto()
    UNSUPERVISED = auto()
    REINFORCEMENT = auto()
    SEMI_SUPERVISED = auto()
    SELF_SUPERVISED = auto()


class MaschinenlernenFeldProzedur(Enum):
    TRAINING = auto()
    VALIDIERUNG = auto()
    TESTEN = auto()
    DEPLOYMENT = auto()
    MONITORING = auto()


_WEIGHT_DELTA = {
    MaschinenlernenFeldTyp.SUPERVISED: 0.0,
    MaschinenlernenFeldTyp.UNSUPERVISED: 1.3,
    MaschinenlernenFeldTyp.REINFORCEMENT: 2.6,
    MaschinenlernenFeldTyp.SEMI_SUPERVISED: 3.9,
    MaschinenlernenFeldTyp.SELF_SUPERVISED: 5.2,
}
_TYP_MAP = {
    MaschinenlernenFeldTyp.SUPERVISED: "supervised",
    MaschinenlernenFeldTyp.UNSUPERVISED: "unsupervised",
    MaschinenlernenFeldTyp.REINFORCEMENT: "reinforcement",
    MaschinenlernenFeldTyp.SEMI_SUPERVISED: "semi_supervised",
    MaschinenlernenFeldTyp.SELF_SUPERVISED: "self_supervised",
}
_PROZEDUR_MAP = {
    MaschinenlernenFeldProzedur.TRAINING: "training",
    MaschinenlernenFeldProzedur.VALIDIERUNG: "validierung",
    MaschinenlernenFeldProzedur.TESTEN: "testen",
    MaschinenlernenFeldProzedur.DEPLOYMENT: "deployment",
    MaschinenlernenFeldProzedur.MONITORING: "monitoring",
}


@dataclass(frozen=True)
class MaschinenlernenFeldNorm:
    typ: MaschinenlernenFeldTyp
    prozedur: MaschinenlernenFeldProzedur
    maschinenlernen_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class MaschinenlernenFeld:
    normen: tuple[MaschinenlernenFeldNorm, ...]
    canonical: bool = True

    def aggregates_feld_signal(self) -> dict:
        return {
            "feld_id": "maschinenlernen-feld-901",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_maschinenlernen_feld(parent: Optional[GlaziologieVerfassung] = None) -> MaschinenlernenFeld:
    if parent is None:
        parent = build_glaziologie_verfassung()
    base = sum(n.glaziologie_weight for n in parent.normen)
    normen = tuple(
        MaschinenlernenFeldNorm(
            typ=t,
            prozedur=list(MaschinenlernenFeldProzedur)[i],
            maschinenlernen_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(MaschinenlernenFeldTyp)
    )
    return MaschinenlernenFeld(normen=normen)
