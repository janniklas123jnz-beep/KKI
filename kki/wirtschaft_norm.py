"""#728 — WirtschaftNorm: Normative Wirtschaftsstandards (*_norm)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.internationale_wirtschaft_senat import InternationaleWirtschaftSenat, build_internationale_wirtschaft_senat


class WirtschaftNormGeltung(str, Enum):
    GESPERRT = "gesperrt"
    WIRT_NORMATIV = "wirt-normativ"
    GRUNDLEGEND_WIRT_NORMATIV = "grundlegend-wirt-normativ"


class WirtschaftNormTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class WirtschaftNormProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}
_GELTUNG_KEY_MAP: dict = {}


@dataclass(frozen=True)
class WirtschaftNormEintrag:
    norm_id: str
    geltung: WirtschaftNormGeltung
    typ: WirtschaftNormTyp
    prozedur: WirtschaftNormProzedur
    wirt_norm_weight: float
    wirt_norm_tier: int
    wirt_norm_ids: List[str]
    wirt_norm_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class WirtschaftNormSatz:
    norm_id: str
    normen: List[WirtschaftNormEintrag]
    parent: InternationaleWirtschaftSenat


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        "gesperrt": 0.0,
        "wirt-normativ": 0.05,
        "grundlegend-wirt-normativ": 0.1,
    })
    _TIER_DELTA.update({
        "gesperrt": 0,
        "wirt-normativ": 1,
        "grundlegend-wirt-normativ": 2,
    })
    _TYP_MAP.update({
        "gesperrt": WirtschaftNormTyp.BEOBACHTUNG,
        "wirt-normativ": WirtschaftNormTyp.ANALYSE,
        "grundlegend-wirt-normativ": WirtschaftNormTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        "gesperrt": WirtschaftNormProzedur.INITIALISIEREN,
        "wirt-normativ": WirtschaftNormProzedur.AKTIVIEREN,
        "grundlegend-wirt-normativ": WirtschaftNormProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        "international-aktiv": WirtschaftNormGeltung.WIRT_NORMATIV,
        "grundlegend-international-aktiv": WirtschaftNormGeltung.GRUNDLEGEND_WIRT_NORMATIV,
        "gesperrt": WirtschaftNormGeltung.GESPERRT,
    })
    _GELTUNG_KEY_MAP.update({
        WirtschaftNormGeltung.GESPERRT: "gesperrt",
        WirtschaftNormGeltung.WIRT_NORMATIV: "wirt-normativ",
        WirtschaftNormGeltung.GRUNDLEGEND_WIRT_NORMATIV: "grundlegend-wirt-normativ",
    })


_init_map()


def build_wirtschaft_norm(*, norm_id: str = "wirtschaft-norm") -> WirtschaftNormSatz:
    parent = build_internationale_wirtschaft_senat(senat_id=f"{norm_id}-parent")
    eintraege: List[WirtschaftNormEintrag] = []
    for g in WirtschaftNormGeltung:
        key = _GELTUNG_KEY_MAP[g]
        eintraege.append(WirtschaftNormEintrag(
            norm_id=f"{norm_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[key],
            prozedur=_PROZEDUR_MAP[key],
            wirt_norm_weight=round(sum(n.wirt_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[key]), 4),
            wirt_norm_tier=max(n.wirt_tier for n in parent.normen) + _TIER_DELTA[key],
            wirt_norm_ids=[f"wn-{norm_id}-{g.value}-001", f"wn-{norm_id}-{g.value}-002"],
            wirt_norm_tags=["wirt", "norm", g.value],
        ))
    return WirtschaftNormSatz(norm_id=norm_id, normen=eintraege, parent=parent)
