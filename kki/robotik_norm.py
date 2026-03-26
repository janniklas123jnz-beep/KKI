"""
#918 RobotikNorm — Robotik-Standards: ISO 10218, IEC 62061 & Sicherheitsnormen (*_norm-Muster).
ISO 10218 (2011): Industrieroboter — Sicherheitsanforderungen für Roboter und Robotersysteme.
IEC 62061 (2021): Sicherheit von Maschinen — funktionale Sicherheit für Steuerungssysteme.
ISO/TS 15066 (2016): Kollaborative Roboter — Kraftgrenzen und Sicherheitszonen.
IEEE P7000 (2021): Ethisch ausgerichtete KI & Robotik — Wertestandards für autonome Systeme.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .schwarm_robotik_senat import SchwarmRobotikSenat, build_schwarm_robotik_senat


class RobotikNormTyp(Enum):
    SICHERHEITSNORM = auto()
    LEISTUNGSNORM = auto()
    KOMMUNIKATIONSNORM = auto()
    ETHIKNORM = auto()
    ZERTIFIZIERUNGSNORM = auto()


class RobotikNormProzedur(Enum):
    NORMIERUNG = auto()
    STANDARDISIERUNG = auto()
    VALIDIERUNG = auto()
    ZERTIFIZIERUNG = auto()
    AKKREDITIERUNG = auto()


_WEIGHT_DELTA = {
    "SICHERHEITSNORM": 0.0,
    "LEISTUNGSNORM": 1.9,
    "KOMMUNIKATIONSNORM": 3.8,
    "ETHIKNORM": 5.7,
    "ZERTIFIZIERUNGSNORM": 7.6,
}
_TYP_MAP = {
    "SICHERHEITSNORM": "sicherheitsnorm",
    "LEISTUNGSNORM": "leistungsnorm",
    "KOMMUNIKATIONSNORM": "kommunikationsnorm",
    "ETHIKNORM": "ethiknorm",
    "ZERTIFIZIERUNGSNORM": "zertifizierungsnorm",
}
_PROZEDUR_MAP = {
    "NORMIERUNG": "normierung",
    "STANDARDISIERUNG": "standardisierung",
    "VALIDIERUNG": "validierung",
    "ZERTIFIZIERUNG": "zertifizierung",
    "AKKREDITIERUNG": "akkreditierung",
}


@dataclass(frozen=True)
class RobotikNormEintrag:
    typ: RobotikNormTyp
    prozedur: RobotikNormProzedur
    robotik_norm_weight: float
    robotik_norm_tier: int
    canonical: bool = True


@dataclass(frozen=True)
class RobotikNorm:
    normen: tuple[RobotikNormEintrag, ...]
    canonical: bool = True

    def aggregates_norm_signal(self) -> dict:
        return {
            "norm_id": "robotik-norm-918",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_robotik_norm(parent: Optional[SchwarmRobotikSenat] = None) -> RobotikNorm:
    if parent is None:
        parent = build_schwarm_robotik_senat()
    base = sum(n.robotik_weight for n in parent.normen)
    normen = tuple(
        RobotikNormEintrag(
            typ=t,
            prozedur=list(RobotikNormProzedur)[i],
            robotik_norm_weight=base + _WEIGHT_DELTA[t.name],
            robotik_norm_tier=i + 1,
        )
        for i, t in enumerate(RobotikNormTyp)
    )
    return RobotikNorm(normen=normen)
