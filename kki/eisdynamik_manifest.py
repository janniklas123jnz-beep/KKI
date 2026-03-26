from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .permafrost_kodex import PermafrostKodex, build_permafrost_kodex


class EisdynamikManifestTyp(Enum):
    GLETSCHERFLUSS = auto()
    KALBUNG = auto()
    SURGE = auto()
    BASALGLEITEN = auto()
    INNERE_VERFORMUNG = auto()


class EisdynamikManifestProzedur(Enum):
    MESSUNG = auto()
    MODELLIERUNG = auto()
    SIMULATION = auto()
    MONITORING = auto()
    ANALYSE = auto()


_WEIGHT_DELTA = {
    EisdynamikManifestTyp.GLETSCHERFLUSS: 0.0,
    EisdynamikManifestTyp.KALBUNG: 1.6,
    EisdynamikManifestTyp.SURGE: 3.2,
    EisdynamikManifestTyp.BASALGLEITEN: 4.8,
    EisdynamikManifestTyp.INNERE_VERFORMUNG: 6.4,
}
_TYP_MAP = {
    EisdynamikManifestTyp.GLETSCHERFLUSS: "gletscherfluss",
    EisdynamikManifestTyp.KALBUNG: "kalbung",
    EisdynamikManifestTyp.SURGE: "surge",
    EisdynamikManifestTyp.BASALGLEITEN: "basalgleiten",
    EisdynamikManifestTyp.INNERE_VERFORMUNG: "innere_verformung",
}
_PROZEDUR_MAP = {
    EisdynamikManifestProzedur.MESSUNG: "messung",
    EisdynamikManifestProzedur.MODELLIERUNG: "modellierung",
    EisdynamikManifestProzedur.SIMULATION: "simulation",
    EisdynamikManifestProzedur.MONITORING: "monitoring",
    EisdynamikManifestProzedur.ANALYSE: "analyse",
}


@dataclass(frozen=True)
class EisdynamikManifestNorm:
    typ: EisdynamikManifestTyp
    prozedur: EisdynamikManifestProzedur
    glaziologie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class EisdynamikManifest:
    normen: tuple[EisdynamikManifestNorm, ...]
    canonical: bool = True

    def aggregates_manifest_signal(self) -> dict:
        return {
            "manifest_id": "eisdynamik-manifest-895",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_eisdynamik_manifest(parent: Optional[PermafrostKodex] = None) -> EisdynamikManifest:
    if parent is None:
        parent = build_permafrost_kodex()
    base = sum(e.glaziologie_weight for e in parent.eintraege)
    normen = tuple(
        EisdynamikManifestNorm(
            typ=t,
            prozedur=list(EisdynamikManifestProzedur)[i],
            glaziologie_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(EisdynamikManifestTyp)
    )
    return EisdynamikManifest(normen=normen)
