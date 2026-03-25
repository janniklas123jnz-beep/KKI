"""#732 — MaschinenbauRegister: Mechanik, Konstruktion & Thermodynamik."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.ingenieur_feld import IngenieurFeld, build_ingenieur_feld


class MaschinenbauRegisterGeltung(str, Enum):
    GESPERRT = "gesperrt"
    MASCHINENBAULICH = "maschinenbaulich"
    GRUNDLEGEND_MASCHINENBAULICH = "grundlegend-maschinenbaulich"


class MaschinenbauRegisterTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class MaschinenbauRegisterProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class MaschinenbauRegisterEintrag:
    eintrag_id: str
    geltung: MaschinenbauRegisterGeltung
    typ: MaschinenbauRegisterTyp
    prozedur: MaschinenbauRegisterProzedur
    ing_weight: float
    ing_tier: int
    ing_ids: List[str]
    ing_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class MaschinenbauRegister:
    register_id: str
    eintraege: List[MaschinenbauRegisterEintrag]
    parent: IngenieurFeld


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        MaschinenbauRegisterGeltung.GESPERRT: 0.0,
        MaschinenbauRegisterGeltung.MASCHINENBAULICH: 0.05,
        MaschinenbauRegisterGeltung.GRUNDLEGEND_MASCHINENBAULICH: 0.1,
    })
    _TIER_DELTA.update({
        MaschinenbauRegisterGeltung.GESPERRT: 0,
        MaschinenbauRegisterGeltung.MASCHINENBAULICH: 1,
        MaschinenbauRegisterGeltung.GRUNDLEGEND_MASCHINENBAULICH: 2,
    })
    _TYP_MAP.update({
        MaschinenbauRegisterGeltung.GESPERRT: MaschinenbauRegisterTyp.BEOBACHTUNG,
        MaschinenbauRegisterGeltung.MASCHINENBAULICH: MaschinenbauRegisterTyp.ANALYSE,
        MaschinenbauRegisterGeltung.GRUNDLEGEND_MASCHINENBAULICH: MaschinenbauRegisterTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        MaschinenbauRegisterGeltung.GESPERRT: MaschinenbauRegisterProzedur.INITIALISIEREN,
        MaschinenbauRegisterGeltung.MASCHINENBAULICH: MaschinenbauRegisterProzedur.AKTIVIEREN,
        MaschinenbauRegisterGeltung.GRUNDLEGEND_MASCHINENBAULICH: MaschinenbauRegisterProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        MaschinenbauRegisterGeltung.GESPERRT: [MaschinenbauRegisterGeltung.GESPERRT],
        MaschinenbauRegisterGeltung.MASCHINENBAULICH: [MaschinenbauRegisterGeltung.MASCHINENBAULICH],
        MaschinenbauRegisterGeltung.GRUNDLEGEND_MASCHINENBAULICH: [MaschinenbauRegisterGeltung.GRUNDLEGEND_MASCHINENBAULICH],
    })


_init_map()


def build_maschinenbau_register(*, register_id: str = "maschinenbau-register") -> MaschinenbauRegister:
    parent = build_ingenieur_feld(feld_id=f"{register_id}-parent")
    eintraege: List[MaschinenbauRegisterEintrag] = []
    for g in MaschinenbauRegisterGeltung:
        eintraege.append(MaschinenbauRegisterEintrag(
            eintrag_id=f"{register_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            ing_weight=round(sum(n.ing_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            ing_tier=max(n.ing_tier for n in parent.normen) + _TIER_DELTA[g],
            ing_ids=[f"mr-{register_id}-{g.value}-001", f"mr-{register_id}-{g.value}-002"],
            ing_tags=["ing", "maschinenbau", g.value],
        ))
    return MaschinenbauRegister(register_id=register_id, eintraege=eintraege, parent=parent)
