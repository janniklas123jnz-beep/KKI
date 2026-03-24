"""#627 MusikEthnologieSenat — Musikethnologie & Weltmusik (parent: MusikgeschichtePakt)."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List
from .musikgeschichte_pakt import MusikgeschichtePakt, build_musikgeschichte_pakt

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class MusikEthnologieSenatGeltung(str, Enum):
    GESPERRT = "gesperrt"
    MUSIKETHNOLOGISCH = "musikethnologisch"
    GRUNDLEGEND_MUSIKETHNOLOGISCH = "grundlegend-musikethnologisch"


class MusikEthnologieSenatTyp(str, Enum):
    ANALYTISCH = "analytisch"
    SYNTHETISCH = "synthetisch"
    HISTORISCH = "historisch"
    KOMPARATIV = "komparativ"


class MusikEthnologieSenatProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class MusikEthnologieSenatNorm:
    musikethnologie_senat_id: str
    geltung: MusikEthnologieSenatGeltung
    typ: MusikEthnologieSenatTyp
    musik_weight: float
    musik_tier: int
    musik_ids: List[str]
    musik_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class MusikEthnologieSenat:
    senat_id: str
    normen: List[MusikEthnologieSenatNorm]
    parent: MusikgeschichtePakt


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        MusikEthnologieSenatGeltung.GESPERRT: 0.0,
        MusikEthnologieSenatGeltung.MUSIKETHNOLOGISCH: 0.05,
        MusikEthnologieSenatGeltung.GRUNDLEGEND_MUSIKETHNOLOGISCH: 0.1,
    })
    _TIER_DELTA.update({
        MusikEthnologieSenatGeltung.GESPERRT: 0,
        MusikEthnologieSenatGeltung.MUSIKETHNOLOGISCH: 1,
        MusikEthnologieSenatGeltung.GRUNDLEGEND_MUSIKETHNOLOGISCH: 2,
    })
    _TYP_MAP.update({
        MusikEthnologieSenatGeltung.GESPERRT: MusikEthnologieSenatTyp.ANALYTISCH,
        MusikEthnologieSenatGeltung.MUSIKETHNOLOGISCH: MusikEthnologieSenatTyp.SYNTHETISCH,
        MusikEthnologieSenatGeltung.GRUNDLEGEND_MUSIKETHNOLOGISCH: MusikEthnologieSenatTyp.HISTORISCH,
    })
    _PROZEDUR_MAP.update({
        MusikEthnologieSenatGeltung.GESPERRT: MusikEthnologieSenatProzedur.INITIALISIEREN,
        MusikEthnologieSenatGeltung.MUSIKETHNOLOGISCH: MusikEthnologieSenatProzedur.AKTIVIEREN,
        MusikEthnologieSenatGeltung.GRUNDLEGEND_MUSIKETHNOLOGISCH: MusikEthnologieSenatProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        MusikEthnologieSenatGeltung.GESPERRT: [MusikEthnologieSenatGeltung.GESPERRT],
        MusikEthnologieSenatGeltung.MUSIKETHNOLOGISCH: [MusikEthnologieSenatGeltung.MUSIKETHNOLOGISCH],
        MusikEthnologieSenatGeltung.GRUNDLEGEND_MUSIKETHNOLOGISCH: [MusikEthnologieSenatGeltung.GRUNDLEGEND_MUSIKETHNOLOGISCH],
    })


_init_map()


def build_musikethnologie_senat(*, senat_id: str = "musikethnologie-senat") -> MusikEthnologieSenat:
    parent = build_musikgeschichte_pakt(pakt_id=f"{senat_id}-parent")
    normen: List[MusikEthnologieSenatNorm] = []
    for g in MusikEthnologieSenatGeltung:
        normen.append(MusikEthnologieSenatNorm(
            musikethnologie_senat_id=f"{senat_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            musik_weight=round(sum(n.musik_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            musik_tier=max(n.musik_tier for n in parent.normen) + _TIER_DELTA[g],
            musik_ids=[f"mes-{senat_id}-{g.value}-001", f"mes-{senat_id}-{g.value}-002"],
            musik_tags=["musikwissenschaft", "musikethnologie", g.value],
        ))
    return MusikEthnologieSenat(senat_id=senat_id, normen=normen, parent=parent)
