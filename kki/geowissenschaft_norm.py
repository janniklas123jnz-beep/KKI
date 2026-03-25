"""#698 — GeowissenschaftNorm: Normative Geowissenschafts-Standards (*_norm)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.atmosphaere_senat import AtmosphaereSenat, build_atmosphaere_senat


class GeowissenschaftNormGeltung(str, Enum):
    GESPERRT = "gesperrt"
    GEO_NORMATIV = "geo-normativ"
    GRUNDLEGEND_GEO_NORMATIV = "grundlegend-geo-normativ"


class GeowissenschaftNormTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class GeowissenschaftNormProzedur(str, Enum):
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
class GeowissenschaftNormEintrag:
    norm_id: str
    geltung: GeowissenschaftNormGeltung
    typ: GeowissenschaftNormTyp
    prozedur: GeowissenschaftNormProzedur
    geo_norm_weight: float
    geo_norm_tier: int
    geo_norm_ids: List[str]
    geo_norm_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class GeowissenschaftNormSatz:
    norm_id: str
    normen: List[GeowissenschaftNormEintrag]
    parent: AtmosphaereSenat


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        "gesperrt": 0.0,
        "geo-normativ": 0.05,
        "grundlegend-geo-normativ": 0.1,
    })
    _TIER_DELTA.update({
        "gesperrt": 0,
        "geo-normativ": 1,
        "grundlegend-geo-normativ": 2,
    })
    _TYP_MAP.update({
        "gesperrt": GeowissenschaftNormTyp.BEOBACHTUNG,
        "geo-normativ": GeowissenschaftNormTyp.ANALYSE,
        "grundlegend-geo-normativ": GeowissenschaftNormTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        "gesperrt": GeowissenschaftNormProzedur.INITIALISIEREN,
        "geo-normativ": GeowissenschaftNormProzedur.AKTIVIEREN,
        "grundlegend-geo-normativ": GeowissenschaftNormProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        "atmosphaerisch-aktiv": GeowissenschaftNormGeltung.GEO_NORMATIV,
        "grundlegend-atmosphaerisch-aktiv": GeowissenschaftNormGeltung.GRUNDLEGEND_GEO_NORMATIV,
        "gesperrt": GeowissenschaftNormGeltung.GESPERRT,
    })
    _GELTUNG_KEY_MAP.update({
        GeowissenschaftNormGeltung.GESPERRT: "gesperrt",
        GeowissenschaftNormGeltung.GEO_NORMATIV: "geo-normativ",
        GeowissenschaftNormGeltung.GRUNDLEGEND_GEO_NORMATIV: "grundlegend-geo-normativ",
    })


_init_map()


def build_geowissenschaft_norm(*, norm_id: str = "geowissenschaft-norm") -> GeowissenschaftNormSatz:
    parent = build_atmosphaere_senat(senat_id=f"{norm_id}-parent")
    eintraege: List[GeowissenschaftNormEintrag] = []
    for g in GeowissenschaftNormGeltung:
        key = _GELTUNG_KEY_MAP[g]
        eintraege.append(GeowissenschaftNormEintrag(
            norm_id=f"{norm_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[key],
            prozedur=_PROZEDUR_MAP[key],
            geo_norm_weight=round(sum(n.geo_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[key]), 4),
            geo_norm_tier=max(n.geo_tier for n in parent.normen) + _TIER_DELTA[key],
            geo_norm_ids=[f"gn-{norm_id}-{g.value}-001", f"gn-{norm_id}-{g.value}-002"],
            geo_norm_tags=["geo", "norm", g.value],
        ))
    return GeowissenschaftNormSatz(norm_id=norm_id, normen=eintraege, parent=parent)
