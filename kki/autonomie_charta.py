"""
#919 AutonomieCharta — Autonome Systeme: SAE-Level, selbstfahrende Fahrzeuge & Drohnen.
SAE International (2014): J3016 — 6 Autonomiestufen für selbstfahrende Fahrzeuge (L0–L5).
Thrun et al. (2006): Stanley — Gewinner DARPA Grand Challenge, autonomes Off-Road-Fahren.
Levinson et al. (2011): Towards Fully Autonomous Driving — Kartenbasierte Wahrnehmung.
FAA (2021): Remote ID für Drohnen — regulatorischer Rahmen für autonome Luftfahrzeuge.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .robotik_norm import RobotikNorm, build_robotik_norm


class AutonomieChartaTyp(Enum):
    FAHRZEUG_AUTONOMIE = auto()
    DROHNEN_AUTONOMIE = auto()
    INDUSTRIELL = auto()
    MEDIZINISCH = auto()
    WELTRAUM = auto()


class AutonomieChartaProzedur(Enum):
    WAHRNEHMUNG = auto()
    ENTSCHEIDUNG = auto()
    AUSFUEHRUNG = auto()
    UEBERWACHUNG = auto()
    NOTABSCHALTUNG = auto()


_WEIGHT_DELTA = {
    AutonomieChartaTyp.FAHRZEUG_AUTONOMIE: 0.0,
    AutonomieChartaTyp.DROHNEN_AUTONOMIE: 2.0,
    AutonomieChartaTyp.INDUSTRIELL: 4.0,
    AutonomieChartaTyp.MEDIZINISCH: 6.0,
    AutonomieChartaTyp.WELTRAUM: 8.0,
}
_TYP_MAP = {
    AutonomieChartaTyp.FAHRZEUG_AUTONOMIE: "fahrzeug_autonomie",
    AutonomieChartaTyp.DROHNEN_AUTONOMIE: "drohnen_autonomie",
    AutonomieChartaTyp.INDUSTRIELL: "industriell",
    AutonomieChartaTyp.MEDIZINISCH: "medizinisch",
    AutonomieChartaTyp.WELTRAUM: "weltraum",
}
_PROZEDUR_MAP = {
    AutonomieChartaProzedur.WAHRNEHMUNG: "wahrnehmung",
    AutonomieChartaProzedur.ENTSCHEIDUNG: "entscheidung",
    AutonomieChartaProzedur.AUSFUEHRUNG: "ausfuehrung",
    AutonomieChartaProzedur.UEBERWACHUNG: "ueberwachung",
    AutonomieChartaProzedur.NOTABSCHALTUNG: "notabschaltung",
}


@dataclass(frozen=True)
class AutonomieChartaNorm:
    typ: AutonomieChartaTyp
    prozedur: AutonomieChartaProzedur
    robotik_weight: float
    robotik_tier: int
    canonical: bool = True


@dataclass(frozen=True)
class AutonomieCharta:
    normen: tuple[AutonomieChartaNorm, ...]
    canonical: bool = True

    def aggregates_charta_signal(self) -> dict:
        return {
            "charta_id": "autonomie-charta-919",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_autonomie_charta(parent: Optional[RobotikNorm] = None) -> AutonomieCharta:
    if parent is None:
        parent = build_robotik_norm()
    base = sum(e.robotik_norm_weight for e in parent.normen)
    normen = tuple(
        AutonomieChartaNorm(
            typ=t,
            prozedur=list(AutonomieChartaProzedur)[i],
            robotik_weight=base + _WEIGHT_DELTA[t],
            robotik_tier=i + 1,
        )
        for i, t in enumerate(AutonomieChartaTyp)
    )
    return AutonomieCharta(normen=normen)
