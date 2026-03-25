"""#722 — MikrooekonomieRegister: Angebot, Nachfrage & Preistheorie."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.wirtschaft_feld import WirtschaftFeld, build_wirtschaft_feld


class MikrooekonomieRegisterGeltung(str, Enum):
    GESPERRT = "gesperrt"
    MIKROOEKONOMISCH = "mikrooekonomisch"
    GRUNDLEGEND_MIKROOEKONOMISCH = "grundlegend-mikrooekonomisch"


class MikrooekonomieRegisterTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class MikrooekonomieRegisterProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class MikrooekonomieRegisterEintrag:
    eintrag_id: str
    geltung: MikrooekonomieRegisterGeltung
    typ: MikrooekonomieRegisterTyp
    prozedur: MikrooekonomieRegisterProzedur
    wirt_weight: float
    wirt_tier: int
    wirt_ids: List[str]
    wirt_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class MikrooekonomieRegister:
    register_id: str
    eintraege: List[MikrooekonomieRegisterEintrag]
    parent: WirtschaftFeld


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        MikrooekonomieRegisterGeltung.GESPERRT: 0.0,
        MikrooekonomieRegisterGeltung.MIKROOEKONOMISCH: 0.05,
        MikrooekonomieRegisterGeltung.GRUNDLEGEND_MIKROOEKONOMISCH: 0.1,
    })
    _TIER_DELTA.update({
        MikrooekonomieRegisterGeltung.GESPERRT: 0,
        MikrooekonomieRegisterGeltung.MIKROOEKONOMISCH: 1,
        MikrooekonomieRegisterGeltung.GRUNDLEGEND_MIKROOEKONOMISCH: 2,
    })
    _TYP_MAP.update({
        MikrooekonomieRegisterGeltung.GESPERRT: MikrooekonomieRegisterTyp.BEOBACHTUNG,
        MikrooekonomieRegisterGeltung.MIKROOEKONOMISCH: MikrooekonomieRegisterTyp.ANALYSE,
        MikrooekonomieRegisterGeltung.GRUNDLEGEND_MIKROOEKONOMISCH: MikrooekonomieRegisterTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        MikrooekonomieRegisterGeltung.GESPERRT: MikrooekonomieRegisterProzedur.INITIALISIEREN,
        MikrooekonomieRegisterGeltung.MIKROOEKONOMISCH: MikrooekonomieRegisterProzedur.AKTIVIEREN,
        MikrooekonomieRegisterGeltung.GRUNDLEGEND_MIKROOEKONOMISCH: MikrooekonomieRegisterProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        MikrooekonomieRegisterGeltung.GESPERRT: [MikrooekonomieRegisterGeltung.GESPERRT],
        MikrooekonomieRegisterGeltung.MIKROOEKONOMISCH: [MikrooekonomieRegisterGeltung.MIKROOEKONOMISCH],
        MikrooekonomieRegisterGeltung.GRUNDLEGEND_MIKROOEKONOMISCH: [MikrooekonomieRegisterGeltung.GRUNDLEGEND_MIKROOEKONOMISCH],
    })


_init_map()


def build_mikrooekonomie_register(*, register_id: str = "mikrooekonomie-register") -> MikrooekonomieRegister:
    parent = build_wirtschaft_feld(feld_id=f"{register_id}-parent")
    eintraege: List[MikrooekonomieRegisterEintrag] = []
    for g in MikrooekonomieRegisterGeltung:
        eintraege.append(MikrooekonomieRegisterEintrag(
            eintrag_id=f"{register_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            wirt_weight=round(sum(n.wirt_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            wirt_tier=max(n.wirt_tier for n in parent.normen) + _TIER_DELTA[g],
            wirt_ids=[f"mr-{register_id}-{g.value}-001", f"mr-{register_id}-{g.value}-002"],
            wirt_tags=["wirt", "mikrooekonomie", g.value],
        ))
    return MikrooekonomieRegister(register_id=register_id, eintraege=eintraege, parent=parent)
