"""#712 — AlgorithmikRegister: Sortieren, Suchen & Graphalgorithmen."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.informatik_feld import InformatikFeld, build_informatik_feld


class AlgorithmikRegisterGeltung(str, Enum):
    GESPERRT = "gesperrt"
    ALGORITHMISCH = "algorithmisch"
    GRUNDLEGEND_ALGORITHMISCH = "grundlegend-algorithmisch"


class AlgorithmikRegisterTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class AlgorithmikRegisterProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class AlgorithmikRegisterEintrag:
    eintrag_id: str
    geltung: AlgorithmikRegisterGeltung
    typ: AlgorithmikRegisterTyp
    prozedur: AlgorithmikRegisterProzedur
    info_weight: float
    info_tier: int
    info_ids: List[str]
    info_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class AlgorithmikRegister:
    register_id: str
    eintraege: List[AlgorithmikRegisterEintrag]
    parent: InformatikFeld


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        AlgorithmikRegisterGeltung.GESPERRT: 0.0,
        AlgorithmikRegisterGeltung.ALGORITHMISCH: 0.05,
        AlgorithmikRegisterGeltung.GRUNDLEGEND_ALGORITHMISCH: 0.1,
    })
    _TIER_DELTA.update({
        AlgorithmikRegisterGeltung.GESPERRT: 0,
        AlgorithmikRegisterGeltung.ALGORITHMISCH: 1,
        AlgorithmikRegisterGeltung.GRUNDLEGEND_ALGORITHMISCH: 2,
    })
    _TYP_MAP.update({
        AlgorithmikRegisterGeltung.GESPERRT: AlgorithmikRegisterTyp.BEOBACHTUNG,
        AlgorithmikRegisterGeltung.ALGORITHMISCH: AlgorithmikRegisterTyp.ANALYSE,
        AlgorithmikRegisterGeltung.GRUNDLEGEND_ALGORITHMISCH: AlgorithmikRegisterTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        AlgorithmikRegisterGeltung.GESPERRT: AlgorithmikRegisterProzedur.INITIALISIEREN,
        AlgorithmikRegisterGeltung.ALGORITHMISCH: AlgorithmikRegisterProzedur.AKTIVIEREN,
        AlgorithmikRegisterGeltung.GRUNDLEGEND_ALGORITHMISCH: AlgorithmikRegisterProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        AlgorithmikRegisterGeltung.GESPERRT: [AlgorithmikRegisterGeltung.GESPERRT],
        AlgorithmikRegisterGeltung.ALGORITHMISCH: [AlgorithmikRegisterGeltung.ALGORITHMISCH],
        AlgorithmikRegisterGeltung.GRUNDLEGEND_ALGORITHMISCH: [AlgorithmikRegisterGeltung.GRUNDLEGEND_ALGORITHMISCH],
    })


_init_map()


def build_algorithmik_register(*, register_id: str = "algorithmik-register") -> AlgorithmikRegister:
    parent = build_informatik_feld(feld_id=f"{register_id}-parent")
    eintraege: List[AlgorithmikRegisterEintrag] = []
    for g in AlgorithmikRegisterGeltung:
        eintraege.append(AlgorithmikRegisterEintrag(
            eintrag_id=f"{register_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            info_weight=round(sum(n.info_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            info_tier=max(n.info_tier for n in parent.normen) + _TIER_DELTA[g],
            info_ids=[f"ar-{register_id}-{g.value}-001", f"ar-{register_id}-{g.value}-002"],
            info_tags=["info", "algorithmik", g.value],
        ))
    return AlgorithmikRegister(register_id=register_id, eintraege=eintraege, parent=parent)
