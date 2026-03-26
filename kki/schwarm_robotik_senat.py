"""
#917 SchwarmRobotikSenat — Schwarm-Robotik: Stigmergie, Emergenz & kollektive Intelligenz.
Dorigo & Gambardella (1997): Ant Colony Optimization — Schwarmintelligenz aus einfachen Regeln.
Reynolds (1987): Boids — emergentes Schwarmverhalten durch drei lokale Regeln.
Dorigo et al. (2004): Swarm-bots — selbstorganisierende Roboterschwärme für kollektive Aufgaben.
Rubenstein et al. (2014): Kilobot — 1024-Roboter-Schwarm demonstriert skalierbare Koordination.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .mensch_robot_pakt import MenschRobotPakt, build_mensch_robot_pakt


class SchwarmRobotikSenatTyp(Enum):
    STIGMERGIE = auto()
    KONSENSBILDUNG = auto()
    AUFGABENVERTEILUNG = auto()
    FORMATION = auto()
    KOLLEKTIV_ENTSCHEIDUNG = auto()


class SchwarmRobotikSenatProzedur(Enum):
    KOORDINATION = auto()
    KOMMUNIKATION = auto()
    SELBSTORGANISATION = auto()
    SKALIERUNG = auto()
    EVALUATION = auto()


_WEIGHT_DELTA = {
    SchwarmRobotikSenatTyp.STIGMERGIE: 0.0,
    SchwarmRobotikSenatTyp.KONSENSBILDUNG: 1.9,
    SchwarmRobotikSenatTyp.AUFGABENVERTEILUNG: 3.8,
    SchwarmRobotikSenatTyp.FORMATION: 5.7,
    SchwarmRobotikSenatTyp.KOLLEKTIV_ENTSCHEIDUNG: 7.6,
}
_TYP_MAP = {
    SchwarmRobotikSenatTyp.STIGMERGIE: "stigmergie",
    SchwarmRobotikSenatTyp.KONSENSBILDUNG: "konsensbildung",
    SchwarmRobotikSenatTyp.AUFGABENVERTEILUNG: "aufgabenverteilung",
    SchwarmRobotikSenatTyp.FORMATION: "formation",
    SchwarmRobotikSenatTyp.KOLLEKTIV_ENTSCHEIDUNG: "kollektiv_entscheidung",
}
_PROZEDUR_MAP = {
    SchwarmRobotikSenatProzedur.KOORDINATION: "koordination",
    SchwarmRobotikSenatProzedur.KOMMUNIKATION: "kommunikation",
    SchwarmRobotikSenatProzedur.SELBSTORGANISATION: "selbstorganisation",
    SchwarmRobotikSenatProzedur.SKALIERUNG: "skalierung",
    SchwarmRobotikSenatProzedur.EVALUATION: "evaluation",
}


@dataclass(frozen=True)
class SchwarmRobotikSenatNorm:
    typ: SchwarmRobotikSenatTyp
    prozedur: SchwarmRobotikSenatProzedur
    robotik_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class SchwarmRobotikSenat:
    normen: tuple[SchwarmRobotikSenatNorm, ...]
    canonical: bool = True

    def aggregates_senat_signal(self) -> dict:
        return {
            "senat_id": "schwarm-robotik-senat-917",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_schwarm_robotik_senat(parent: Optional[MenschRobotPakt] = None) -> SchwarmRobotikSenat:
    if parent is None:
        parent = build_mensch_robot_pakt()
    base = sum(e.robotik_weight for e in parent.eintraege)
    normen = tuple(
        SchwarmRobotikSenatNorm(
            typ=t,
            prozedur=list(SchwarmRobotikSenatProzedur)[i],
            robotik_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(SchwarmRobotikSenatTyp)
    )
    return SchwarmRobotikSenat(normen=normen)
