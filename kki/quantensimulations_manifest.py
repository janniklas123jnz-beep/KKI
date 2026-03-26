"""
#935 QuantensimulationsManifest — Quantensimulation: Hubbard-Modell, Chemie & Optimierung.
Feynman (1982): Simulating Physics with Computers — Vision des Quantensimulators;
  klassische Computer versagen bei exponentiell wachsendem Hilbert-Raum.
Abrams & Lloyd (1997): Simulation of Many-Body Fermi Systems — Quantensimulation
  chemischer Systeme; exponentielle Beschleunigung für Elektronenstruktur-Probleme.
Google Quantum AI (2020): Hartree-Fock on a Superconducting Qubit Quantum Computer —
  erste praxisnahe Quantenchemie-Simulation; Basis für Pharmako- und Materialforschung.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .quantenfehler_kodex import QuantenfehlerKodex, build_quantenfehler_kodex


class QuantensimulationsManifestTyp(Enum):
    QUANTENCHEMIE = auto()
    MATERIALWISSENSCHAFT = auto()
    OPTIMIERUNG = auto()
    VIELTEILCHENSYSTEM = auto()
    FINANZSIMULATION = auto()


class QuantensimulationsManifestProzedur(Enum):
    HAMILTONIAN_KODIERUNG = auto()
    TROTTERISIERUNG = auto()
    VARIATIONELLE_OPTIMIERUNG = auto()
    PHASENSCHAETZUNG = auto()
    ERGEBNISEXTRAKTION = auto()


_WEIGHT_DELTA = {
    QuantensimulationsManifestTyp.QUANTENCHEMIE: 0.0,
    QuantensimulationsManifestTyp.MATERIALWISSENSCHAFT: 1.6,
    QuantensimulationsManifestTyp.OPTIMIERUNG: 3.2,
    QuantensimulationsManifestTyp.VIELTEILCHENSYSTEM: 4.8,
    QuantensimulationsManifestTyp.FINANZSIMULATION: 6.4,
}
_TYP_MAP = {
    QuantensimulationsManifestTyp.QUANTENCHEMIE: "quantenchemie",
    QuantensimulationsManifestTyp.MATERIALWISSENSCHAFT: "materialwissenschaft",
    QuantensimulationsManifestTyp.OPTIMIERUNG: "optimierung",
    QuantensimulationsManifestTyp.VIELTEILCHENSYSTEM: "vielteilchensystem",
    QuantensimulationsManifestTyp.FINANZSIMULATION: "finanzsimulation",
}
_PROZEDUR_MAP = {
    QuantensimulationsManifestProzedur.HAMILTONIAN_KODIERUNG: "hamiltonian_kodierung",
    QuantensimulationsManifestProzedur.TROTTERISIERUNG: "trotterisierung",
    QuantensimulationsManifestProzedur.VARIATIONELLE_OPTIMIERUNG: "variationelle_optimierung",
    QuantensimulationsManifestProzedur.PHASENSCHAETZUNG: "phasenschaetzung",
    QuantensimulationsManifestProzedur.ERGEBNISEXTRAKTION: "ergebnisextraktion",
}


@dataclass(frozen=True)
class QuantensimulationsManifestNorm:
    typ: QuantensimulationsManifestTyp
    prozedur: QuantensimulationsManifestProzedur
    quanten_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class QuantensimulationsManifest:
    normen: tuple[QuantensimulationsManifestNorm, ...]
    canonical: bool = True

    def aggregates_manifest_signal(self) -> dict:
        return {
            "manifest_id": "quantensimulations-manifest-935",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_quantensimulations_manifest(parent: Optional[QuantenfehlerKodex] = None) -> QuantensimulationsManifest:
    if parent is None:
        parent = build_quantenfehler_kodex()
    base = sum(e.quanten_weight for e in parent.eintraege)
    normen = tuple(
        QuantensimulationsManifestNorm(
            typ=t,
            prozedur=list(QuantensimulationsManifestProzedur)[i],
            quanten_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(QuantensimulationsManifestTyp)
    )
    return QuantensimulationsManifest(normen=normen)
