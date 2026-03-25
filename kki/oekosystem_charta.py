"""#663 OekosystemCharta — Ökosystem-Strukturen & Dynamik (parent: BiotopRegister)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .biotop_register import BiotopRegister, build_biotop_register

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class OekosystemChartaGeltung(str, Enum):
    GESPERRT = "gesperrt"
    OEKOSYSTEMISCH = "oekosystemisch"
    GRUNDLEGEND_OEKOSYSTEMISCH = "grundlegend-oekosystemisch"


class OekosystemChartaTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"
    SCHUTZ = "schutz"


class OekosystemChartaProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class OekosystemChartaNorm:
    oekosystem_charta_id: str
    geltung: OekosystemChartaGeltung
    typ: OekosystemChartaTyp
    prozedur: OekosystemChartaProzedur
    oekologie_weight: float
    oekologie_tier: int
    oekologie_ids: List[str]
    oekologie_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class OekosystemCharta:
    charta_id: str
    normen: List[OekosystemChartaNorm]
    parent: BiotopRegister


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        OekosystemChartaGeltung.GESPERRT: 0.0,
        OekosystemChartaGeltung.OEKOSYSTEMISCH: 0.05,
        OekosystemChartaGeltung.GRUNDLEGEND_OEKOSYSTEMISCH: 0.1,
    })
    _TIER_DELTA.update({
        OekosystemChartaGeltung.GESPERRT: 0,
        OekosystemChartaGeltung.OEKOSYSTEMISCH: 1,
        OekosystemChartaGeltung.GRUNDLEGEND_OEKOSYSTEMISCH: 2,
    })
    _TYP_MAP.update({
        OekosystemChartaGeltung.GESPERRT: OekosystemChartaTyp.BEOBACHTUNG,
        OekosystemChartaGeltung.OEKOSYSTEMISCH: OekosystemChartaTyp.ANALYSE,
        OekosystemChartaGeltung.GRUNDLEGEND_OEKOSYSTEMISCH: OekosystemChartaTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        OekosystemChartaGeltung.GESPERRT: OekosystemChartaProzedur.INITIALISIEREN,
        OekosystemChartaGeltung.OEKOSYSTEMISCH: OekosystemChartaProzedur.AKTIVIEREN,
        OekosystemChartaGeltung.GRUNDLEGEND_OEKOSYSTEMISCH: OekosystemChartaProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        OekosystemChartaGeltung.GESPERRT: [OekosystemChartaGeltung.GESPERRT],
        OekosystemChartaGeltung.OEKOSYSTEMISCH: [OekosystemChartaGeltung.OEKOSYSTEMISCH],
        OekosystemChartaGeltung.GRUNDLEGEND_OEKOSYSTEMISCH: [OekosystemChartaGeltung.GRUNDLEGEND_OEKOSYSTEMISCH],
    })


_init_map()


def build_oekosystem_charta(*, charta_id: str = "oekosystem-charta") -> OekosystemCharta:
    parent = build_biotop_register(register_id=f"{charta_id}-parent")
    normen: List[OekosystemChartaNorm] = []
    for g in OekosystemChartaGeltung:
        normen.append(OekosystemChartaNorm(
            oekosystem_charta_id=f"{charta_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            oekologie_weight=round(sum(e.oekologie_weight for e in parent.eintraege) * (1.0 + _WEIGHT_DELTA[g]), 4),
            oekologie_tier=max(e.oekologie_tier for e in parent.eintraege) + _TIER_DELTA[g],
            oekologie_ids=[f"oc-{charta_id}-{g.value}-001", f"oc-{charta_id}-{g.value}-002"],
            oekologie_tags=["oekologie", "oekosystem", "charta", g.value],
        ))
    return OekosystemCharta(charta_id=charta_id, normen=normen, parent=parent)
