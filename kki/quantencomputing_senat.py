"""
#937 QuantencomputingSenat — Quanten-Governance: IBM, Google, IonQ & Regulierung.
IBM Quantum (2016): IBM Q Experience — erste öffentlich zugängliche Quantencomputer;
  Cloud-Quantencomputing demokratisiert den Zugang zu Quantenhardware.
Google Quantum AI (2019): Quantum Supremacy — 53-Qubit Sycamore-Prozessor löst
  Benchmark in 200 Sekunden; klassischer Supercomputer bräuchte 10.000 Jahre.
NIST (2022): Post-Quantum Cryptography Standardization — CRYSTALS-Kyber und
  CRYSTALS-Dilithium als quantensichere Kryptographie-Standards; regulatorische Antwort.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .quantenkommunikation_pakt import QuantenkommunikationPakt, build_quantenkommunikation_pakt


class QuantencomputingSenatTyp(Enum):
    CLOUD_QUANTENCOMPUTING = auto()
    QUANTENÜBERLEGENHEIT = auto()
    POST_QUANTUM_STANDARD = auto()
    QUANTEN_REGULIERUNG = auto()
    QUANTEN_BILDUNG = auto()


class QuantencomputingSenatProzedur(Enum):
    STANDARDISIERUNG = auto()
    ZERTIFIZIERUNG = auto()
    REGULIERUNG = auto()
    FOERDERUNG = auto()
    INTERNATIONALE_KOOPERATION = auto()


_WEIGHT_DELTA = {
    QuantencomputingSenatTyp.CLOUD_QUANTENCOMPUTING: 0.0,
    QuantencomputingSenatTyp.QUANTENÜBERLEGENHEIT: 1.9,
    QuantencomputingSenatTyp.POST_QUANTUM_STANDARD: 3.8,
    QuantencomputingSenatTyp.QUANTEN_REGULIERUNG: 5.7,
    QuantencomputingSenatTyp.QUANTEN_BILDUNG: 7.6,
}
_TYP_MAP = {
    QuantencomputingSenatTyp.CLOUD_QUANTENCOMPUTING: "cloud_quantencomputing",
    QuantencomputingSenatTyp.QUANTENÜBERLEGENHEIT: "quantenueberlegenheit",
    QuantencomputingSenatTyp.POST_QUANTUM_STANDARD: "post_quantum_standard",
    QuantencomputingSenatTyp.QUANTEN_REGULIERUNG: "quanten_regulierung",
    QuantencomputingSenatTyp.QUANTEN_BILDUNG: "quanten_bildung",
}
_PROZEDUR_MAP = {
    QuantencomputingSenatProzedur.STANDARDISIERUNG: "standardisierung",
    QuantencomputingSenatProzedur.ZERTIFIZIERUNG: "zertifizierung",
    QuantencomputingSenatProzedur.REGULIERUNG: "regulierung",
    QuantencomputingSenatProzedur.FOERDERUNG: "foerderung",
    QuantencomputingSenatProzedur.INTERNATIONALE_KOOPERATION: "internationale_kooperation",
}


@dataclass(frozen=True)
class QuantencomputingSenatNorm:
    typ: QuantencomputingSenatTyp
    prozedur: QuantencomputingSenatProzedur
    quanten_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class QuantencomputingSenat:
    normen: tuple[QuantencomputingSenatNorm, ...]
    canonical: bool = True

    def aggregates_senat_signal(self) -> dict:
        return {
            "senat_id": "quantencomputing-senat-937",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_quantencomputing_senat(parent: Optional[QuantenkommunikationPakt] = None) -> QuantencomputingSenat:
    if parent is None:
        parent = build_quantenkommunikation_pakt()
    base = sum(e.quanten_weight for e in parent.eintraege)
    normen = tuple(
        QuantencomputingSenatNorm(
            typ=t,
            prozedur=list(QuantencomputingSenatProzedur)[i],
            quanten_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(QuantencomputingSenatTyp)
    )
    return QuantencomputingSenat(normen=normen)
