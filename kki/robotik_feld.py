"""
#911 RobotikFeld — Robotik: Kybernetik, Asimovs Gesetze & Brooks' Subsumtion.
Norbert Wiener (1948): Cybernetics — Regelkreise und Feedback als Basis aller Robotik.
Isaac Asimov (1942): Drei Gesetze der Robotik — normative Grundlage für Roboter-Ethik.
Rodney Brooks (1986): Subsumption Architecture — verhaltensbasierte Robotik ohne zentrale Planung.
Raibert (1986): Laufende Roboter — dynamisches Gleichgewicht durch Reflexregelung.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .maschinenlernen_verfassung import MaschinenlernenVerfassung, build_maschinenlernen_verfassung


class RobotikFeldTyp(Enum):
    INDUSTRIEROBOTER = auto()
    SERVICEROBOTER = auto()
    KOLLABORATIV = auto()
    MOBIL = auto()
    HUMANOIDE = auto()


class RobotikFeldProzedur(Enum):
    PLANUNG = auto()
    AUSFUEHRUNG = auto()
    MONITORING = auto()
    KALIBRIERUNG = auto()
    WARTUNG = auto()


_WEIGHT_DELTA = {
    RobotikFeldTyp.INDUSTRIEROBOTER: 0.0,
    RobotikFeldTyp.SERVICEROBOTER: 1.3,
    RobotikFeldTyp.KOLLABORATIV: 2.6,
    RobotikFeldTyp.MOBIL: 3.9,
    RobotikFeldTyp.HUMANOIDE: 5.2,
}
_TYP_MAP = {
    RobotikFeldTyp.INDUSTRIEROBOTER: "industrieroboter",
    RobotikFeldTyp.SERVICEROBOTER: "serviceroboter",
    RobotikFeldTyp.KOLLABORATIV: "kollaborativ",
    RobotikFeldTyp.MOBIL: "mobil",
    RobotikFeldTyp.HUMANOIDE: "humanoide",
}
_PROZEDUR_MAP = {
    RobotikFeldProzedur.PLANUNG: "planung",
    RobotikFeldProzedur.AUSFUEHRUNG: "ausfuehrung",
    RobotikFeldProzedur.MONITORING: "monitoring",
    RobotikFeldProzedur.KALIBRIERUNG: "kalibrierung",
    RobotikFeldProzedur.WARTUNG: "wartung",
}


@dataclass(frozen=True)
class RobotikFeldNorm:
    typ: RobotikFeldTyp
    prozedur: RobotikFeldProzedur
    robotik_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class RobotikFeld:
    normen: tuple[RobotikFeldNorm, ...]
    canonical: bool = True

    def aggregates_feld_signal(self) -> dict:
        return {
            "feld_id": "robotik-feld-911",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_robotik_feld(parent: Optional[MaschinenlernenVerfassung] = None) -> RobotikFeld:
    if parent is None:
        parent = build_maschinenlernen_verfassung()
    base = sum(n.maschinenlernen_weight for n in parent.normen)
    normen = tuple(
        RobotikFeldNorm(
            typ=t,
            prozedur=list(RobotikFeldProzedur)[i],
            robotik_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(RobotikFeldTyp)
    )
    return RobotikFeld(normen=normen)
