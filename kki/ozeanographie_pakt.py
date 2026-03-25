"""#696 — OzeanographiePakt: Meeresströmungen, Tiefsee & Ozeanchemie."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.vulkanismus_manifest import VulkanismusManifest, build_vulkanismus_manifest


class OzeanographiePaktGeltung(str, Enum):
    GESPERRT = "gesperrt"
    OZEANOGRAPHISCH = "ozeanographisch"
    GRUNDLEGEND_OZEANOGRAPHISCH = "grundlegend-ozeanographisch"


class OzeanographiePaktTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class OzeanographiePaktProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class OzeanographiePaktEintrag:
    eintrag_id: str
    geltung: OzeanographiePaktGeltung
    typ: OzeanographiePaktTyp
    prozedur: OzeanographiePaktProzedur
    geo_weight: float
    geo_tier: int
    geo_ids: List[str]
    geo_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class OzeanographiePakt:
    pakt_id: str
    eintraege: List[OzeanographiePaktEintrag]
    parent: VulkanismusManifest


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        OzeanographiePaktGeltung.GESPERRT: 0.0,
        OzeanographiePaktGeltung.OZEANOGRAPHISCH: 0.05,
        OzeanographiePaktGeltung.GRUNDLEGEND_OZEANOGRAPHISCH: 0.1,
    })
    _TIER_DELTA.update({
        OzeanographiePaktGeltung.GESPERRT: 0,
        OzeanographiePaktGeltung.OZEANOGRAPHISCH: 1,
        OzeanographiePaktGeltung.GRUNDLEGEND_OZEANOGRAPHISCH: 2,
    })
    _TYP_MAP.update({
        OzeanographiePaktGeltung.GESPERRT: OzeanographiePaktTyp.BEOBACHTUNG,
        OzeanographiePaktGeltung.OZEANOGRAPHISCH: OzeanographiePaktTyp.ANALYSE,
        OzeanographiePaktGeltung.GRUNDLEGEND_OZEANOGRAPHISCH: OzeanographiePaktTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        OzeanographiePaktGeltung.GESPERRT: OzeanographiePaktProzedur.INITIALISIEREN,
        OzeanographiePaktGeltung.OZEANOGRAPHISCH: OzeanographiePaktProzedur.AKTIVIEREN,
        OzeanographiePaktGeltung.GRUNDLEGEND_OZEANOGRAPHISCH: OzeanographiePaktProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        OzeanographiePaktGeltung.GESPERRT: [OzeanographiePaktGeltung.GESPERRT],
        OzeanographiePaktGeltung.OZEANOGRAPHISCH: [OzeanographiePaktGeltung.OZEANOGRAPHISCH],
        OzeanographiePaktGeltung.GRUNDLEGEND_OZEANOGRAPHISCH: [OzeanographiePaktGeltung.GRUNDLEGEND_OZEANOGRAPHISCH],
    })


_init_map()


def build_ozeanographie_pakt(*, pakt_id: str = "ozeanographie-pakt") -> OzeanographiePakt:
    parent = build_vulkanismus_manifest(manifest_id=f"{pakt_id}-parent")
    eintraege: List[OzeanographiePaktEintrag] = []
    for g in OzeanographiePaktGeltung:
        eintraege.append(OzeanographiePaktEintrag(
            eintrag_id=f"{pakt_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            geo_weight=round(sum(n.geo_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            geo_tier=max(n.geo_tier for n in parent.normen) + _TIER_DELTA[g],
            geo_ids=[f"op-{pakt_id}-{g.value}-001", f"op-{pakt_id}-{g.value}-002"],
            geo_tags=["geo", "ozeanographie", g.value],
        ))
    return OzeanographiePakt(pakt_id=pakt_id, eintraege=eintraege, parent=parent)
