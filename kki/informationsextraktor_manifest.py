"""#655 InformationsextraktorManifest — Informationsextraktion & Inhaltsanalyse (parent: QuellenvalidierungKodex)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .quellenvalidierung_kodex import QuellenvalidierungKodex, build_quellenvalidierung_kodex

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class InformationsextraktorManifestGeltung(str, Enum):
    GESPERRT = "gesperrt"
    INFORMATIONSEXTRAHIERT = "informationsextrahiert"
    GRUNDLEGEND_INFORMATIONSEXTRAHIERT = "grundlegend-informationsextrahiert"


class InformationsextraktorManifestTyp(str, Enum):
    RECHERCHE = "recherche"
    VALIDIERUNG = "validierung"
    AGGREGATION = "aggregation"
    AUTONOME_ENTDECKUNG = "autonome-entdeckung"


class InformationsextraktorManifestProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class InformationsextraktorManifestNorm:
    manifest_id: str
    geltung: InformationsextraktorManifestGeltung
    typ: InformationsextraktorManifestTyp
    prozedur: InformationsextraktorManifestProzedur
    internet_weight: float
    internet_tier: int
    internet_ids: List[str]
    internet_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class InformationsextraktorManifest:
    manifest_id: str
    normen: List[InformationsextraktorManifestNorm]
    parent: QuellenvalidierungKodex


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        InformationsextraktorManifestGeltung.GESPERRT: 0.0,
        InformationsextraktorManifestGeltung.INFORMATIONSEXTRAHIERT: 0.05,
        InformationsextraktorManifestGeltung.GRUNDLEGEND_INFORMATIONSEXTRAHIERT: 0.1,
    })
    _TIER_DELTA.update({
        InformationsextraktorManifestGeltung.GESPERRT: 0,
        InformationsextraktorManifestGeltung.INFORMATIONSEXTRAHIERT: 1,
        InformationsextraktorManifestGeltung.GRUNDLEGEND_INFORMATIONSEXTRAHIERT: 2,
    })
    _TYP_MAP.update({
        InformationsextraktorManifestGeltung.GESPERRT: InformationsextraktorManifestTyp.RECHERCHE,
        InformationsextraktorManifestGeltung.INFORMATIONSEXTRAHIERT: InformationsextraktorManifestTyp.VALIDIERUNG,
        InformationsextraktorManifestGeltung.GRUNDLEGEND_INFORMATIONSEXTRAHIERT: InformationsextraktorManifestTyp.AGGREGATION,
    })
    _PROZEDUR_MAP.update({
        InformationsextraktorManifestGeltung.GESPERRT: InformationsextraktorManifestProzedur.INITIALISIEREN,
        InformationsextraktorManifestGeltung.INFORMATIONSEXTRAHIERT: InformationsextraktorManifestProzedur.AKTIVIEREN,
        InformationsextraktorManifestGeltung.GRUNDLEGEND_INFORMATIONSEXTRAHIERT: InformationsextraktorManifestProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        InformationsextraktorManifestGeltung.GESPERRT: [InformationsextraktorManifestGeltung.GESPERRT],
        InformationsextraktorManifestGeltung.INFORMATIONSEXTRAHIERT: [InformationsextraktorManifestGeltung.INFORMATIONSEXTRAHIERT],
        InformationsextraktorManifestGeltung.GRUNDLEGEND_INFORMATIONSEXTRAHIERT: [InformationsextraktorManifestGeltung.GRUNDLEGEND_INFORMATIONSEXTRAHIERT],
    })


_init_map()


def build_informationsextraktor_manifest(*, manifest_id: str = "informationsextraktor-manifest") -> InformationsextraktorManifest:
    parent = build_quellenvalidierung_kodex(kodex_id=f"{manifest_id}-parent")
    normen: List[InformationsextraktorManifestNorm] = []
    for g in InformationsextraktorManifestGeltung:
        normen.append(InformationsextraktorManifestNorm(
            manifest_id=f"{manifest_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            internet_weight=round(sum(e.internet_weight for e in parent.eintraege) * (1.0 + _WEIGHT_DELTA[g]), 4),
            internet_tier=max(e.internet_tier for e in parent.eintraege) + _TIER_DELTA[g],
            internet_ids=[f"iem-{manifest_id}-{g.value}-001", f"iem-{manifest_id}-{g.value}-002"],
            internet_tags=["internet", "informationsextraktion", g.value],
        ))
    return InformationsextraktorManifest(manifest_id=manifest_id, normen=normen, parent=parent)
