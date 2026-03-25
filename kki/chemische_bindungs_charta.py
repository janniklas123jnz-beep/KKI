"""#673 ChemischeBindungsCharta — Chemische Bindungen & Molekülstrukturen (parent: AtomstrukturRegister)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .atomstruktur_register import AtomstrukturRegister, build_atomstruktur_register

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class ChemischeBindungsChartaGeltung(str, Enum):
    GESPERRT = "gesperrt"
    CHEMISCH_GEBUNDEN = "chemisch-gebunden"
    GRUNDLEGEND_CHEMISCH_GEBUNDEN = "grundlegend-chemisch-gebunden"


class ChemischeBindungsChartaTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"
    KATALYSE = "katalyse"


class ChemischeBindungsChartaProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class ChemischeBindungsChartaNorm:
    chemische_bindungs_charta_id: str
    geltung: ChemischeBindungsChartaGeltung
    typ: ChemischeBindungsChartaTyp
    prozedur: ChemischeBindungsChartaProzedur
    chemie_weight: float
    chemie_tier: int
    chemie_ids: List[str]
    chemie_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class ChemischeBindungsCharta:
    charta_id: str
    normen: List[ChemischeBindungsChartaNorm]
    parent: AtomstrukturRegister


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        ChemischeBindungsChartaGeltung.GESPERRT: 0.0,
        ChemischeBindungsChartaGeltung.CHEMISCH_GEBUNDEN: 0.05,
        ChemischeBindungsChartaGeltung.GRUNDLEGEND_CHEMISCH_GEBUNDEN: 0.1,
    })
    _TIER_DELTA.update({
        ChemischeBindungsChartaGeltung.GESPERRT: 0,
        ChemischeBindungsChartaGeltung.CHEMISCH_GEBUNDEN: 1,
        ChemischeBindungsChartaGeltung.GRUNDLEGEND_CHEMISCH_GEBUNDEN: 2,
    })
    _TYP_MAP.update({
        ChemischeBindungsChartaGeltung.GESPERRT: ChemischeBindungsChartaTyp.BEOBACHTUNG,
        ChemischeBindungsChartaGeltung.CHEMISCH_GEBUNDEN: ChemischeBindungsChartaTyp.ANALYSE,
        ChemischeBindungsChartaGeltung.GRUNDLEGEND_CHEMISCH_GEBUNDEN: ChemischeBindungsChartaTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        ChemischeBindungsChartaGeltung.GESPERRT: ChemischeBindungsChartaProzedur.INITIALISIEREN,
        ChemischeBindungsChartaGeltung.CHEMISCH_GEBUNDEN: ChemischeBindungsChartaProzedur.AKTIVIEREN,
        ChemischeBindungsChartaGeltung.GRUNDLEGEND_CHEMISCH_GEBUNDEN: ChemischeBindungsChartaProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        ChemischeBindungsChartaGeltung.GESPERRT: [ChemischeBindungsChartaGeltung.GESPERRT],
        ChemischeBindungsChartaGeltung.CHEMISCH_GEBUNDEN: [ChemischeBindungsChartaGeltung.CHEMISCH_GEBUNDEN],
        ChemischeBindungsChartaGeltung.GRUNDLEGEND_CHEMISCH_GEBUNDEN: [ChemischeBindungsChartaGeltung.GRUNDLEGEND_CHEMISCH_GEBUNDEN],
    })


_init_map()


def build_chemische_bindungs_charta(*, charta_id: str = "chemische-bindungs-charta") -> ChemischeBindungsCharta:
    parent = build_atomstruktur_register(register_id=f"{charta_id}-parent")
    normen: List[ChemischeBindungsChartaNorm] = []
    for g in ChemischeBindungsChartaGeltung:
        normen.append(ChemischeBindungsChartaNorm(
            chemische_bindungs_charta_id=f"{charta_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            chemie_weight=round(sum(e.chemie_weight for e in parent.eintraege) * (1.0 + _WEIGHT_DELTA[g]), 4),
            chemie_tier=max(e.chemie_tier for e in parent.eintraege) + _TIER_DELTA[g],
            chemie_ids=[f"cbc-{charta_id}-{g.value}-001", f"cbc-{charta_id}-{g.value}-002"],
            chemie_tags=["chemie", "bindung", "charta", g.value],
        ))
    return ChemischeBindungsCharta(charta_id=charta_id, normen=normen, parent=parent)
