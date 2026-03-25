"""#693 — GesteinsCharta: Magmatite, Sedimentite & Metamorphite."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.mineralogie_register import MineralogieRegister, build_mineralogie_register


class GesteinsChartaGeltung(str, Enum):
    GESPERRT = "gesperrt"
    GESTEINSFEST = "gesteinsfest"
    GRUNDLEGEND_GESTEINSFEST = "grundlegend-gesteinsfest"


class GesteinsChartaTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class GesteinsChartaProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class GesteinsChartaNorm:
    norm_id: str
    geltung: GesteinsChartaGeltung
    typ: GesteinsChartaTyp
    prozedur: GesteinsChartaProzedur
    geo_weight: float
    geo_tier: int
    geo_ids: List[str]
    geo_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class GesteinsCharta:
    charta_id: str
    normen: List[GesteinsChartaNorm]
    parent: MineralogieRegister


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        GesteinsChartaGeltung.GESPERRT: 0.0,
        GesteinsChartaGeltung.GESTEINSFEST: 0.05,
        GesteinsChartaGeltung.GRUNDLEGEND_GESTEINSFEST: 0.1,
    })
    _TIER_DELTA.update({
        GesteinsChartaGeltung.GESPERRT: 0,
        GesteinsChartaGeltung.GESTEINSFEST: 1,
        GesteinsChartaGeltung.GRUNDLEGEND_GESTEINSFEST: 2,
    })
    _TYP_MAP.update({
        GesteinsChartaGeltung.GESPERRT: GesteinsChartaTyp.BEOBACHTUNG,
        GesteinsChartaGeltung.GESTEINSFEST: GesteinsChartaTyp.ANALYSE,
        GesteinsChartaGeltung.GRUNDLEGEND_GESTEINSFEST: GesteinsChartaTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        GesteinsChartaGeltung.GESPERRT: GesteinsChartaProzedur.INITIALISIEREN,
        GesteinsChartaGeltung.GESTEINSFEST: GesteinsChartaProzedur.AKTIVIEREN,
        GesteinsChartaGeltung.GRUNDLEGEND_GESTEINSFEST: GesteinsChartaProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        GesteinsChartaGeltung.GESPERRT: [GesteinsChartaGeltung.GESPERRT],
        GesteinsChartaGeltung.GESTEINSFEST: [GesteinsChartaGeltung.GESTEINSFEST],
        GesteinsChartaGeltung.GRUNDLEGEND_GESTEINSFEST: [GesteinsChartaGeltung.GRUNDLEGEND_GESTEINSFEST],
    })


_init_map()


def build_gesteins_charta(*, charta_id: str = "gesteins-charta") -> GesteinsCharta:
    parent = build_mineralogie_register(register_id=f"{charta_id}-parent")
    normen: List[GesteinsChartaNorm] = []
    for g in GesteinsChartaGeltung:
        normen.append(GesteinsChartaNorm(
            norm_id=f"{charta_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            geo_weight=round(sum(e.geo_weight for e in parent.eintraege) * (1.0 + _WEIGHT_DELTA[g]), 4),
            geo_tier=max(e.geo_tier for e in parent.eintraege) + _TIER_DELTA[g],
            geo_ids=[f"gc-{charta_id}-{g.value}-001", f"gc-{charta_id}-{g.value}-002"],
            geo_tags=["geo", "gestein", g.value],
        ))
    return GesteinsCharta(charta_id=charta_id, normen=normen, parent=parent)
