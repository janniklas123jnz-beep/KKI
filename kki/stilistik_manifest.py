"""#635 StilistikManifest — Stilistik & rhetorische Analyse (parent: DramatikKodex)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .dramatik_kodex import DramatikKodex, build_dramatik_kodex

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class StilistikManifestGeltung(str, Enum):
    GESPERRT = "gesperrt"
    STILISTISCH = "stilistisch"
    GRUNDLEGEND_STILISTISCH = "grundlegend-stilistisch"


class StilistikManifestTyp(str, Enum):
    ANALYTISCH = "analytisch"
    SYNTHETISCH = "synthetisch"
    HISTORISCH = "historisch"
    KOMPARATIV = "komparativ"


class StilistikManifestProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class StilistikManifestNorm:
    stilistik_manifest_id: str
    geltung: StilistikManifestGeltung
    typ: StilistikManifestTyp
    literatur_weight: float
    literatur_tier: int
    literatur_ids: List[str]
    literatur_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class StilistikManifest:
    manifest_id: str
    normen: List[StilistikManifestNorm]
    parent: DramatikKodex


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        StilistikManifestGeltung.GESPERRT: 0.0,
        StilistikManifestGeltung.STILISTISCH: 0.05,
        StilistikManifestGeltung.GRUNDLEGEND_STILISTISCH: 0.1,
    })
    _TIER_DELTA.update({
        StilistikManifestGeltung.GESPERRT: 0,
        StilistikManifestGeltung.STILISTISCH: 1,
        StilistikManifestGeltung.GRUNDLEGEND_STILISTISCH: 2,
    })
    _TYP_MAP.update({
        StilistikManifestGeltung.GESPERRT: StilistikManifestTyp.ANALYTISCH,
        StilistikManifestGeltung.STILISTISCH: StilistikManifestTyp.SYNTHETISCH,
        StilistikManifestGeltung.GRUNDLEGEND_STILISTISCH: StilistikManifestTyp.HISTORISCH,
    })
    _PROZEDUR_MAP.update({
        StilistikManifestGeltung.GESPERRT: StilistikManifestProzedur.INITIALISIEREN,
        StilistikManifestGeltung.STILISTISCH: StilistikManifestProzedur.AKTIVIEREN,
        StilistikManifestGeltung.GRUNDLEGEND_STILISTISCH: StilistikManifestProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        StilistikManifestGeltung.GESPERRT: [StilistikManifestGeltung.GESPERRT],
        StilistikManifestGeltung.STILISTISCH: [StilistikManifestGeltung.STILISTISCH],
        StilistikManifestGeltung.GRUNDLEGEND_STILISTISCH: [StilistikManifestGeltung.GRUNDLEGEND_STILISTISCH],
    })


_init_map()


def build_stilistik_manifest(*, manifest_id: str = "stilistik-manifest") -> StilistikManifest:
    parent = build_dramatik_kodex(kodex_id=f"{manifest_id}-parent")
    normen: List[StilistikManifestNorm] = []
    for g in StilistikManifestGeltung:
        normen.append(StilistikManifestNorm(
            stilistik_manifest_id=f"sm-{manifest_id}-{g.value}-001",
            geltung=g,
            typ=_TYP_MAP[g],
            literatur_weight=round(sum(n.literatur_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            literatur_tier=max(n.literatur_tier for n in parent.normen) + _TIER_DELTA[g],
            literatur_ids=[f"sm-{manifest_id}-{g.value}-001", f"sm-{manifest_id}-{g.value}-002"],
            literatur_tags=["literaturwissenschaft", "stilistik", g.value],
        ))
    return StilistikManifest(manifest_id=manifest_id, normen=normen, parent=parent)
