"""#729 — DigitaleWirtschaftCharta: Plattformökonomie, Krypto & digitale Märkte."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.wirtschaft_norm import WirtschaftNormSatz, build_wirtschaft_norm


class DigitaleWirtschaftChartaGeltung(str, Enum):
    GESPERRT = "gesperrt"
    DIGITAL_WIRTSCHAFTLICH = "digital-wirtschaftlich"
    GRUNDLEGEND_DIGITAL_WIRTSCHAFTLICH = "grundlegend-digital-wirtschaftlich"


class DigitaleWirtschaftChartaTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class DigitaleWirtschaftChartaProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class DigitaleWirtschaftChartaNorm:
    charta_id: str
    geltung: DigitaleWirtschaftChartaGeltung
    typ: DigitaleWirtschaftChartaTyp
    prozedur: DigitaleWirtschaftChartaProzedur
    wirt_weight: float
    wirt_tier: int
    wirt_ids: List[str]
    wirt_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class DigitaleWirtschaftCharta:
    charta_id: str
    normen: List[DigitaleWirtschaftChartaNorm]
    parent: WirtschaftNormSatz


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        DigitaleWirtschaftChartaGeltung.GESPERRT: 0.0,
        DigitaleWirtschaftChartaGeltung.DIGITAL_WIRTSCHAFTLICH: 0.05,
        DigitaleWirtschaftChartaGeltung.GRUNDLEGEND_DIGITAL_WIRTSCHAFTLICH: 0.1,
    })
    _TIER_DELTA.update({
        DigitaleWirtschaftChartaGeltung.GESPERRT: 0,
        DigitaleWirtschaftChartaGeltung.DIGITAL_WIRTSCHAFTLICH: 1,
        DigitaleWirtschaftChartaGeltung.GRUNDLEGEND_DIGITAL_WIRTSCHAFTLICH: 2,
    })
    _TYP_MAP.update({
        DigitaleWirtschaftChartaGeltung.GESPERRT: DigitaleWirtschaftChartaTyp.BEOBACHTUNG,
        DigitaleWirtschaftChartaGeltung.DIGITAL_WIRTSCHAFTLICH: DigitaleWirtschaftChartaTyp.ANALYSE,
        DigitaleWirtschaftChartaGeltung.GRUNDLEGEND_DIGITAL_WIRTSCHAFTLICH: DigitaleWirtschaftChartaTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        DigitaleWirtschaftChartaGeltung.GESPERRT: DigitaleWirtschaftChartaProzedur.INITIALISIEREN,
        DigitaleWirtschaftChartaGeltung.DIGITAL_WIRTSCHAFTLICH: DigitaleWirtschaftChartaProzedur.AKTIVIEREN,
        DigitaleWirtschaftChartaGeltung.GRUNDLEGEND_DIGITAL_WIRTSCHAFTLICH: DigitaleWirtschaftChartaProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        DigitaleWirtschaftChartaGeltung.GESPERRT: [DigitaleWirtschaftChartaGeltung.GESPERRT],
        DigitaleWirtschaftChartaGeltung.DIGITAL_WIRTSCHAFTLICH: [DigitaleWirtschaftChartaGeltung.DIGITAL_WIRTSCHAFTLICH],
        DigitaleWirtschaftChartaGeltung.GRUNDLEGEND_DIGITAL_WIRTSCHAFTLICH: [DigitaleWirtschaftChartaGeltung.GRUNDLEGEND_DIGITAL_WIRTSCHAFTLICH],
    })


_init_map()


def build_digitale_wirtschaft_charta(*, charta_id: str = "digitale-wirtschaft-charta") -> DigitaleWirtschaftCharta:
    parent = build_wirtschaft_norm(norm_id=f"{charta_id}-parent")
    normen: List[DigitaleWirtschaftChartaNorm] = []
    for g in DigitaleWirtschaftChartaGeltung:
        normen.append(DigitaleWirtschaftChartaNorm(
            charta_id=f"{charta_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            wirt_weight=round(sum(e.wirt_norm_weight for e in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            wirt_tier=max(e.wirt_norm_tier for e in parent.normen) + _TIER_DELTA[g],
            wirt_ids=[f"dwc-{charta_id}-{g.value}-001", f"dwc-{charta_id}-{g.value}-002"],
            wirt_tags=["wirt", "digitale-wirtschaft", g.value],
        ))
    return DigitaleWirtschaftCharta(charta_id=charta_id, normen=normen, parent=parent)
