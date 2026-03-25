"""#735 — StrukturtechnikManifest: Statik, Dynamik & Materialversagen."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.verfahrenstechnik_kodex import VerfahrenstechnikKodex, build_verfahrenstechnik_kodex


class StrukturtechnikManifestGeltung(str, Enum):
    GESPERRT = "gesperrt"
    STRUKTURTECHNISCH = "strukturtechnisch"
    GRUNDLEGEND_STRUKTURTECHNISCH = "grundlegend-strukturtechnisch"


class StrukturtechnikManifestTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class StrukturtechnikManifestProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class StrukturtechnikManifestNorm:
    manifest_id: str
    geltung: StrukturtechnikManifestGeltung
    typ: StrukturtechnikManifestTyp
    prozedur: StrukturtechnikManifestProzedur
    ing_weight: float
    ing_tier: int
    ing_ids: List[str]
    ing_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class StrukturtechnikManifest:
    manifest_id: str
    normen: List[StrukturtechnikManifestNorm]
    parent: VerfahrenstechnikKodex


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        StrukturtechnikManifestGeltung.GESPERRT: 0.0,
        StrukturtechnikManifestGeltung.STRUKTURTECHNISCH: 0.05,
        StrukturtechnikManifestGeltung.GRUNDLEGEND_STRUKTURTECHNISCH: 0.1,
    })
    _TIER_DELTA.update({
        StrukturtechnikManifestGeltung.GESPERRT: 0,
        StrukturtechnikManifestGeltung.STRUKTURTECHNISCH: 1,
        StrukturtechnikManifestGeltung.GRUNDLEGEND_STRUKTURTECHNISCH: 2,
    })
    _TYP_MAP.update({
        StrukturtechnikManifestGeltung.GESPERRT: StrukturtechnikManifestTyp.BEOBACHTUNG,
        StrukturtechnikManifestGeltung.STRUKTURTECHNISCH: StrukturtechnikManifestTyp.ANALYSE,
        StrukturtechnikManifestGeltung.GRUNDLEGEND_STRUKTURTECHNISCH: StrukturtechnikManifestTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        StrukturtechnikManifestGeltung.GESPERRT: StrukturtechnikManifestProzedur.INITIALISIEREN,
        StrukturtechnikManifestGeltung.STRUKTURTECHNISCH: StrukturtechnikManifestProzedur.AKTIVIEREN,
        StrukturtechnikManifestGeltung.GRUNDLEGEND_STRUKTURTECHNISCH: StrukturtechnikManifestProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        StrukturtechnikManifestGeltung.GESPERRT: [StrukturtechnikManifestGeltung.GESPERRT],
        StrukturtechnikManifestGeltung.STRUKTURTECHNISCH: [StrukturtechnikManifestGeltung.STRUKTURTECHNISCH],
        StrukturtechnikManifestGeltung.GRUNDLEGEND_STRUKTURTECHNISCH: [StrukturtechnikManifestGeltung.GRUNDLEGEND_STRUKTURTECHNISCH],
    })


_init_map()


def build_strukturtechnik_manifest(*, manifest_id: str = "strukturtechnik-manifest") -> StrukturtechnikManifest:
    parent = build_verfahrenstechnik_kodex(kodex_id=f"{manifest_id}-parent")
    normen: List[StrukturtechnikManifestNorm] = []
    for g in StrukturtechnikManifestGeltung:
        normen.append(StrukturtechnikManifestNorm(
            manifest_id=f"{manifest_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            ing_weight=round(sum(e.ing_weight for e in parent.eintraege) * (1.0 + _WEIGHT_DELTA[g]), 4),
            ing_tier=max(e.ing_tier for e in parent.eintraege) + _TIER_DELTA[g],
            ing_ids=[f"sm-{manifest_id}-{g.value}-001", f"sm-{manifest_id}-{g.value}-002"],
            ing_tags=["ing", "strukturtechnik", g.value],
        ))
    return StrukturtechnikManifest(manifest_id=manifest_id, normen=normen, parent=parent)
