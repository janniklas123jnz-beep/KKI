from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .agrar_verfassung import AgrarVerfassung, build_agrar_verfassung


class OzeanFeldGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_OZEANOGRAPHISCH = auto()
    OZEANOGRAPHISCH = auto()
    OZEANOGRAPHISCH_AKTIV = auto()
    OZEAN_SOUVERAEN = auto()


class OzeanFeldTyp(Enum):
    OZEANFELD = auto()
    OZEANSYSTEM = auto()
    OZEANKOMPONENTE = auto()


class OzeanFeldProzedur(Enum):
    OZEANANALYSE = auto()
    OZEANSYNTHESE = auto()
    OZEANBEWERTUNG = auto()


_WEIGHT_DELTA: dict[OzeanFeldGeltung, float] = {
    OzeanFeldGeltung.GESPERRT: 0.0,
    OzeanFeldGeltung.GRUNDLEGEND_OZEANOGRAPHISCH: 1.2,
    OzeanFeldGeltung.OZEANOGRAPHISCH: 2.4,
    OzeanFeldGeltung.OZEANOGRAPHISCH_AKTIV: 3.6,
    OzeanFeldGeltung.OZEAN_SOUVERAEN: 5.0,
}

_TYP_MAP = {
    OzeanFeldGeltung.GESPERRT: OzeanFeldTyp.OZEANFELD,
    OzeanFeldGeltung.GRUNDLEGEND_OZEANOGRAPHISCH: OzeanFeldTyp.OZEANKOMPONENTE,
    OzeanFeldGeltung.OZEANOGRAPHISCH: OzeanFeldTyp.OZEANKOMPONENTE,
    OzeanFeldGeltung.OZEANOGRAPHISCH_AKTIV: OzeanFeldTyp.OZEANSYSTEM,
    OzeanFeldGeltung.OZEAN_SOUVERAEN: OzeanFeldTyp.OZEANSYSTEM,
}

_PROZEDUR_MAP = {
    OzeanFeldGeltung.GESPERRT: OzeanFeldProzedur.OZEANANALYSE,
    OzeanFeldGeltung.GRUNDLEGEND_OZEANOGRAPHISCH: OzeanFeldProzedur.OZEANANALYSE,
    OzeanFeldGeltung.OZEANOGRAPHISCH: OzeanFeldProzedur.OZEANSYNTHESE,
    OzeanFeldGeltung.OZEANOGRAPHISCH_AKTIV: OzeanFeldProzedur.OZEANSYNTHESE,
    OzeanFeldGeltung.OZEAN_SOUVERAEN: OzeanFeldProzedur.OZEANBEWERTUNG,
}


@dataclass(frozen=True)
class OzeanFeldNorm:
    geltung: OzeanFeldGeltung
    ozean_weight: float
    ozean_tier: int
    ozean_ids: tuple[str, ...]
    ozean_tags: tuple[str, ...]
    typ: OzeanFeldTyp
    prozedur: OzeanFeldProzedur
    canonical: bool = True


@dataclass(frozen=True)
class OzeanFeld:
    normen: tuple[OzeanFeldNorm, ...]
    parent: Optional[AgrarVerfassung] = None


def build_ozean_feld(parent: Optional[AgrarVerfassung] = None) -> OzeanFeld:
    if parent is None:
        parent = build_agrar_verfassung()
    base = sum(n.agrar_weight for n in parent.normen)
    normen = tuple(
        OzeanFeldNorm(
            geltung=g,
            ozean_weight=round(base + _WEIGHT_DELTA[g], 4),
            ozean_tier=i + 1,
            ozean_ids=(f"ozean-feld-{g.name.lower()}-001",),
            ozean_tags=("ozean", "feld", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(OzeanFeldGeltung)
    )
    return OzeanFeld(normen=normen, parent=parent)
