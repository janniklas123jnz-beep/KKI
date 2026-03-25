from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .klima_verfassung import KlimaVerfassung, build_klima_verfassung


class StatistikFeldGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_STATISTISCH = auto()
    STATISTISCH = auto()
    STATISTISCH_AKTIV = auto()
    STATISTIK_SOUVERAEN = auto()


class StatistikFeldTyp(Enum):
    STATISTIKFELD = auto()
    STATISTIKSYSTEM = auto()
    STATISTIKKOMPONENTE = auto()


class StatistikFeldProzedur(Enum):
    STATISTIKANALYSE = auto()
    STATISTIKSYNTHESE = auto()
    STATISTIKBEWERTUNG = auto()


_WEIGHT_DELTA: dict[StatistikFeldGeltung, float] = {
    StatistikFeldGeltung.GESPERRT: 0.0,
    StatistikFeldGeltung.GRUNDLEGEND_STATISTISCH: 1.2,
    StatistikFeldGeltung.STATISTISCH: 2.4,
    StatistikFeldGeltung.STATISTISCH_AKTIV: 3.6,
    StatistikFeldGeltung.STATISTIK_SOUVERAEN: 5.0,
}

_TYP_MAP = {
    StatistikFeldGeltung.GESPERRT: StatistikFeldTyp.STATISTIKFELD,
    StatistikFeldGeltung.GRUNDLEGEND_STATISTISCH: StatistikFeldTyp.STATISTIKKOMPONENTE,
    StatistikFeldGeltung.STATISTISCH: StatistikFeldTyp.STATISTIKKOMPONENTE,
    StatistikFeldGeltung.STATISTISCH_AKTIV: StatistikFeldTyp.STATISTIKSYSTEM,
    StatistikFeldGeltung.STATISTIK_SOUVERAEN: StatistikFeldTyp.STATISTIKSYSTEM,
}

_PROZEDUR_MAP = {
    StatistikFeldGeltung.GESPERRT: StatistikFeldProzedur.STATISTIKANALYSE,
    StatistikFeldGeltung.GRUNDLEGEND_STATISTISCH: StatistikFeldProzedur.STATISTIKANALYSE,
    StatistikFeldGeltung.STATISTISCH: StatistikFeldProzedur.STATISTIKSYNTHESE,
    StatistikFeldGeltung.STATISTISCH_AKTIV: StatistikFeldProzedur.STATISTIKSYNTHESE,
    StatistikFeldGeltung.STATISTIK_SOUVERAEN: StatistikFeldProzedur.STATISTIKBEWERTUNG,
}


@dataclass(frozen=True)
class StatistikFeldNorm:
    geltung: StatistikFeldGeltung
    stat_weight: float
    stat_tier: int
    stat_ids: tuple[str, ...]
    stat_tags: tuple[str, ...]
    typ: StatistikFeldTyp
    prozedur: StatistikFeldProzedur
    canonical: bool = True


@dataclass(frozen=True)
class StatistikFeld:
    normen: tuple[StatistikFeldNorm, ...]
    parent: Optional[KlimaVerfassung] = None


def build_statistik_feld(parent: Optional[KlimaVerfassung] = None) -> StatistikFeld:
    if parent is None:
        parent = build_klima_verfassung()
    base = sum(n.klima_weight for n in parent.normen)
    normen = tuple(
        StatistikFeldNorm(
            geltung=g,
            stat_weight=round(base + _WEIGHT_DELTA[g], 4),
            stat_tier=i + 1,
            stat_ids=(f"statistik-feld-{g.name.lower()}-001",),
            stat_tags=("statistik", "feld", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(StatistikFeldGeltung)
    )
    return StatistikFeld(normen=normen, parent=parent)
