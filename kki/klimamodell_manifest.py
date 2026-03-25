from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .ozeanographie_kodex import OzeanographieKodex, build_ozeanographie_kodex


class KlimamodellManifestGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_KLIMAMODELLHAFT = auto()
    KLIMAMODELLHAFT = auto()
    KLIMAMODELLHAFT_AKTIV = auto()
    KLIMAMODELL_SOUVERAEN = auto()


class KlimamodellManifestTyp(Enum):
    KLIMAMODELLMANIFEST = auto()
    KLIMASIMULATION = auto()
    KLIMAPARAMETER = auto()


class KlimamodellManifestProzedur(Enum):
    KLIMAMODELLIERUNG = auto()
    KLIMASIMULATION = auto()
    KLIMAVALIDIERUNG = auto()


_WEIGHT_DELTA: dict[KlimamodellManifestGeltung, float] = {
    KlimamodellManifestGeltung.GESPERRT: 0.0,
    KlimamodellManifestGeltung.GRUNDLEGEND_KLIMAMODELLHAFT: 1.6,
    KlimamodellManifestGeltung.KLIMAMODELLHAFT: 3.2,
    KlimamodellManifestGeltung.KLIMAMODELLHAFT_AKTIV: 4.8,
    KlimamodellManifestGeltung.KLIMAMODELL_SOUVERAEN: 6.4,
}

_TYP_MAP = {
    KlimamodellManifestGeltung.GESPERRT: KlimamodellManifestTyp.KLIMAMODELLMANIFEST,
    KlimamodellManifestGeltung.GRUNDLEGEND_KLIMAMODELLHAFT: KlimamodellManifestTyp.KLIMAPARAMETER,
    KlimamodellManifestGeltung.KLIMAMODELLHAFT: KlimamodellManifestTyp.KLIMAPARAMETER,
    KlimamodellManifestGeltung.KLIMAMODELLHAFT_AKTIV: KlimamodellManifestTyp.KLIMASIMULATION,
    KlimamodellManifestGeltung.KLIMAMODELL_SOUVERAEN: KlimamodellManifestTyp.KLIMASIMULATION,
}

_PROZEDUR_MAP = {
    KlimamodellManifestGeltung.GESPERRT: KlimamodellManifestProzedur.KLIMAMODELLIERUNG,
    KlimamodellManifestGeltung.GRUNDLEGEND_KLIMAMODELLHAFT: KlimamodellManifestProzedur.KLIMAMODELLIERUNG,
    KlimamodellManifestGeltung.KLIMAMODELLHAFT: KlimamodellManifestProzedur.KLIMASIMULATION,
    KlimamodellManifestGeltung.KLIMAMODELLHAFT_AKTIV: KlimamodellManifestProzedur.KLIMASIMULATION,
    KlimamodellManifestGeltung.KLIMAMODELL_SOUVERAEN: KlimamodellManifestProzedur.KLIMAVALIDIERUNG,
}


@dataclass(frozen=True)
class KlimamodellManifestNorm:
    geltung: KlimamodellManifestGeltung
    klima_weight: float
    klima_tier: int
    klima_ids: tuple[str, ...]
    klima_tags: tuple[str, ...]
    typ: KlimamodellManifestTyp
    prozedur: KlimamodellManifestProzedur
    canonical: bool = True


@dataclass(frozen=True)
class KlimamodellManifest:
    normen: tuple[KlimamodellManifestNorm, ...]
    parent: Optional[OzeanographieKodex] = None


def build_klimamodell_manifest(parent: Optional[OzeanographieKodex] = None) -> KlimamodellManifest:
    if parent is None:
        parent = build_ozeanographie_kodex()
    base = sum(e.klima_weight for e in parent.eintraege)
    normen = tuple(
        KlimamodellManifestNorm(
            geltung=g,
            klima_weight=round(base + _WEIGHT_DELTA[g], 4),
            klima_tier=i + 1,
            klima_ids=(f"klimamodell-manifest-{g.name.lower()}-001",),
            klima_tags=("klimamodell", "manifest", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(KlimamodellManifestGeltung)
    )
    return KlimamodellManifest(normen=normen, parent=parent)
