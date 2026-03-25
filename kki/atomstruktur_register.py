"""#672 AtomstrukturRegister — Atomaufbau & Periodensystem (parent: ChemieFeld)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .chemie_feld import ChemieFeld, build_chemie_feld

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class AtomstrukturRegisterGeltung(str, Enum):
    GESPERRT = "gesperrt"
    ATOMSTRUKTURIERT = "atomstrukturiert"
    GRUNDLEGEND_ATOMSTRUKTURIERT = "grundlegend-atomstrukturiert"


class AtomstrukturRegisterTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"
    KATALYSE = "katalyse"


class AtomstrukturRegisterProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class AtomstrukturRegisterEintrag:
    atomstruktur_register_id: str
    geltung: AtomstrukturRegisterGeltung
    typ: AtomstrukturRegisterTyp
    prozedur: AtomstrukturRegisterProzedur
    chemie_weight: float
    chemie_tier: int
    chemie_ids: List[str]
    chemie_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class AtomstrukturRegister:
    register_id: str
    eintraege: List[AtomstrukturRegisterEintrag]
    parent: ChemieFeld


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        AtomstrukturRegisterGeltung.GESPERRT: 0.0,
        AtomstrukturRegisterGeltung.ATOMSTRUKTURIERT: 0.05,
        AtomstrukturRegisterGeltung.GRUNDLEGEND_ATOMSTRUKTURIERT: 0.1,
    })
    _TIER_DELTA.update({
        AtomstrukturRegisterGeltung.GESPERRT: 0,
        AtomstrukturRegisterGeltung.ATOMSTRUKTURIERT: 1,
        AtomstrukturRegisterGeltung.GRUNDLEGEND_ATOMSTRUKTURIERT: 2,
    })
    _TYP_MAP.update({
        AtomstrukturRegisterGeltung.GESPERRT: AtomstrukturRegisterTyp.BEOBACHTUNG,
        AtomstrukturRegisterGeltung.ATOMSTRUKTURIERT: AtomstrukturRegisterTyp.ANALYSE,
        AtomstrukturRegisterGeltung.GRUNDLEGEND_ATOMSTRUKTURIERT: AtomstrukturRegisterTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        AtomstrukturRegisterGeltung.GESPERRT: AtomstrukturRegisterProzedur.INITIALISIEREN,
        AtomstrukturRegisterGeltung.ATOMSTRUKTURIERT: AtomstrukturRegisterProzedur.AKTIVIEREN,
        AtomstrukturRegisterGeltung.GRUNDLEGEND_ATOMSTRUKTURIERT: AtomstrukturRegisterProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        AtomstrukturRegisterGeltung.GESPERRT: [AtomstrukturRegisterGeltung.GESPERRT],
        AtomstrukturRegisterGeltung.ATOMSTRUKTURIERT: [AtomstrukturRegisterGeltung.ATOMSTRUKTURIERT],
        AtomstrukturRegisterGeltung.GRUNDLEGEND_ATOMSTRUKTURIERT: [AtomstrukturRegisterGeltung.GRUNDLEGEND_ATOMSTRUKTURIERT],
    })


_init_map()


def build_atomstruktur_register(*, register_id: str = "atomstruktur-register") -> AtomstrukturRegister:
    parent = build_chemie_feld(feld_id=f"{register_id}-parent")
    eintraege: List[AtomstrukturRegisterEintrag] = []
    for g in AtomstrukturRegisterGeltung:
        eintraege.append(AtomstrukturRegisterEintrag(
            atomstruktur_register_id=f"{register_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            chemie_weight=round(sum(n.chemie_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            chemie_tier=max(n.chemie_tier for n in parent.normen) + _TIER_DELTA[g],
            chemie_ids=[f"ar-{register_id}-{g.value}-001", f"ar-{register_id}-{g.value}-002"],
            chemie_tags=["chemie", "atomstruktur", "register", g.value],
        ))
    return AtomstrukturRegister(register_id=register_id, eintraege=eintraege, parent=parent)
