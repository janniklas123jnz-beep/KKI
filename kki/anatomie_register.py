"""#642 AnatomieRegister — Anatomie & Körperstruktur (parent: MedizinFeld)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .medizin_feld import MedizinFeld, build_medizin_feld

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class AnatomieRegisterGeltung(str, Enum):
    GESPERRT = "gesperrt"
    ANATOMISCH = "anatomisch"
    GRUNDLEGEND_ANATOMISCH = "grundlegend-anatomisch"


class AnatomieRegisterTyp(str, Enum):
    KLINISCH = "klinisch"
    THEORETISCH = "theoretisch"
    ANGEWANDT = "angewandt"
    PRAEVENTIV = "praeventiv"


class AnatomieRegisterProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class AnatomieRegisterEintrag:
    register_id: str
    geltung: AnatomieRegisterGeltung
    typ: AnatomieRegisterTyp
    prozedur: AnatomieRegisterProzedur
    medizin_weight: float
    medizin_tier: int
    medizin_ids: List[str]
    medizin_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class AnatomieRegister:
    register_id: str
    eintraege: List[AnatomieRegisterEintrag]
    parent: MedizinFeld


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        AnatomieRegisterGeltung.GESPERRT: 0.0,
        AnatomieRegisterGeltung.ANATOMISCH: 0.05,
        AnatomieRegisterGeltung.GRUNDLEGEND_ANATOMISCH: 0.1,
    })
    _TIER_DELTA.update({
        AnatomieRegisterGeltung.GESPERRT: 0,
        AnatomieRegisterGeltung.ANATOMISCH: 1,
        AnatomieRegisterGeltung.GRUNDLEGEND_ANATOMISCH: 2,
    })
    _TYP_MAP.update({
        AnatomieRegisterGeltung.GESPERRT: AnatomieRegisterTyp.KLINISCH,
        AnatomieRegisterGeltung.ANATOMISCH: AnatomieRegisterTyp.THEORETISCH,
        AnatomieRegisterGeltung.GRUNDLEGEND_ANATOMISCH: AnatomieRegisterTyp.ANGEWANDT,
    })
    _PROZEDUR_MAP.update({
        AnatomieRegisterGeltung.GESPERRT: AnatomieRegisterProzedur.INITIALISIEREN,
        AnatomieRegisterGeltung.ANATOMISCH: AnatomieRegisterProzedur.AKTIVIEREN,
        AnatomieRegisterGeltung.GRUNDLEGEND_ANATOMISCH: AnatomieRegisterProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        AnatomieRegisterGeltung.GESPERRT: [AnatomieRegisterGeltung.GESPERRT],
        AnatomieRegisterGeltung.ANATOMISCH: [AnatomieRegisterGeltung.ANATOMISCH],
        AnatomieRegisterGeltung.GRUNDLEGEND_ANATOMISCH: [AnatomieRegisterGeltung.GRUNDLEGEND_ANATOMISCH],
    })


_init_map()


def build_anatomie_register(*, register_id: str = "anatomie-register") -> AnatomieRegister:
    parent = build_medizin_feld(feld_id=f"{register_id}-parent")
    eintraege: List[AnatomieRegisterEintrag] = []
    for g in AnatomieRegisterGeltung:
        eintraege.append(AnatomieRegisterEintrag(
            register_id=f"{register_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            medizin_weight=round(sum(n.medizin_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            medizin_tier=max(n.medizin_tier for n in parent.normen) + _TIER_DELTA[g],
            medizin_ids=[f"ar-{register_id}-{g.value}-001", f"ar-{register_id}-{g.value}-002"],
            medizin_tags=["medizin", "anatomie", g.value],
        ))
    return AnatomieRegister(register_id=register_id, eintraege=eintraege, parent=parent)
