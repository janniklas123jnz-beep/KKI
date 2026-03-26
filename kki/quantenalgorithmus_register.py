"""
#932 QuantenalgorithmusRegister — Quantenalgorithmen: Shor, Grover & VQE.
Shor (1994): Polynomial-Time Algorithms for Prime Factorization — Shor-Algorithmus
  bricht RSA in polynomialer Zeit; direkter Angriff auf klassische Kryptographie.
Grover (1996): A Fast Quantum Mechanical Algorithm for Database Search — quadratische
  Beschleunigung bei unstrukturierter Suche; fundamentaler Quantenvorteil.
Peruzzo et al. (2014): Variational Quantum Eigensolver — hybride Quanten-Klassik-
  Algorithmen für Quantenchemie; NISQ-Ära-Algorithmus für kurze Kohärenzzeiten.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .quantencomputing_feld import QuantencomputingFeld, build_quantencomputing_feld


class QuantenalgorithmusRegisterTyp(Enum):
    SHOR_ALGORITHMUS = auto()
    GROVER_SUCHE = auto()
    VQE_HYBRID = auto()
    QAOA_OPTIMIERUNG = auto()
    QFT_TRANSFORM = auto()


class QuantenalgorithmusRegisterProzedur(Enum):
    PROBLEMKODIERUNG = auto()
    QUANTENSCHALTKREIS = auto()
    AMPLITUDENVERSTAERKUNG = auto()
    MESSUNG = auto()
    KLASSISCHES_POSTPROCESSING = auto()


_WEIGHT_DELTA = {
    QuantenalgorithmusRegisterTyp.SHOR_ALGORITHMUS: 0.0,
    QuantenalgorithmusRegisterTyp.GROVER_SUCHE: 1.5,
    QuantenalgorithmusRegisterTyp.VQE_HYBRID: 3.0,
    QuantenalgorithmusRegisterTyp.QAOA_OPTIMIERUNG: 4.5,
    QuantenalgorithmusRegisterTyp.QFT_TRANSFORM: 6.0,
}
_TYP_MAP = {
    QuantenalgorithmusRegisterTyp.SHOR_ALGORITHMUS: "shor_algorithmus",
    QuantenalgorithmusRegisterTyp.GROVER_SUCHE: "grover_suche",
    QuantenalgorithmusRegisterTyp.VQE_HYBRID: "vqe_hybrid",
    QuantenalgorithmusRegisterTyp.QAOA_OPTIMIERUNG: "qaoa_optimierung",
    QuantenalgorithmusRegisterTyp.QFT_TRANSFORM: "qft_transform",
}
_PROZEDUR_MAP = {
    QuantenalgorithmusRegisterProzedur.PROBLEMKODIERUNG: "problemkodierung",
    QuantenalgorithmusRegisterProzedur.QUANTENSCHALTKREIS: "quantenschaltkreis",
    QuantenalgorithmusRegisterProzedur.AMPLITUDENVERSTAERKUNG: "amplitudenverstaerkung",
    QuantenalgorithmusRegisterProzedur.MESSUNG: "messung",
    QuantenalgorithmusRegisterProzedur.KLASSISCHES_POSTPROCESSING: "klassisches_postprocessing",
}


@dataclass(frozen=True)
class QuantenalgorithmusRegisterEintrag:
    typ: QuantenalgorithmusRegisterTyp
    prozedur: QuantenalgorithmusRegisterProzedur
    quanten_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class QuantenalgorithmusRegister:
    eintraege: tuple[QuantenalgorithmusRegisterEintrag, ...]
    canonical: bool = True

    def aggregates_register_signal(self) -> dict:
        return {
            "register_id": "quantenalgorithmus-register-932",
            "eintraege_count": len(self.eintraege),
            "canonical": self.canonical,
        }


def build_quantenalgorithmus_register(parent: Optional[QuantencomputingFeld] = None) -> QuantenalgorithmusRegister:
    if parent is None:
        parent = build_quantencomputing_feld()
    base = sum(n.quanten_weight for n in parent.normen)
    eintraege = tuple(
        QuantenalgorithmusRegisterEintrag(
            typ=t,
            prozedur=list(QuantenalgorithmusRegisterProzedur)[i],
            quanten_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(QuantenalgorithmusRegisterTyp)
    )
    return QuantenalgorithmusRegister(eintraege=eintraege)
