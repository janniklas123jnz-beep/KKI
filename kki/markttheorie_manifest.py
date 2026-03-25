"""#725 — MarkttheorieManifest: Marktstrukturen, Wettbewerb & Preisbildung."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.finanztheorie_kodex import FinanztheorieKodex, build_finanztheorie_kodex


class MarkttheorieManifestGeltung(str, Enum):
    GESPERRT = "gesperrt"
    MARKTTHEORETISCH = "markttheoretisch"
    GRUNDLEGEND_MARKTTHEORETISCH = "grundlegend-markttheoretisch"


class MarkttheorieManifestTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class MarkttheorieManifestProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class MarkttheorieManifestNorm:
    manifest_id: str
    geltung: MarkttheorieManifestGeltung
    typ: MarkttheorieManifestTyp
    prozedur: MarkttheorieManifestProzedur
    wirt_weight: float
    wirt_tier: int
    wirt_ids: List[str]
    wirt_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class MarkttheorieManifest:
    manifest_id: str
    normen: List[MarkttheorieManifestNorm]
    parent: FinanztheorieKodex


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        MarkttheorieManifestGeltung.GESPERRT: 0.0,
        MarkttheorieManifestGeltung.MARKTTHEORETISCH: 0.05,
        MarkttheorieManifestGeltung.GRUNDLEGEND_MARKTTHEORETISCH: 0.1,
    })
    _TIER_DELTA.update({
        MarkttheorieManifestGeltung.GESPERRT: 0,
        MarkttheorieManifestGeltung.MARKTTHEORETISCH: 1,
        MarkttheorieManifestGeltung.GRUNDLEGEND_MARKTTHEORETISCH: 2,
    })
    _TYP_MAP.update({
        MarkttheorieManifestGeltung.GESPERRT: MarkttheorieManifestTyp.BEOBACHTUNG,
        MarkttheorieManifestGeltung.MARKTTHEORETISCH: MarkttheorieManifestTyp.ANALYSE,
        MarkttheorieManifestGeltung.GRUNDLEGEND_MARKTTHEORETISCH: MarkttheorieManifestTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        MarkttheorieManifestGeltung.GESPERRT: MarkttheorieManifestProzedur.INITIALISIEREN,
        MarkttheorieManifestGeltung.MARKTTHEORETISCH: MarkttheorieManifestProzedur.AKTIVIEREN,
        MarkttheorieManifestGeltung.GRUNDLEGEND_MARKTTHEORETISCH: MarkttheorieManifestProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        MarkttheorieManifestGeltung.GESPERRT: [MarkttheorieManifestGeltung.GESPERRT],
        MarkttheorieManifestGeltung.MARKTTHEORETISCH: [MarkttheorieManifestGeltung.MARKTTHEORETISCH],
        MarkttheorieManifestGeltung.GRUNDLEGEND_MARKTTHEORETISCH: [MarkttheorieManifestGeltung.GRUNDLEGEND_MARKTTHEORETISCH],
    })


_init_map()


def build_markttheorie_manifest(*, manifest_id: str = "markttheorie-manifest") -> MarkttheorieManifest:
    parent = build_finanztheorie_kodex(kodex_id=f"{manifest_id}-parent")
    normen: List[MarkttheorieManifestNorm] = []
    for g in MarkttheorieManifestGeltung:
        normen.append(MarkttheorieManifestNorm(
            manifest_id=f"{manifest_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            wirt_weight=round(sum(e.wirt_weight for e in parent.eintraege) * (1.0 + _WEIGHT_DELTA[g]), 4),
            wirt_tier=max(e.wirt_tier for e in parent.eintraege) + _TIER_DELTA[g],
            wirt_ids=[f"mm-{manifest_id}-{g.value}-001", f"mm-{manifest_id}-{g.value}-002"],
            wirt_tags=["wirt", "markttheorie", g.value],
        ))
    return MarkttheorieManifest(manifest_id=manifest_id, normen=normen, parent=parent)
