from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .atmosphaere_register import AtmosphaereRegister, build_atmosphaere_register


class MeteorologieChartaGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_METEOROLOGISCH = auto()
    METEOROLOGISCH = auto()
    METEOROLOGISCH_AKTIV = auto()
    METEOROLOGIE_SOUVERAEN = auto()


class MeteorologieChartaTyp(Enum):
    METEOROLOGIECHARTA = auto()
    WETTERMUSTER = auto()
    KLIMAPHÄNOMEN = auto()


class MeteorologieChartaProzedur(Enum):
    WETTERANALYSE = auto()
    WETTERSYNTHESE = auto()
    WETTERBEWERTUNG = auto()


_WEIGHT_DELTA: dict[MeteorologieChartaGeltung, float] = {
    MeteorologieChartaGeltung.GESPERRT: 0.0,
    MeteorologieChartaGeltung.GRUNDLEGEND_METEOROLOGISCH: 1.4,
    MeteorologieChartaGeltung.METEOROLOGISCH: 2.8,
    MeteorologieChartaGeltung.METEOROLOGISCH_AKTIV: 4.2,
    MeteorologieChartaGeltung.METEOROLOGIE_SOUVERAEN: 5.6,
}

_TYP_MAP = {
    MeteorologieChartaGeltung.GESPERRT: MeteorologieChartaTyp.METEOROLOGIECHARTA,
    MeteorologieChartaGeltung.GRUNDLEGEND_METEOROLOGISCH: MeteorologieChartaTyp.KLIMAPHÄNOMEN,
    MeteorologieChartaGeltung.METEOROLOGISCH: MeteorologieChartaTyp.KLIMAPHÄNOMEN,
    MeteorologieChartaGeltung.METEOROLOGISCH_AKTIV: MeteorologieChartaTyp.WETTERMUSTER,
    MeteorologieChartaGeltung.METEOROLOGIE_SOUVERAEN: MeteorologieChartaTyp.WETTERMUSTER,
}

_PROZEDUR_MAP = {
    MeteorologieChartaGeltung.GESPERRT: MeteorologieChartaProzedur.WETTERANALYSE,
    MeteorologieChartaGeltung.GRUNDLEGEND_METEOROLOGISCH: MeteorologieChartaProzedur.WETTERANALYSE,
    MeteorologieChartaGeltung.METEOROLOGISCH: MeteorologieChartaProzedur.WETTERSYNTHESE,
    MeteorologieChartaGeltung.METEOROLOGISCH_AKTIV: MeteorologieChartaProzedur.WETTERSYNTHESE,
    MeteorologieChartaGeltung.METEOROLOGIE_SOUVERAEN: MeteorologieChartaProzedur.WETTERBEWERTUNG,
}


@dataclass(frozen=True)
class MeteorologieChartaNorm:
    geltung: MeteorologieChartaGeltung
    klima_weight: float
    klima_tier: int
    klima_ids: tuple[str, ...]
    klima_tags: tuple[str, ...]
    typ: MeteorologieChartaTyp
    prozedur: MeteorologieChartaProzedur
    canonical: bool = True


@dataclass(frozen=True)
class MeteorologieCharta:
    normen: tuple[MeteorologieChartaNorm, ...]
    parent: Optional[AtmosphaereRegister] = None


def build_meteorologie_charta(parent: Optional[AtmosphaereRegister] = None) -> MeteorologieCharta:
    if parent is None:
        parent = build_atmosphaere_register()
    base = sum(e.klima_weight for e in parent.eintraege)
    normen = tuple(
        MeteorologieChartaNorm(
            geltung=g,
            klima_weight=round(base + _WEIGHT_DELTA[g], 4),
            klima_tier=i + 1,
            klima_ids=(f"meteorologie-charta-{g.name.lower()}-001",),
            klima_tags=("meteorologie", "charta", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(MeteorologieChartaGeltung)
    )
    return MeteorologieCharta(normen=normen, parent=parent)
