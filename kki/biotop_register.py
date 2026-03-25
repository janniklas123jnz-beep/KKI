"""#662 BiotopRegister — Biotope & Lebensräume (parent: OekologieFeld)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .oekologie_feld import OekologieFeld, build_oekologie_feld

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class BiotopRegisterGeltung(str, Enum):
    GESPERRT = "gesperrt"
    BIOTOPISCH_ERFASST = "biotopisch-erfasst"
    GRUNDLEGEND_BIOTOPISCH_ERFASST = "grundlegend-biotopisch-erfasst"


class BiotopRegisterTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"
    SCHUTZ = "schutz"


class BiotopRegisterProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class BiotopRegisterEintrag:
    biotop_register_id: str
    geltung: BiotopRegisterGeltung
    typ: BiotopRegisterTyp
    prozedur: BiotopRegisterProzedur
    oekologie_weight: float
    oekologie_tier: int
    oekologie_ids: List[str]
    oekologie_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class BiotopRegister:
    register_id: str
    eintraege: List[BiotopRegisterEintrag]
    parent: OekologieFeld


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        BiotopRegisterGeltung.GESPERRT: 0.0,
        BiotopRegisterGeltung.BIOTOPISCH_ERFASST: 0.05,
        BiotopRegisterGeltung.GRUNDLEGEND_BIOTOPISCH_ERFASST: 0.1,
    })
    _TIER_DELTA.update({
        BiotopRegisterGeltung.GESPERRT: 0,
        BiotopRegisterGeltung.BIOTOPISCH_ERFASST: 1,
        BiotopRegisterGeltung.GRUNDLEGEND_BIOTOPISCH_ERFASST: 2,
    })
    _TYP_MAP.update({
        BiotopRegisterGeltung.GESPERRT: BiotopRegisterTyp.BEOBACHTUNG,
        BiotopRegisterGeltung.BIOTOPISCH_ERFASST: BiotopRegisterTyp.ANALYSE,
        BiotopRegisterGeltung.GRUNDLEGEND_BIOTOPISCH_ERFASST: BiotopRegisterTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        BiotopRegisterGeltung.GESPERRT: BiotopRegisterProzedur.INITIALISIEREN,
        BiotopRegisterGeltung.BIOTOPISCH_ERFASST: BiotopRegisterProzedur.AKTIVIEREN,
        BiotopRegisterGeltung.GRUNDLEGEND_BIOTOPISCH_ERFASST: BiotopRegisterProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        BiotopRegisterGeltung.GESPERRT: [BiotopRegisterGeltung.GESPERRT],
        BiotopRegisterGeltung.BIOTOPISCH_ERFASST: [BiotopRegisterGeltung.BIOTOPISCH_ERFASST],
        BiotopRegisterGeltung.GRUNDLEGEND_BIOTOPISCH_ERFASST: [BiotopRegisterGeltung.GRUNDLEGEND_BIOTOPISCH_ERFASST],
    })


_init_map()


def build_biotop_register(*, register_id: str = "biotop-register") -> BiotopRegister:
    parent = build_oekologie_feld(feld_id=f"{register_id}-parent")
    eintraege: List[BiotopRegisterEintrag] = []
    for g in BiotopRegisterGeltung:
        eintraege.append(BiotopRegisterEintrag(
            biotop_register_id=f"{register_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            oekologie_weight=round(sum(n.oekologie_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            oekologie_tier=max(n.oekologie_tier for n in parent.normen) + _TIER_DELTA[g],
            oekologie_ids=[f"br-{register_id}-{g.value}-001", f"br-{register_id}-{g.value}-002"],
            oekologie_tags=["oekologie", "biotop", "register", g.value],
        ))
    return BiotopRegister(register_id=register_id, eintraege=eintraege, parent=parent)
