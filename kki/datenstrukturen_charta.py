"""#713 — DatenstrukturenCharta: Listen, Bäume, Graphen & Hash-Tabellen."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.algorithmik_register import AlgorithmikRegister, build_algorithmik_register


class DatenstrukturenChartaGeltung(str, Enum):
    GESPERRT = "gesperrt"
    DATENSTRUKTURELL = "datenstrukturell"
    GRUNDLEGEND_DATENSTRUKTURELL = "grundlegend-datenstrukturell"


class DatenstrukturenChartaTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class DatenstrukturenChartaProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class DatenstrukturenChartaNorm:
    charta_id: str
    geltung: DatenstrukturenChartaGeltung
    typ: DatenstrukturenChartaTyp
    prozedur: DatenstrukturenChartaProzedur
    info_weight: float
    info_tier: int
    info_ids: List[str]
    info_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class DatenstrukturenCharta:
    charta_id: str
    normen: List[DatenstrukturenChartaNorm]
    parent: AlgorithmikRegister


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        DatenstrukturenChartaGeltung.GESPERRT: 0.0,
        DatenstrukturenChartaGeltung.DATENSTRUKTURELL: 0.05,
        DatenstrukturenChartaGeltung.GRUNDLEGEND_DATENSTRUKTURELL: 0.1,
    })
    _TIER_DELTA.update({
        DatenstrukturenChartaGeltung.GESPERRT: 0,
        DatenstrukturenChartaGeltung.DATENSTRUKTURELL: 1,
        DatenstrukturenChartaGeltung.GRUNDLEGEND_DATENSTRUKTURELL: 2,
    })
    _TYP_MAP.update({
        DatenstrukturenChartaGeltung.GESPERRT: DatenstrukturenChartaTyp.BEOBACHTUNG,
        DatenstrukturenChartaGeltung.DATENSTRUKTURELL: DatenstrukturenChartaTyp.ANALYSE,
        DatenstrukturenChartaGeltung.GRUNDLEGEND_DATENSTRUKTURELL: DatenstrukturenChartaTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        DatenstrukturenChartaGeltung.GESPERRT: DatenstrukturenChartaProzedur.INITIALISIEREN,
        DatenstrukturenChartaGeltung.DATENSTRUKTURELL: DatenstrukturenChartaProzedur.AKTIVIEREN,
        DatenstrukturenChartaGeltung.GRUNDLEGEND_DATENSTRUKTURELL: DatenstrukturenChartaProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        DatenstrukturenChartaGeltung.GESPERRT: [DatenstrukturenChartaGeltung.GESPERRT],
        DatenstrukturenChartaGeltung.DATENSTRUKTURELL: [DatenstrukturenChartaGeltung.DATENSTRUKTURELL],
        DatenstrukturenChartaGeltung.GRUNDLEGEND_DATENSTRUKTURELL: [DatenstrukturenChartaGeltung.GRUNDLEGEND_DATENSTRUKTURELL],
    })


_init_map()


def build_datenstrukturen_charta(*, charta_id: str = "datenstrukturen-charta") -> DatenstrukturenCharta:
    parent = build_algorithmik_register(register_id=f"{charta_id}-parent")
    normen: List[DatenstrukturenChartaNorm] = []
    for g in DatenstrukturenChartaGeltung:
        normen.append(DatenstrukturenChartaNorm(
            charta_id=f"{charta_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            info_weight=round(sum(e.info_weight for e in parent.eintraege) * (1.0 + _WEIGHT_DELTA[g]), 4),
            info_tier=max(e.info_tier for e in parent.eintraege) + _TIER_DELTA[g],
            info_ids=[f"ds-{charta_id}-{g.value}-001", f"ds-{charta_id}-{g.value}-002"],
            info_tags=["info", "datenstrukturen", g.value],
        ))
    return DatenstrukturenCharta(charta_id=charta_id, normen=normen, parent=parent)
