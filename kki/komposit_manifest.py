"""#685 — KompositManifest: Verbundwerkstoffe, Matrix & Verstärkungsfasern."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.polymer_kodex import PolymerKodex, build_polymer_kodex


class KompositManifestGeltung(str, Enum):
    GESPERRT = "gesperrt"
    KOMPOSIT_GEFUEGT = "komposit-gefuegt"
    GRUNDLEGEND_KOMPOSIT_GEFUEGT = "grundlegend-komposit-gefuegt"


class KompositManifestTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class KompositManifestProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class KompositManifestNorm:
    norm_id: str
    geltung: KompositManifestGeltung
    typ: KompositManifestTyp
    prozedur: KompositManifestProzedur
    material_weight: float
    material_tier: int
    material_ids: List[str]
    material_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class KompositManifest:
    manifest_id: str
    normen: List[KompositManifestNorm]
    parent: PolymerKodex


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        KompositManifestGeltung.GESPERRT: 0.0,
        KompositManifestGeltung.KOMPOSIT_GEFUEGT: 0.05,
        KompositManifestGeltung.GRUNDLEGEND_KOMPOSIT_GEFUEGT: 0.1,
    })
    _TIER_DELTA.update({
        KompositManifestGeltung.GESPERRT: 0,
        KompositManifestGeltung.KOMPOSIT_GEFUEGT: 1,
        KompositManifestGeltung.GRUNDLEGEND_KOMPOSIT_GEFUEGT: 2,
    })
    _TYP_MAP.update({
        KompositManifestGeltung.GESPERRT: KompositManifestTyp.BEOBACHTUNG,
        KompositManifestGeltung.KOMPOSIT_GEFUEGT: KompositManifestTyp.ANALYSE,
        KompositManifestGeltung.GRUNDLEGEND_KOMPOSIT_GEFUEGT: KompositManifestTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        KompositManifestGeltung.GESPERRT: KompositManifestProzedur.INITIALISIEREN,
        KompositManifestGeltung.KOMPOSIT_GEFUEGT: KompositManifestProzedur.AKTIVIEREN,
        KompositManifestGeltung.GRUNDLEGEND_KOMPOSIT_GEFUEGT: KompositManifestProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        KompositManifestGeltung.GESPERRT: [KompositManifestGeltung.GESPERRT],
        KompositManifestGeltung.KOMPOSIT_GEFUEGT: [KompositManifestGeltung.KOMPOSIT_GEFUEGT],
        KompositManifestGeltung.GRUNDLEGEND_KOMPOSIT_GEFUEGT: [KompositManifestGeltung.GRUNDLEGEND_KOMPOSIT_GEFUEGT],
    })


_init_map()


def build_komposit_manifest(*, manifest_id: str = "komposit-manifest") -> KompositManifest:
    parent = build_polymer_kodex(kodex_id=f"{manifest_id}-parent")
    normen: List[KompositManifestNorm] = []
    for g in KompositManifestGeltung:
        normen.append(KompositManifestNorm(
            norm_id=f"{manifest_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            material_weight=round(sum(e.material_weight for e in parent.eintraege) * (1.0 + _WEIGHT_DELTA[g]), 4),
            material_tier=max(e.material_tier for e in parent.eintraege) + _TIER_DELTA[g],
            material_ids=[f"km-{manifest_id}-{g.value}-001", f"km-{manifest_id}-{g.value}-002"],
            material_tags=["material", "komposit", g.value],
        ))
    return KompositManifest(manifest_id=manifest_id, normen=normen, parent=parent)
