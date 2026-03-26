"""
#938 QuantenNorm — Quanten-Standards: ISO/IEC, NIST PQC & IEEE (*_norm-Muster).
ISO/IEC JTC 1/SC 27 (2023): Quantum Key Distribution — internationale Normierung
  für Quantenschlüsselverteilung; Interoperabilität zwischen QKD-Systemen.
NIST (2024): Post-Quantum Cryptography Standards — FIPS 203/204/205: ML-KEM,
  ML-DSA, SLH-DSA als erste quantensichere NIST-Standards; Migrationsleitfaden.
IEEE P7130 (2019): Standard for Quantum Technologies — einheitliche Definitionen
  und Metriken für Quantencomputing; Benchmarking und Vergleichbarkeit.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .quantencomputing_senat import QuantencomputingSenat, build_quantencomputing_senat


class QuantenNormTyp(Enum):
    ISO_QUANTEN = auto()
    NIST_PQC = auto()
    IEEE_QUANTEN = auto()
    ETSI_QUANTEN = auto()
    BRANCHENSTANDARD = auto()


class QuantenNormProzedur(Enum):
    NORMIERUNG = auto()
    STANDARDISIERUNG = auto()
    VALIDIERUNG = auto()
    ZERTIFIZIERUNG = auto()
    AKKREDITIERUNG = auto()


_WEIGHT_DELTA = {
    "ISO_QUANTEN": 0.0,
    "NIST_PQC": 2.0,
    "IEEE_QUANTEN": 4.0,
    "ETSI_QUANTEN": 6.0,
    "BRANCHENSTANDARD": 8.0,
}
_TYP_MAP = {
    "ISO_QUANTEN": "iso_quanten",
    "NIST_PQC": "nist_pqc",
    "IEEE_QUANTEN": "ieee_quanten",
    "ETSI_QUANTEN": "etsi_quanten",
    "BRANCHENSTANDARD": "branchenstandard",
}
_PROZEDUR_MAP = {
    "NORMIERUNG": "normierung",
    "STANDARDISIERUNG": "standardisierung",
    "VALIDIERUNG": "validierung",
    "ZERTIFIZIERUNG": "zertifizierung",
    "AKKREDITIERUNG": "akkreditierung",
}


@dataclass(frozen=True)
class QuantenNormEintrag:
    typ: QuantenNormTyp
    prozedur: QuantenNormProzedur
    quanten_norm_weight: float
    quanten_norm_tier: int
    canonical: bool = True


@dataclass(frozen=True)
class QuantenNorm:
    normen: tuple[QuantenNormEintrag, ...]
    canonical: bool = True

    def aggregates_norm_signal(self) -> dict:
        return {
            "norm_id": "quanten-norm-938",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_quanten_norm(parent: Optional[QuantencomputingSenat] = None) -> QuantenNorm:
    if parent is None:
        parent = build_quantencomputing_senat()
    base = sum(n.quanten_weight for n in parent.normen)
    normen = tuple(
        QuantenNormEintrag(
            typ=t,
            prozedur=list(QuantenNormProzedur)[i],
            quanten_norm_weight=base + _WEIGHT_DELTA[t.name],
            quanten_norm_tier=i + 1,
        )
        for i, t in enumerate(QuantenNormTyp)
    )
    return QuantenNorm(normen=normen)
