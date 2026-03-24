"""#636 LiteraturgeschichtePakt — Literaturgeschichte & Epochen (parent: StilistikManifest)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .stilistik_manifest import StilistikManifest, build_stilistik_manifest

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class LiteraturgeschichtePaktGeltung(str, Enum):
    GESPERRT = "gesperrt"
    LITERATURHISTORISCH = "literaturhistorisch"
    GRUNDLEGEND_LITERATURHISTORISCH = "grundlegend-literaturhistorisch"


class LiteraturgeschichtePaktTyp(str, Enum):
    ANALYTISCH = "analytisch"
    SYNTHETISCH = "synthetisch"
    HISTORISCH = "historisch"
    KOMPARATIV = "komparativ"


class LiteraturgeschichtePaktProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class LiteraturgeschichtePaktNorm:
    literaturgeschichte_pakt_id: str
    geltung: LiteraturgeschichtePaktGeltung
    typ: LiteraturgeschichtePaktTyp
    literatur_weight: float
    literatur_tier: int
    literatur_ids: List[str]
    literatur_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class LiteraturgeschichtePakt:
    pakt_id: str
    normen: List[LiteraturgeschichtePaktNorm]
    parent: StilistikManifest


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        LiteraturgeschichtePaktGeltung.GESPERRT: 0.0,
        LiteraturgeschichtePaktGeltung.LITERATURHISTORISCH: 0.05,
        LiteraturgeschichtePaktGeltung.GRUNDLEGEND_LITERATURHISTORISCH: 0.1,
    })
    _TIER_DELTA.update({
        LiteraturgeschichtePaktGeltung.GESPERRT: 0,
        LiteraturgeschichtePaktGeltung.LITERATURHISTORISCH: 1,
        LiteraturgeschichtePaktGeltung.GRUNDLEGEND_LITERATURHISTORISCH: 2,
    })
    _TYP_MAP.update({
        LiteraturgeschichtePaktGeltung.GESPERRT: LiteraturgeschichtePaktTyp.ANALYTISCH,
        LiteraturgeschichtePaktGeltung.LITERATURHISTORISCH: LiteraturgeschichtePaktTyp.SYNTHETISCH,
        LiteraturgeschichtePaktGeltung.GRUNDLEGEND_LITERATURHISTORISCH: LiteraturgeschichtePaktTyp.HISTORISCH,
    })
    _PROZEDUR_MAP.update({
        LiteraturgeschichtePaktGeltung.GESPERRT: LiteraturgeschichtePaktProzedur.INITIALISIEREN,
        LiteraturgeschichtePaktGeltung.LITERATURHISTORISCH: LiteraturgeschichtePaktProzedur.AKTIVIEREN,
        LiteraturgeschichtePaktGeltung.GRUNDLEGEND_LITERATURHISTORISCH: LiteraturgeschichtePaktProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        LiteraturgeschichtePaktGeltung.GESPERRT: [LiteraturgeschichtePaktGeltung.GESPERRT],
        LiteraturgeschichtePaktGeltung.LITERATURHISTORISCH: [LiteraturgeschichtePaktGeltung.LITERATURHISTORISCH],
        LiteraturgeschichtePaktGeltung.GRUNDLEGEND_LITERATURHISTORISCH: [LiteraturgeschichtePaktGeltung.GRUNDLEGEND_LITERATURHISTORISCH],
    })


_init_map()


def build_literaturgeschichte_pakt(*, pakt_id: str = "literaturgeschichte-pakt") -> LiteraturgeschichtePakt:
    parent = build_stilistik_manifest(manifest_id=f"{pakt_id}-parent")
    normen: List[LiteraturgeschichtePaktNorm] = []
    for g in LiteraturgeschichtePaktGeltung:
        normen.append(LiteraturgeschichtePaktNorm(
            literaturgeschichte_pakt_id=f"lgp-{pakt_id}-{g.value}-001",
            geltung=g,
            typ=_TYP_MAP[g],
            literatur_weight=round(sum(n.literatur_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            literatur_tier=max(n.literatur_tier for n in parent.normen) + _TIER_DELTA[g],
            literatur_ids=[f"lgp-{pakt_id}-{g.value}-001", f"lgp-{pakt_id}-{g.value}-002"],
            literatur_tags=["literaturwissenschaft", "literaturgeschichte", g.value],
        ))
    return LiteraturgeschichtePakt(pakt_id=pakt_id, normen=normen, parent=parent)
