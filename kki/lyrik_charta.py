"""#633 LyrikCharta — Lyrik & Poetik (parent: NarrativRegister)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .narrativ_register import NarrativRegister, build_narrativ_register

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class LyrikChartaGeltung(str, Enum):
    GESPERRT = "gesperrt"
    LYRISCH = "lyrisch"
    GRUNDLEGEND_LYRISCH = "grundlegend-lyrisch"


class LyrikChartaTyp(str, Enum):
    ANALYTISCH = "analytisch"
    SYNTHETISCH = "synthetisch"
    HISTORISCH = "historisch"
    KOMPARATIV = "komparativ"


class LyrikChartaProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class LyrikChartaNorm:
    lyrik_charta_id: str
    geltung: LyrikChartaGeltung
    typ: LyrikChartaTyp
    literatur_weight: float
    literatur_tier: int
    literatur_ids: List[str]
    literatur_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class LyrikCharta:
    charta_id: str
    normen: List[LyrikChartaNorm]
    parent: NarrativRegister


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        LyrikChartaGeltung.GESPERRT: 0.0,
        LyrikChartaGeltung.LYRISCH: 0.05,
        LyrikChartaGeltung.GRUNDLEGEND_LYRISCH: 0.1,
    })
    _TIER_DELTA.update({
        LyrikChartaGeltung.GESPERRT: 0,
        LyrikChartaGeltung.LYRISCH: 1,
        LyrikChartaGeltung.GRUNDLEGEND_LYRISCH: 2,
    })
    _TYP_MAP.update({
        LyrikChartaGeltung.GESPERRT: LyrikChartaTyp.ANALYTISCH,
        LyrikChartaGeltung.LYRISCH: LyrikChartaTyp.SYNTHETISCH,
        LyrikChartaGeltung.GRUNDLEGEND_LYRISCH: LyrikChartaTyp.HISTORISCH,
    })
    _PROZEDUR_MAP.update({
        LyrikChartaGeltung.GESPERRT: LyrikChartaProzedur.INITIALISIEREN,
        LyrikChartaGeltung.LYRISCH: LyrikChartaProzedur.AKTIVIEREN,
        LyrikChartaGeltung.GRUNDLEGEND_LYRISCH: LyrikChartaProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        LyrikChartaGeltung.GESPERRT: [LyrikChartaGeltung.GESPERRT],
        LyrikChartaGeltung.LYRISCH: [LyrikChartaGeltung.LYRISCH],
        LyrikChartaGeltung.GRUNDLEGEND_LYRISCH: [LyrikChartaGeltung.GRUNDLEGEND_LYRISCH],
    })


_init_map()


def build_lyrik_charta(*, charta_id: str = "lyrik-charta") -> LyrikCharta:
    parent = build_narrativ_register(register_id=f"{charta_id}-parent")
    normen: List[LyrikChartaNorm] = []
    for g in LyrikChartaGeltung:
        normen.append(LyrikChartaNorm(
            lyrik_charta_id=f"lc-{charta_id}-{g.value}-001",
            geltung=g,
            typ=_TYP_MAP[g],
            literatur_weight=round(sum(n.literatur_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            literatur_tier=max(n.literatur_tier for n in parent.normen) + _TIER_DELTA[g],
            literatur_ids=[f"lc-{charta_id}-{g.value}-001", f"lc-{charta_id}-{g.value}-002"],
            literatur_tags=["literaturwissenschaft", "lyrik", g.value],
        ))
    return LyrikCharta(charta_id=charta_id, normen=normen, parent=parent)
