"""
#931 QuantencomputingFeld — Quantencomputing: Qubit, Superposition & Verschränkung.
Feynman (1982): Simulating Physics with Computers — Quantencomputer als einzige
  effiziente Methode zur Simulation quantenmechanischer Systeme; Gründungsmoment.
Deutsch (1985): Quantum Theory, the Church-Turing Principle — erster Quantenalgorithmus;
  Quantum Parallelism durch Superposition; Grundlage aller Quantenalgorithmen.
Nielsen & Chuang (2000): Quantum Computation and Quantum Information — Standardwerk;
  Qubit als Zwei-Zustand-Quantensystem; Verschränkung als nicht-klassische Ressource.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .cyber_verfassung import CyberVerfassung, build_cyber_verfassung


class QuantencomputingFeldTyp(Enum):
    QUBIT = auto()
    SUPERPOSITION = auto()
    VERSCHRAENKUNG = auto()
    QUANTENGATTER = auto()
    DEKOHÄRENZ = auto()


class QuantencomputingFeldProzedur(Enum):
    INITIALISIERUNG = auto()
    MANIPULATION = auto()
    MESSUNG = auto()
    FEHLERKORREKTUR = auto()
    READOUT = auto()


_WEIGHT_DELTA = {
    QuantencomputingFeldTyp.QUBIT: 0.0,
    QuantencomputingFeldTyp.SUPERPOSITION: 1.4,
    QuantencomputingFeldTyp.VERSCHRAENKUNG: 2.8,
    QuantencomputingFeldTyp.QUANTENGATTER: 4.2,
    QuantencomputingFeldTyp.DEKOHÄRENZ: 5.6,
}
_TYP_MAP = {
    QuantencomputingFeldTyp.QUBIT: "qubit",
    QuantencomputingFeldTyp.SUPERPOSITION: "superposition",
    QuantencomputingFeldTyp.VERSCHRAENKUNG: "verschraenkung",
    QuantencomputingFeldTyp.QUANTENGATTER: "quantengatter",
    QuantencomputingFeldTyp.DEKOHÄRENZ: "dekohärenz",
}
_PROZEDUR_MAP = {
    QuantencomputingFeldProzedur.INITIALISIERUNG: "initialisierung",
    QuantencomputingFeldProzedur.MANIPULATION: "manipulation",
    QuantencomputingFeldProzedur.MESSUNG: "messung",
    QuantencomputingFeldProzedur.FEHLERKORREKTUR: "fehlerkorrektur",
    QuantencomputingFeldProzedur.READOUT: "readout",
}


@dataclass(frozen=True)
class QuantencomputingFeldNorm:
    typ: QuantencomputingFeldTyp
    prozedur: QuantencomputingFeldProzedur
    quanten_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class QuantencomputingFeld:
    normen: tuple[QuantencomputingFeldNorm, ...]
    canonical: bool = True

    def aggregates_feld_signal(self) -> dict:
        return {
            "feld_id": "quantencomputing-feld-931",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_quantencomputing_feld(parent: Optional[CyberVerfassung] = None) -> QuantencomputingFeld:
    if parent is None:
        parent = build_cyber_verfassung()
    base = sum(n.cyber_weight for n in parent.normen)
    normen = tuple(
        QuantencomputingFeldNorm(
            typ=t,
            prozedur=list(QuantencomputingFeldProzedur)[i],
            quanten_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(QuantencomputingFeldTyp)
    )
    return QuantencomputingFeld(normen=normen)
