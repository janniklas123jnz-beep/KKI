from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .geomorphologie_feld import GeomorphologieFeld, build_geomorphologie_feld


class ErosionsRegisterGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_GEOMORPHOLOGISCH = auto()
    GEOMORPHOLOGISCH = auto()
    GEOMORPHOLOGISCH_AKTIV = auto()
    GEOMORPHOLOGIE_SOUVERAEN = auto()


class ErosionsRegisterTyp(Enum):
    EROSIONSREGISTER = auto()
    EROSIONSSAMMLUNG = auto()
    EROSIONSEINTRAG = auto()


class ErosionsRegisterProzedur(Enum):
    EROSIONSANALYSE = auto()
    EROSIONSSYNTHESE = auto()
    EROSIONSBEWERTUNG = auto()


_WEIGHT_DELTA: dict[ErosionsRegisterGeltung, float] = {
    ErosionsRegisterGeltung.GESPERRT: 0.0,
    ErosionsRegisterGeltung.GRUNDLEGEND_GEOMORPHOLOGISCH: 1.3,
    ErosionsRegisterGeltung.GEOMORPHOLOGISCH: 2.6,
    ErosionsRegisterGeltung.GEOMORPHOLOGISCH_AKTIV: 3.9,
    ErosionsRegisterGeltung.GEOMORPHOLOGIE_SOUVERAEN: 5.2,
}

_TYP_MAP = {
    ErosionsRegisterGeltung.GESPERRT: ErosionsRegisterTyp.EROSIONSREGISTER,
    ErosionsRegisterGeltung.GRUNDLEGEND_GEOMORPHOLOGISCH: ErosionsRegisterTyp.EROSIONSEINTRAG,
    ErosionsRegisterGeltung.GEOMORPHOLOGISCH: ErosionsRegisterTyp.EROSIONSEINTRAG,
    ErosionsRegisterGeltung.GEOMORPHOLOGISCH_AKTIV: ErosionsRegisterTyp.EROSIONSSAMMLUNG,
    ErosionsRegisterGeltung.GEOMORPHOLOGIE_SOUVERAEN: ErosionsRegisterTyp.EROSIONSSAMMLUNG,
}

_PROZEDUR_MAP = {
    ErosionsRegisterGeltung.GESPERRT: ErosionsRegisterProzedur.EROSIONSANALYSE,
    ErosionsRegisterGeltung.GRUNDLEGEND_GEOMORPHOLOGISCH: ErosionsRegisterProzedur.EROSIONSANALYSE,
    ErosionsRegisterGeltung.GEOMORPHOLOGISCH: ErosionsRegisterProzedur.EROSIONSSYNTHESE,
    ErosionsRegisterGeltung.GEOMORPHOLOGISCH_AKTIV: ErosionsRegisterProzedur.EROSIONSSYNTHESE,
    ErosionsRegisterGeltung.GEOMORPHOLOGIE_SOUVERAEN: ErosionsRegisterProzedur.EROSIONSBEWERTUNG,
}


@dataclass(frozen=True)
class ErosionsRegisterEintrag:
    geltung: ErosionsRegisterGeltung
    geomorphologie_weight: float
    geomorphologie_tier: int
    geomorphologie_ids: tuple[str, ...]
    geomorphologie_tags: tuple[str, ...]
    typ: ErosionsRegisterTyp
    prozedur: ErosionsRegisterProzedur
    canonical: bool = True


@dataclass(frozen=True)
class ErosionsRegister:
    eintraege: tuple[ErosionsRegisterEintrag, ...]
    parent: Optional[GeomorphologieFeld] = None


def build_erosions_register(parent: Optional[GeomorphologieFeld] = None) -> ErosionsRegister:
    if parent is None:
        parent = build_geomorphologie_feld()
    base = sum(n.geomorphologie_weight for n in parent.normen)
    eintraege = tuple(
        ErosionsRegisterEintrag(
            geltung=g,
            geomorphologie_weight=round(base + _WEIGHT_DELTA[g], 4),
            geomorphologie_tier=i + 1,
            geomorphologie_ids=(f"erosions-register-{g.name.lower()}-001",),
            geomorphologie_tags=("geomorphologie", "erosion", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(ErosionsRegisterGeltung)
    )
    return ErosionsRegister(eintraege=eintraege, parent=parent)
