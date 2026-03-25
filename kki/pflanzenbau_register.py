from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .agrar_feld import AgrarFeld, build_agrar_feld


class PflanzenbauRegisterGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_PFLANZENBAULICH = auto()
    PFLANZENBAULICH = auto()
    PFLANZENBAULICH_AKTIV = auto()
    PFLANZENBAU_SOUVERAEN = auto()


class PflanzenbauRegisterTyp(Enum):
    PFLANZENBAUREGISTER = auto()
    SORTENREGISTER = auto()
    ANBAUSYSTEMKATALOG = auto()


class PflanzenbauRegisterProzedur(Enum):
    ANBAUANALYSE = auto()
    ERTRAGSBEWERTUNG = auto()
    SORTENSELEKTION = auto()


_WEIGHT_DELTA: dict[PflanzenbauRegisterGeltung, float] = {
    PflanzenbauRegisterGeltung.GESPERRT: 0.0,
    PflanzenbauRegisterGeltung.GRUNDLEGEND_PFLANZENBAULICH: 1.3,
    PflanzenbauRegisterGeltung.PFLANZENBAULICH: 2.6,
    PflanzenbauRegisterGeltung.PFLANZENBAULICH_AKTIV: 3.9,
    PflanzenbauRegisterGeltung.PFLANZENBAU_SOUVERAEN: 5.2,
}

_TYP_MAP = {
    PflanzenbauRegisterGeltung.GESPERRT: PflanzenbauRegisterTyp.PFLANZENBAUREGISTER,
    PflanzenbauRegisterGeltung.GRUNDLEGEND_PFLANZENBAULICH: PflanzenbauRegisterTyp.SORTENREGISTER,
    PflanzenbauRegisterGeltung.PFLANZENBAULICH: PflanzenbauRegisterTyp.SORTENREGISTER,
    PflanzenbauRegisterGeltung.PFLANZENBAULICH_AKTIV: PflanzenbauRegisterTyp.ANBAUSYSTEMKATALOG,
    PflanzenbauRegisterGeltung.PFLANZENBAU_SOUVERAEN: PflanzenbauRegisterTyp.ANBAUSYSTEMKATALOG,
}

_PROZEDUR_MAP = {
    PflanzenbauRegisterGeltung.GESPERRT: PflanzenbauRegisterProzedur.ANBAUANALYSE,
    PflanzenbauRegisterGeltung.GRUNDLEGEND_PFLANZENBAULICH: PflanzenbauRegisterProzedur.ANBAUANALYSE,
    PflanzenbauRegisterGeltung.PFLANZENBAULICH: PflanzenbauRegisterProzedur.ERTRAGSBEWERTUNG,
    PflanzenbauRegisterGeltung.PFLANZENBAULICH_AKTIV: PflanzenbauRegisterProzedur.ERTRAGSBEWERTUNG,
    PflanzenbauRegisterGeltung.PFLANZENBAU_SOUVERAEN: PflanzenbauRegisterProzedur.SORTENSELEKTION,
}


@dataclass(frozen=True)
class PflanzenbauRegisterEintrag:
    geltung: PflanzenbauRegisterGeltung
    agrar_weight: float
    agrar_tier: int
    agrar_ids: tuple[str, ...]
    agrar_tags: tuple[str, ...]
    typ: PflanzenbauRegisterTyp
    prozedur: PflanzenbauRegisterProzedur
    canonical: bool = True


@dataclass(frozen=True)
class PflanzenbauRegister:
    eintraege: tuple[PflanzenbauRegisterEintrag, ...]
    parent: Optional[AgrarFeld] = None


def build_pflanzenbau_register(parent: Optional[AgrarFeld] = None) -> PflanzenbauRegister:
    if parent is None:
        parent = build_agrar_feld()
    base = sum(n.agrar_weight for n in parent.normen)
    eintraege = tuple(
        PflanzenbauRegisterEintrag(
            geltung=g,
            agrar_weight=round(base + _WEIGHT_DELTA[g], 4),
            agrar_tier=i + 1,
            agrar_ids=(f"pflanzenbau-{g.name.lower()}-001",),
            agrar_tags=("pflanzenbau", "register", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(PflanzenbauRegisterGeltung)
    )
    return PflanzenbauRegister(eintraege=eintraege, parent=parent)
