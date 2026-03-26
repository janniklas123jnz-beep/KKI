"""
#951 EnergieFeld — Energiewissenschaft: Thermodynamik, Carnot & Energiewende.
Carnot (1824): Réflexions sur la puissance motrice du feu — maximaler Wirkungsgrad
  einer Wärmekraftmaschine; Carnot-Wirkungsgrad als thermodynamische Grenze.
Clausius (1865): Über verschiedene für die Anwendung bequeme Formen der
  Hauptgleichungen der mechanischen Wärmetheorie — Entropie als Zustandsgröße;
  zweiter Hauptsatz als fundamentale Grenze aller Energieumwandlung.
Brundtland (1987): Our Common Future — nachhaltige Entwicklung als Leitprinzip;
  Energiewende als gesellschaftliche Aufgabe; Basis von Leitsterns Energie-Ethik.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .biotechnologie_verfassung import BiotechnologieVerfassung, build_biotechnologie_verfassung


class EnergieFeldTyp(Enum):
    THERMODYNAMIK = auto()
    ELEKTRODYNAMIK = auto()
    ERNEUERBARE_ENERGIE = auto()
    SPEICHERTECHNOLOGIE = auto()
    ENERGIEEFFIZIENZ = auto()


class EnergieFeldProzedur(Enum):
    ERZEUGUNG = auto()
    UMWANDLUNG = auto()
    SPEICHERUNG = auto()
    UEBERTRAGUNG = auto()
    VERBRAUCH = auto()


_WEIGHT_DELTA = {
    EnergieFeldTyp.THERMODYNAMIK: 0.0,
    EnergieFeldTyp.ELEKTRODYNAMIK: 1.4,
    EnergieFeldTyp.ERNEUERBARE_ENERGIE: 2.8,
    EnergieFeldTyp.SPEICHERTECHNOLOGIE: 4.2,
    EnergieFeldTyp.ENERGIEEFFIZIENZ: 5.6,
}
_TYP_MAP = {
    EnergieFeldTyp.THERMODYNAMIK: "thermodynamik",
    EnergieFeldTyp.ELEKTRODYNAMIK: "elektrodynamik",
    EnergieFeldTyp.ERNEUERBARE_ENERGIE: "erneuerbare_energie",
    EnergieFeldTyp.SPEICHERTECHNOLOGIE: "speichertechnologie",
    EnergieFeldTyp.ENERGIEEFFIZIENZ: "energieeffizienz",
}
_PROZEDUR_MAP = {
    EnergieFeldProzedur.ERZEUGUNG: "erzeugung",
    EnergieFeldProzedur.UMWANDLUNG: "umwandlung",
    EnergieFeldProzedur.SPEICHERUNG: "speicherung",
    EnergieFeldProzedur.UEBERTRAGUNG: "uebertragung",
    EnergieFeldProzedur.VERBRAUCH: "verbrauch",
}


@dataclass(frozen=True)
class EnergieFeldNorm:
    typ: EnergieFeldTyp
    prozedur: EnergieFeldProzedur
    energie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class EnergieFeld:
    normen: tuple[EnergieFeldNorm, ...]
    canonical: bool = True

    def aggregates_feld_signal(self) -> dict:
        return {
            "feld_id": "energie-feld-951",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_energie_feld(parent: Optional[BiotechnologieVerfassung] = None) -> EnergieFeld:
    if parent is None:
        parent = build_biotechnologie_verfassung()
    base = sum(n.biotech_weight for n in parent.normen)
    normen = tuple(
        EnergieFeldNorm(
            typ=t,
            prozedur=list(EnergieFeldProzedur)[i],
            energie_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(EnergieFeldTyp)
    )
    return EnergieFeld(normen=normen)
