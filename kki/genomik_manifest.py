"""#705 — GenomikManifest: Genomsequenzierung, Bioinformatik & Genomik."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.molekularbiologie_kodex import MolekularbiologieKodex, build_molekularbiologie_kodex


class GenomikManifestGeltung(str, Enum):
    GESPERRT = "gesperrt"
    GENOMISCH_AKTIV = "genomisch-aktiv"
    GRUNDLEGEND_GENOMISCH_AKTIV = "grundlegend-genomisch-aktiv"


class GenomikManifestTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class GenomikManifestProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class GenomikManifestNorm:
    manifest_id: str
    geltung: GenomikManifestGeltung
    typ: GenomikManifestTyp
    prozedur: GenomikManifestProzedur
    bio_weight: float
    bio_tier: int
    bio_ids: List[str]
    bio_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class GenomikManifest:
    manifest_id: str
    normen: List[GenomikManifestNorm]
    parent: MolekularbiologieKodex


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        GenomikManifestGeltung.GESPERRT: 0.0,
        GenomikManifestGeltung.GENOMISCH_AKTIV: 0.05,
        GenomikManifestGeltung.GRUNDLEGEND_GENOMISCH_AKTIV: 0.1,
    })
    _TIER_DELTA.update({
        GenomikManifestGeltung.GESPERRT: 0,
        GenomikManifestGeltung.GENOMISCH_AKTIV: 1,
        GenomikManifestGeltung.GRUNDLEGEND_GENOMISCH_AKTIV: 2,
    })
    _TYP_MAP.update({
        GenomikManifestGeltung.GESPERRT: GenomikManifestTyp.BEOBACHTUNG,
        GenomikManifestGeltung.GENOMISCH_AKTIV: GenomikManifestTyp.ANALYSE,
        GenomikManifestGeltung.GRUNDLEGEND_GENOMISCH_AKTIV: GenomikManifestTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        GenomikManifestGeltung.GESPERRT: GenomikManifestProzedur.INITIALISIEREN,
        GenomikManifestGeltung.GENOMISCH_AKTIV: GenomikManifestProzedur.AKTIVIEREN,
        GenomikManifestGeltung.GRUNDLEGEND_GENOMISCH_AKTIV: GenomikManifestProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        GenomikManifestGeltung.GESPERRT: [GenomikManifestGeltung.GESPERRT],
        GenomikManifestGeltung.GENOMISCH_AKTIV: [GenomikManifestGeltung.GENOMISCH_AKTIV],
        GenomikManifestGeltung.GRUNDLEGEND_GENOMISCH_AKTIV: [GenomikManifestGeltung.GRUNDLEGEND_GENOMISCH_AKTIV],
    })


_init_map()


def build_genomik_manifest(*, manifest_id: str = "genomik-manifest") -> GenomikManifest:
    parent = build_molekularbiologie_kodex(kodex_id=f"{manifest_id}-parent")
    normen: List[GenomikManifestNorm] = []
    for g in GenomikManifestGeltung:
        normen.append(GenomikManifestNorm(
            manifest_id=f"{manifest_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            bio_weight=round(sum(e.bio_weight for e in parent.eintraege) * (1.0 + _WEIGHT_DELTA[g]), 4),
            bio_tier=max(e.bio_tier for e in parent.eintraege) + _TIER_DELTA[g],
            bio_ids=[f"gm-{manifest_id}-{g.value}-001", f"gm-{manifest_id}-{g.value}-002"],
            bio_tags=["bio", "genomik", g.value],
        ))
    return GenomikManifest(manifest_id=manifest_id, normen=normen, parent=parent)
