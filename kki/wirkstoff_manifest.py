from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .pharmakodynamik_kodex import PharmakodynamikKodex, build_pharmakodynamik_kodex


class WirkstoffManifestGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_WIRKSAM = auto()
    WIRKSAM = auto()
    WIRKSAM_AKTIV = auto()
    WIRKSTOFF_SOUVERAEN = auto()


class WirkstoffManifestTyp(Enum):
    WIRKSTOFFMANIFEST = auto()
    LEITSTRUKTUR = auto()
    PHARMAKOPHOR = auto()


class WirkstoffManifestProzedur(Enum):
    WIRKSTOFFDESIGN = auto()
    STRUKTUROPTIMIERUNG = auto()
    BINDUNGSAFFINITAETSANALYSE = auto()


_WEIGHT_DELTA: dict[WirkstoffManifestGeltung, float] = {
    WirkstoffManifestGeltung.GESPERRT: 0.0,
    WirkstoffManifestGeltung.GRUNDLEGEND_WIRKSAM: 1.7,
    WirkstoffManifestGeltung.WIRKSAM: 3.4,
    WirkstoffManifestGeltung.WIRKSAM_AKTIV: 5.1,
    WirkstoffManifestGeltung.WIRKSTOFF_SOUVERAEN: 6.8,
}

_TYP_MAP = {
    WirkstoffManifestGeltung.GESPERRT: WirkstoffManifestTyp.WIRKSTOFFMANIFEST,
    WirkstoffManifestGeltung.GRUNDLEGEND_WIRKSAM: WirkstoffManifestTyp.PHARMAKOPHOR,
    WirkstoffManifestGeltung.WIRKSAM: WirkstoffManifestTyp.PHARMAKOPHOR,
    WirkstoffManifestGeltung.WIRKSAM_AKTIV: WirkstoffManifestTyp.LEITSTRUKTUR,
    WirkstoffManifestGeltung.WIRKSTOFF_SOUVERAEN: WirkstoffManifestTyp.LEITSTRUKTUR,
}

_PROZEDUR_MAP = {
    WirkstoffManifestGeltung.GESPERRT: WirkstoffManifestProzedur.WIRKSTOFFDESIGN,
    WirkstoffManifestGeltung.GRUNDLEGEND_WIRKSAM: WirkstoffManifestProzedur.WIRKSTOFFDESIGN,
    WirkstoffManifestGeltung.WIRKSAM: WirkstoffManifestProzedur.STRUKTUROPTIMIERUNG,
    WirkstoffManifestGeltung.WIRKSAM_AKTIV: WirkstoffManifestProzedur.STRUKTUROPTIMIERUNG,
    WirkstoffManifestGeltung.WIRKSTOFF_SOUVERAEN: WirkstoffManifestProzedur.BINDUNGSAFFINITAETSANALYSE,
}


@dataclass(frozen=True)
class WirkstoffManifestNorm:
    geltung: WirkstoffManifestGeltung
    pharma_weight: float
    pharma_tier: int
    pharma_ids: tuple[str, ...]
    pharma_tags: tuple[str, ...]
    typ: WirkstoffManifestTyp
    prozedur: WirkstoffManifestProzedur
    canonical: bool = True


@dataclass(frozen=True)
class WirkstoffManifest:
    normen: tuple[WirkstoffManifestNorm, ...]
    parent: Optional[PharmakodynamikKodex] = None


def build_wirkstoff_manifest(parent: Optional[PharmakodynamikKodex] = None) -> WirkstoffManifest:
    if parent is None:
        parent = build_pharmakodynamik_kodex()
    base = sum(e.pharma_weight for e in parent.eintraege)
    normen = tuple(
        WirkstoffManifestNorm(
            geltung=g,
            pharma_weight=round(base + _WEIGHT_DELTA[g], 4),
            pharma_tier=i + 1,
            pharma_ids=(f"wirkstoff-{g.name.lower()}-001",),
            pharma_tags=("wirkstoff", "manifest", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(WirkstoffManifestGeltung)
    )
    return WirkstoffManifest(normen=normen, parent=parent)
