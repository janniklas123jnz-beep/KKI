"""#640 LiteraturwissenschaftVerfassung — Block-Krone Literaturwissenschaft (parent: HermeneutikCharta)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .hermeneutik_charta import HermeneutikCharta, build_hermeneutik_charta

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class LiteraturwissenschaftVerfassungGeltung(str, Enum):
    GESPERRT = "gesperrt"
    LITERATURWISS_SOUVERAEN = "literaturwiss-souveraen"
    GRUNDLEGEND_LITERATURWISS_SOUVERAEN = "grundlegend-literaturwiss-souveraen"


class LiteraturwissenschaftVerfassungTyp(str, Enum):
    ANALYTISCH = "analytisch"
    SYNTHETISCH = "synthetisch"
    HISTORISCH = "historisch"
    KOMPARATIV = "komparativ"


class LiteraturwissenschaftVerfassungProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class LiteraturwissenschaftVerfassungsNorm:
    literaturwiss_verfassung_id: str
    geltung: LiteraturwissenschaftVerfassungGeltung
    typ: LiteraturwissenschaftVerfassungTyp
    prozedur: LiteraturwissenschaftVerfassungProzedur
    literatur_weight: float
    literatur_tier: int
    literatur_ids: List[str]
    literatur_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class LiteraturwissenschaftVerfassung:
    verfassung_id: str
    normen: List[LiteraturwissenschaftVerfassungsNorm]
    parent: HermeneutikCharta

    def aggregates_verfassung_signal(self) -> dict:
        return {
            "verfassung_id": self.verfassung_id,
            "total_weight": round(sum(n.literatur_weight for n in self.normen if n.canonical), 4),
            "norm_count": len(self.normen),
        }


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        LiteraturwissenschaftVerfassungGeltung.GESPERRT: 0.0,
        LiteraturwissenschaftVerfassungGeltung.LITERATURWISS_SOUVERAEN: 0.05,
        LiteraturwissenschaftVerfassungGeltung.GRUNDLEGEND_LITERATURWISS_SOUVERAEN: 0.1,
    })
    _TIER_DELTA.update({
        LiteraturwissenschaftVerfassungGeltung.GESPERRT: 0,
        LiteraturwissenschaftVerfassungGeltung.LITERATURWISS_SOUVERAEN: 1,
        LiteraturwissenschaftVerfassungGeltung.GRUNDLEGEND_LITERATURWISS_SOUVERAEN: 2,
    })
    _TYP_MAP.update({
        LiteraturwissenschaftVerfassungGeltung.GESPERRT: LiteraturwissenschaftVerfassungTyp.ANALYTISCH,
        LiteraturwissenschaftVerfassungGeltung.LITERATURWISS_SOUVERAEN: LiteraturwissenschaftVerfassungTyp.SYNTHETISCH,
        LiteraturwissenschaftVerfassungGeltung.GRUNDLEGEND_LITERATURWISS_SOUVERAEN: LiteraturwissenschaftVerfassungTyp.HISTORISCH,
    })
    _PROZEDUR_MAP.update({
        LiteraturwissenschaftVerfassungGeltung.GESPERRT: LiteraturwissenschaftVerfassungProzedur.INITIALISIEREN,
        LiteraturwissenschaftVerfassungGeltung.LITERATURWISS_SOUVERAEN: LiteraturwissenschaftVerfassungProzedur.AKTIVIEREN,
        LiteraturwissenschaftVerfassungGeltung.GRUNDLEGEND_LITERATURWISS_SOUVERAEN: LiteraturwissenschaftVerfassungProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        LiteraturwissenschaftVerfassungGeltung.GESPERRT: [LiteraturwissenschaftVerfassungGeltung.GESPERRT],
        LiteraturwissenschaftVerfassungGeltung.LITERATURWISS_SOUVERAEN: [LiteraturwissenschaftVerfassungGeltung.LITERATURWISS_SOUVERAEN],
        LiteraturwissenschaftVerfassungGeltung.GRUNDLEGEND_LITERATURWISS_SOUVERAEN: [LiteraturwissenschaftVerfassungGeltung.GRUNDLEGEND_LITERATURWISS_SOUVERAEN],
    })


_init_map()


def build_literaturwissenschaft_verfassung(*, verfassung_id: str = "literaturwiss-verfassung") -> LiteraturwissenschaftVerfassung:
    parent = build_hermeneutik_charta(charta_id=f"{verfassung_id}-parent")
    normen: List[LiteraturwissenschaftVerfassungsNorm] = []
    for g in LiteraturwissenschaftVerfassungGeltung:
        normen.append(LiteraturwissenschaftVerfassungsNorm(
            literaturwiss_verfassung_id=f"{verfassung_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            literatur_weight=round(sum(n.literatur_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            literatur_tier=max(n.literatur_tier for n in parent.normen) + _TIER_DELTA[g],
            literatur_ids=[f"lv-{verfassung_id}-{g.value}-001", f"lv-{verfassung_id}-{g.value}-002"],
            literatur_tags=["literaturwissenschaft", "verfassung", g.value],
        ))
    return LiteraturwissenschaftVerfassung(verfassung_id=verfassung_id, normen=normen, parent=parent)
