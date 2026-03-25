from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .sport_norm import SportNormSatz, build_sport_norm


class SportmedizinChartaGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_SPORTMEDIZINISCH = auto()
    SPORTMEDIZINISCH = auto()
    SPORTMEDIZINISCH_AKTIV = auto()
    SPORTMEDIZIN_SOUVERAEN = auto()


class SportmedizinChartaTyp(Enum):
    SPORTMEDIZINCHARTA = auto()
    VERLETZUNGSPRAEVENTION = auto()
    REHABILITATIONSPROTOKOLL = auto()


class SportmedizinChartaProzedur(Enum):
    SPORTTAUGLICHKEITSUNTERSUCHUNG = auto()
    VERLETZUNGSDIAGNOSTIK = auto()
    REHABILITATIONSBEWERTUNG = auto()


_WEIGHT_DELTA: dict[SportmedizinChartaGeltung, float] = {
    SportmedizinChartaGeltung.GESPERRT: 0.0,
    SportmedizinChartaGeltung.GRUNDLEGEND_SPORTMEDIZINISCH: 2.0,
    SportmedizinChartaGeltung.SPORTMEDIZINISCH: 4.0,
    SportmedizinChartaGeltung.SPORTMEDIZINISCH_AKTIV: 6.0,
    SportmedizinChartaGeltung.SPORTMEDIZIN_SOUVERAEN: 8.0,
}

_TYP_MAP = {
    SportmedizinChartaGeltung.GESPERRT: SportmedizinChartaTyp.SPORTMEDIZINCHARTA,
    SportmedizinChartaGeltung.GRUNDLEGEND_SPORTMEDIZINISCH: SportmedizinChartaTyp.VERLETZUNGSPRAEVENTION,
    SportmedizinChartaGeltung.SPORTMEDIZINISCH: SportmedizinChartaTyp.VERLETZUNGSPRAEVENTION,
    SportmedizinChartaGeltung.SPORTMEDIZINISCH_AKTIV: SportmedizinChartaTyp.REHABILITATIONSPROTOKOLL,
    SportmedizinChartaGeltung.SPORTMEDIZIN_SOUVERAEN: SportmedizinChartaTyp.REHABILITATIONSPROTOKOLL,
}

_PROZEDUR_MAP = {
    SportmedizinChartaGeltung.GESPERRT: SportmedizinChartaProzedur.SPORTTAUGLICHKEITSUNTERSUCHUNG,
    SportmedizinChartaGeltung.GRUNDLEGEND_SPORTMEDIZINISCH: SportmedizinChartaProzedur.SPORTTAUGLICHKEITSUNTERSUCHUNG,
    SportmedizinChartaGeltung.SPORTMEDIZINISCH: SportmedizinChartaProzedur.VERLETZUNGSDIAGNOSTIK,
    SportmedizinChartaGeltung.SPORTMEDIZINISCH_AKTIV: SportmedizinChartaProzedur.VERLETZUNGSDIAGNOSTIK,
    SportmedizinChartaGeltung.SPORTMEDIZIN_SOUVERAEN: SportmedizinChartaProzedur.REHABILITATIONSBEWERTUNG,
}


@dataclass(frozen=True)
class SportmedizinChartaNorm:
    geltung: SportmedizinChartaGeltung
    sport_weight: float
    sport_tier: int
    sport_ids: tuple[str, ...]
    sport_tags: tuple[str, ...]
    typ: SportmedizinChartaTyp
    prozedur: SportmedizinChartaProzedur
    canonical: bool = True


@dataclass(frozen=True)
class SportmedizinCharta:
    normen: tuple[SportmedizinChartaNorm, ...]
    parent: Optional[SportNormSatz] = None


def build_sportmedizin_charta(parent: Optional[SportNormSatz] = None) -> SportmedizinCharta:
    if parent is None:
        parent = build_sport_norm()
    base = sum(e.sport_norm_weight for e in parent.normen)
    tier_base = max(e.sport_norm_tier for e in parent.normen)
    normen = tuple(
        SportmedizinChartaNorm(
            geltung=g,
            sport_weight=round(base + _WEIGHT_DELTA[g], 4),
            sport_tier=tier_base + i + 1,
            sport_ids=(f"sportmedizin-{g.name.lower()}-001",),
            sport_tags=("sportmedizin", "charta", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(SportmedizinChartaGeltung)
    )
    return SportmedizinCharta(normen=normen, parent=parent)
