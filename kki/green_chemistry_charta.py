"""#679 GreenChemistryCharta — Grüne Chemie & Nachhaltigkeit (parent: ChemieNormSatz)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .chemie_norm import ChemieNormSatz, build_chemie_norm

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class GreenChemistryChartaGeltung(str, Enum):
    GESPERRT = "gesperrt"
    GREEN_CHEMISCH = "green-chemisch"
    GRUNDLEGEND_GREEN_CHEMISCH = "grundlegend-green-chemisch"


class GreenChemistryChartaTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"
    KATALYSE = "katalyse"


class GreenChemistryChartaProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class GreenChemistryChartaNorm:
    green_chemistry_charta_id: str
    geltung: GreenChemistryChartaGeltung
    typ: GreenChemistryChartaTyp
    prozedur: GreenChemistryChartaProzedur
    chemie_weight: float
    chemie_tier: int
    chemie_ids: List[str]
    chemie_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class GreenChemistryCharta:
    charta_id: str
    normen: List[GreenChemistryChartaNorm]
    parent: ChemieNormSatz


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        GreenChemistryChartaGeltung.GESPERRT: 0.0,
        GreenChemistryChartaGeltung.GREEN_CHEMISCH: 0.05,
        GreenChemistryChartaGeltung.GRUNDLEGEND_GREEN_CHEMISCH: 0.1,
    })
    _TIER_DELTA.update({
        GreenChemistryChartaGeltung.GESPERRT: 0,
        GreenChemistryChartaGeltung.GREEN_CHEMISCH: 1,
        GreenChemistryChartaGeltung.GRUNDLEGEND_GREEN_CHEMISCH: 2,
    })
    _TYP_MAP.update({
        GreenChemistryChartaGeltung.GESPERRT: GreenChemistryChartaTyp.BEOBACHTUNG,
        GreenChemistryChartaGeltung.GREEN_CHEMISCH: GreenChemistryChartaTyp.ANALYSE,
        GreenChemistryChartaGeltung.GRUNDLEGEND_GREEN_CHEMISCH: GreenChemistryChartaTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        GreenChemistryChartaGeltung.GESPERRT: GreenChemistryChartaProzedur.INITIALISIEREN,
        GreenChemistryChartaGeltung.GREEN_CHEMISCH: GreenChemistryChartaProzedur.AKTIVIEREN,
        GreenChemistryChartaGeltung.GRUNDLEGEND_GREEN_CHEMISCH: GreenChemistryChartaProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        GreenChemistryChartaGeltung.GESPERRT: [GreenChemistryChartaGeltung.GESPERRT],
        GreenChemistryChartaGeltung.GREEN_CHEMISCH: [GreenChemistryChartaGeltung.GREEN_CHEMISCH],
        GreenChemistryChartaGeltung.GRUNDLEGEND_GREEN_CHEMISCH: [GreenChemistryChartaGeltung.GRUNDLEGEND_GREEN_CHEMISCH],
    })


_init_map()


def build_green_chemistry_charta(*, charta_id: str = "green-chemistry-charta") -> GreenChemistryCharta:
    parent = build_chemie_norm(norm_id=f"{charta_id}-parent")
    normen: List[GreenChemistryChartaNorm] = []
    for g in GreenChemistryChartaGeltung:
        normen.append(GreenChemistryChartaNorm(
            green_chemistry_charta_id=f"{charta_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            chemie_weight=round(sum(e.chemie_norm_weight for e in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            chemie_tier=max(e.chemie_norm_tier for e in parent.normen) + _TIER_DELTA[g],
            chemie_ids=[f"gcc-{charta_id}-{g.value}-001", f"gcc-{charta_id}-{g.value}-002"],
            chemie_tags=["chemie", "green", "charta", g.value],
        ))
    return GreenChemistryCharta(charta_id=charta_id, normen=normen, parent=parent)
