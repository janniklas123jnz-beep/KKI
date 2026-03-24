"""#622 HarmonikRegister — Harmonik & Musiktheorie (parent: MusikFeld)."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List
from .musik_feld import MusikFeld, build_musik_feld

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class HarmonikRegisterGeltung(str, Enum):
    GESPERRT = "gesperrt"
    HARMONISCH = "harmonisch"
    GRUNDLEGEND_HARMONISCH = "grundlegend-harmonisch"


class HarmonikRegisterTyp(str, Enum):
    ANALYTISCH = "analytisch"
    SYNTHETISCH = "synthetisch"
    HISTORISCH = "historisch"
    KOMPARATIV = "komparativ"


class HarmonikRegisterProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class HarmonikRegisterNorm:
    harmonik_register_id: str
    geltung: HarmonikRegisterGeltung
    typ: HarmonikRegisterTyp
    musik_weight: float
    musik_tier: int
    musik_ids: List[str]
    musik_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class HarmonikRegister:
    register_id: str
    normen: List[HarmonikRegisterNorm]
    parent: MusikFeld


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        HarmonikRegisterGeltung.GESPERRT: 0.0,
        HarmonikRegisterGeltung.HARMONISCH: 0.05,
        HarmonikRegisterGeltung.GRUNDLEGEND_HARMONISCH: 0.1,
    })
    _TIER_DELTA.update({
        HarmonikRegisterGeltung.GESPERRT: 0,
        HarmonikRegisterGeltung.HARMONISCH: 1,
        HarmonikRegisterGeltung.GRUNDLEGEND_HARMONISCH: 2,
    })
    _TYP_MAP.update({
        HarmonikRegisterGeltung.GESPERRT: HarmonikRegisterTyp.ANALYTISCH,
        HarmonikRegisterGeltung.HARMONISCH: HarmonikRegisterTyp.SYNTHETISCH,
        HarmonikRegisterGeltung.GRUNDLEGEND_HARMONISCH: HarmonikRegisterTyp.HISTORISCH,
    })
    _PROZEDUR_MAP.update({
        HarmonikRegisterGeltung.GESPERRT: HarmonikRegisterProzedur.INITIALISIEREN,
        HarmonikRegisterGeltung.HARMONISCH: HarmonikRegisterProzedur.AKTIVIEREN,
        HarmonikRegisterGeltung.GRUNDLEGEND_HARMONISCH: HarmonikRegisterProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        HarmonikRegisterGeltung.GESPERRT: [HarmonikRegisterGeltung.GESPERRT],
        HarmonikRegisterGeltung.HARMONISCH: [HarmonikRegisterGeltung.HARMONISCH],
        HarmonikRegisterGeltung.GRUNDLEGEND_HARMONISCH: [HarmonikRegisterGeltung.GRUNDLEGEND_HARMONISCH],
    })


_init_map()


def build_harmonik_register(*, register_id: str = "harmonik-register") -> HarmonikRegister:
    parent = build_musik_feld(feld_id=f"{register_id}-parent")
    normen: List[HarmonikRegisterNorm] = []
    for g in HarmonikRegisterGeltung:
        normen.append(HarmonikRegisterNorm(
            harmonik_register_id=f"{register_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            musik_weight=round(sum(n.musik_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            musik_tier=max(n.musik_tier for n in parent.normen) + _TIER_DELTA[g],
            musik_ids=[f"hr-{register_id}-{g.value}-001", f"hr-{register_id}-{g.value}-002"],
            musik_tags=["musikwissenschaft", "harmonik", g.value],
        ))
    return HarmonikRegister(register_id=register_id, normen=normen, parent=parent)
