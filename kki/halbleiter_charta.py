"""#683 — HalbleiterCharta: Leitfähigkeit, Dotierung & Bandstruktur."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.kristallstruktur_register import KristallstrukturRegister, build_kristallstruktur_register


class HalbleiterChartaGeltung(str, Enum):
    GESPERRT = "gesperrt"
    HALBLEITER_AKTIV = "halbleiter-aktiv"
    GRUNDLEGEND_HALBLEITER_AKTIV = "grundlegend-halbleiter-aktiv"


class HalbleiterChartaTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class HalbleiterChartaProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class HalbleiterChartaNorm:
    norm_id: str
    geltung: HalbleiterChartaGeltung
    typ: HalbleiterChartaTyp
    prozedur: HalbleiterChartaProzedur
    material_weight: float
    material_tier: int
    material_ids: List[str]
    material_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class HalbleiterCharta:
    charta_id: str
    normen: List[HalbleiterChartaNorm]
    parent: KristallstrukturRegister


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        HalbleiterChartaGeltung.GESPERRT: 0.0,
        HalbleiterChartaGeltung.HALBLEITER_AKTIV: 0.05,
        HalbleiterChartaGeltung.GRUNDLEGEND_HALBLEITER_AKTIV: 0.1,
    })
    _TIER_DELTA.update({
        HalbleiterChartaGeltung.GESPERRT: 0,
        HalbleiterChartaGeltung.HALBLEITER_AKTIV: 1,
        HalbleiterChartaGeltung.GRUNDLEGEND_HALBLEITER_AKTIV: 2,
    })
    _TYP_MAP.update({
        HalbleiterChartaGeltung.GESPERRT: HalbleiterChartaTyp.BEOBACHTUNG,
        HalbleiterChartaGeltung.HALBLEITER_AKTIV: HalbleiterChartaTyp.ANALYSE,
        HalbleiterChartaGeltung.GRUNDLEGEND_HALBLEITER_AKTIV: HalbleiterChartaTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        HalbleiterChartaGeltung.GESPERRT: HalbleiterChartaProzedur.INITIALISIEREN,
        HalbleiterChartaGeltung.HALBLEITER_AKTIV: HalbleiterChartaProzedur.AKTIVIEREN,
        HalbleiterChartaGeltung.GRUNDLEGEND_HALBLEITER_AKTIV: HalbleiterChartaProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        HalbleiterChartaGeltung.GESPERRT: [HalbleiterChartaGeltung.GESPERRT],
        HalbleiterChartaGeltung.HALBLEITER_AKTIV: [HalbleiterChartaGeltung.HALBLEITER_AKTIV],
        HalbleiterChartaGeltung.GRUNDLEGEND_HALBLEITER_AKTIV: [HalbleiterChartaGeltung.GRUNDLEGEND_HALBLEITER_AKTIV],
    })


_init_map()


def build_halbleiter_charta(*, charta_id: str = "halbleiter-charta") -> HalbleiterCharta:
    parent = build_kristallstruktur_register(register_id=f"{charta_id}-parent")
    normen: List[HalbleiterChartaNorm] = []
    for g in HalbleiterChartaGeltung:
        normen.append(HalbleiterChartaNorm(
            norm_id=f"{charta_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            material_weight=round(sum(e.material_weight for e in parent.eintraege) * (1.0 + _WEIGHT_DELTA[g]), 4),
            material_tier=max(e.material_tier for e in parent.eintraege) + _TIER_DELTA[g],
            material_ids=[f"hc-{charta_id}-{g.value}-001", f"hc-{charta_id}-{g.value}-002"],
            material_tags=["material", "halbleiter", g.value],
        ))
    return HalbleiterCharta(charta_id=charta_id, normen=normen, parent=parent)
