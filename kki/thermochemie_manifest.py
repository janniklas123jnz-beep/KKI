"""#675 ThermochemieManifest — Thermochemie & Energetik (parent: ReaktionskinetikKodex)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .reaktionskinetik_kodex import ReaktionskinetikKodex, build_reaktionskinetik_kodex

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class ThermochemieManifestGeltung(str, Enum):
    GESPERRT = "gesperrt"
    THERMOCHEMISCH_AKTIV = "thermochemisch-aktiv"
    GRUNDLEGEND_THERMOCHEMISCH_AKTIV = "grundlegend-thermochemisch-aktiv"


class ThermochemieManifestTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"
    KATALYSE = "katalyse"


class ThermochemieManifestProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class ThermochemieManifestNorm:
    thermochemie_manifest_id: str
    geltung: ThermochemieManifestGeltung
    typ: ThermochemieManifestTyp
    prozedur: ThermochemieManifestProzedur
    chemie_weight: float
    chemie_tier: int
    chemie_ids: List[str]
    chemie_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class ThermochemieManifest:
    manifest_id: str
    normen: List[ThermochemieManifestNorm]
    parent: ReaktionskinetikKodex


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        ThermochemieManifestGeltung.GESPERRT: 0.0,
        ThermochemieManifestGeltung.THERMOCHEMISCH_AKTIV: 0.05,
        ThermochemieManifestGeltung.GRUNDLEGEND_THERMOCHEMISCH_AKTIV: 0.1,
    })
    _TIER_DELTA.update({
        ThermochemieManifestGeltung.GESPERRT: 0,
        ThermochemieManifestGeltung.THERMOCHEMISCH_AKTIV: 1,
        ThermochemieManifestGeltung.GRUNDLEGEND_THERMOCHEMISCH_AKTIV: 2,
    })
    _TYP_MAP.update({
        ThermochemieManifestGeltung.GESPERRT: ThermochemieManifestTyp.BEOBACHTUNG,
        ThermochemieManifestGeltung.THERMOCHEMISCH_AKTIV: ThermochemieManifestTyp.ANALYSE,
        ThermochemieManifestGeltung.GRUNDLEGEND_THERMOCHEMISCH_AKTIV: ThermochemieManifestTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        ThermochemieManifestGeltung.GESPERRT: ThermochemieManifestProzedur.INITIALISIEREN,
        ThermochemieManifestGeltung.THERMOCHEMISCH_AKTIV: ThermochemieManifestProzedur.AKTIVIEREN,
        ThermochemieManifestGeltung.GRUNDLEGEND_THERMOCHEMISCH_AKTIV: ThermochemieManifestProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        ThermochemieManifestGeltung.GESPERRT: [ThermochemieManifestGeltung.GESPERRT],
        ThermochemieManifestGeltung.THERMOCHEMISCH_AKTIV: [ThermochemieManifestGeltung.THERMOCHEMISCH_AKTIV],
        ThermochemieManifestGeltung.GRUNDLEGEND_THERMOCHEMISCH_AKTIV: [ThermochemieManifestGeltung.GRUNDLEGEND_THERMOCHEMISCH_AKTIV],
    })


_init_map()


def build_thermochemie_manifest(*, manifest_id: str = "thermochemie-manifest") -> ThermochemieManifest:
    parent = build_reaktionskinetik_kodex(kodex_id=f"{manifest_id}-parent")
    normen: List[ThermochemieManifestNorm] = []
    for g in ThermochemieManifestGeltung:
        normen.append(ThermochemieManifestNorm(
            thermochemie_manifest_id=f"{manifest_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            chemie_weight=round(sum(e.chemie_weight for e in parent.eintraege) * (1.0 + _WEIGHT_DELTA[g]), 4),
            chemie_tier=max(e.chemie_tier for e in parent.eintraege) + _TIER_DELTA[g],
            chemie_ids=[f"tm-{manifest_id}-{g.value}-001", f"tm-{manifest_id}-{g.value}-002"],
            chemie_tags=["chemie", "thermochemie", "manifest", g.value],
        ))
    return ThermochemieManifest(manifest_id=manifest_id, normen=normen, parent=parent)
