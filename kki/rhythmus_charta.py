"""#623 RhythmusCharta — Rhythmik & Metrik (parent: HarmonikRegister)."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List
from .harmonik_register import HarmonikRegister, build_harmonik_register

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class RhythmusChartaGeltung(str, Enum):
    GESPERRT = "gesperrt"
    RHYTHMISCH = "rhythmisch"
    GRUNDLEGEND_RHYTHMISCH = "grundlegend-rhythmisch"


class RhythmusChartaTyp(str, Enum):
    ANALYTISCH = "analytisch"
    SYNTHETISCH = "synthetisch"
    HISTORISCH = "historisch"
    KOMPARATIV = "komparativ"


class RhythmusChartaProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class RhythmusChartaNorm:
    rhythmus_charta_id: str
    geltung: RhythmusChartaGeltung
    typ: RhythmusChartaTyp
    musik_weight: float
    musik_tier: int
    musik_ids: List[str]
    musik_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class RhythmusCharta:
    charta_id: str
    normen: List[RhythmusChartaNorm]
    parent: HarmonikRegister


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        RhythmusChartaGeltung.GESPERRT: 0.0,
        RhythmusChartaGeltung.RHYTHMISCH: 0.05,
        RhythmusChartaGeltung.GRUNDLEGEND_RHYTHMISCH: 0.1,
    })
    _TIER_DELTA.update({
        RhythmusChartaGeltung.GESPERRT: 0,
        RhythmusChartaGeltung.RHYTHMISCH: 1,
        RhythmusChartaGeltung.GRUNDLEGEND_RHYTHMISCH: 2,
    })
    _TYP_MAP.update({
        RhythmusChartaGeltung.GESPERRT: RhythmusChartaTyp.ANALYTISCH,
        RhythmusChartaGeltung.RHYTHMISCH: RhythmusChartaTyp.SYNTHETISCH,
        RhythmusChartaGeltung.GRUNDLEGEND_RHYTHMISCH: RhythmusChartaTyp.HISTORISCH,
    })
    _PROZEDUR_MAP.update({
        RhythmusChartaGeltung.GESPERRT: RhythmusChartaProzedur.INITIALISIEREN,
        RhythmusChartaGeltung.RHYTHMISCH: RhythmusChartaProzedur.AKTIVIEREN,
        RhythmusChartaGeltung.GRUNDLEGEND_RHYTHMISCH: RhythmusChartaProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        RhythmusChartaGeltung.GESPERRT: [RhythmusChartaGeltung.GESPERRT],
        RhythmusChartaGeltung.RHYTHMISCH: [RhythmusChartaGeltung.RHYTHMISCH],
        RhythmusChartaGeltung.GRUNDLEGEND_RHYTHMISCH: [RhythmusChartaGeltung.GRUNDLEGEND_RHYTHMISCH],
    })


_init_map()


def build_rhythmus_charta(*, charta_id: str = "rhythmus-charta") -> RhythmusCharta:
    parent = build_harmonik_register(register_id=f"{charta_id}-parent")
    normen: List[RhythmusChartaNorm] = []
    for g in RhythmusChartaGeltung:
        normen.append(RhythmusChartaNorm(
            rhythmus_charta_id=f"{charta_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            musik_weight=round(sum(n.musik_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            musik_tier=max(n.musik_tier for n in parent.normen) + _TIER_DELTA[g],
            musik_ids=[f"rc-{charta_id}-{g.value}-001", f"rc-{charta_id}-{g.value}-002"],
            musik_tags=["musikwissenschaft", "rhythmik", g.value],
        ))
    return RhythmusCharta(charta_id=charta_id, normen=normen, parent=parent)
