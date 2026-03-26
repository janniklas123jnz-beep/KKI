"""
#912 KinematikRegister — Kinematik: Denavit-Hartenberg & inverse Kinematik.
Denavit & Hartenberg (1955): DH-Parameter — einheitliche Beschreibung von Robotergelenken.
Pieper (1968): Geschlossene Lösung der inversen Kinematik für 6-DOF-Arme.
Featherstone (1987): Rigid Body Dynamics Algorithms — effiziente Dynamikberechnung.
Khalil & Dombre (2002): Modeling, Identification & Control of Robots — Standardreferenz.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .robotik_feld import RobotikFeld, build_robotik_feld


class KinematikRegisterTyp(Enum):
    VORWAERTSKINEMATIK = auto()
    RUECKWAERTSKINEMATIK = auto()
    JACOBI_MATRIX = auto()
    SINGULARITAET = auto()
    WORKSPACE = auto()


class KinematikRegisterProzedur(Enum):
    MODELLIERUNG = auto()
    BERECHNUNG = auto()
    OPTIMIERUNG = auto()
    VALIDIERUNG = auto()
    SIMULATION = auto()


_WEIGHT_DELTA = {
    KinematikRegisterTyp.VORWAERTSKINEMATIK: 0.0,
    KinematikRegisterTyp.RUECKWAERTSKINEMATIK: 1.5,
    KinematikRegisterTyp.JACOBI_MATRIX: 3.0,
    KinematikRegisterTyp.SINGULARITAET: 4.5,
    KinematikRegisterTyp.WORKSPACE: 6.0,
}
_TYP_MAP = {
    KinematikRegisterTyp.VORWAERTSKINEMATIK: "vorwaertskinematik",
    KinematikRegisterTyp.RUECKWAERTSKINEMATIK: "rueckwaertskinematik",
    KinematikRegisterTyp.JACOBI_MATRIX: "jacobi_matrix",
    KinematikRegisterTyp.SINGULARITAET: "singularitaet",
    KinematikRegisterTyp.WORKSPACE: "workspace",
}
_PROZEDUR_MAP = {
    KinematikRegisterProzedur.MODELLIERUNG: "modellierung",
    KinematikRegisterProzedur.BERECHNUNG: "berechnung",
    KinematikRegisterProzedur.OPTIMIERUNG: "optimierung",
    KinematikRegisterProzedur.VALIDIERUNG: "validierung",
    KinematikRegisterProzedur.SIMULATION: "simulation",
}


@dataclass(frozen=True)
class KinematikRegisterEintrag:
    typ: KinematikRegisterTyp
    prozedur: KinematikRegisterProzedur
    robotik_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class KinematikRegister:
    eintraege: tuple[KinematikRegisterEintrag, ...]
    canonical: bool = True

    def aggregates_register_signal(self) -> dict:
        return {
            "register_id": "kinematik-register-912",
            "eintraege_count": len(self.eintraege),
            "canonical": self.canonical,
        }


def build_kinematik_register(parent: Optional[RobotikFeld] = None) -> KinematikRegister:
    if parent is None:
        parent = build_robotik_feld()
    base = sum(n.robotik_weight for n in parent.normen)
    eintraege = tuple(
        KinematikRegisterEintrag(
            typ=t,
            prozedur=list(KinematikRegisterProzedur)[i],
            robotik_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(KinematikRegisterTyp)
    )
    return KinematikRegister(eintraege=eintraege)
