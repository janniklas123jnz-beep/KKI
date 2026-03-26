"""
#933 QuantenhardwareCharta — Quantenhardware: Transmon, Ionenfalle & Photonik.
Koch et al. (2007): Charge-insensitive Qubit Design — Transmon-Qubit als robustes
  supraleitendes Qubit; Grundlage von IBM Quantum und Google Sycamore.
Cirac & Zoller (1995): Quantum Computations with Cold Trapped Ions — Ionenfallen-
  Quantencomputer; höchste Gate-Fidelity durch elektromagnetische Speicherung.
Kok et al. (2007): Linear Optical Quantum Computing — photonische Quantencomputer;
  raumtemperaturstabile Qubits durch Lichtteilchen; Basis von PsiQuantum.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .quantenalgorithmus_register import QuantenalgorithmusRegister, build_quantenalgorithmus_register


class QuantenhardwareChartaTyp(Enum):
    SUPRALEITEND = auto()
    IONENFALLE = auto()
    PHOTONIK = auto()
    TOPOLOGISCH = auto()
    SPIN_QUBIT = auto()


class QuantenhardwareChartaProzedur(Enum):
    KUEHLUNGSTECHNIK = auto()
    GATE_KALIBRIERUNG = auto()
    QUBIT_KOPPLUNG = auto()
    FIDELITY_MESSUNG = auto()
    SKALIERUNG = auto()


_WEIGHT_DELTA = {
    QuantenhardwareChartaTyp.SUPRALEITEND: 0.0,
    QuantenhardwareChartaTyp.IONENFALLE: 1.7,
    QuantenhardwareChartaTyp.PHOTONIK: 3.4,
    QuantenhardwareChartaTyp.TOPOLOGISCH: 5.1,
    QuantenhardwareChartaTyp.SPIN_QUBIT: 6.8,
}
_TYP_MAP = {
    QuantenhardwareChartaTyp.SUPRALEITEND: "supraleitend",
    QuantenhardwareChartaTyp.IONENFALLE: "ionenfalle",
    QuantenhardwareChartaTyp.PHOTONIK: "photonik",
    QuantenhardwareChartaTyp.TOPOLOGISCH: "topologisch",
    QuantenhardwareChartaTyp.SPIN_QUBIT: "spin_qubit",
}
_PROZEDUR_MAP = {
    QuantenhardwareChartaProzedur.KUEHLUNGSTECHNIK: "kuehlungstechnik",
    QuantenhardwareChartaProzedur.GATE_KALIBRIERUNG: "gate_kalibrierung",
    QuantenhardwareChartaProzedur.QUBIT_KOPPLUNG: "qubit_kopplung",
    QuantenhardwareChartaProzedur.FIDELITY_MESSUNG: "fidelity_messung",
    QuantenhardwareChartaProzedur.SKALIERUNG: "skalierung",
}


@dataclass(frozen=True)
class QuantenhardwareChartaNorm:
    typ: QuantenhardwareChartaTyp
    prozedur: QuantenhardwareChartaProzedur
    quanten_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class QuantenhardwareCharta:
    normen: tuple[QuantenhardwareChartaNorm, ...]
    canonical: bool = True

    def aggregates_charta_signal(self) -> dict:
        return {
            "charta_id": "quantenhardware-charta-933",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_quantenhardware_charta(parent: Optional[QuantenalgorithmusRegister] = None) -> QuantenhardwareCharta:
    if parent is None:
        parent = build_quantenalgorithmus_register()
    base = sum(e.quanten_weight for e in parent.eintraege)
    normen = tuple(
        QuantenhardwareChartaNorm(
            typ=t,
            prozedur=list(QuantenhardwareChartaProzedur)[i],
            quanten_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(QuantenhardwareChartaTyp)
    )
    return QuantenhardwareCharta(normen=normen)
