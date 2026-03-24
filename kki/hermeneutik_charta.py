"""#639 HermeneutikCharta — Hermeneutik & Interpretationstheorie (parent: LiteraturNormSatz)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .literatur_norm import LiteraturNormSatz, build_literatur_norm

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class HermeneutikChartaGeltung(str, Enum):
    GESPERRT = "gesperrt"
    HERMENEUTISCH_SOUVERAEN = "hermeneutisch-souveraen"
    GRUNDLEGEND_HERMENEUTISCH_SOUVERAEN = "grundlegend-hermeneutisch-souveraen"


class HermeneutikChartaTyp(str, Enum):
    ANALYTISCH = "analytisch"
    SYNTHETISCH = "synthetisch"
    HISTORISCH = "historisch"
    KOMPARATIV = "komparativ"


class HermeneutikChartaProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class HermeneutikChartaNorm:
    hermeneutik_charta_id: str
    geltung: HermeneutikChartaGeltung
    typ: HermeneutikChartaTyp
    prozedur: HermeneutikChartaProzedur
    literatur_weight: float
    literatur_tier: int
    literatur_ids: List[str]
    literatur_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class HermeneutikCharta:
    charta_id: str
    normen: List[HermeneutikChartaNorm]
    parent: LiteraturNormSatz


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        HermeneutikChartaGeltung.GESPERRT: 0.0,
        HermeneutikChartaGeltung.HERMENEUTISCH_SOUVERAEN: 0.05,
        HermeneutikChartaGeltung.GRUNDLEGEND_HERMENEUTISCH_SOUVERAEN: 0.1,
    })
    _TIER_DELTA.update({
        HermeneutikChartaGeltung.GESPERRT: 0,
        HermeneutikChartaGeltung.HERMENEUTISCH_SOUVERAEN: 1,
        HermeneutikChartaGeltung.GRUNDLEGEND_HERMENEUTISCH_SOUVERAEN: 2,
    })
    _TYP_MAP.update({
        HermeneutikChartaGeltung.GESPERRT: HermeneutikChartaTyp.ANALYTISCH,
        HermeneutikChartaGeltung.HERMENEUTISCH_SOUVERAEN: HermeneutikChartaTyp.SYNTHETISCH,
        HermeneutikChartaGeltung.GRUNDLEGEND_HERMENEUTISCH_SOUVERAEN: HermeneutikChartaTyp.HISTORISCH,
    })
    _PROZEDUR_MAP.update({
        HermeneutikChartaGeltung.GESPERRT: HermeneutikChartaProzedur.INITIALISIEREN,
        HermeneutikChartaGeltung.HERMENEUTISCH_SOUVERAEN: HermeneutikChartaProzedur.AKTIVIEREN,
        HermeneutikChartaGeltung.GRUNDLEGEND_HERMENEUTISCH_SOUVERAEN: HermeneutikChartaProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        HermeneutikChartaGeltung.GESPERRT: [HermeneutikChartaGeltung.GESPERRT],
        HermeneutikChartaGeltung.HERMENEUTISCH_SOUVERAEN: [HermeneutikChartaGeltung.HERMENEUTISCH_SOUVERAEN],
        HermeneutikChartaGeltung.GRUNDLEGEND_HERMENEUTISCH_SOUVERAEN: [HermeneutikChartaGeltung.GRUNDLEGEND_HERMENEUTISCH_SOUVERAEN],
    })


_init_map()


def build_hermeneutik_charta(*, charta_id: str = "hermeneutik-charta") -> HermeneutikCharta:
    parent = build_literatur_norm(norm_id=f"{charta_id}-parent")
    normen: List[HermeneutikChartaNorm] = []
    for g in HermeneutikChartaGeltung:
        normen.append(HermeneutikChartaNorm(
            hermeneutik_charta_id=f"{charta_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            literatur_weight=round(sum(e.literatur_norm_weight for e in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            literatur_tier=max(e.literatur_norm_tier for e in parent.normen) + _TIER_DELTA[g],
            literatur_ids=[f"hc-{charta_id}-{g.value}-001", f"hc-{charta_id}-{g.value}-002"],
            literatur_tags=["literaturwissenschaft", "hermeneutik", g.value],
        ))
    return HermeneutikCharta(charta_id=charta_id, normen=normen, parent=parent)
