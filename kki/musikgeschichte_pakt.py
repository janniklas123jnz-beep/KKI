"""#626 MusikgeschichtePakt — Musikgeschichte & Stilperioden (parent: KompositionsManifest)."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List
from .kompositions_manifest import KompositionsManifest, build_kompositions_manifest

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class MusikgeschichtePaktGeltung(str, Enum):
    GESPERRT = "gesperrt"
    MUSIKHISTORISCH = "musikhistorisch"
    GRUNDLEGEND_MUSIKHISTORISCH = "grundlegend-musikhistorisch"


class MusikgeschichtePaktTyp(str, Enum):
    ANALYTISCH = "analytisch"
    SYNTHETISCH = "synthetisch"
    HISTORISCH = "historisch"
    KOMPARATIV = "komparativ"


class MusikgeschichtePaktProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class MusikgeschichtePaktNorm:
    musikgeschichte_pakt_id: str
    geltung: MusikgeschichtePaktGeltung
    typ: MusikgeschichtePaktTyp
    musik_weight: float
    musik_tier: int
    musik_ids: List[str]
    musik_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class MusikgeschichtePakt:
    pakt_id: str
    normen: List[MusikgeschichtePaktNorm]
    parent: KompositionsManifest


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        MusikgeschichtePaktGeltung.GESPERRT: 0.0,
        MusikgeschichtePaktGeltung.MUSIKHISTORISCH: 0.05,
        MusikgeschichtePaktGeltung.GRUNDLEGEND_MUSIKHISTORISCH: 0.1,
    })
    _TIER_DELTA.update({
        MusikgeschichtePaktGeltung.GESPERRT: 0,
        MusikgeschichtePaktGeltung.MUSIKHISTORISCH: 1,
        MusikgeschichtePaktGeltung.GRUNDLEGEND_MUSIKHISTORISCH: 2,
    })
    _TYP_MAP.update({
        MusikgeschichtePaktGeltung.GESPERRT: MusikgeschichtePaktTyp.ANALYTISCH,
        MusikgeschichtePaktGeltung.MUSIKHISTORISCH: MusikgeschichtePaktTyp.SYNTHETISCH,
        MusikgeschichtePaktGeltung.GRUNDLEGEND_MUSIKHISTORISCH: MusikgeschichtePaktTyp.HISTORISCH,
    })
    _PROZEDUR_MAP.update({
        MusikgeschichtePaktGeltung.GESPERRT: MusikgeschichtePaktProzedur.INITIALISIEREN,
        MusikgeschichtePaktGeltung.MUSIKHISTORISCH: MusikgeschichtePaktProzedur.AKTIVIEREN,
        MusikgeschichtePaktGeltung.GRUNDLEGEND_MUSIKHISTORISCH: MusikgeschichtePaktProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        MusikgeschichtePaktGeltung.GESPERRT: [MusikgeschichtePaktGeltung.GESPERRT],
        MusikgeschichtePaktGeltung.MUSIKHISTORISCH: [MusikgeschichtePaktGeltung.MUSIKHISTORISCH],
        MusikgeschichtePaktGeltung.GRUNDLEGEND_MUSIKHISTORISCH: [MusikgeschichtePaktGeltung.GRUNDLEGEND_MUSIKHISTORISCH],
    })


_init_map()


def build_musikgeschichte_pakt(*, pakt_id: str = "musikgeschichte-pakt") -> MusikgeschichtePakt:
    parent = build_kompositions_manifest(manifest_id=f"{pakt_id}-parent")
    normen: List[MusikgeschichtePaktNorm] = []
    for g in MusikgeschichtePaktGeltung:
        normen.append(MusikgeschichtePaktNorm(
            musikgeschichte_pakt_id=f"{pakt_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            musik_weight=round(sum(n.musik_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            musik_tier=max(n.musik_tier for n in parent.normen) + _TIER_DELTA[g],
            musik_ids=[f"mgp-{pakt_id}-{g.value}-001", f"mgp-{pakt_id}-{g.value}-002"],
            musik_tags=["musikwissenschaft", "musikgeschichte", g.value],
        ))
    return MusikgeschichtePakt(pakt_id=pakt_id, normen=normen, parent=parent)
