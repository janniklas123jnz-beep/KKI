"""#657 WissensaggregatSenat — Wissensaggregation & Synthese (parent: RecherchePakt)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .recherche_pakt import RecherchePakt, build_recherche_pakt

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class WissensaggregatSenatGeltung(str, Enum):
    GESPERRT = "gesperrt"
    WISSENSAGGREGIERT = "wissensaggregiert"
    GRUNDLEGEND_WISSENSAGGREGIERT = "grundlegend-wissensaggregiert"


class WissensaggregatSenatTyp(str, Enum):
    RECHERCHE = "recherche"
    VALIDIERUNG = "validierung"
    AGGREGATION = "aggregation"
    AUTONOME_ENTDECKUNG = "autonome-entdeckung"


class WissensaggregatSenatProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class WissensaggregatSenatNorm:
    senat_id: str
    geltung: WissensaggregatSenatGeltung
    typ: WissensaggregatSenatTyp
    prozedur: WissensaggregatSenatProzedur
    internet_weight: float
    internet_tier: int
    internet_ids: List[str]
    internet_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class WissensaggregatSenat:
    senat_id: str
    normen: List[WissensaggregatSenatNorm]
    parent: RecherchePakt


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        WissensaggregatSenatGeltung.GESPERRT: 0.0,
        WissensaggregatSenatGeltung.WISSENSAGGREGIERT: 0.05,
        WissensaggregatSenatGeltung.GRUNDLEGEND_WISSENSAGGREGIERT: 0.1,
    })
    _TIER_DELTA.update({
        WissensaggregatSenatGeltung.GESPERRT: 0,
        WissensaggregatSenatGeltung.WISSENSAGGREGIERT: 1,
        WissensaggregatSenatGeltung.GRUNDLEGEND_WISSENSAGGREGIERT: 2,
    })
    _TYP_MAP.update({
        WissensaggregatSenatGeltung.GESPERRT: WissensaggregatSenatTyp.RECHERCHE,
        WissensaggregatSenatGeltung.WISSENSAGGREGIERT: WissensaggregatSenatTyp.VALIDIERUNG,
        WissensaggregatSenatGeltung.GRUNDLEGEND_WISSENSAGGREGIERT: WissensaggregatSenatTyp.AGGREGATION,
    })
    _PROZEDUR_MAP.update({
        WissensaggregatSenatGeltung.GESPERRT: WissensaggregatSenatProzedur.INITIALISIEREN,
        WissensaggregatSenatGeltung.WISSENSAGGREGIERT: WissensaggregatSenatProzedur.AKTIVIEREN,
        WissensaggregatSenatGeltung.GRUNDLEGEND_WISSENSAGGREGIERT: WissensaggregatSenatProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        WissensaggregatSenatGeltung.GESPERRT: [WissensaggregatSenatGeltung.GESPERRT],
        WissensaggregatSenatGeltung.WISSENSAGGREGIERT: [WissensaggregatSenatGeltung.WISSENSAGGREGIERT],
        WissensaggregatSenatGeltung.GRUNDLEGEND_WISSENSAGGREGIERT: [WissensaggregatSenatGeltung.GRUNDLEGEND_WISSENSAGGREGIERT],
    })


_init_map()


def build_wissensaggregat_senat(*, senat_id: str = "wissensaggregat-senat") -> WissensaggregatSenat:
    parent = build_recherche_pakt(pakt_id=f"{senat_id}-parent")
    normen: List[WissensaggregatSenatNorm] = []
    for g in WissensaggregatSenatGeltung:
        normen.append(WissensaggregatSenatNorm(
            senat_id=f"{senat_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            internet_weight=round(sum(e.internet_weight for e in parent.eintraege) * (1.0 + _WEIGHT_DELTA[g]), 4),
            internet_tier=max(e.internet_tier for e in parent.eintraege) + _TIER_DELTA[g],
            internet_ids=[f"was-{senat_id}-{g.value}-001", f"was-{senat_id}-{g.value}-002"],
            internet_tags=["internet", "wissensaggregat", g.value],
        ))
    return WissensaggregatSenat(senat_id=senat_id, normen=normen, parent=parent)
