"""#632 NarrativRegister — Narratologie & Erzähltheorie (parent: LiteraturFeld)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .literatur_feld import LiteraturFeld, build_literatur_feld

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class NarrativRegisterGeltung(str, Enum):
    GESPERRT = "gesperrt"
    NARRATIV = "narrativ"
    GRUNDLEGEND_NARRATIV = "grundlegend-narrativ"


class NarrativRegisterTyp(str, Enum):
    ANALYTISCH = "analytisch"
    SYNTHETISCH = "synthetisch"
    HISTORISCH = "historisch"
    KOMPARATIV = "komparativ"


class NarrativRegisterProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class NarrativRegisterNorm:
    narrativ_register_id: str
    geltung: NarrativRegisterGeltung
    typ: NarrativRegisterTyp
    literatur_weight: float
    literatur_tier: int
    literatur_ids: List[str]
    literatur_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class NarrativRegister:
    register_id: str
    normen: List[NarrativRegisterNorm]
    parent: LiteraturFeld


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        NarrativRegisterGeltung.GESPERRT: 0.0,
        NarrativRegisterGeltung.NARRATIV: 0.05,
        NarrativRegisterGeltung.GRUNDLEGEND_NARRATIV: 0.1,
    })
    _TIER_DELTA.update({
        NarrativRegisterGeltung.GESPERRT: 0,
        NarrativRegisterGeltung.NARRATIV: 1,
        NarrativRegisterGeltung.GRUNDLEGEND_NARRATIV: 2,
    })
    _TYP_MAP.update({
        NarrativRegisterGeltung.GESPERRT: NarrativRegisterTyp.ANALYTISCH,
        NarrativRegisterGeltung.NARRATIV: NarrativRegisterTyp.SYNTHETISCH,
        NarrativRegisterGeltung.GRUNDLEGEND_NARRATIV: NarrativRegisterTyp.HISTORISCH,
    })
    _PROZEDUR_MAP.update({
        NarrativRegisterGeltung.GESPERRT: NarrativRegisterProzedur.INITIALISIEREN,
        NarrativRegisterGeltung.NARRATIV: NarrativRegisterProzedur.AKTIVIEREN,
        NarrativRegisterGeltung.GRUNDLEGEND_NARRATIV: NarrativRegisterProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        NarrativRegisterGeltung.GESPERRT: [NarrativRegisterGeltung.GESPERRT],
        NarrativRegisterGeltung.NARRATIV: [NarrativRegisterGeltung.NARRATIV],
        NarrativRegisterGeltung.GRUNDLEGEND_NARRATIV: [NarrativRegisterGeltung.GRUNDLEGEND_NARRATIV],
    })


_init_map()


def build_narrativ_register(*, register_id: str = "narrativ-register") -> NarrativRegister:
    parent = build_literatur_feld(feld_id=f"{register_id}-parent")
    normen: List[NarrativRegisterNorm] = []
    for g in NarrativRegisterGeltung:
        normen.append(NarrativRegisterNorm(
            narrativ_register_id=f"nr-{register_id}-{g.value}-001",
            geltung=g,
            typ=_TYP_MAP[g],
            literatur_weight=round(sum(n.literatur_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            literatur_tier=max(n.literatur_tier for n in parent.normen) + _TIER_DELTA[g],
            literatur_ids=[f"nr-{register_id}-{g.value}-001", f"nr-{register_id}-{g.value}-002"],
            literatur_tags=["literaturwissenschaft", "narratologie", g.value],
        ))
    return NarrativRegister(register_id=register_id, normen=normen, parent=parent)
