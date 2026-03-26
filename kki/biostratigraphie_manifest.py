from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .stratigraphie_kodex import StartigraphieKodex, build_stratigraphie_kodex


class BiostratigraphieManifestTyp(Enum):
    LEITFOSSIL = auto()
    BIOZONE = auto()
    ASSEMBLAGE = auto()
    REICHWEITE = auto()
    ACME = auto()


class BiostratigraphieManifestProzedur(Enum):
    DEFINITION = auto()
    KORRELATION = auto()
    KALIBRIERUNG = auto()
    REVISION = auto()
    PUBLIKATION = auto()


_WEIGHT_DELTA = {
    BiostratigraphieManifestTyp.LEITFOSSIL: 0.0,
    BiostratigraphieManifestTyp.BIOZONE: 1.6,
    BiostratigraphieManifestTyp.ASSEMBLAGE: 3.2,
    BiostratigraphieManifestTyp.REICHWEITE: 4.8,
    BiostratigraphieManifestTyp.ACME: 6.4,
}
_TYP_MAP = {
    BiostratigraphieManifestTyp.LEITFOSSIL: "leitfossil",
    BiostratigraphieManifestTyp.BIOZONE: "biozone",
    BiostratigraphieManifestTyp.ASSEMBLAGE: "assemblage",
    BiostratigraphieManifestTyp.REICHWEITE: "reichweite",
    BiostratigraphieManifestTyp.ACME: "acme",
}
_PROZEDUR_MAP = {
    BiostratigraphieManifestProzedur.DEFINITION: "definition",
    BiostratigraphieManifestProzedur.KORRELATION: "korrelation",
    BiostratigraphieManifestProzedur.KALIBRIERUNG: "kalibrierung",
    BiostratigraphieManifestProzedur.REVISION: "revision",
    BiostratigraphieManifestProzedur.PUBLIKATION: "publikation",
}


@dataclass(frozen=True)
class BiostratigraphieManifestNorm:
    typ: BiostratigraphieManifestTyp
    prozedur: BiostratigraphieManifestProzedur
    geochronologie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class BiostratigraphieManifest:
    normen: tuple[BiostratigraphieManifestNorm, ...]
    canonical: bool = True

    def aggregates_manifest_signal(self) -> dict:
        return {
            "manifest_id": "biostratigraphie-manifest-875",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_biostratigraphie_manifest(parent: Optional[StartigraphieKodex] = None) -> BiostratigraphieManifest:
    if parent is None:
        parent = build_stratigraphie_kodex()
    base = sum(e.geochronologie_weight for e in parent.eintraege)
    normen = tuple(
        BiostratigraphieManifestNorm(
            typ=t,
            prozedur=list(BiostratigraphieManifestProzedur)[i],
            geochronologie_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(BiostratigraphieManifestTyp)
    )
    return BiostratigraphieManifest(normen=normen)
