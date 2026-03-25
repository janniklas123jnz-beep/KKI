from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .ozean_feld import OzeanFeld, build_ozean_feld


class MeeresstroemungRegisterGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_OZEANOGRAPHISCH = auto()
    OZEANOGRAPHISCH = auto()
    OZEANOGRAPHISCH_AKTIV = auto()
    OZEAN_SOUVERAEN = auto()


class MeeresstroemungRegisterTyp(Enum):
    MEERESSTROEMUNG = auto()
    ZIRKULATIONSSYSTEM = auto()
    STROEMUNGSKOMPONENTE = auto()


class MeeresstroemungRegisterProzedur(Enum):
    STROEMUNGSANALYSE = auto()
    STROEMUNGSSYNTHESE = auto()
    STROEMUNGSBEWERTUNG = auto()


_WEIGHT_DELTA: dict[MeeresstroemungRegisterGeltung, float] = {
    MeeresstroemungRegisterGeltung.GESPERRT: 0.0,
    MeeresstroemungRegisterGeltung.GRUNDLEGEND_OZEANOGRAPHISCH: 1.3,
    MeeresstroemungRegisterGeltung.OZEANOGRAPHISCH: 2.6,
    MeeresstroemungRegisterGeltung.OZEANOGRAPHISCH_AKTIV: 3.9,
    MeeresstroemungRegisterGeltung.OZEAN_SOUVERAEN: 5.2,
}

_TYP_MAP = {
    MeeresstroemungRegisterGeltung.GESPERRT: MeeresstroemungRegisterTyp.MEERESSTROEMUNG,
    MeeresstroemungRegisterGeltung.GRUNDLEGEND_OZEANOGRAPHISCH: MeeresstroemungRegisterTyp.STROEMUNGSKOMPONENTE,
    MeeresstroemungRegisterGeltung.OZEANOGRAPHISCH: MeeresstroemungRegisterTyp.STROEMUNGSKOMPONENTE,
    MeeresstroemungRegisterGeltung.OZEANOGRAPHISCH_AKTIV: MeeresstroemungRegisterTyp.ZIRKULATIONSSYSTEM,
    MeeresstroemungRegisterGeltung.OZEAN_SOUVERAEN: MeeresstroemungRegisterTyp.ZIRKULATIONSSYSTEM,
}

_PROZEDUR_MAP = {
    MeeresstroemungRegisterGeltung.GESPERRT: MeeresstroemungRegisterProzedur.STROEMUNGSANALYSE,
    MeeresstroemungRegisterGeltung.GRUNDLEGEND_OZEANOGRAPHISCH: MeeresstroemungRegisterProzedur.STROEMUNGSANALYSE,
    MeeresstroemungRegisterGeltung.OZEANOGRAPHISCH: MeeresstroemungRegisterProzedur.STROEMUNGSSYNTHESE,
    MeeresstroemungRegisterGeltung.OZEANOGRAPHISCH_AKTIV: MeeresstroemungRegisterProzedur.STROEMUNGSSYNTHESE,
    MeeresstroemungRegisterGeltung.OZEAN_SOUVERAEN: MeeresstroemungRegisterProzedur.STROEMUNGSBEWERTUNG,
}


@dataclass(frozen=True)
class MeeresstroemungRegisterEintrag:
    geltung: MeeresstroemungRegisterGeltung
    ozean_weight: float
    ozean_tier: int
    ozean_ids: tuple[str, ...]
    ozean_tags: tuple[str, ...]
    typ: MeeresstroemungRegisterTyp
    prozedur: MeeresstroemungRegisterProzedur
    canonical: bool = True


@dataclass(frozen=True)
class MeeresstroemungRegister:
    eintraege: tuple[MeeresstroemungRegisterEintrag, ...]
    parent: Optional[OzeanFeld] = None


def build_meeresstroemung_register(parent: Optional[OzeanFeld] = None) -> MeeresstroemungRegister:
    if parent is None:
        parent = build_ozean_feld()
    base = sum(n.ozean_weight for n in parent.normen)
    eintraege = tuple(
        MeeresstroemungRegisterEintrag(
            geltung=g,
            ozean_weight=round(base + _WEIGHT_DELTA[g], 4),
            ozean_tier=i + 1,
            ozean_ids=(f"meeresstroemung-{g.name.lower()}-001",),
            ozean_tags=("ozean", "meeresstroemung", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(MeeresstroemungRegisterGeltung)
    )
    return MeeresstroemungRegister(eintraege=eintraege, parent=parent)
