"""#699 — PlanetologieCharta: Planetenentstehung, Exoplaneten & Sonnensystem."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.geowissenschaft_norm import GeowissenschaftNormSatz, build_geowissenschaft_norm


class PlanetologieChartaGeltung(str, Enum):
    GESPERRT = "gesperrt"
    PLANETOLOGISCH = "planetologisch"
    GRUNDLEGEND_PLANETOLOGISCH = "grundlegend-planetologisch"


class PlanetologieChartaTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class PlanetologieChartaProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class PlanetologieChartaNorm:
    norm_id: str
    geltung: PlanetologieChartaGeltung
    typ: PlanetologieChartaTyp
    prozedur: PlanetologieChartaProzedur
    geo_weight: float
    geo_tier: int
    geo_ids: List[str]
    geo_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class PlanetologieCharta:
    charta_id: str
    normen: List[PlanetologieChartaNorm]
    parent: GeowissenschaftNormSatz


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        PlanetologieChartaGeltung.GESPERRT: 0.0,
        PlanetologieChartaGeltung.PLANETOLOGISCH: 0.05,
        PlanetologieChartaGeltung.GRUNDLEGEND_PLANETOLOGISCH: 0.1,
    })
    _TIER_DELTA.update({
        PlanetologieChartaGeltung.GESPERRT: 0,
        PlanetologieChartaGeltung.PLANETOLOGISCH: 1,
        PlanetologieChartaGeltung.GRUNDLEGEND_PLANETOLOGISCH: 2,
    })
    _TYP_MAP.update({
        PlanetologieChartaGeltung.GESPERRT: PlanetologieChartaTyp.BEOBACHTUNG,
        PlanetologieChartaGeltung.PLANETOLOGISCH: PlanetologieChartaTyp.ANALYSE,
        PlanetologieChartaGeltung.GRUNDLEGEND_PLANETOLOGISCH: PlanetologieChartaTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        PlanetologieChartaGeltung.GESPERRT: PlanetologieChartaProzedur.INITIALISIEREN,
        PlanetologieChartaGeltung.PLANETOLOGISCH: PlanetologieChartaProzedur.AKTIVIEREN,
        PlanetologieChartaGeltung.GRUNDLEGEND_PLANETOLOGISCH: PlanetologieChartaProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        PlanetologieChartaGeltung.GESPERRT: [PlanetologieChartaGeltung.GESPERRT],
        PlanetologieChartaGeltung.PLANETOLOGISCH: [PlanetologieChartaGeltung.PLANETOLOGISCH],
        PlanetologieChartaGeltung.GRUNDLEGEND_PLANETOLOGISCH: [PlanetologieChartaGeltung.GRUNDLEGEND_PLANETOLOGISCH],
    })


_init_map()


def build_planetologie_charta(*, charta_id: str = "planetologie-charta") -> PlanetologieCharta:
    parent = build_geowissenschaft_norm(norm_id=f"{charta_id}-parent")
    normen: List[PlanetologieChartaNorm] = []
    for g in PlanetologieChartaGeltung:
        normen.append(PlanetologieChartaNorm(
            norm_id=f"{charta_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            geo_weight=round(sum(e.geo_norm_weight for e in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            geo_tier=max(e.geo_norm_tier for e in parent.normen) + _TIER_DELTA[g],
            geo_ids=[f"pc-{charta_id}-{g.value}-001", f"pc-{charta_id}-{g.value}-002"],
            geo_tags=["geo", "planetologie", g.value],
        ))
    return PlanetologieCharta(charta_id=charta_id, normen=normen, parent=parent)
