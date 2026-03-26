from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .ozean_verfassung import OzeanVerfassung, build_ozean_verfassung


class GeophysikFeldGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_GEOPHYSIKALISCH = auto()
    GEOPHYSIKALISCH = auto()
    GEOPHYSIKALISCH_AKTIV = auto()
    GEOPHYSIK_SOUVERAEN = auto()


class GeophysikFeldTyp(Enum):
    GEOPHYSIKFELD = auto()
    GEOPHYSIKSYSTEM = auto()
    GEOPHYSIKKOMPONENTE = auto()


class GeophysikFeldProzedur(Enum):
    GEOPHYSIKANALYSE = auto()
    GEOPHYSIKSYNTHESE = auto()
    GEOPHYSIKBEWERTUNG = auto()


_WEIGHT_DELTA: dict[GeophysikFeldGeltung, float] = {
    GeophysikFeldGeltung.GESPERRT: 0.0,
    GeophysikFeldGeltung.GRUNDLEGEND_GEOPHYSIKALISCH: 1.2,
    GeophysikFeldGeltung.GEOPHYSIKALISCH: 2.4,
    GeophysikFeldGeltung.GEOPHYSIKALISCH_AKTIV: 3.6,
    GeophysikFeldGeltung.GEOPHYSIK_SOUVERAEN: 5.0,
}

_TYP_MAP = {
    GeophysikFeldGeltung.GESPERRT: GeophysikFeldTyp.GEOPHYSIKFELD,
    GeophysikFeldGeltung.GRUNDLEGEND_GEOPHYSIKALISCH: GeophysikFeldTyp.GEOPHYSIKKOMPONENTE,
    GeophysikFeldGeltung.GEOPHYSIKALISCH: GeophysikFeldTyp.GEOPHYSIKKOMPONENTE,
    GeophysikFeldGeltung.GEOPHYSIKALISCH_AKTIV: GeophysikFeldTyp.GEOPHYSIKSYSTEM,
    GeophysikFeldGeltung.GEOPHYSIK_SOUVERAEN: GeophysikFeldTyp.GEOPHYSIKSYSTEM,
}

_PROZEDUR_MAP = {
    GeophysikFeldGeltung.GESPERRT: GeophysikFeldProzedur.GEOPHYSIKANALYSE,
    GeophysikFeldGeltung.GRUNDLEGEND_GEOPHYSIKALISCH: GeophysikFeldProzedur.GEOPHYSIKANALYSE,
    GeophysikFeldGeltung.GEOPHYSIKALISCH: GeophysikFeldProzedur.GEOPHYSIKSYNTHESE,
    GeophysikFeldGeltung.GEOPHYSIKALISCH_AKTIV: GeophysikFeldProzedur.GEOPHYSIKSYNTHESE,
    GeophysikFeldGeltung.GEOPHYSIK_SOUVERAEN: GeophysikFeldProzedur.GEOPHYSIKBEWERTUNG,
}


@dataclass(frozen=True)
class GeophysikFeldNorm:
    geltung: GeophysikFeldGeltung
    geophysik_weight: float
    geophysik_tier: int
    geophysik_ids: tuple[str, ...]
    geophysik_tags: tuple[str, ...]
    typ: GeophysikFeldTyp
    prozedur: GeophysikFeldProzedur
    canonical: bool = True


@dataclass(frozen=True)
class GeophysikFeld:
    normen: tuple[GeophysikFeldNorm, ...]
    parent: Optional[OzeanVerfassung] = None


def build_geophysik_feld(parent: Optional[OzeanVerfassung] = None) -> GeophysikFeld:
    if parent is None:
        parent = build_ozean_verfassung()
    base = sum(n.ozean_weight for n in parent.normen)
    normen = tuple(
        GeophysikFeldNorm(
            geltung=g,
            geophysik_weight=round(base + _WEIGHT_DELTA[g], 4),
            geophysik_tier=i + 1,
            geophysik_ids=(f"geophysik-feld-{g.name.lower()}-001",),
            geophysik_tags=("geophysik", "feld", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(GeophysikFeldGeltung)
    )
    return GeophysikFeld(normen=normen, parent=parent)
