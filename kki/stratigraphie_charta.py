from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .fossilien_register import FossilienRegister, build_fossilien_register


class StratigraphieChartaGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_PALAEONTOLOGISCH = auto()
    PALAEONTOLOGISCH = auto()
    PALAEONTOLOGISCH_AKTIV = auto()
    PALAEONTOLOGIE_SOUVERAEN = auto()


class StratigraphieChartaTyp(Enum):
    STRATIGRAPHIECHARTA = auto()
    STRATIGRAPHIESYSTEM = auto()
    STRATIGRAPHIEKOMPONENTE = auto()


class StratigraphieChartaProzedur(Enum):
    STRATIGRAPHIEANALYSE = auto()
    STRATIGRAPHIESYNTHESE = auto()
    STRATIGRAPHIEBEWERTUNG = auto()


_WEIGHT_DELTA: dict[StratigraphieChartaGeltung, float] = {
    StratigraphieChartaGeltung.GESPERRT: 0.0,
    StratigraphieChartaGeltung.GRUNDLEGEND_PALAEONTOLOGISCH: 1.4,
    StratigraphieChartaGeltung.PALAEONTOLOGISCH: 2.8,
    StratigraphieChartaGeltung.PALAEONTOLOGISCH_AKTIV: 4.2,
    StratigraphieChartaGeltung.PALAEONTOLOGIE_SOUVERAEN: 5.6,
}

_TYP_MAP = {
    StratigraphieChartaGeltung.GESPERRT: StratigraphieChartaTyp.STRATIGRAPHIECHARTA,
    StratigraphieChartaGeltung.GRUNDLEGEND_PALAEONTOLOGISCH: StratigraphieChartaTyp.STRATIGRAPHIEKOMPONENTE,
    StratigraphieChartaGeltung.PALAEONTOLOGISCH: StratigraphieChartaTyp.STRATIGRAPHIEKOMPONENTE,
    StratigraphieChartaGeltung.PALAEONTOLOGISCH_AKTIV: StratigraphieChartaTyp.STRATIGRAPHIESYSTEM,
    StratigraphieChartaGeltung.PALAEONTOLOGIE_SOUVERAEN: StratigraphieChartaTyp.STRATIGRAPHIESYSTEM,
}

_PROZEDUR_MAP = {
    StratigraphieChartaGeltung.GESPERRT: StratigraphieChartaProzedur.STRATIGRAPHIEANALYSE,
    StratigraphieChartaGeltung.GRUNDLEGEND_PALAEONTOLOGISCH: StratigraphieChartaProzedur.STRATIGRAPHIEANALYSE,
    StratigraphieChartaGeltung.PALAEONTOLOGISCH: StratigraphieChartaProzedur.STRATIGRAPHIESYNTHESE,
    StratigraphieChartaGeltung.PALAEONTOLOGISCH_AKTIV: StratigraphieChartaProzedur.STRATIGRAPHIESYNTHESE,
    StratigraphieChartaGeltung.PALAEONTOLOGIE_SOUVERAEN: StratigraphieChartaProzedur.STRATIGRAPHIEBEWERTUNG,
}


@dataclass(frozen=True)
class StratigraphieChartaNorm:
    geltung: StratigraphieChartaGeltung
    palaeontologie_weight: float
    palaeontologie_tier: int
    palaeontologie_ids: tuple[str, ...]
    palaeontologie_tags: tuple[str, ...]
    typ: StratigraphieChartaTyp
    prozedur: StratigraphieChartaProzedur
    canonical: bool = True


@dataclass(frozen=True)
class StratigraphieCharta:
    normen: tuple[StratigraphieChartaNorm, ...]
    parent: Optional[FossilienRegister] = None


def build_stratigraphie_charta(parent: Optional[FossilienRegister] = None) -> StratigraphieCharta:
    if parent is None:
        parent = build_fossilien_register()
    base = sum(e.palaeontologie_weight for e in parent.eintraege)
    normen = tuple(
        StratigraphieChartaNorm(
            geltung=g,
            palaeontologie_weight=round(base + _WEIGHT_DELTA[g], 4),
            palaeontologie_tier=i + 1,
            palaeontologie_ids=(f"stratigraphie-charta-{g.name.lower()}-001",),
            palaeontologie_tags=("palaeontologie", "stratigraphie", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(StratigraphieChartaGeltung)
    )
    return StratigraphieCharta(normen=normen, parent=parent)
