"""#700 — GeowissenschaftVerfassung ⭐: Block-Krone & Abschluss der 600er-Reihe."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.planetologie_charta import PlanetologieCharta, build_planetologie_charta


class GeowissenschaftVerfassungGeltung(str, Enum):
    GESPERRT = "gesperrt"
    GEOWISS_SOUVERAEN = "geowiss-souveraen"
    GRUNDLEGEND_GEOWISS_SOUVERAEN = "grundlegend-geowiss-souveraen"


class GeowissenschaftVerfassungTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class GeowissenschaftVerfassungProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class GeowissenschaftVerfassungsNorm:
    geowiss_verfassung_id: str
    geltung: GeowissenschaftVerfassungGeltung
    typ: GeowissenschaftVerfassungTyp
    prozedur: GeowissenschaftVerfassungProzedur
    geo_weight: float
    geo_tier: int
    geo_ids: List[str]
    geo_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class GeowissenschaftVerfassung:
    verfassung_id: str
    normen: List[GeowissenschaftVerfassungsNorm]
    parent: PlanetologieCharta

    def aggregates_verfassung_signal(self) -> dict:
        return {
            "verfassung_id": self.verfassung_id,
            "total_weight": round(sum(n.geo_weight for n in self.normen), 4),
            "norm_count": len(self.normen),
        }


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        GeowissenschaftVerfassungGeltung.GESPERRT: 0.0,
        GeowissenschaftVerfassungGeltung.GEOWISS_SOUVERAEN: 0.05,
        GeowissenschaftVerfassungGeltung.GRUNDLEGEND_GEOWISS_SOUVERAEN: 0.1,
    })
    _TIER_DELTA.update({
        GeowissenschaftVerfassungGeltung.GESPERRT: 0,
        GeowissenschaftVerfassungGeltung.GEOWISS_SOUVERAEN: 1,
        GeowissenschaftVerfassungGeltung.GRUNDLEGEND_GEOWISS_SOUVERAEN: 2,
    })
    _TYP_MAP.update({
        GeowissenschaftVerfassungGeltung.GESPERRT: GeowissenschaftVerfassungTyp.BEOBACHTUNG,
        GeowissenschaftVerfassungGeltung.GEOWISS_SOUVERAEN: GeowissenschaftVerfassungTyp.ANALYSE,
        GeowissenschaftVerfassungGeltung.GRUNDLEGEND_GEOWISS_SOUVERAEN: GeowissenschaftVerfassungTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        GeowissenschaftVerfassungGeltung.GESPERRT: GeowissenschaftVerfassungProzedur.INITIALISIEREN,
        GeowissenschaftVerfassungGeltung.GEOWISS_SOUVERAEN: GeowissenschaftVerfassungProzedur.AKTIVIEREN,
        GeowissenschaftVerfassungGeltung.GRUNDLEGEND_GEOWISS_SOUVERAEN: GeowissenschaftVerfassungProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        GeowissenschaftVerfassungGeltung.GESPERRT: [GeowissenschaftVerfassungGeltung.GESPERRT],
        GeowissenschaftVerfassungGeltung.GEOWISS_SOUVERAEN: [GeowissenschaftVerfassungGeltung.GEOWISS_SOUVERAEN],
        GeowissenschaftVerfassungGeltung.GRUNDLEGEND_GEOWISS_SOUVERAEN: [GeowissenschaftVerfassungGeltung.GRUNDLEGEND_GEOWISS_SOUVERAEN],
    })


_init_map()


def build_geowissenschaft_verfassung(*, verfassung_id: str = "geowissenschaft-verfassung") -> GeowissenschaftVerfassung:
    parent = build_planetologie_charta(charta_id=f"{verfassung_id}-parent")
    normen: List[GeowissenschaftVerfassungsNorm] = []
    for g in GeowissenschaftVerfassungGeltung:
        normen.append(GeowissenschaftVerfassungsNorm(
            geowiss_verfassung_id=f"{verfassung_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            geo_weight=round(sum(n.geo_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            geo_tier=max(n.geo_tier for n in parent.normen) + _TIER_DELTA[g],
            geo_ids=[f"gv-{verfassung_id}-{g.value}-001", f"gv-{verfassung_id}-{g.value}-002"],
            geo_tags=["geo", "geowissenschaft", "verfassung", g.value],
        ))
    return GeowissenschaftVerfassung(verfassung_id=verfassung_id, normen=normen, parent=parent)
