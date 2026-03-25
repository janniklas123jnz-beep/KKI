"""#691 — GeowissenschaftFeld: Geowissenschaft & Planetologie Wurzel."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.materialwissenschaft_verfassung import MaterialwissenschaftVerfassung, build_materialwissenschaft_verfassung


class GeowissenschaftFeldGeltung(str, Enum):
    GESPERRT = "gesperrt"
    GEO_AKTIV = "geo-aktiv"
    GRUNDLEGEND_GEO_AKTIV = "grundlegend-geo-aktiv"


class GeowissenschaftFeldTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class GeowissenschaftFeldProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class GeowissenschaftFeldNorm:
    geo_feld_id: str
    geltung: GeowissenschaftFeldGeltung
    typ: GeowissenschaftFeldTyp
    prozedur: GeowissenschaftFeldProzedur
    geo_weight: float
    geo_tier: int
    geo_ids: List[str]
    geo_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class GeowissenschaftFeld:
    feld_id: str
    normen: List[GeowissenschaftFeldNorm]
    parent: MaterialwissenschaftVerfassung


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        GeowissenschaftFeldGeltung.GESPERRT: 0.0,
        GeowissenschaftFeldGeltung.GEO_AKTIV: 0.05,
        GeowissenschaftFeldGeltung.GRUNDLEGEND_GEO_AKTIV: 0.1,
    })
    _TIER_DELTA.update({
        GeowissenschaftFeldGeltung.GESPERRT: 0,
        GeowissenschaftFeldGeltung.GEO_AKTIV: 1,
        GeowissenschaftFeldGeltung.GRUNDLEGEND_GEO_AKTIV: 2,
    })
    _TYP_MAP.update({
        GeowissenschaftFeldGeltung.GESPERRT: GeowissenschaftFeldTyp.BEOBACHTUNG,
        GeowissenschaftFeldGeltung.GEO_AKTIV: GeowissenschaftFeldTyp.ANALYSE,
        GeowissenschaftFeldGeltung.GRUNDLEGEND_GEO_AKTIV: GeowissenschaftFeldTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        GeowissenschaftFeldGeltung.GESPERRT: GeowissenschaftFeldProzedur.INITIALISIEREN,
        GeowissenschaftFeldGeltung.GEO_AKTIV: GeowissenschaftFeldProzedur.AKTIVIEREN,
        GeowissenschaftFeldGeltung.GRUNDLEGEND_GEO_AKTIV: GeowissenschaftFeldProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        GeowissenschaftFeldGeltung.GESPERRT: [GeowissenschaftFeldGeltung.GESPERRT],
        GeowissenschaftFeldGeltung.GEO_AKTIV: [GeowissenschaftFeldGeltung.GEO_AKTIV],
        GeowissenschaftFeldGeltung.GRUNDLEGEND_GEO_AKTIV: [GeowissenschaftFeldGeltung.GRUNDLEGEND_GEO_AKTIV],
    })


_init_map()


def build_geowissenschaft_feld(*, feld_id: str = "geowissenschaft-feld") -> GeowissenschaftFeld:
    parent = build_materialwissenschaft_verfassung(verfassung_id=f"{feld_id}-parent")
    normen: List[GeowissenschaftFeldNorm] = []
    for g in GeowissenschaftFeldGeltung:
        normen.append(GeowissenschaftFeldNorm(
            geo_feld_id=f"{feld_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            geo_weight=round(sum(n.material_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            geo_tier=max(n.material_tier for n in parent.normen) + _TIER_DELTA[g],
            geo_ids=[f"gf-{feld_id}-{g.value}-001", f"gf-{feld_id}-{g.value}-002"],
            geo_tags=["geo", "feld", g.value],
        ))
    return GeowissenschaftFeld(feld_id=feld_id, normen=normen, parent=parent)
