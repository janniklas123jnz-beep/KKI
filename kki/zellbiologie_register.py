"""#702 — ZellbiologieRegister: Zellorganellen, Membranphysiologie & Zellzyklus."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.biologie_feld import BiologieFeld, build_biologie_feld


class ZellbiologieRegisterGeltung(str, Enum):
    GESPERRT = "gesperrt"
    ZELLBIOLOGISCH = "zellbiologisch"
    GRUNDLEGEND_ZELLBIOLOGISCH = "grundlegend-zellbiologisch"


class ZellbiologieRegisterTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class ZellbiologieRegisterProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class ZellbiologieRegisterEintrag:
    eintrag_id: str
    geltung: ZellbiologieRegisterGeltung
    typ: ZellbiologieRegisterTyp
    prozedur: ZellbiologieRegisterProzedur
    bio_weight: float
    bio_tier: int
    bio_ids: List[str]
    bio_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class ZellbiologieRegister:
    register_id: str
    eintraege: List[ZellbiologieRegisterEintrag]
    parent: BiologieFeld


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        ZellbiologieRegisterGeltung.GESPERRT: 0.0,
        ZellbiologieRegisterGeltung.ZELLBIOLOGISCH: 0.05,
        ZellbiologieRegisterGeltung.GRUNDLEGEND_ZELLBIOLOGISCH: 0.1,
    })
    _TIER_DELTA.update({
        ZellbiologieRegisterGeltung.GESPERRT: 0,
        ZellbiologieRegisterGeltung.ZELLBIOLOGISCH: 1,
        ZellbiologieRegisterGeltung.GRUNDLEGEND_ZELLBIOLOGISCH: 2,
    })
    _TYP_MAP.update({
        ZellbiologieRegisterGeltung.GESPERRT: ZellbiologieRegisterTyp.BEOBACHTUNG,
        ZellbiologieRegisterGeltung.ZELLBIOLOGISCH: ZellbiologieRegisterTyp.ANALYSE,
        ZellbiologieRegisterGeltung.GRUNDLEGEND_ZELLBIOLOGISCH: ZellbiologieRegisterTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        ZellbiologieRegisterGeltung.GESPERRT: ZellbiologieRegisterProzedur.INITIALISIEREN,
        ZellbiologieRegisterGeltung.ZELLBIOLOGISCH: ZellbiologieRegisterProzedur.AKTIVIEREN,
        ZellbiologieRegisterGeltung.GRUNDLEGEND_ZELLBIOLOGISCH: ZellbiologieRegisterProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        ZellbiologieRegisterGeltung.GESPERRT: [ZellbiologieRegisterGeltung.GESPERRT],
        ZellbiologieRegisterGeltung.ZELLBIOLOGISCH: [ZellbiologieRegisterGeltung.ZELLBIOLOGISCH],
        ZellbiologieRegisterGeltung.GRUNDLEGEND_ZELLBIOLOGISCH: [ZellbiologieRegisterGeltung.GRUNDLEGEND_ZELLBIOLOGISCH],
    })


_init_map()


def build_zellbiologie_register(*, register_id: str = "zellbiologie-register") -> ZellbiologieRegister:
    parent = build_biologie_feld(feld_id=f"{register_id}-parent")
    eintraege: List[ZellbiologieRegisterEintrag] = []
    for g in ZellbiologieRegisterGeltung:
        eintraege.append(ZellbiologieRegisterEintrag(
            eintrag_id=f"{register_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            bio_weight=round(sum(n.bio_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            bio_tier=max(n.bio_tier for n in parent.normen) + _TIER_DELTA[g],
            bio_ids=[f"zr-{register_id}-{g.value}-001", f"zr-{register_id}-{g.value}-002"],
            bio_tags=["bio", "zellbiologie", g.value],
        ))
    return ZellbiologieRegister(register_id=register_id, eintraege=eintraege, parent=parent)
