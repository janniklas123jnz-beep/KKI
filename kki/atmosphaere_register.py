from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional
from .klima_feld import KlimaFeld, build_klima_feld


class AtmosphaereRegisterGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_ATMOSPHAERISCH = auto()
    ATMOSPHAERISCH = auto()
    ATMOSPHAERISCH_AKTIV = auto()
    ATMOSPHAERE_SOUVERAEN = auto()


class AtmosphaereRegisterTyp(Enum):
    ATMOSPHAEREREGISTER = auto()
    ATMOSPHAERESCHICHT = auto()
    ATMOSPHAEREKOMPONENTE = auto()


class AtmosphaereRegisterProzedur(Enum):
    ATMOSPHAEREANALYSE = auto()
    ATMOSPHAERESYNTHESE = auto()
    ATMOSPHAEREBEWERTUNG = auto()


_WEIGHT_DELTA: dict[AtmosphaereRegisterGeltung, float] = {
    AtmosphaereRegisterGeltung.GESPERRT: 0.0,
    AtmosphaereRegisterGeltung.GRUNDLEGEND_ATMOSPHAERISCH: 1.3,
    AtmosphaereRegisterGeltung.ATMOSPHAERISCH: 2.6,
    AtmosphaereRegisterGeltung.ATMOSPHAERISCH_AKTIV: 3.9,
    AtmosphaereRegisterGeltung.ATMOSPHAERE_SOUVERAEN: 5.2,
}

_TYP_MAP: dict[AtmosphaereRegisterGeltung, AtmosphaereRegisterTyp] = {
    AtmosphaereRegisterGeltung.GESPERRT: AtmosphaereRegisterTyp.ATMOSPHAEREREGISTER,
    AtmosphaereRegisterGeltung.GRUNDLEGEND_ATMOSPHAERISCH: AtmosphaereRegisterTyp.ATMOSPHAEREKOMPONENTE,
    AtmosphaereRegisterGeltung.ATMOSPHAERISCH: AtmosphaereRegisterTyp.ATMOSPHAEREKOMPONENTE,
    AtmosphaereRegisterGeltung.ATMOSPHAERISCH_AKTIV: AtmosphaereRegisterTyp.ATMOSPHAERESCHICHT,
    AtmosphaereRegisterGeltung.ATMOSPHAERE_SOUVERAEN: AtmosphaereRegisterTyp.ATMOSPHAERESCHICHT,
}

_PROZEDUR_MAP: dict[AtmosphaereRegisterGeltung, AtmosphaereRegisterProzedur] = {
    AtmosphaereRegisterGeltung.GESPERRT: AtmosphaereRegisterProzedur.ATMOSPHAEREANALYSE,
    AtmosphaereRegisterGeltung.GRUNDLEGEND_ATMOSPHAERISCH: AtmosphaereRegisterProzedur.ATMOSPHAEREANALYSE,
    AtmosphaereRegisterGeltung.ATMOSPHAERISCH: AtmosphaereRegisterProzedur.ATMOSPHAERESYNTHESE,
    AtmosphaereRegisterGeltung.ATMOSPHAERISCH_AKTIV: AtmosphaereRegisterProzedur.ATMOSPHAERESYNTHESE,
    AtmosphaereRegisterGeltung.ATMOSPHAERE_SOUVERAEN: AtmosphaereRegisterProzedur.ATMOSPHAEREBEWERTUNG,
}


@dataclass(frozen=True)
class AtmosphaereRegisterEintrag:
    geltung: AtmosphaereRegisterGeltung
    klima_weight: float
    klima_tier: int
    klima_ids: tuple[str, ...]
    klima_tags: tuple[str, ...]
    typ: AtmosphaereRegisterTyp
    prozedur: AtmosphaereRegisterProzedur
    canonical: bool = True


@dataclass(frozen=True)
class AtmosphaereRegister:
    eintraege: tuple[AtmosphaereRegisterEintrag, ...]
    parent: Optional[KlimaFeld] = None


def build_atmosphaere_register(parent: Optional[KlimaFeld] = None) -> AtmosphaereRegister:
    if parent is None:
        parent = build_klima_feld()
    base = sum(n.klima_weight for n in parent.normen)
    eintraege = tuple(
        AtmosphaereRegisterEintrag(
            geltung=g,
            klima_weight=round(base + _WEIGHT_DELTA[g], 4),
            klima_tier=i + 1,
            klima_ids=(f"atmosphaere-register-{g.name.lower()}-001",),
            klima_tags=("atmosphaere", "register", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(AtmosphaereRegisterGeltung)
    )
    return AtmosphaereRegister(eintraege=eintraege, parent=parent)
