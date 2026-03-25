"""#695 — VulkanismusManifest: Magmatypen, Ausbruchsdynamik & Vulkangefahren."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.tektonik_kodex import TektonikKodex, build_tektonik_kodex


class VulkanismusManifestGeltung(str, Enum):
    GESPERRT = "gesperrt"
    VULKANISCH_AKTIV = "vulkanisch-aktiv"
    GRUNDLEGEND_VULKANISCH_AKTIV = "grundlegend-vulkanisch-aktiv"


class VulkanismusManifestTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class VulkanismusManifestProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class VulkanismusManifestNorm:
    norm_id: str
    geltung: VulkanismusManifestGeltung
    typ: VulkanismusManifestTyp
    prozedur: VulkanismusManifestProzedur
    geo_weight: float
    geo_tier: int
    geo_ids: List[str]
    geo_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class VulkanismusManifest:
    manifest_id: str
    normen: List[VulkanismusManifestNorm]
    parent: TektonikKodex


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        VulkanismusManifestGeltung.GESPERRT: 0.0,
        VulkanismusManifestGeltung.VULKANISCH_AKTIV: 0.05,
        VulkanismusManifestGeltung.GRUNDLEGEND_VULKANISCH_AKTIV: 0.1,
    })
    _TIER_DELTA.update({
        VulkanismusManifestGeltung.GESPERRT: 0,
        VulkanismusManifestGeltung.VULKANISCH_AKTIV: 1,
        VulkanismusManifestGeltung.GRUNDLEGEND_VULKANISCH_AKTIV: 2,
    })
    _TYP_MAP.update({
        VulkanismusManifestGeltung.GESPERRT: VulkanismusManifestTyp.BEOBACHTUNG,
        VulkanismusManifestGeltung.VULKANISCH_AKTIV: VulkanismusManifestTyp.ANALYSE,
        VulkanismusManifestGeltung.GRUNDLEGEND_VULKANISCH_AKTIV: VulkanismusManifestTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        VulkanismusManifestGeltung.GESPERRT: VulkanismusManifestProzedur.INITIALISIEREN,
        VulkanismusManifestGeltung.VULKANISCH_AKTIV: VulkanismusManifestProzedur.AKTIVIEREN,
        VulkanismusManifestGeltung.GRUNDLEGEND_VULKANISCH_AKTIV: VulkanismusManifestProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        VulkanismusManifestGeltung.GESPERRT: [VulkanismusManifestGeltung.GESPERRT],
        VulkanismusManifestGeltung.VULKANISCH_AKTIV: [VulkanismusManifestGeltung.VULKANISCH_AKTIV],
        VulkanismusManifestGeltung.GRUNDLEGEND_VULKANISCH_AKTIV: [VulkanismusManifestGeltung.GRUNDLEGEND_VULKANISCH_AKTIV],
    })


_init_map()


def build_vulkanismus_manifest(*, manifest_id: str = "vulkanismus-manifest") -> VulkanismusManifest:
    parent = build_tektonik_kodex(kodex_id=f"{manifest_id}-parent")
    normen: List[VulkanismusManifestNorm] = []
    for g in VulkanismusManifestGeltung:
        normen.append(VulkanismusManifestNorm(
            norm_id=f"{manifest_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            geo_weight=round(sum(e.geo_weight for e in parent.eintraege) * (1.0 + _WEIGHT_DELTA[g]), 4),
            geo_tier=max(e.geo_tier for e in parent.eintraege) + _TIER_DELTA[g],
            geo_ids=[f"vm-{manifest_id}-{g.value}-001", f"vm-{manifest_id}-{g.value}-002"],
            geo_tags=["geo", "vulkanismus", g.value],
        ))
    return VulkanismusManifest(manifest_id=manifest_id, normen=normen, parent=parent)
