"""#730 — WirtschaftVerfassung ⭐: Block-Krone Wirtschaft & Ökonomik."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.digitale_wirtschaft_charta import DigitaleWirtschaftCharta, build_digitale_wirtschaft_charta


class WirtschaftVerfassungGeltung(str, Enum):
    GESPERRT = "gesperrt"
    WIRT_SOUVERAEN = "wirt-souveraen"
    GRUNDLEGEND_WIRT_SOUVERAEN = "grundlegend-wirt-souveraen"


class WirtschaftVerfassungTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class WirtschaftVerfassungProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class WirtschaftVerfassungsNorm:
    wirt_verfassung_id: str
    geltung: WirtschaftVerfassungGeltung
    typ: WirtschaftVerfassungTyp
    prozedur: WirtschaftVerfassungProzedur
    wirt_weight: float
    wirt_tier: int
    wirt_ids: List[str]
    wirt_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class WirtschaftVerfassung:
    verfassung_id: str
    normen: List[WirtschaftVerfassungsNorm]
    parent: DigitaleWirtschaftCharta

    def aggregates_verfassung_signal(self) -> dict:
        return {
            "verfassung_id": self.verfassung_id,
            "total_weight": round(sum(n.wirt_weight for n in self.normen), 4),
            "norm_count": len(self.normen),
        }


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        WirtschaftVerfassungGeltung.GESPERRT: 0.0,
        WirtschaftVerfassungGeltung.WIRT_SOUVERAEN: 0.05,
        WirtschaftVerfassungGeltung.GRUNDLEGEND_WIRT_SOUVERAEN: 0.1,
    })
    _TIER_DELTA.update({
        WirtschaftVerfassungGeltung.GESPERRT: 0,
        WirtschaftVerfassungGeltung.WIRT_SOUVERAEN: 1,
        WirtschaftVerfassungGeltung.GRUNDLEGEND_WIRT_SOUVERAEN: 2,
    })
    _TYP_MAP.update({
        WirtschaftVerfassungGeltung.GESPERRT: WirtschaftVerfassungTyp.BEOBACHTUNG,
        WirtschaftVerfassungGeltung.WIRT_SOUVERAEN: WirtschaftVerfassungTyp.ANALYSE,
        WirtschaftVerfassungGeltung.GRUNDLEGEND_WIRT_SOUVERAEN: WirtschaftVerfassungTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        WirtschaftVerfassungGeltung.GESPERRT: WirtschaftVerfassungProzedur.INITIALISIEREN,
        WirtschaftVerfassungGeltung.WIRT_SOUVERAEN: WirtschaftVerfassungProzedur.AKTIVIEREN,
        WirtschaftVerfassungGeltung.GRUNDLEGEND_WIRT_SOUVERAEN: WirtschaftVerfassungProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        WirtschaftVerfassungGeltung.GESPERRT: [WirtschaftVerfassungGeltung.GESPERRT],
        WirtschaftVerfassungGeltung.WIRT_SOUVERAEN: [WirtschaftVerfassungGeltung.WIRT_SOUVERAEN],
        WirtschaftVerfassungGeltung.GRUNDLEGEND_WIRT_SOUVERAEN: [WirtschaftVerfassungGeltung.GRUNDLEGEND_WIRT_SOUVERAEN],
    })


_init_map()


def build_wirtschaft_verfassung(*, verfassung_id: str = "wirtschaft-verfassung") -> WirtschaftVerfassung:
    parent = build_digitale_wirtschaft_charta(charta_id=f"{verfassung_id}-parent")
    normen: List[WirtschaftVerfassungsNorm] = []
    for g in WirtschaftVerfassungGeltung:
        normen.append(WirtschaftVerfassungsNorm(
            wirt_verfassung_id=f"{verfassung_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            wirt_weight=round(sum(n.wirt_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            wirt_tier=max(n.wirt_tier for n in parent.normen) + _TIER_DELTA[g],
            wirt_ids=[f"wv-{verfassung_id}-{g.value}-001", f"wv-{verfassung_id}-{g.value}-002"],
            wirt_tags=["wirt", "wirtschaft", "verfassung", g.value],
        ))
    return WirtschaftVerfassung(verfassung_id=verfassung_id, normen=normen, parent=parent)
