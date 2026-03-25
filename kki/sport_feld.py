from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .pharma_verfassung import PharmaVerfassung, build_pharma_verfassung


class SportFeldGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_SPORTLICH = auto()
    SPORTLICH = auto()
    SPORTLICH_AKTIV = auto()
    SPORT_SOUVERAEN = auto()


class SportFeldTyp(Enum):
    SPORTFELD = auto()
    SPORTSYSTEM = auto()
    SPORTKOMPONENTE = auto()


class SportFeldProzedur(Enum):
    SPORTANALYSE = auto()
    SPORTSYNTHESE = auto()
    SPORTBEWERTUNG = auto()


_WEIGHT_DELTA: dict[SportFeldGeltung, float] = {
    SportFeldGeltung.GESPERRT: 0.0,
    SportFeldGeltung.GRUNDLEGEND_SPORTLICH: 1.2,
    SportFeldGeltung.SPORTLICH: 2.4,
    SportFeldGeltung.SPORTLICH_AKTIV: 3.6,
    SportFeldGeltung.SPORT_SOUVERAEN: 5.0,
}

_TYP_MAP = {
    SportFeldGeltung.GESPERRT: SportFeldTyp.SPORTFELD,
    SportFeldGeltung.GRUNDLEGEND_SPORTLICH: SportFeldTyp.SPORTKOMPONENTE,
    SportFeldGeltung.SPORTLICH: SportFeldTyp.SPORTKOMPONENTE,
    SportFeldGeltung.SPORTLICH_AKTIV: SportFeldTyp.SPORTSYSTEM,
    SportFeldGeltung.SPORT_SOUVERAEN: SportFeldTyp.SPORTSYSTEM,
}

_PROZEDUR_MAP = {
    SportFeldGeltung.GESPERRT: SportFeldProzedur.SPORTANALYSE,
    SportFeldGeltung.GRUNDLEGEND_SPORTLICH: SportFeldProzedur.SPORTANALYSE,
    SportFeldGeltung.SPORTLICH: SportFeldProzedur.SPORTSYNTHESE,
    SportFeldGeltung.SPORTLICH_AKTIV: SportFeldProzedur.SPORTSYNTHESE,
    SportFeldGeltung.SPORT_SOUVERAEN: SportFeldProzedur.SPORTBEWERTUNG,
}


@dataclass(frozen=True)
class SportFeldNorm:
    geltung: SportFeldGeltung
    sport_weight: float
    sport_tier: int
    sport_ids: tuple[str, ...]
    sport_tags: tuple[str, ...]
    typ: SportFeldTyp
    prozedur: SportFeldProzedur
    canonical: bool = True


@dataclass(frozen=True)
class SportFeld:
    normen: tuple[SportFeldNorm, ...]
    parent: Optional[PharmaVerfassung] = None


def build_sport_feld(parent: Optional[PharmaVerfassung] = None) -> SportFeld:
    if parent is None:
        parent = build_pharma_verfassung()
    base = sum(n.pharma_weight for n in parent.normen)
    normen = tuple(
        SportFeldNorm(
            geltung=g,
            sport_weight=round(base + _WEIGHT_DELTA[g], 4),
            sport_tier=i + 1,
            sport_ids=(f"sport-feld-{g.name.lower()}-001",),
            sport_tags=("sport", "feld", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(SportFeldGeltung)
    )
    return SportFeld(normen=normen, parent=parent)
