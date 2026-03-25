from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .meeresstroemung_register import MeeresstroemungRegister, build_meeresstroemung_register


class TiefseekartierungChartaGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_OZEANOGRAPHISCH = auto()
    OZEANOGRAPHISCH = auto()
    OZEANOGRAPHISCH_AKTIV = auto()
    OZEAN_SOUVERAEN = auto()


class TiefseekartierungChartaTyp(Enum):
    TIEFSEEKARTIERUNG = auto()
    BATHYMETRIESYSTEM = auto()
    KARTIERUNGSKOMPONENTE = auto()


class TiefseekartierungChartaProzedur(Enum):
    KARTIERUNGSANALYSE = auto()
    KARTIERUNGSSYNTHESE = auto()
    KARTIERUNGSBEWERTUNG = auto()


_WEIGHT_DELTA: dict[TiefseekartierungChartaGeltung, float] = {
    TiefseekartierungChartaGeltung.GESPERRT: 0.0,
    TiefseekartierungChartaGeltung.GRUNDLEGEND_OZEANOGRAPHISCH: 1.4,
    TiefseekartierungChartaGeltung.OZEANOGRAPHISCH: 2.8,
    TiefseekartierungChartaGeltung.OZEANOGRAPHISCH_AKTIV: 4.2,
    TiefseekartierungChartaGeltung.OZEAN_SOUVERAEN: 5.6,
}

_TYP_MAP = {
    TiefseekartierungChartaGeltung.GESPERRT: TiefseekartierungChartaTyp.TIEFSEEKARTIERUNG,
    TiefseekartierungChartaGeltung.GRUNDLEGEND_OZEANOGRAPHISCH: TiefseekartierungChartaTyp.KARTIERUNGSKOMPONENTE,
    TiefseekartierungChartaGeltung.OZEANOGRAPHISCH: TiefseekartierungChartaTyp.KARTIERUNGSKOMPONENTE,
    TiefseekartierungChartaGeltung.OZEANOGRAPHISCH_AKTIV: TiefseekartierungChartaTyp.BATHYMETRIESYSTEM,
    TiefseekartierungChartaGeltung.OZEAN_SOUVERAEN: TiefseekartierungChartaTyp.BATHYMETRIESYSTEM,
}

_PROZEDUR_MAP = {
    TiefseekartierungChartaGeltung.GESPERRT: TiefseekartierungChartaProzedur.KARTIERUNGSANALYSE,
    TiefseekartierungChartaGeltung.GRUNDLEGEND_OZEANOGRAPHISCH: TiefseekartierungChartaProzedur.KARTIERUNGSANALYSE,
    TiefseekartierungChartaGeltung.OZEANOGRAPHISCH: TiefseekartierungChartaProzedur.KARTIERUNGSSYNTHESE,
    TiefseekartierungChartaGeltung.OZEANOGRAPHISCH_AKTIV: TiefseekartierungChartaProzedur.KARTIERUNGSSYNTHESE,
    TiefseekartierungChartaGeltung.OZEAN_SOUVERAEN: TiefseekartierungChartaProzedur.KARTIERUNGSBEWERTUNG,
}


@dataclass(frozen=True)
class TiefseekartierungChartaNorm:
    geltung: TiefseekartierungChartaGeltung
    ozean_weight: float
    ozean_tier: int
    ozean_ids: tuple[str, ...]
    ozean_tags: tuple[str, ...]
    typ: TiefseekartierungChartaTyp
    prozedur: TiefseekartierungChartaProzedur
    canonical: bool = True


@dataclass(frozen=True)
class TiefseekartierungCharta:
    normen: tuple[TiefseekartierungChartaNorm, ...]
    parent: Optional[MeeresstroemungRegister] = None


def build_tiefseekartierung_charta(parent: Optional[MeeresstroemungRegister] = None) -> TiefseekartierungCharta:
    if parent is None:
        parent = build_meeresstroemung_register()
    base = sum(e.ozean_weight for e in parent.eintraege)
    normen = tuple(
        TiefseekartierungChartaNorm(
            geltung=g,
            ozean_weight=round(base + _WEIGHT_DELTA[g], 4),
            ozean_tier=i + 1,
            ozean_ids=(f"tiefseekartierung-{g.name.lower()}-001",),
            ozean_tags=("ozean", "tiefseekartierung", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(TiefseekartierungChartaGeltung)
    )
    return TiefseekartierungCharta(normen=normen, parent=parent)
