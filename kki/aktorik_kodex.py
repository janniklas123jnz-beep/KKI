"""
#914 AktorikKodex — Aktorik: Servos, Hydraulik & Soft Robotics als Antriebssysteme.
Salisbury (1980): Aktive Steifigkeit — Impedanzregelung für sichere Mensch-Roboter-Interaktion.
Pratt & Williamson (1995): Series Elastic Actuators — nachgiebige Aktuatoren für Cobots.
Rus & Tolley (2015): Design, Fabrication & Control of Soft Robots — Nature-Review.
Shepherd et al. (2011): Multigait Soft Robot — pneumatische Weichroboter.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .sensorik_charta import SensorikCharta, build_sensorik_charta


class AktorikKodexTyp(Enum):
    ELEKTROMOTOR = auto()
    HYDRAULISCH = auto()
    PNEUMATISCH = auto()
    PIEZO = auto()
    SOFT_AKTOR = auto()


class AktorikKodexProzedur(Enum):
    ANSTEUERUNG = auto()
    REGELUNG = auto()
    KRAFTMESSUNG = auto()
    POSITIONIERUNG = auto()
    SICHERHEITSABSCHALTUNG = auto()


_WEIGHT_DELTA = {
    AktorikKodexTyp.ELEKTROMOTOR: 0.0,
    AktorikKodexTyp.HYDRAULISCH: 1.8,
    AktorikKodexTyp.PNEUMATISCH: 3.6,
    AktorikKodexTyp.PIEZO: 5.4,
    AktorikKodexTyp.SOFT_AKTOR: 7.2,
}
_TYP_MAP = {
    AktorikKodexTyp.ELEKTROMOTOR: "elektromotor",
    AktorikKodexTyp.HYDRAULISCH: "hydraulisch",
    AktorikKodexTyp.PNEUMATISCH: "pneumatisch",
    AktorikKodexTyp.PIEZO: "piezo",
    AktorikKodexTyp.SOFT_AKTOR: "soft_aktor",
}
_PROZEDUR_MAP = {
    AktorikKodexProzedur.ANSTEUERUNG: "ansteuerung",
    AktorikKodexProzedur.REGELUNG: "regelung",
    AktorikKodexProzedur.KRAFTMESSUNG: "kraftmessung",
    AktorikKodexProzedur.POSITIONIERUNG: "positionierung",
    AktorikKodexProzedur.SICHERHEITSABSCHALTUNG: "sicherheitsabschaltung",
}


@dataclass(frozen=True)
class AktorikKodexEintrag:
    typ: AktorikKodexTyp
    prozedur: AktorikKodexProzedur
    robotik_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class AktorikKodex:
    eintraege: tuple[AktorikKodexEintrag, ...]
    canonical: bool = True

    def aggregates_kodex_signal(self) -> dict:
        return {
            "kodex_id": "aktorik-kodex-914",
            "eintraege_count": len(self.eintraege),
            "canonical": self.canonical,
        }


def build_aktorik_kodex(parent: Optional[SensorikCharta] = None) -> AktorikKodex:
    if parent is None:
        parent = build_sensorik_charta()
    base = sum(n.robotik_weight for n in parent.normen)
    eintraege = tuple(
        AktorikKodexEintrag(
            typ=t,
            prozedur=list(AktorikKodexProzedur)[i],
            robotik_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(AktorikKodexTyp)
    )
    return AktorikKodex(eintraege=eintraege)
