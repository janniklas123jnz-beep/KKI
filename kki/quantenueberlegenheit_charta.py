"""
#939 QuantenüberlegenheitCharta — Quantenvorteil: Sycamore, NISQ & Quantum Advantage.
Preskill (2018): Quantum Computing in the NISQ Era and Beyond — NISQ (Noisy
  Intermediate-Scale Quantum) als aktuelle Ära; Quantenvorteil ohne Fehlerkorrektur.
Arute et al./Google (2019): Quantum Supremacy Using a Programmable Superconducting
  Processor — 53 Qubits, Random Circuit Sampling; erste experimentelle Demonstration
  quantenüberlegener Berechnung in 200 Sekunden vs. 10.000 Jahre klassisch.
Zhong et al./USTC (2020): Quantum Computational Advantage Using Photons — Jiuzhang
  photonischer Quantencomputer; Gaussian Boson Sampling in 200 Sekunden.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .quanten_norm import QuantenNorm, build_quanten_norm


class QuantenueberlegenheitChartaTyp(Enum):
    NISQ_REGIME = auto()
    RANDOM_CIRCUIT_SAMPLING = auto()
    GAUSSIAN_BOSON_SAMPLING = auto()
    FEHLERTOLERANTES_COMPUTING = auto()
    PRAKTISCHER_QUANTENVORTEIL = auto()


class QuantenueberlegenheitChartaProzedur(Enum):
    BENCHMARK_DESIGN = auto()
    QUANTENSCHALTKREIS = auto()
    KLASSISCHER_VERGLEICH = auto()
    VORTEILSNACHWEIS = auto()
    SKALIERUNG = auto()


_WEIGHT_DELTA = {
    QuantenueberlegenheitChartaTyp.NISQ_REGIME: 0.0,
    QuantenueberlegenheitChartaTyp.RANDOM_CIRCUIT_SAMPLING: 2.1,
    QuantenueberlegenheitChartaTyp.GAUSSIAN_BOSON_SAMPLING: 4.2,
    QuantenueberlegenheitChartaTyp.FEHLERTOLERANTES_COMPUTING: 6.3,
    QuantenueberlegenheitChartaTyp.PRAKTISCHER_QUANTENVORTEIL: 8.4,
}
_TYP_MAP = {
    QuantenueberlegenheitChartaTyp.NISQ_REGIME: "nisq_regime",
    QuantenueberlegenheitChartaTyp.RANDOM_CIRCUIT_SAMPLING: "random_circuit_sampling",
    QuantenueberlegenheitChartaTyp.GAUSSIAN_BOSON_SAMPLING: "gaussian_boson_sampling",
    QuantenueberlegenheitChartaTyp.FEHLERTOLERANTES_COMPUTING: "fehlertolerantes_computing",
    QuantenueberlegenheitChartaTyp.PRAKTISCHER_QUANTENVORTEIL: "praktischer_quantenvorteil",
}
_PROZEDUR_MAP = {
    QuantenueberlegenheitChartaProzedur.BENCHMARK_DESIGN: "benchmark_design",
    QuantenueberlegenheitChartaProzedur.QUANTENSCHALTKREIS: "quantenschaltkreis",
    QuantenueberlegenheitChartaProzedur.KLASSISCHER_VERGLEICH: "klassischer_vergleich",
    QuantenueberlegenheitChartaProzedur.VORTEILSNACHWEIS: "vorteilsnachweis",
    QuantenueberlegenheitChartaProzedur.SKALIERUNG: "skalierung",
}


@dataclass(frozen=True)
class QuantenueberlegenheitChartaNorm:
    typ: QuantenueberlegenheitChartaTyp
    prozedur: QuantenueberlegenheitChartaProzedur
    quanten_weight: float
    quanten_tier: int
    canonical: bool = True


@dataclass(frozen=True)
class QuantenueberlegenheitCharta:
    normen: tuple[QuantenueberlegenheitChartaNorm, ...]
    canonical: bool = True

    def aggregates_charta_signal(self) -> dict:
        return {
            "charta_id": "quantenueberlegenheit-charta-939",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_quantenueberlegenheit_charta(parent: Optional[QuantenNorm] = None) -> QuantenueberlegenheitCharta:
    if parent is None:
        parent = build_quanten_norm()
    base = sum(e.quanten_norm_weight for e in parent.normen)
    normen = tuple(
        QuantenueberlegenheitChartaNorm(
            typ=t,
            prozedur=list(QuantenueberlegenheitChartaProzedur)[i],
            quanten_weight=base + _WEIGHT_DELTA[t],
            quanten_tier=i + 1,
        )
        for i, t in enumerate(QuantenueberlegenheitChartaTyp)
    )
    return QuantenueberlegenheitCharta(normen=normen)
