from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .geomagnetismus_manifest import GeomagnetismusManifest, build_geomagnetismus_manifest


class VulkanismusPaktGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_GEOPHYSIKALISCH = auto()
    GEOPHYSIKALISCH = auto()
    GEOPHYSIKALISCH_AKTIV = auto()
    GEOPHYSIK_SOUVERAEN = auto()


class VulkanismusPaktTyp(Enum):
    VULKANISMUS = auto()
    MAGMASYSTEM = auto()
    VULKANKOMPONENTE = auto()


class VulkanismusPaktProzedur(Enum):
    VULKANANALYSE = auto()
    VULKANSYNTHESE = auto()
    VULKANBEWERTUNG = auto()


_WEIGHT_DELTA: dict[VulkanismusPaktGeltung, float] = {
    VulkanismusPaktGeltung.GESPERRT: 0.0,
    VulkanismusPaktGeltung.GRUNDLEGEND_GEOPHYSIKALISCH: 1.7,
    VulkanismusPaktGeltung.GEOPHYSIKALISCH: 3.4,
    VulkanismusPaktGeltung.GEOPHYSIKALISCH_AKTIV: 5.1,
    VulkanismusPaktGeltung.GEOPHYSIK_SOUVERAEN: 6.8,
}

_TYP_MAP = {
    VulkanismusPaktGeltung.GESPERRT: VulkanismusPaktTyp.VULKANISMUS,
    VulkanismusPaktGeltung.GRUNDLEGEND_GEOPHYSIKALISCH: VulkanismusPaktTyp.VULKANKOMPONENTE,
    VulkanismusPaktGeltung.GEOPHYSIKALISCH: VulkanismusPaktTyp.VULKANKOMPONENTE,
    VulkanismusPaktGeltung.GEOPHYSIKALISCH_AKTIV: VulkanismusPaktTyp.MAGMASYSTEM,
    VulkanismusPaktGeltung.GEOPHYSIK_SOUVERAEN: VulkanismusPaktTyp.MAGMASYSTEM,
}

_PROZEDUR_MAP = {
    VulkanismusPaktGeltung.GESPERRT: VulkanismusPaktProzedur.VULKANANALYSE,
    VulkanismusPaktGeltung.GRUNDLEGEND_GEOPHYSIKALISCH: VulkanismusPaktProzedur.VULKANANALYSE,
    VulkanismusPaktGeltung.GEOPHYSIKALISCH: VulkanismusPaktProzedur.VULKANSYNTHESE,
    VulkanismusPaktGeltung.GEOPHYSIKALISCH_AKTIV: VulkanismusPaktProzedur.VULKANSYNTHESE,
    VulkanismusPaktGeltung.GEOPHYSIK_SOUVERAEN: VulkanismusPaktProzedur.VULKANBEWERTUNG,
}


@dataclass(frozen=True)
class VulkanismusPaktEintrag:
    geltung: VulkanismusPaktGeltung
    geophysik_weight: float
    geophysik_tier: int
    geophysik_ids: tuple[str, ...]
    geophysik_tags: tuple[str, ...]
    typ: VulkanismusPaktTyp
    prozedur: VulkanismusPaktProzedur
    canonical: bool = True


@dataclass(frozen=True)
class VulkanismusPakt:
    eintraege: tuple[VulkanismusPaktEintrag, ...]
    parent: Optional[GeomagnetismusManifest] = None


def build_vulkanismus_pakt(parent: Optional[GeomagnetismusManifest] = None) -> VulkanismusPakt:
    if parent is None:
        parent = build_geomagnetismus_manifest()
    base = sum(n.geophysik_weight for n in parent.normen)
    eintraege = tuple(
        VulkanismusPaktEintrag(
            geltung=g,
            geophysik_weight=round(base + _WEIGHT_DELTA[g], 4),
            geophysik_tier=i + 1,
            geophysik_ids=(f"vulkanismus-{g.name.lower()}-001",),
            geophysik_tags=("geophysik", "vulkanismus", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(VulkanismusPaktGeltung)
    )
    return VulkanismusPakt(eintraege=eintraege, parent=parent)
