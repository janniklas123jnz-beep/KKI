"""#652 WebSuchRegister — Websuch & Anfrageverwaltung (parent: InternetFeld)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .internet_feld import InternetFeld, build_internet_feld

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class WebSuchRegisterGeltung(str, Enum):
    GESPERRT = "gesperrt"
    WEBSUCHEND = "websuchend"
    GRUNDLEGEND_WEBSUCHEND = "grundlegend-websuchend"


class WebSuchRegisterTyp(str, Enum):
    RECHERCHE = "recherche"
    VALIDIERUNG = "validierung"
    AGGREGATION = "aggregation"
    AUTONOME_ENTDECKUNG = "autonome-entdeckung"


class WebSuchRegisterProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class WebSuchRegisterEintrag:
    register_id: str
    geltung: WebSuchRegisterGeltung
    typ: WebSuchRegisterTyp
    prozedur: WebSuchRegisterProzedur
    internet_weight: float
    internet_tier: int
    internet_ids: List[str]
    internet_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class WebSuchRegister:
    register_id: str
    eintraege: List[WebSuchRegisterEintrag]
    parent: InternetFeld


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        WebSuchRegisterGeltung.GESPERRT: 0.0,
        WebSuchRegisterGeltung.WEBSUCHEND: 0.05,
        WebSuchRegisterGeltung.GRUNDLEGEND_WEBSUCHEND: 0.1,
    })
    _TIER_DELTA.update({
        WebSuchRegisterGeltung.GESPERRT: 0,
        WebSuchRegisterGeltung.WEBSUCHEND: 1,
        WebSuchRegisterGeltung.GRUNDLEGEND_WEBSUCHEND: 2,
    })
    _TYP_MAP.update({
        WebSuchRegisterGeltung.GESPERRT: WebSuchRegisterTyp.RECHERCHE,
        WebSuchRegisterGeltung.WEBSUCHEND: WebSuchRegisterTyp.VALIDIERUNG,
        WebSuchRegisterGeltung.GRUNDLEGEND_WEBSUCHEND: WebSuchRegisterTyp.AGGREGATION,
    })
    _PROZEDUR_MAP.update({
        WebSuchRegisterGeltung.GESPERRT: WebSuchRegisterProzedur.INITIALISIEREN,
        WebSuchRegisterGeltung.WEBSUCHEND: WebSuchRegisterProzedur.AKTIVIEREN,
        WebSuchRegisterGeltung.GRUNDLEGEND_WEBSUCHEND: WebSuchRegisterProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        WebSuchRegisterGeltung.GESPERRT: [WebSuchRegisterGeltung.GESPERRT],
        WebSuchRegisterGeltung.WEBSUCHEND: [WebSuchRegisterGeltung.WEBSUCHEND],
        WebSuchRegisterGeltung.GRUNDLEGEND_WEBSUCHEND: [WebSuchRegisterGeltung.GRUNDLEGEND_WEBSUCHEND],
    })


_init_map()


def build_websuch_register(*, register_id: str = "websuch-register") -> WebSuchRegister:
    parent = build_internet_feld(feld_id=f"{register_id}-parent")
    eintraege: List[WebSuchRegisterEintrag] = []
    for g in WebSuchRegisterGeltung:
        eintraege.append(WebSuchRegisterEintrag(
            register_id=f"{register_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            internet_weight=round(sum(n.internet_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            internet_tier=max(n.internet_tier for n in parent.normen) + _TIER_DELTA[g],
            internet_ids=[f"wsr-{register_id}-{g.value}-001", f"wsr-{register_id}-{g.value}-002"],
            internet_tags=["internet", "websuch", g.value],
        ))
    return WebSuchRegister(register_id=register_id, eintraege=eintraege, parent=parent)
