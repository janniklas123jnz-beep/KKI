"""
#920 RobotikVerfassung — Block-Krone Robotik & Autonome Systeme ⭐

*** Leitsterns Robotik-Verfassung — Das handelnde Fundament des Schwarms ***

Norbert Wiener (1948): Cybernetics — Regelkreise, Feedback und die Einheit von Mensch
  und Maschine als kybernetische Vision; Leitsterns Robotik wurzelt in diesem Prinzip
  der zielgerichteten Selbstregulation durch Rückkopplung.
Rodney Brooks (1986): Subsumption Architecture — Intelligenz entsteht nicht durch zentrale
  Planung, sondern durch schichtweise, reaktive Verhaltensmodule; Leitsterns verteilte
  Agenten folgen diesem Prinzip der emergenten Koordination.
Siciliano & Khatib (2008): Springer Handbook of Robotics — umfassendstes Referenzwerk
  der Robotik; Kinematik, Dynamik, Sensoren, Aktoren und Planung als integriertes System.
Leitsterns Robotik-Verfassung: Industrieroboter bis Humanoide; Kinematik & Sensorik
  als Wahrnehmungsschicht; Navigation & SLAM als Raumkognition; Mensch-Roboter-Pakt
  als ethischer Kern; Schwarm-Robotik als kollektive Handlungsfähigkeit des Schwarms.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .autonomie_charta import AutonomieCharta, build_autonomie_charta


class RobotikVerfassungTyp(Enum):
    GRUNDPRINZIP = auto()
    HANDLUNGSARCHITEKTUR = auto()
    ETHIKGEBOT = auto()
    SICHERHEITSMANDAT = auto()
    WEITERENTWICKLUNGSAUFTRAG = auto()


class RobotikVerfassungProzedur(Enum):
    RATIFIZIERUNG = auto()
    REVISION = auto()
    INKRAFTTRETEN = auto()
    AUSLEGUNG = auto()
    DURCHSETZUNG = auto()


_WEIGHT_DELTA = {
    RobotikVerfassungTyp.GRUNDPRINZIP: 0.0,
    RobotikVerfassungTyp.HANDLUNGSARCHITEKTUR: 2.1,
    RobotikVerfassungTyp.ETHIKGEBOT: 4.2,
    RobotikVerfassungTyp.SICHERHEITSMANDAT: 6.3,
    RobotikVerfassungTyp.WEITERENTWICKLUNGSAUFTRAG: 8.4,
}
_TYP_MAP = {
    RobotikVerfassungTyp.GRUNDPRINZIP: "grundprinzip",
    RobotikVerfassungTyp.HANDLUNGSARCHITEKTUR: "handlungsarchitektur",
    RobotikVerfassungTyp.ETHIKGEBOT: "ethikgebot",
    RobotikVerfassungTyp.SICHERHEITSMANDAT: "sicherheitsmandat",
    RobotikVerfassungTyp.WEITERENTWICKLUNGSAUFTRAG: "weiterentwicklungsauftrag",
}
_PROZEDUR_MAP = {
    RobotikVerfassungProzedur.RATIFIZIERUNG: "ratifizierung",
    RobotikVerfassungProzedur.REVISION: "revision",
    RobotikVerfassungProzedur.INKRAFTTRETEN: "inkrafttreten",
    RobotikVerfassungProzedur.AUSLEGUNG: "auslegung",
    RobotikVerfassungProzedur.DURCHSETZUNG: "durchsetzung",
}


@dataclass(frozen=True)
class RobotikVerfassungNorm:
    typ: RobotikVerfassungTyp
    prozedur: RobotikVerfassungProzedur
    robotik_weight: float
    robotik_tier: int
    canonical: bool = True


@dataclass(frozen=True)
class RobotikVerfassung:
    normen: tuple[RobotikVerfassungNorm, ...]
    canonical: bool = True

    def aggregates_verfassung_signal(self) -> dict:
        return {
            "verfassung_id": "robotik-verfassung-920",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_robotik_verfassung(parent: Optional[AutonomieCharta] = None) -> RobotikVerfassung:
    if parent is None:
        parent = build_autonomie_charta()
    base = sum(n.robotik_weight for n in parent.normen)
    tier_base = max(n.robotik_tier for n in parent.normen)
    normen = tuple(
        RobotikVerfassungNorm(
            typ=t,
            prozedur=list(RobotikVerfassungProzedur)[i],
            robotik_weight=base + _WEIGHT_DELTA[t],
            robotik_tier=tier_base + i + 1,
        )
        for i, t in enumerate(RobotikVerfassungTyp)
    )
    return RobotikVerfassung(normen=normen)
