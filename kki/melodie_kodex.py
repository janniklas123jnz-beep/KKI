"""#624 melodieKodex — Melodie & thematische Entwicklung (parent: RhythmusCharta)."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List
from .rhythmus_charta import RhythmusCharta, build_rhythmus_charta

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class MelodieKodexGeltung(str, Enum):
    GESPERRT = "gesperrt"
    MELODISCH = "melodisch"
    GRUNDLEGEND_MELODISCH = "grundlegend-melodisch"


class MelodieKodexTyp(str, Enum):
    ANALYTISCH = "analytisch"
    SYNTHETISCH = "synthetisch"
    HISTORISCH = "historisch"
    KOMPARATIV = "komparativ"


class MelodieKodexProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class MelodieKodexNorm:
    melodie_kodex_id: str
    geltung: MelodieKodexGeltung
    typ: MelodieKodexTyp
    musik_weight: float
    musik_tier: int
    musik_ids: List[str]
    musik_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class MelodieKodex:
    kodex_id: str
    normen: List[MelodieKodexNorm]
    parent: RhythmusCharta


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        MelodieKodexGeltung.GESPERRT: 0.0,
        MelodieKodexGeltung.MELODISCH: 0.05,
        MelodieKodexGeltung.GRUNDLEGEND_MELODISCH: 0.1,
    })
    _TIER_DELTA.update({
        MelodieKodexGeltung.GESPERRT: 0,
        MelodieKodexGeltung.MELODISCH: 1,
        MelodieKodexGeltung.GRUNDLEGEND_MELODISCH: 2,
    })
    _TYP_MAP.update({
        MelodieKodexGeltung.GESPERRT: MelodieKodexTyp.ANALYTISCH,
        MelodieKodexGeltung.MELODISCH: MelodieKodexTyp.SYNTHETISCH,
        MelodieKodexGeltung.GRUNDLEGEND_MELODISCH: MelodieKodexTyp.HISTORISCH,
    })
    _PROZEDUR_MAP.update({
        MelodieKodexGeltung.GESPERRT: MelodieKodexProzedur.INITIALISIEREN,
        MelodieKodexGeltung.MELODISCH: MelodieKodexProzedur.AKTIVIEREN,
        MelodieKodexGeltung.GRUNDLEGEND_MELODISCH: MelodieKodexProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        MelodieKodexGeltung.GESPERRT: [MelodieKodexGeltung.GESPERRT],
        MelodieKodexGeltung.MELODISCH: [MelodieKodexGeltung.MELODISCH],
        MelodieKodexGeltung.GRUNDLEGEND_MELODISCH: [MelodieKodexGeltung.GRUNDLEGEND_MELODISCH],
    })


_init_map()


def build_melodie_kodex(*, kodex_id: str = "melodie-kodex") -> MelodieKodex:
    parent = build_rhythmus_charta(charta_id=f"{kodex_id}-parent")
    normen: List[MelodieKodexNorm] = []
    for g in MelodieKodexGeltung:
        normen.append(MelodieKodexNorm(
            melodie_kodex_id=f"{kodex_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            musik_weight=round(sum(n.musik_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            musik_tier=max(n.musik_tier for n in parent.normen) + _TIER_DELTA[g],
            musik_ids=[f"mk-{kodex_id}-{g.value}-001", f"mk-{kodex_id}-{g.value}-002"],
            musik_tags=["musikwissenschaft", "melodie", g.value],
        ))
    return MelodieKodex(kodex_id=kodex_id, normen=normen, parent=parent)
