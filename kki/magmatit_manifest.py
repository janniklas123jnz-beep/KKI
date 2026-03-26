from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .metamorphose_kodex import MetamorphoseKodex, build_metamorphose_kodex


class MagmatitManifestTyp(Enum):
    GRANIT = auto()
    BASALT = auto()
    GABBRO = auto()
    RHYOLITH = auto()
    ANDESIT = auto()


class MagmatitManifestProzedur(Enum):
    KLASSIFIKATION = auto()
    GEOCHEMIE = auto()
    PETROLOGIE = auto()
    GENESE = auto()
    DATING = auto()


_WEIGHT_DELTA = {
    MagmatitManifestTyp.GRANIT: 0.0,
    MagmatitManifestTyp.BASALT: 1.6,
    MagmatitManifestTyp.GABBRO: 3.2,
    MagmatitManifestTyp.RHYOLITH: 4.8,
    MagmatitManifestTyp.ANDESIT: 6.4,
}
_TYP_MAP = {
    MagmatitManifestTyp.GRANIT: "granit",
    MagmatitManifestTyp.BASALT: "basalt",
    MagmatitManifestTyp.GABBRO: "gabbro",
    MagmatitManifestTyp.RHYOLITH: "rhyolith",
    MagmatitManifestTyp.ANDESIT: "andesit",
}
_PROZEDUR_MAP = {
    MagmatitManifestProzedur.KLASSIFIKATION: "klassifikation",
    MagmatitManifestProzedur.GEOCHEMIE: "geochemie",
    MagmatitManifestProzedur.PETROLOGIE: "petrologie",
    MagmatitManifestProzedur.GENESE: "genese",
    MagmatitManifestProzedur.DATING: "dating",
}


@dataclass(frozen=True)
class MagmatitManifestNorm:
    typ: MagmatitManifestTyp
    prozedur: MagmatitManifestProzedur
    petrographie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class MagmatitManifest:
    normen: tuple[MagmatitManifestNorm, ...]
    canonical: bool = True

    def aggregates_manifest_signal(self) -> dict:
        return {
            "manifest_id": "magmatit-manifest-885",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_magmatit_manifest(parent: Optional[MetamorphoseKodex] = None) -> MagmatitManifest:
    if parent is None:
        parent = build_metamorphose_kodex()
    base = sum(e.petrographie_weight for e in parent.eintraege)
    normen = tuple(
        MagmatitManifestNorm(
            typ=t,
            prozedur=list(MagmatitManifestProzedur)[i],
            petrographie_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(MagmatitManifestTyp)
    )
    return MagmatitManifest(normen=normen)
