from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .seismologie_register import SeismologieRegister, build_seismologie_register


class TektonikChartaGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_GEOPHYSIKALISCH = auto()
    GEOPHYSIKALISCH = auto()
    GEOPHYSIKALISCH_AKTIV = auto()
    GEOPHYSIK_SOUVERAEN = auto()


class TektonikChartaTyp(Enum):
    TEKTONIK = auto()
    PLATTENSYSTEM = auto()
    TEKTONIKKOMPONENTE = auto()


class TektonikChartaProzedur(Enum):
    TEKTONIKANALYSE = auto()
    TEKTONIKSYNTHESE = auto()
    TEKTONIKBEWERTUNG = auto()


_WEIGHT_DELTA: dict[TektonikChartaGeltung, float] = {
    TektonikChartaGeltung.GESPERRT: 0.0,
    TektonikChartaGeltung.GRUNDLEGEND_GEOPHYSIKALISCH: 1.4,
    TektonikChartaGeltung.GEOPHYSIKALISCH: 2.8,
    TektonikChartaGeltung.GEOPHYSIKALISCH_AKTIV: 4.2,
    TektonikChartaGeltung.GEOPHYSIK_SOUVERAEN: 5.6,
}

_TYP_MAP = {
    TektonikChartaGeltung.GESPERRT: TektonikChartaTyp.TEKTONIK,
    TektonikChartaGeltung.GRUNDLEGEND_GEOPHYSIKALISCH: TektonikChartaTyp.TEKTONIKKOMPONENTE,
    TektonikChartaGeltung.GEOPHYSIKALISCH: TektonikChartaTyp.TEKTONIKKOMPONENTE,
    TektonikChartaGeltung.GEOPHYSIKALISCH_AKTIV: TektonikChartaTyp.PLATTENSYSTEM,
    TektonikChartaGeltung.GEOPHYSIK_SOUVERAEN: TektonikChartaTyp.PLATTENSYSTEM,
}

_PROZEDUR_MAP = {
    TektonikChartaGeltung.GESPERRT: TektonikChartaProzedur.TEKTONIKANALYSE,
    TektonikChartaGeltung.GRUNDLEGEND_GEOPHYSIKALISCH: TektonikChartaProzedur.TEKTONIKANALYSE,
    TektonikChartaGeltung.GEOPHYSIKALISCH: TektonikChartaProzedur.TEKTONIKSYNTHESE,
    TektonikChartaGeltung.GEOPHYSIKALISCH_AKTIV: TektonikChartaProzedur.TEKTONIKSYNTHESE,
    TektonikChartaGeltung.GEOPHYSIK_SOUVERAEN: TektonikChartaProzedur.TEKTONIKBEWERTUNG,
}


@dataclass(frozen=True)
class TektonikChartaNorm:
    geltung: TektonikChartaGeltung
    geophysik_weight: float
    geophysik_tier: int
    geophysik_ids: tuple[str, ...]
    geophysik_tags: tuple[str, ...]
    typ: TektonikChartaTyp
    prozedur: TektonikChartaProzedur
    canonical: bool = True


@dataclass(frozen=True)
class TektonikCharta:
    normen: tuple[TektonikChartaNorm, ...]
    parent: Optional[SeismologieRegister] = None


def build_tektonik_charta(parent: Optional[SeismologieRegister] = None) -> TektonikCharta:
    if parent is None:
        parent = build_seismologie_register()
    base = sum(e.geophysik_weight for e in parent.eintraege)
    normen = tuple(
        TektonikChartaNorm(
            geltung=g,
            geophysik_weight=round(base + _WEIGHT_DELTA[g], 4),
            geophysik_tier=i + 1,
            geophysik_ids=(f"tektonik-{g.name.lower()}-001",),
            geophysik_tags=("geophysik", "tektonik", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(TektonikChartaGeltung)
    )
    return TektonikCharta(normen=normen, parent=parent)
