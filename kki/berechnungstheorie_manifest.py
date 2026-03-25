"""#715 — BerechnungstheorieManifest: Turing-Maschinen, Lambda-Kalkül & Berechenbarkeit."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.komplexitaetstheorie_kodex import KomplexitaetstheorieKodex, build_komplexitaetstheorie_kodex


class BerechnungstheorieManifestGeltung(str, Enum):
    GESPERRT = "gesperrt"
    BERECHENBAR = "berechenbar"
    GRUNDLEGEND_BERECHENBAR = "grundlegend-berechenbar"


class BerechnungstheorieManifestTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class BerechnungstheorieManifestProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class BerechnungstheorieManifestNorm:
    manifest_id: str
    geltung: BerechnungstheorieManifestGeltung
    typ: BerechnungstheorieManifestTyp
    prozedur: BerechnungstheorieManifestProzedur
    info_weight: float
    info_tier: int
    info_ids: List[str]
    info_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class BerechnungstheorieManifest:
    manifest_id: str
    normen: List[BerechnungstheorieManifestNorm]
    parent: KomplexitaetstheorieKodex


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        BerechnungstheorieManifestGeltung.GESPERRT: 0.0,
        BerechnungstheorieManifestGeltung.BERECHENBAR: 0.05,
        BerechnungstheorieManifestGeltung.GRUNDLEGEND_BERECHENBAR: 0.1,
    })
    _TIER_DELTA.update({
        BerechnungstheorieManifestGeltung.GESPERRT: 0,
        BerechnungstheorieManifestGeltung.BERECHENBAR: 1,
        BerechnungstheorieManifestGeltung.GRUNDLEGEND_BERECHENBAR: 2,
    })
    _TYP_MAP.update({
        BerechnungstheorieManifestGeltung.GESPERRT: BerechnungstheorieManifestTyp.BEOBACHTUNG,
        BerechnungstheorieManifestGeltung.BERECHENBAR: BerechnungstheorieManifestTyp.ANALYSE,
        BerechnungstheorieManifestGeltung.GRUNDLEGEND_BERECHENBAR: BerechnungstheorieManifestTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        BerechnungstheorieManifestGeltung.GESPERRT: BerechnungstheorieManifestProzedur.INITIALISIEREN,
        BerechnungstheorieManifestGeltung.BERECHENBAR: BerechnungstheorieManifestProzedur.AKTIVIEREN,
        BerechnungstheorieManifestGeltung.GRUNDLEGEND_BERECHENBAR: BerechnungstheorieManifestProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        BerechnungstheorieManifestGeltung.GESPERRT: [BerechnungstheorieManifestGeltung.GESPERRT],
        BerechnungstheorieManifestGeltung.BERECHENBAR: [BerechnungstheorieManifestGeltung.BERECHENBAR],
        BerechnungstheorieManifestGeltung.GRUNDLEGEND_BERECHENBAR: [BerechnungstheorieManifestGeltung.GRUNDLEGEND_BERECHENBAR],
    })


_init_map()


def build_berechnungstheorie_manifest(*, manifest_id: str = "berechnungstheorie-manifest") -> BerechnungstheorieManifest:
    parent = build_komplexitaetstheorie_kodex(kodex_id=f"{manifest_id}-parent")
    normen: List[BerechnungstheorieManifestNorm] = []
    for g in BerechnungstheorieManifestGeltung:
        normen.append(BerechnungstheorieManifestNorm(
            manifest_id=f"{manifest_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            info_weight=round(sum(e.info_weight for e in parent.eintraege) * (1.0 + _WEIGHT_DELTA[g]), 4),
            info_tier=max(e.info_tier for e in parent.eintraege) + _TIER_DELTA[g],
            info_ids=[f"bt-{manifest_id}-{g.value}-001", f"bt-{manifest_id}-{g.value}-002"],
            info_tags=["info", "berechnungstheorie", g.value],
        ))
    return BerechnungstheorieManifest(manifest_id=manifest_id, normen=normen, parent=parent)
