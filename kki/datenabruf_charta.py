"""#653 DatenAbrufCharta — Datenabruf & HTTP-Ressourcen (parent: WebSuchRegister)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .websuch_register import WebSuchRegister, build_websuch_register

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class DatenAbrufChartaGeltung(str, Enum):
    GESPERRT = "gesperrt"
    DATENABRUFEND = "datenabrufend"
    GRUNDLEGEND_DATENABRUFEND = "grundlegend-datenabrufend"


class DatenAbrufChartaTyp(str, Enum):
    RECHERCHE = "recherche"
    VALIDIERUNG = "validierung"
    AGGREGATION = "aggregation"
    AUTONOME_ENTDECKUNG = "autonome-entdeckung"


class DatenAbrufChartaProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class DatenAbrufChartaNorm:
    charta_id: str
    geltung: DatenAbrufChartaGeltung
    typ: DatenAbrufChartaTyp
    prozedur: DatenAbrufChartaProzedur
    internet_weight: float
    internet_tier: int
    internet_ids: List[str]
    internet_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class DatenAbrufCharta:
    charta_id: str
    normen: List[DatenAbrufChartaNorm]
    parent: WebSuchRegister


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        DatenAbrufChartaGeltung.GESPERRT: 0.0,
        DatenAbrufChartaGeltung.DATENABRUFEND: 0.05,
        DatenAbrufChartaGeltung.GRUNDLEGEND_DATENABRUFEND: 0.1,
    })
    _TIER_DELTA.update({
        DatenAbrufChartaGeltung.GESPERRT: 0,
        DatenAbrufChartaGeltung.DATENABRUFEND: 1,
        DatenAbrufChartaGeltung.GRUNDLEGEND_DATENABRUFEND: 2,
    })
    _TYP_MAP.update({
        DatenAbrufChartaGeltung.GESPERRT: DatenAbrufChartaTyp.RECHERCHE,
        DatenAbrufChartaGeltung.DATENABRUFEND: DatenAbrufChartaTyp.VALIDIERUNG,
        DatenAbrufChartaGeltung.GRUNDLEGEND_DATENABRUFEND: DatenAbrufChartaTyp.AGGREGATION,
    })
    _PROZEDUR_MAP.update({
        DatenAbrufChartaGeltung.GESPERRT: DatenAbrufChartaProzedur.INITIALISIEREN,
        DatenAbrufChartaGeltung.DATENABRUFEND: DatenAbrufChartaProzedur.AKTIVIEREN,
        DatenAbrufChartaGeltung.GRUNDLEGEND_DATENABRUFEND: DatenAbrufChartaProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        DatenAbrufChartaGeltung.GESPERRT: [DatenAbrufChartaGeltung.GESPERRT],
        DatenAbrufChartaGeltung.DATENABRUFEND: [DatenAbrufChartaGeltung.DATENABRUFEND],
        DatenAbrufChartaGeltung.GRUNDLEGEND_DATENABRUFEND: [DatenAbrufChartaGeltung.GRUNDLEGEND_DATENABRUFEND],
    })


_init_map()


def build_datenabruf_charta(*, charta_id: str = "datenabruf-charta") -> DatenAbrufCharta:
    parent = build_websuch_register(register_id=f"{charta_id}-parent")
    normen: List[DatenAbrufChartaNorm] = []
    for g in DatenAbrufChartaGeltung:
        normen.append(DatenAbrufChartaNorm(
            charta_id=f"{charta_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            internet_weight=round(sum(e.internet_weight for e in parent.eintraege) * (1.0 + _WEIGHT_DELTA[g]), 4),
            internet_tier=max(e.internet_tier for e in parent.eintraege) + _TIER_DELTA[g],
            internet_ids=[f"dac-{charta_id}-{g.value}-001", f"dac-{charta_id}-{g.value}-002"],
            internet_tags=["internet", "datenabruf", g.value],
        ))
    return DatenAbrufCharta(charta_id=charta_id, normen=normen, parent=parent)
