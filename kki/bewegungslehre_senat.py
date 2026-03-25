from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .sportpsychologie_pakt import SportpsychologiePakt, build_sportpsychologie_pakt


class BewegungslehreSenatGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_BEWEGUNGSWISSENSCHAFTLICH = auto()
    BEWEGUNGSWISSENSCHAFTLICH = auto()
    BEWEGUNGSWISSENSCHAFTLICH_AKTIV = auto()
    BEWEGUNGSLEHRE_SOUVERAEN = auto()


class BewegungslehreSenatTyp(Enum):
    BEWEGUNGSLEHRESENAT = auto()
    KOORDINATIONSRAT = auto()
    BEWEGUNGSMUSTERAUSSCHUSS = auto()


class BewegungslehreSenatProzedur(Enum):
    KOORDINATIONSANALYSE = auto()
    BEWEGUNGSMUSTERERFASSUNG = auto()
    MOTORIKBEWERTUNG = auto()


_WEIGHT_DELTA: dict[BewegungslehreSenatGeltung, float] = {
    BewegungslehreSenatGeltung.GESPERRT: 0.0,
    BewegungslehreSenatGeltung.GRUNDLEGEND_BEWEGUNGSWISSENSCHAFTLICH: 1.8,
    BewegungslehreSenatGeltung.BEWEGUNGSWISSENSCHAFTLICH: 3.6,
    BewegungslehreSenatGeltung.BEWEGUNGSWISSENSCHAFTLICH_AKTIV: 5.4,
    BewegungslehreSenatGeltung.BEWEGUNGSLEHRE_SOUVERAEN: 7.2,
}

_TYP_MAP = {
    BewegungslehreSenatGeltung.GESPERRT: BewegungslehreSenatTyp.BEWEGUNGSLEHRESENAT,
    BewegungslehreSenatGeltung.GRUNDLEGEND_BEWEGUNGSWISSENSCHAFTLICH: BewegungslehreSenatTyp.KOORDINATIONSRAT,
    BewegungslehreSenatGeltung.BEWEGUNGSWISSENSCHAFTLICH: BewegungslehreSenatTyp.KOORDINATIONSRAT,
    BewegungslehreSenatGeltung.BEWEGUNGSWISSENSCHAFTLICH_AKTIV: BewegungslehreSenatTyp.BEWEGUNGSMUSTERAUSSCHUSS,
    BewegungslehreSenatGeltung.BEWEGUNGSLEHRE_SOUVERAEN: BewegungslehreSenatTyp.BEWEGUNGSMUSTERAUSSCHUSS,
}

_PROZEDUR_MAP = {
    BewegungslehreSenatGeltung.GESPERRT: BewegungslehreSenatProzedur.KOORDINATIONSANALYSE,
    BewegungslehreSenatGeltung.GRUNDLEGEND_BEWEGUNGSWISSENSCHAFTLICH: BewegungslehreSenatProzedur.KOORDINATIONSANALYSE,
    BewegungslehreSenatGeltung.BEWEGUNGSWISSENSCHAFTLICH: BewegungslehreSenatProzedur.BEWEGUNGSMUSTERERFASSUNG,
    BewegungslehreSenatGeltung.BEWEGUNGSWISSENSCHAFTLICH_AKTIV: BewegungslehreSenatProzedur.BEWEGUNGSMUSTERERFASSUNG,
    BewegungslehreSenatGeltung.BEWEGUNGSLEHRE_SOUVERAEN: BewegungslehreSenatProzedur.MOTORIKBEWERTUNG,
}


@dataclass(frozen=True)
class BewegungslehreSenatNorm:
    geltung: BewegungslehreSenatGeltung
    sport_weight: float
    sport_tier: int
    sport_ids: tuple[str, ...]
    sport_tags: tuple[str, ...]
    typ: BewegungslehreSenatTyp
    prozedur: BewegungslehreSenatProzedur
    canonical: bool = True


@dataclass(frozen=True)
class BewegungslehreSenat:
    normen: tuple[BewegungslehreSenatNorm, ...]
    parent: Optional[SportpsychologiePakt] = None


def build_bewegungslehre_senat(parent: Optional[SportpsychologiePakt] = None) -> BewegungslehreSenat:
    if parent is None:
        parent = build_sportpsychologie_pakt()
    base = sum(e.sport_weight for e in parent.eintraege)
    normen = tuple(
        BewegungslehreSenatNorm(
            geltung=g,
            sport_weight=round(base + _WEIGHT_DELTA[g], 4),
            sport_tier=i + 1,
            sport_ids=(f"bewegungslehre-senat-{g.name.lower()}-001",),
            sport_tags=("bewegungslehre", "senat", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(BewegungslehreSenatGeltung)
    )
    return BewegungslehreSenat(normen=normen, parent=parent)
