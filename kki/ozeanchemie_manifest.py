from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .marine_biologie_kodex import MarineBiologieKodex, build_marine_biologie_kodex


class OzeanchemieManifestGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_OZEANOGRAPHISCH = auto()
    OZEANOGRAPHISCH = auto()
    OZEANOGRAPHISCH_AKTIV = auto()
    OZEAN_SOUVERAEN = auto()


class OzeanchemieManifestTyp(Enum):
    OZEANCHEMIE = auto()
    CHEMIESYSTEM = auto()
    CHEMIEKOMPONENTE = auto()


class OzeanchemieManifestProzedur(Enum):
    CHEMIEANALYSE = auto()
    CHEMIESYNTHESE = auto()
    CHEMIEBEWERTUNG = auto()


_WEIGHT_DELTA: dict[OzeanchemieManifestGeltung, float] = {
    OzeanchemieManifestGeltung.GESPERRT: 0.0,
    OzeanchemieManifestGeltung.GRUNDLEGEND_OZEANOGRAPHISCH: 1.6,
    OzeanchemieManifestGeltung.OZEANOGRAPHISCH: 3.2,
    OzeanchemieManifestGeltung.OZEANOGRAPHISCH_AKTIV: 4.8,
    OzeanchemieManifestGeltung.OZEAN_SOUVERAEN: 6.4,
}

_TYP_MAP = {
    OzeanchemieManifestGeltung.GESPERRT: OzeanchemieManifestTyp.OZEANCHEMIE,
    OzeanchemieManifestGeltung.GRUNDLEGEND_OZEANOGRAPHISCH: OzeanchemieManifestTyp.CHEMIEKOMPONENTE,
    OzeanchemieManifestGeltung.OZEANOGRAPHISCH: OzeanchemieManifestTyp.CHEMIEKOMPONENTE,
    OzeanchemieManifestGeltung.OZEANOGRAPHISCH_AKTIV: OzeanchemieManifestTyp.CHEMIESYSTEM,
    OzeanchemieManifestGeltung.OZEAN_SOUVERAEN: OzeanchemieManifestTyp.CHEMIESYSTEM,
}

_PROZEDUR_MAP = {
    OzeanchemieManifestGeltung.GESPERRT: OzeanchemieManifestProzedur.CHEMIEANALYSE,
    OzeanchemieManifestGeltung.GRUNDLEGEND_OZEANOGRAPHISCH: OzeanchemieManifestProzedur.CHEMIEANALYSE,
    OzeanchemieManifestGeltung.OZEANOGRAPHISCH: OzeanchemieManifestProzedur.CHEMIESYNTHESE,
    OzeanchemieManifestGeltung.OZEANOGRAPHISCH_AKTIV: OzeanchemieManifestProzedur.CHEMIESYNTHESE,
    OzeanchemieManifestGeltung.OZEAN_SOUVERAEN: OzeanchemieManifestProzedur.CHEMIEBEWERTUNG,
}


@dataclass(frozen=True)
class OzeanchemieManifestNorm:
    geltung: OzeanchemieManifestGeltung
    ozean_weight: float
    ozean_tier: int
    ozean_ids: tuple[str, ...]
    ozean_tags: tuple[str, ...]
    typ: OzeanchemieManifestTyp
    prozedur: OzeanchemieManifestProzedur
    canonical: bool = True


@dataclass(frozen=True)
class OzeanchemieManifest:
    normen: tuple[OzeanchemieManifestNorm, ...]
    parent: Optional[MarineBiologieKodex] = None


def build_ozeanchemie_manifest(parent: Optional[MarineBiologieKodex] = None) -> OzeanchemieManifest:
    if parent is None:
        parent = build_marine_biologie_kodex()
    base = sum(e.ozean_weight for e in parent.eintraege)
    normen = tuple(
        OzeanchemieManifestNorm(
            geltung=g,
            ozean_weight=round(base + _WEIGHT_DELTA[g], 4),
            ozean_tier=i + 1,
            ozean_ids=(f"ozeanchemie-{g.name.lower()}-001",),
            ozean_tags=("ozean", "ozeanchemie", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(OzeanchemieManifestGeltung)
    )
    return OzeanchemieManifest(normen=normen, parent=parent)
