"""
#934 QuantenfehlerKodex — Quantenfehlerkorrektur: QEC, Surface Codes & Stabilisatoren.
Shor (1995): Scheme for Reducing Decoherence in Quantum Computer Memory — erster
  Quantenfehlerkorrekturcode; 9-Qubit-Code schützt ein logisches Qubit vor beliebigen
  Einzelqubit-Fehlern; Grundlage fehlertoleranten Quantencomputings.
Kitaev (2003): Fault-Tolerant Quantum Computation by Anyons — topologische Codes;
  Surface Code als vielversprechendster Weg zu fehlertoleranten Quantencomputern.
Gottesman (1997): Stabilizer Codes — algebraische Struktur der Quantenfehlerkorrektur;
  Pauli-Gruppe als Stabilisatoren; Clifford-Gruppe als transversale Gates.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .quantenhardware_charta import QuantenhardwareCharta, build_quantenhardware_charta


class QuantenfehlerKodexTyp(Enum):
    SURFACE_CODE = auto()
    STEANECODE = auto()
    REPETITIONSCODE = auto()
    TOPOLOGISCHER_CODE = auto()
    LDPC_CODE = auto()


class QuantenfehlerKodexProzedur(Enum):
    SYNDROME_MESSUNG = auto()
    FEHLERDIAGNOSE = auto()
    FEHLERKORREKTUR = auto()
    LOGISCHES_GATING = auto()
    THRESHOLD_ANALYSE = auto()


_WEIGHT_DELTA = {
    QuantenfehlerKodexTyp.SURFACE_CODE: 0.0,
    QuantenfehlerKodexTyp.STEANECODE: 1.8,
    QuantenfehlerKodexTyp.REPETITIONSCODE: 3.6,
    QuantenfehlerKodexTyp.TOPOLOGISCHER_CODE: 5.4,
    QuantenfehlerKodexTyp.LDPC_CODE: 7.2,
}
_TYP_MAP = {
    QuantenfehlerKodexTyp.SURFACE_CODE: "surface_code",
    QuantenfehlerKodexTyp.STEANECODE: "steanecode",
    QuantenfehlerKodexTyp.REPETITIONSCODE: "repetitionscode",
    QuantenfehlerKodexTyp.TOPOLOGISCHER_CODE: "topologischer_code",
    QuantenfehlerKodexTyp.LDPC_CODE: "ldpc_code",
}
_PROZEDUR_MAP = {
    QuantenfehlerKodexProzedur.SYNDROME_MESSUNG: "syndrome_messung",
    QuantenfehlerKodexProzedur.FEHLERDIAGNOSE: "fehlerdiagnose",
    QuantenfehlerKodexProzedur.FEHLERKORREKTUR: "fehlerkorrektur",
    QuantenfehlerKodexProzedur.LOGISCHES_GATING: "logisches_gating",
    QuantenfehlerKodexProzedur.THRESHOLD_ANALYSE: "threshold_analyse",
}


@dataclass(frozen=True)
class QuantenfehlerKodexEintrag:
    typ: QuantenfehlerKodexTyp
    prozedur: QuantenfehlerKodexProzedur
    quanten_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class QuantenfehlerKodex:
    eintraege: tuple[QuantenfehlerKodexEintrag, ...]
    canonical: bool = True

    def aggregates_kodex_signal(self) -> dict:
        return {
            "kodex_id": "quantenfehler-kodex-934",
            "eintraege_count": len(self.eintraege),
            "canonical": self.canonical,
        }


def build_quantenfehler_kodex(parent: Optional[QuantenhardwareCharta] = None) -> QuantenfehlerKodex:
    if parent is None:
        parent = build_quantenhardware_charta()
    base = sum(n.quanten_weight for n in parent.normen)
    eintraege = tuple(
        QuantenfehlerKodexEintrag(
            typ=t,
            prozedur=list(QuantenfehlerKodexProzedur)[i],
            quanten_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(QuantenfehlerKodexTyp)
    )
    return QuantenfehlerKodex(eintraege=eintraege)
