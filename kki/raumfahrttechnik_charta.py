"""#739 — RaumfahrttechnikCharta: Raketen, Satelliten & Weltraumtechnik."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.ingenieur_norm import IngenieurNormSatz, build_ingenieur_norm


class RaumfahrttechnikChartaGeltung(str, Enum):
    GESPERRT = "gesperrt"
    RAUMFAHRTTECHNISCH = "raumfahrttechnisch"
    GRUNDLEGEND_RAUMFAHRTTECHNISCH = "grundlegend-raumfahrttechnisch"


class RaumfahrttechnikChartaTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class RaumfahrttechnikChartaProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class RaumfahrttechnikChartaNorm:
    charta_id: str
    geltung: RaumfahrttechnikChartaGeltung
    typ: RaumfahrttechnikChartaTyp
    prozedur: RaumfahrttechnikChartaProzedur
    ing_weight: float
    ing_tier: int
    ing_ids: List[str]
    ing_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class RaumfahrttechnikCharta:
    charta_id: str
    normen: List[RaumfahrttechnikChartaNorm]
    parent: IngenieurNormSatz


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        RaumfahrttechnikChartaGeltung.GESPERRT: 0.0,
        RaumfahrttechnikChartaGeltung.RAUMFAHRTTECHNISCH: 0.05,
        RaumfahrttechnikChartaGeltung.GRUNDLEGEND_RAUMFAHRTTECHNISCH: 0.1,
    })
    _TIER_DELTA.update({
        RaumfahrttechnikChartaGeltung.GESPERRT: 0,
        RaumfahrttechnikChartaGeltung.RAUMFAHRTTECHNISCH: 1,
        RaumfahrttechnikChartaGeltung.GRUNDLEGEND_RAUMFAHRTTECHNISCH: 2,
    })
    _TYP_MAP.update({
        RaumfahrttechnikChartaGeltung.GESPERRT: RaumfahrttechnikChartaTyp.BEOBACHTUNG,
        RaumfahrttechnikChartaGeltung.RAUMFAHRTTECHNISCH: RaumfahrttechnikChartaTyp.ANALYSE,
        RaumfahrttechnikChartaGeltung.GRUNDLEGEND_RAUMFAHRTTECHNISCH: RaumfahrttechnikChartaTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        RaumfahrttechnikChartaGeltung.GESPERRT: RaumfahrttechnikChartaProzedur.INITIALISIEREN,
        RaumfahrttechnikChartaGeltung.RAUMFAHRTTECHNISCH: RaumfahrttechnikChartaProzedur.AKTIVIEREN,
        RaumfahrttechnikChartaGeltung.GRUNDLEGEND_RAUMFAHRTTECHNISCH: RaumfahrttechnikChartaProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        RaumfahrttechnikChartaGeltung.GESPERRT: [RaumfahrttechnikChartaGeltung.GESPERRT],
        RaumfahrttechnikChartaGeltung.RAUMFAHRTTECHNISCH: [RaumfahrttechnikChartaGeltung.RAUMFAHRTTECHNISCH],
        RaumfahrttechnikChartaGeltung.GRUNDLEGEND_RAUMFAHRTTECHNISCH: [RaumfahrttechnikChartaGeltung.GRUNDLEGEND_RAUMFAHRTTECHNISCH],
    })


_init_map()


def build_raumfahrttechnik_charta(*, charta_id: str = "raumfahrttechnik-charta") -> RaumfahrttechnikCharta:
    parent = build_ingenieur_norm(norm_id=f"{charta_id}-parent")
    normen: List[RaumfahrttechnikChartaNorm] = []
    for g in RaumfahrttechnikChartaGeltung:
        normen.append(RaumfahrttechnikChartaNorm(
            charta_id=f"{charta_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            ing_weight=round(sum(e.ing_norm_weight for e in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            ing_tier=max(e.ing_norm_tier for e in parent.normen) + _TIER_DELTA[g],
            ing_ids=[f"rc-{charta_id}-{g.value}-001", f"rc-{charta_id}-{g.value}-002"],
            ing_tags=["ing", "raumfahrttechnik", g.value],
        ))
    return RaumfahrttechnikCharta(charta_id=charta_id, normen=normen, parent=parent)
