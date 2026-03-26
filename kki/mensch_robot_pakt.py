"""
#916 MenschRobotPakt — Human-Robot Interaction: Cobots, Sicherheit & Vertrauen.
Fong, Nourbakhsh & Dautenhahn (2003): Survey of Socially Interactive Robots — HRI-Grundlagen.
Haddadin et al. (2008): Kollisionserkennung und -reaktion für sichere Cobots.
ISO/TS 15066 (2016): Kollaborative Roboter — Sicherheitsstandards für Mensch-Roboter-Kooperation.
Breazeal (2004): Sociable Robots — emotionale Intelligenz für Mensch-Roboter-Vertrauen.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .navigations_manifest import NavigationsManifest, build_navigations_manifest


class MenschRobotPaktTyp(Enum):
    KOLLABORATION = auto()
    SICHERHEIT = auto()
    KOMMUNIKATION = auto()
    VERTRAUEN = auto()
    ANPASSUNG = auto()


class MenschRobotPaktProzedur(Enum):
    KONTAKTERKENNUNG = auto()
    ABSICHTSPRUEFUNG = auto()
    HANDLUNGSAUSHANDLUNG = auto()
    FEEDBACK = auto()
    LERNEN = auto()


_WEIGHT_DELTA = {
    MenschRobotPaktTyp.KOLLABORATION: 0.0,
    MenschRobotPaktTyp.SICHERHEIT: 1.6,
    MenschRobotPaktTyp.KOMMUNIKATION: 3.2,
    MenschRobotPaktTyp.VERTRAUEN: 4.8,
    MenschRobotPaktTyp.ANPASSUNG: 6.4,
}
_TYP_MAP = {
    MenschRobotPaktTyp.KOLLABORATION: "kollaboration",
    MenschRobotPaktTyp.SICHERHEIT: "sicherheit",
    MenschRobotPaktTyp.KOMMUNIKATION: "kommunikation",
    MenschRobotPaktTyp.VERTRAUEN: "vertrauen",
    MenschRobotPaktTyp.ANPASSUNG: "anpassung",
}
_PROZEDUR_MAP = {
    MenschRobotPaktProzedur.KONTAKTERKENNUNG: "kontakterkennung",
    MenschRobotPaktProzedur.ABSICHTSPRUEFUNG: "absichtspruefung",
    MenschRobotPaktProzedur.HANDLUNGSAUSHANDLUNG: "handlungsaushandlung",
    MenschRobotPaktProzedur.FEEDBACK: "feedback",
    MenschRobotPaktProzedur.LERNEN: "lernen",
}


@dataclass(frozen=True)
class MenschRobotPaktEintrag:
    typ: MenschRobotPaktTyp
    prozedur: MenschRobotPaktProzedur
    robotik_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class MenschRobotPakt:
    eintraege: tuple[MenschRobotPaktEintrag, ...]
    canonical: bool = True

    def aggregates_pakt_signal(self) -> dict:
        return {
            "pakt_id": "mensch-robot-pakt-916",
            "eintraege_count": len(self.eintraege),
            "canonical": self.canonical,
        }


def build_mensch_robot_pakt(parent: Optional[NavigationsManifest] = None) -> MenschRobotPakt:
    if parent is None:
        parent = build_navigations_manifest()
    base = sum(n.robotik_weight for n in parent.normen)
    eintraege = tuple(
        MenschRobotPaktEintrag(
            typ=t,
            prozedur=list(MenschRobotPaktProzedur)[i],
            robotik_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(MenschRobotPaktTyp)
    )
    return MenschRobotPakt(eintraege=eintraege)
