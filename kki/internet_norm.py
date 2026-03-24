"""#658 InternetNorm — normative Internetnutzung & Recherche-Standards (*_norm pattern, parent: WissensaggregatSenat)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .wissensaggregat_senat import WissensaggregatSenat, build_wissensaggregat_senat

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class InternetNormTyp(str, Enum):
    RECHERCHE = "recherche"
    VALIDIERUNG = "validierung"
    AGGREGATION = "aggregation"
    AUTONOME_ENTDECKUNG = "autonome-entdeckung"


class InternetNormProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


class InternetNormGeltung(str, Enum):
    GESPERRT = "gesperrt"
    INTERNET_NORMATIV = "internet-normativ"
    GRUNDLEGEND_INTERNET_NORMATIV = "grundlegend-internet-normativ"


@dataclass(frozen=True)
class InternetNormEintrag:
    norm_id: str
    geltung: InternetNormGeltung
    typ: InternetNormTyp
    prozedur: InternetNormProzedur
    internet_norm_weight: float
    internet_norm_tier: int
    internet_norm_ids: List[str]
    internet_norm_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class InternetNormSatz:
    norm_id: str
    normen: List[InternetNormEintrag]
    parent: WissensaggregatSenat


_GELTUNG_KEY_MAP: dict = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        "gesperrt": 0.0,
        "internet-normativ": 0.05,
        "grundlegend-internet-normativ": 0.1,
    })
    _TIER_DELTA.update({
        "gesperrt": 0,
        "internet-normativ": 1,
        "grundlegend-internet-normativ": 2,
    })
    _TYP_MAP.update({
        "gesperrt": InternetNormTyp.RECHERCHE,
        "internet-normativ": InternetNormTyp.VALIDIERUNG,
        "grundlegend-internet-normativ": InternetNormTyp.AGGREGATION,
    })
    _PROZEDUR_MAP.update({
        "gesperrt": InternetNormProzedur.INITIALISIEREN,
        "internet-normativ": InternetNormProzedur.AKTIVIEREN,
        "grundlegend-internet-normativ": InternetNormProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        "wissensaggregiert": InternetNormGeltung.INTERNET_NORMATIV,
        "grundlegend-wissensaggregiert": InternetNormGeltung.GRUNDLEGEND_INTERNET_NORMATIV,
        "gesperrt": InternetNormGeltung.GESPERRT,
    })
    _GELTUNG_KEY_MAP.update({
        InternetNormGeltung.GESPERRT: "gesperrt",
        InternetNormGeltung.INTERNET_NORMATIV: "internet-normativ",
        InternetNormGeltung.GRUNDLEGEND_INTERNET_NORMATIV: "grundlegend-internet-normativ",
    })


_init_map()


def build_internet_norm(*, norm_id: str = "internet-norm") -> InternetNormSatz:
    parent = build_wissensaggregat_senat(senat_id=f"{norm_id}-parent")
    eintraege: List[InternetNormEintrag] = []
    for g in InternetNormGeltung:
        key = _GELTUNG_KEY_MAP[g]
        eintraege.append(InternetNormEintrag(
            norm_id=f"{norm_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[key],
            prozedur=_PROZEDUR_MAP[key],
            internet_norm_weight=round(sum(n.internet_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[key]), 4),
            internet_norm_tier=max(n.internet_tier for n in parent.normen) + _TIER_DELTA[key],
            internet_norm_ids=[f"in-{norm_id}-{g.value}-001", f"in-{norm_id}-{g.value}-002"],
            internet_norm_tags=["internet", "norm", g.value],
        ))
    return InternetNormSatz(norm_id=norm_id, normen=eintraege, parent=parent)
