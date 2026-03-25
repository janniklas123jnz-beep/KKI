from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .sport_feld import SportFeld, build_sport_feld


class BiomechanikRegisterGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_BIOMECHANISCH = auto()
    BIOMECHANISCH = auto()
    BIOMECHANISCH_AKTIV = auto()
    BIOMECHANIK_SOUVERAEN = auto()


class BiomechanikRegisterTyp(Enum):
    BIOMECHANIKREGISTER = auto()
    BEWEGUNGSANALYSE = auto()
    KRAFTMESSPROTOKOLL = auto()


class BiomechanikRegisterProzedur(Enum):
    KINEMATIKANALYSE = auto()
    KINETIKBERECHNUNG = auto()
    BEWEGUNGSOPTIMIERUNG = auto()


_WEIGHT_DELTA: dict[BiomechanikRegisterGeltung, float] = {
    BiomechanikRegisterGeltung.GESPERRT: 0.0,
    BiomechanikRegisterGeltung.GRUNDLEGEND_BIOMECHANISCH: 1.3,
    BiomechanikRegisterGeltung.BIOMECHANISCH: 2.6,
    BiomechanikRegisterGeltung.BIOMECHANISCH_AKTIV: 3.9,
    BiomechanikRegisterGeltung.BIOMECHANIK_SOUVERAEN: 5.2,
}

_TYP_MAP = {
    BiomechanikRegisterGeltung.GESPERRT: BiomechanikRegisterTyp.BIOMECHANIKREGISTER,
    BiomechanikRegisterGeltung.GRUNDLEGEND_BIOMECHANISCH: BiomechanikRegisterTyp.BEWEGUNGSANALYSE,
    BiomechanikRegisterGeltung.BIOMECHANISCH: BiomechanikRegisterTyp.BEWEGUNGSANALYSE,
    BiomechanikRegisterGeltung.BIOMECHANISCH_AKTIV: BiomechanikRegisterTyp.KRAFTMESSPROTOKOLL,
    BiomechanikRegisterGeltung.BIOMECHANIK_SOUVERAEN: BiomechanikRegisterTyp.KRAFTMESSPROTOKOLL,
}

_PROZEDUR_MAP = {
    BiomechanikRegisterGeltung.GESPERRT: BiomechanikRegisterProzedur.KINEMATIKANALYSE,
    BiomechanikRegisterGeltung.GRUNDLEGEND_BIOMECHANISCH: BiomechanikRegisterProzedur.KINEMATIKANALYSE,
    BiomechanikRegisterGeltung.BIOMECHANISCH: BiomechanikRegisterProzedur.KINETIKBERECHNUNG,
    BiomechanikRegisterGeltung.BIOMECHANISCH_AKTIV: BiomechanikRegisterProzedur.KINETIKBERECHNUNG,
    BiomechanikRegisterGeltung.BIOMECHANIK_SOUVERAEN: BiomechanikRegisterProzedur.BEWEGUNGSOPTIMIERUNG,
}


@dataclass(frozen=True)
class BiomechanikRegisterEintrag:
    geltung: BiomechanikRegisterGeltung
    sport_weight: float
    sport_tier: int
    sport_ids: tuple[str, ...]
    sport_tags: tuple[str, ...]
    typ: BiomechanikRegisterTyp
    prozedur: BiomechanikRegisterProzedur
    canonical: bool = True


@dataclass(frozen=True)
class BiomechanikRegister:
    eintraege: tuple[BiomechanikRegisterEintrag, ...]
    parent: Optional[SportFeld] = None


def build_biomechanik_register(parent: Optional[SportFeld] = None) -> BiomechanikRegister:
    if parent is None:
        parent = build_sport_feld()
    base = sum(n.sport_weight for n in parent.normen)
    eintraege = tuple(
        BiomechanikRegisterEintrag(
            geltung=g,
            sport_weight=round(base + _WEIGHT_DELTA[g], 4),
            sport_tier=i + 1,
            sport_ids=(f"biomechanik-{g.name.lower()}-001",),
            sport_tags=("biomechanik", "register", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(BiomechanikRegisterGeltung)
    )
    return BiomechanikRegister(eintraege=eintraege, parent=parent)
