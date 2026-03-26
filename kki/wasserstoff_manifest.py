"""
#955 WasserstoffManifest — Wasserstoffwirtschaft: Elektrolyse, Brennstoffzelle & Power-to-X.
Grove (1839): On Voltaic Series and the Combination of Gases — erste Brennstoffzelle;
  elektrochemische Umwandlung von Wasserstoff und Sauerstoff zu Strom und Wasser.
Faraday (1834): Experimental Researches in Electricity — Faraday-Gesetze der
  Elektrolyse; Grundlage der Wasserelektrolyse zur Wasserstoffproduktion.
EU Hydrogen Strategy (2020): A Hydrogen Strategy for a Climate-Neutral Europe —
  grüner Wasserstoff als Energieträger; Power-to-X als Sektorenkopplung;
  40 GW Elektrolyseurkapazität bis 2030.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .fusionsenergie_kodex import FusionsenergieKodex, build_fusionsenergie_kodex


class WasserstoffManifestTyp(Enum):
    GRUENER_WASSERSTOFF = auto()
    BLAUER_WASSERSTOFF = auto()
    BRENNSTOFFZELLE = auto()
    POWER_TO_X = auto()
    WASSERSTOFFTRANSPORT = auto()


class WasserstoffManifestProzedur(Enum):
    ELEKTROLYSE = auto()
    SPEICHERUNG = auto()
    TRANSPORT = auto()
    RUECKVERSTROMUNG = auto()
    SEKTORENKOPPLUNG = auto()


_WEIGHT_DELTA = {
    WasserstoffManifestTyp.GRUENER_WASSERSTOFF: 0.0,
    WasserstoffManifestTyp.BLAUER_WASSERSTOFF: 1.6,
    WasserstoffManifestTyp.BRENNSTOFFZELLE: 3.2,
    WasserstoffManifestTyp.POWER_TO_X: 4.8,
    WasserstoffManifestTyp.WASSERSTOFFTRANSPORT: 6.4,
}
_TYP_MAP = {
    WasserstoffManifestTyp.GRUENER_WASSERSTOFF: "gruener_wasserstoff",
    WasserstoffManifestTyp.BLAUER_WASSERSTOFF: "blauer_wasserstoff",
    WasserstoffManifestTyp.BRENNSTOFFZELLE: "brennstoffzelle",
    WasserstoffManifestTyp.POWER_TO_X: "power_to_x",
    WasserstoffManifestTyp.WASSERSTOFFTRANSPORT: "wasserstofftransport",
}
_PROZEDUR_MAP = {
    WasserstoffManifestProzedur.ELEKTROLYSE: "elektrolyse",
    WasserstoffManifestProzedur.SPEICHERUNG: "speicherung",
    WasserstoffManifestProzedur.TRANSPORT: "transport",
    WasserstoffManifestProzedur.RUECKVERSTROMUNG: "rueckverstromung",
    WasserstoffManifestProzedur.SEKTORENKOPPLUNG: "sektorenkopplung",
}


@dataclass(frozen=True)
class WasserstoffManifestNorm:
    typ: WasserstoffManifestTyp
    prozedur: WasserstoffManifestProzedur
    energie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class WasserstoffManifest:
    normen: tuple[WasserstoffManifestNorm, ...]
    canonical: bool = True

    def aggregates_manifest_signal(self) -> dict:
        return {
            "manifest_id": "wasserstoff-manifest-955",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_wasserstoff_manifest(parent: Optional[FusionsenergieKodex] = None) -> WasserstoffManifest:
    if parent is None:
        parent = build_fusionsenergie_kodex()
    base = sum(e.energie_weight for e in parent.eintraege)
    normen = tuple(
        WasserstoffManifestNorm(
            typ=t,
            prozedur=list(WasserstoffManifestProzedur)[i],
            energie_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(WasserstoffManifestTyp)
    )
    return WasserstoffManifest(normen=normen)
