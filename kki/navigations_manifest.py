"""
#915 NavigationsManifest — Navigation: SLAM, Pfadplanung & autonome Bewegung.
Hart, Nilsson & Raphael (1968): A*-Algorithmus — optimale Pfadplanung in Graphen.
Elfes & Moravec (1985): SLAM-Grundlagen — simultane Lokalisierung und Kartierung.
LaValle (1998): RRT — schnell erkundende Zufallsbäume für Bewegungsplanung.
Thrun et al. (2005): Probabilistic Robotics — SLAM als Bayes-Filter-Standardwerk.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .aktorik_kodex import AktorikKodex, build_aktorik_kodex


class NavigationsManifestTyp(Enum):
    SLAM = auto()
    PFADPLANUNG = auto()
    HINDERNISVERMEIDUNG = auto()
    LOKALISATION = auto()
    KARTIERUNG = auto()


class NavigationsManifestProzedur(Enum):
    EXPLORATION = auto()
    PLANUNG = auto()
    AUSFUEHRUNG = auto()
    KORREKTUR = auto()
    ZIELERFASSUNG = auto()


_WEIGHT_DELTA = {
    NavigationsManifestTyp.SLAM: 0.0,
    NavigationsManifestTyp.PFADPLANUNG: 1.6,
    NavigationsManifestTyp.HINDERNISVERMEIDUNG: 3.2,
    NavigationsManifestTyp.LOKALISATION: 4.8,
    NavigationsManifestTyp.KARTIERUNG: 6.4,
}
_TYP_MAP = {
    NavigationsManifestTyp.SLAM: "slam",
    NavigationsManifestTyp.PFADPLANUNG: "pfadplanung",
    NavigationsManifestTyp.HINDERNISVERMEIDUNG: "hindernisvermeidung",
    NavigationsManifestTyp.LOKALISATION: "lokalisation",
    NavigationsManifestTyp.KARTIERUNG: "kartierung",
}
_PROZEDUR_MAP = {
    NavigationsManifestProzedur.EXPLORATION: "exploration",
    NavigationsManifestProzedur.PLANUNG: "planung",
    NavigationsManifestProzedur.AUSFUEHRUNG: "ausfuehrung",
    NavigationsManifestProzedur.KORREKTUR: "korrektur",
    NavigationsManifestProzedur.ZIELERFASSUNG: "zielerfassung",
}


@dataclass(frozen=True)
class NavigationsManifestNorm:
    typ: NavigationsManifestTyp
    prozedur: NavigationsManifestProzedur
    robotik_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class NavigationsManifest:
    normen: tuple[NavigationsManifestNorm, ...]
    canonical: bool = True

    def aggregates_manifest_signal(self) -> dict:
        return {
            "manifest_id": "navigations-manifest-915",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_navigations_manifest(parent: Optional[AktorikKodex] = None) -> NavigationsManifest:
    if parent is None:
        parent = build_aktorik_kodex()
    base = sum(e.robotik_weight for e in parent.eintraege)
    normen = tuple(
        NavigationsManifestNorm(
            typ=t,
            prozedur=list(NavigationsManifestProzedur)[i],
            robotik_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(NavigationsManifestTyp)
    )
    return NavigationsManifest(normen=normen)
