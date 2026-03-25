"""#703 — GenetikCharta: DNA, RNA, Erbgang & Mendel'sche Gesetze."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.zellbiologie_register import ZellbiologieRegister, build_zellbiologie_register


class GenetikChartaGeltung(str, Enum):
    GESPERRT = "gesperrt"
    GENETISCH_AKTIV = "genetisch-aktiv"
    GRUNDLEGEND_GENETISCH_AKTIV = "grundlegend-genetisch-aktiv"


class GenetikChartaTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class GenetikChartaProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class GenetikChartaNorm:
    charta_id: str
    geltung: GenetikChartaGeltung
    typ: GenetikChartaTyp
    prozedur: GenetikChartaProzedur
    bio_weight: float
    bio_tier: int
    bio_ids: List[str]
    bio_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class GenetikCharta:
    charta_id: str
    normen: List[GenetikChartaNorm]
    parent: ZellbiologieRegister


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        GenetikChartaGeltung.GESPERRT: 0.0,
        GenetikChartaGeltung.GENETISCH_AKTIV: 0.05,
        GenetikChartaGeltung.GRUNDLEGEND_GENETISCH_AKTIV: 0.1,
    })
    _TIER_DELTA.update({
        GenetikChartaGeltung.GESPERRT: 0,
        GenetikChartaGeltung.GENETISCH_AKTIV: 1,
        GenetikChartaGeltung.GRUNDLEGEND_GENETISCH_AKTIV: 2,
    })
    _TYP_MAP.update({
        GenetikChartaGeltung.GESPERRT: GenetikChartaTyp.BEOBACHTUNG,
        GenetikChartaGeltung.GENETISCH_AKTIV: GenetikChartaTyp.ANALYSE,
        GenetikChartaGeltung.GRUNDLEGEND_GENETISCH_AKTIV: GenetikChartaTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        GenetikChartaGeltung.GESPERRT: GenetikChartaProzedur.INITIALISIEREN,
        GenetikChartaGeltung.GENETISCH_AKTIV: GenetikChartaProzedur.AKTIVIEREN,
        GenetikChartaGeltung.GRUNDLEGEND_GENETISCH_AKTIV: GenetikChartaProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        GenetikChartaGeltung.GESPERRT: [GenetikChartaGeltung.GESPERRT],
        GenetikChartaGeltung.GENETISCH_AKTIV: [GenetikChartaGeltung.GENETISCH_AKTIV],
        GenetikChartaGeltung.GRUNDLEGEND_GENETISCH_AKTIV: [GenetikChartaGeltung.GRUNDLEGEND_GENETISCH_AKTIV],
    })


_init_map()


def build_genetik_charta(*, charta_id: str = "genetik-charta") -> GenetikCharta:
    parent = build_zellbiologie_register(register_id=f"{charta_id}-parent")
    normen: List[GenetikChartaNorm] = []
    for g in GenetikChartaGeltung:
        normen.append(GenetikChartaNorm(
            charta_id=f"{charta_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            bio_weight=round(sum(e.bio_weight for e in parent.eintraege) * (1.0 + _WEIGHT_DELTA[g]), 4),
            bio_tier=max(e.bio_tier for e in parent.eintraege) + _TIER_DELTA[g],
            bio_ids=[f"gc-{charta_id}-{g.value}-001", f"gc-{charta_id}-{g.value}-002"],
            bio_tags=["bio", "genetik", g.value],
        ))
    return GenetikCharta(charta_id=charta_id, normen=normen, parent=parent)
