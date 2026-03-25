"""#692 — MineralogieRegister: Minerale, Kristallchemie & Edelsteine."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.geowissenschaft_feld import GeowissenschaftFeld, build_geowissenschaft_feld


class MineralogieRegisterGeltung(str, Enum):
    GESPERRT = "gesperrt"
    MINERALOGISCH = "mineralogisch"
    GRUNDLEGEND_MINERALOGISCH = "grundlegend-mineralogisch"


class MineralogieRegisterTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class MineralogieRegisterProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class MineralogieRegisterEintrag:
    eintrag_id: str
    geltung: MineralogieRegisterGeltung
    typ: MineralogieRegisterTyp
    prozedur: MineralogieRegisterProzedur
    geo_weight: float
    geo_tier: int
    geo_ids: List[str]
    geo_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class MineralogieRegister:
    register_id: str
    eintraege: List[MineralogieRegisterEintrag]
    parent: GeowissenschaftFeld


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        MineralogieRegisterGeltung.GESPERRT: 0.0,
        MineralogieRegisterGeltung.MINERALOGISCH: 0.05,
        MineralogieRegisterGeltung.GRUNDLEGEND_MINERALOGISCH: 0.1,
    })
    _TIER_DELTA.update({
        MineralogieRegisterGeltung.GESPERRT: 0,
        MineralogieRegisterGeltung.MINERALOGISCH: 1,
        MineralogieRegisterGeltung.GRUNDLEGEND_MINERALOGISCH: 2,
    })
    _TYP_MAP.update({
        MineralogieRegisterGeltung.GESPERRT: MineralogieRegisterTyp.BEOBACHTUNG,
        MineralogieRegisterGeltung.MINERALOGISCH: MineralogieRegisterTyp.ANALYSE,
        MineralogieRegisterGeltung.GRUNDLEGEND_MINERALOGISCH: MineralogieRegisterTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        MineralogieRegisterGeltung.GESPERRT: MineralogieRegisterProzedur.INITIALISIEREN,
        MineralogieRegisterGeltung.MINERALOGISCH: MineralogieRegisterProzedur.AKTIVIEREN,
        MineralogieRegisterGeltung.GRUNDLEGEND_MINERALOGISCH: MineralogieRegisterProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        MineralogieRegisterGeltung.GESPERRT: [MineralogieRegisterGeltung.GESPERRT],
        MineralogieRegisterGeltung.MINERALOGISCH: [MineralogieRegisterGeltung.MINERALOGISCH],
        MineralogieRegisterGeltung.GRUNDLEGEND_MINERALOGISCH: [MineralogieRegisterGeltung.GRUNDLEGEND_MINERALOGISCH],
    })


_init_map()


def build_mineralogie_register(*, register_id: str = "mineralogie-register") -> MineralogieRegister:
    parent = build_geowissenschaft_feld(feld_id=f"{register_id}-parent")
    eintraege: List[MineralogieRegisterEintrag] = []
    for g in MineralogieRegisterGeltung:
        eintraege.append(MineralogieRegisterEintrag(
            eintrag_id=f"{register_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            geo_weight=round(sum(n.geo_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            geo_tier=max(n.geo_tier for n in parent.normen) + _TIER_DELTA[g],
            geo_ids=[f"mr-{register_id}-{g.value}-001", f"mr-{register_id}-{g.value}-002"],
            geo_tags=["geo", "mineralogie", g.value],
        ))
    return MineralogieRegister(register_id=register_id, eintraege=eintraege, parent=parent)
