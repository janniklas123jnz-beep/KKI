"""#721 — WirtschaftFeld: Wirtschaft & Ökonomik Wurzel."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.informatik_verfassung import InformatikVerfassung, build_informatik_verfassung


class WirtschaftFeldGeltung(str, Enum):
    GESPERRT = "gesperrt"
    WIRTSCHAFTLICH = "wirtschaftlich"
    GRUNDLEGEND_WIRTSCHAFTLICH = "grundlegend-wirtschaftlich"


class WirtschaftFeldTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class WirtschaftFeldProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class WirtschaftFeldNorm:
    wirt_feld_id: str
    geltung: WirtschaftFeldGeltung
    typ: WirtschaftFeldTyp
    prozedur: WirtschaftFeldProzedur
    wirt_weight: float
    wirt_tier: int
    wirt_ids: List[str]
    wirt_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class WirtschaftFeld:
    feld_id: str
    normen: List[WirtschaftFeldNorm]
    parent: InformatikVerfassung


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        WirtschaftFeldGeltung.GESPERRT: 0.0,
        WirtschaftFeldGeltung.WIRTSCHAFTLICH: 0.05,
        WirtschaftFeldGeltung.GRUNDLEGEND_WIRTSCHAFTLICH: 0.1,
    })
    _TIER_DELTA.update({
        WirtschaftFeldGeltung.GESPERRT: 0,
        WirtschaftFeldGeltung.WIRTSCHAFTLICH: 1,
        WirtschaftFeldGeltung.GRUNDLEGEND_WIRTSCHAFTLICH: 2,
    })
    _TYP_MAP.update({
        WirtschaftFeldGeltung.GESPERRT: WirtschaftFeldTyp.BEOBACHTUNG,
        WirtschaftFeldGeltung.WIRTSCHAFTLICH: WirtschaftFeldTyp.ANALYSE,
        WirtschaftFeldGeltung.GRUNDLEGEND_WIRTSCHAFTLICH: WirtschaftFeldTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        WirtschaftFeldGeltung.GESPERRT: WirtschaftFeldProzedur.INITIALISIEREN,
        WirtschaftFeldGeltung.WIRTSCHAFTLICH: WirtschaftFeldProzedur.AKTIVIEREN,
        WirtschaftFeldGeltung.GRUNDLEGEND_WIRTSCHAFTLICH: WirtschaftFeldProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        WirtschaftFeldGeltung.GESPERRT: [WirtschaftFeldGeltung.GESPERRT],
        WirtschaftFeldGeltung.WIRTSCHAFTLICH: [WirtschaftFeldGeltung.WIRTSCHAFTLICH],
        WirtschaftFeldGeltung.GRUNDLEGEND_WIRTSCHAFTLICH: [WirtschaftFeldGeltung.GRUNDLEGEND_WIRTSCHAFTLICH],
    })


_init_map()


def build_wirtschaft_feld(*, feld_id: str = "wirtschaft-feld") -> WirtschaftFeld:
    parent = build_informatik_verfassung(verfassung_id=f"{feld_id}-parent")
    normen: List[WirtschaftFeldNorm] = []
    for g in WirtschaftFeldGeltung:
        normen.append(WirtschaftFeldNorm(
            wirt_feld_id=f"{feld_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            wirt_weight=round(sum(n.info_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            wirt_tier=max(n.info_tier for n in parent.normen) + _TIER_DELTA[g],
            wirt_ids=[f"wf-{feld_id}-{g.value}-001", f"wf-{feld_id}-{g.value}-002"],
            wirt_tags=["wirt", "wirtschaft", g.value],
        ))
    return WirtschaftFeld(feld_id=feld_id, normen=normen, parent=parent)
