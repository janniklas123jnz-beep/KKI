"""#733 — ElektrotechnikCharta: Schaltkreise, Signale & Energietechnik."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.maschinenbau_register import MaschinenbauRegister, build_maschinenbau_register


class ElektrotechnikChartaGeltung(str, Enum):
    GESPERRT = "gesperrt"
    ELEKTROTECHNISCH = "elektrotechnisch"
    GRUNDLEGEND_ELEKTROTECHNISCH = "grundlegend-elektrotechnisch"


class ElektrotechnikChartaTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class ElektrotechnikChartaProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class ElektrotechnikChartaNorm:
    charta_id: str
    geltung: ElektrotechnikChartaGeltung
    typ: ElektrotechnikChartaTyp
    prozedur: ElektrotechnikChartaProzedur
    ing_weight: float
    ing_tier: int
    ing_ids: List[str]
    ing_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class ElektrotechnikCharta:
    charta_id: str
    normen: List[ElektrotechnikChartaNorm]
    parent: MaschinenbauRegister


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        ElektrotechnikChartaGeltung.GESPERRT: 0.0,
        ElektrotechnikChartaGeltung.ELEKTROTECHNISCH: 0.05,
        ElektrotechnikChartaGeltung.GRUNDLEGEND_ELEKTROTECHNISCH: 0.1,
    })
    _TIER_DELTA.update({
        ElektrotechnikChartaGeltung.GESPERRT: 0,
        ElektrotechnikChartaGeltung.ELEKTROTECHNISCH: 1,
        ElektrotechnikChartaGeltung.GRUNDLEGEND_ELEKTROTECHNISCH: 2,
    })
    _TYP_MAP.update({
        ElektrotechnikChartaGeltung.GESPERRT: ElektrotechnikChartaTyp.BEOBACHTUNG,
        ElektrotechnikChartaGeltung.ELEKTROTECHNISCH: ElektrotechnikChartaTyp.ANALYSE,
        ElektrotechnikChartaGeltung.GRUNDLEGEND_ELEKTROTECHNISCH: ElektrotechnikChartaTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        ElektrotechnikChartaGeltung.GESPERRT: ElektrotechnikChartaProzedur.INITIALISIEREN,
        ElektrotechnikChartaGeltung.ELEKTROTECHNISCH: ElektrotechnikChartaProzedur.AKTIVIEREN,
        ElektrotechnikChartaGeltung.GRUNDLEGEND_ELEKTROTECHNISCH: ElektrotechnikChartaProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        ElektrotechnikChartaGeltung.GESPERRT: [ElektrotechnikChartaGeltung.GESPERRT],
        ElektrotechnikChartaGeltung.ELEKTROTECHNISCH: [ElektrotechnikChartaGeltung.ELEKTROTECHNISCH],
        ElektrotechnikChartaGeltung.GRUNDLEGEND_ELEKTROTECHNISCH: [ElektrotechnikChartaGeltung.GRUNDLEGEND_ELEKTROTECHNISCH],
    })


_init_map()


def build_elektrotechnik_charta(*, charta_id: str = "elektrotechnik-charta") -> ElektrotechnikCharta:
    parent = build_maschinenbau_register(register_id=f"{charta_id}-parent")
    normen: List[ElektrotechnikChartaNorm] = []
    for g in ElektrotechnikChartaGeltung:
        normen.append(ElektrotechnikChartaNorm(
            charta_id=f"{charta_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            ing_weight=round(sum(e.ing_weight for e in parent.eintraege) * (1.0 + _WEIGHT_DELTA[g]), 4),
            ing_tier=max(e.ing_tier for e in parent.eintraege) + _TIER_DELTA[g],
            ing_ids=[f"ec-{charta_id}-{g.value}-001", f"ec-{charta_id}-{g.value}-002"],
            ing_tags=["ing", "elektrotechnik", g.value],
        ))
    return ElektrotechnikCharta(charta_id=charta_id, normen=normen, parent=parent)
