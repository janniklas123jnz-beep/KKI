from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .palaeontologie_norm import PalaeontologieNormSatz, build_palaeontologie_norm


class TaphonomieChartaGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_PALAEONTOLOGISCH = auto()
    PALAEONTOLOGISCH = auto()
    PALAEONTOLOGISCH_AKTIV = auto()
    PALAEONTOLOGIE_SOUVERAEN = auto()


class TaphonomieChartaTyp(Enum):
    TAPHONOMIECHARTA = auto()
    TAPHONOMIESYSTEM = auto()
    TAPHONOMIEKOMPONENTE = auto()


class TaphonomieChartaProzedur(Enum):
    TAPHONOMIEANALYSE = auto()
    TAPHONOMIESYNTHESE = auto()
    TAPHONOMIEBEWERTUNG = auto()


_WEIGHT_DELTA: dict[TaphonomieChartaGeltung, float] = {
    TaphonomieChartaGeltung.GESPERRT: 0.0,
    TaphonomieChartaGeltung.GRUNDLEGEND_PALAEONTOLOGISCH: 2.0,
    TaphonomieChartaGeltung.PALAEONTOLOGISCH: 4.0,
    TaphonomieChartaGeltung.PALAEONTOLOGISCH_AKTIV: 6.0,
    TaphonomieChartaGeltung.PALAEONTOLOGIE_SOUVERAEN: 8.0,
}

_TYP_MAP = {
    TaphonomieChartaGeltung.GESPERRT: TaphonomieChartaTyp.TAPHONOMIECHARTA,
    TaphonomieChartaGeltung.GRUNDLEGEND_PALAEONTOLOGISCH: TaphonomieChartaTyp.TAPHONOMIEKOMPONENTE,
    TaphonomieChartaGeltung.PALAEONTOLOGISCH: TaphonomieChartaTyp.TAPHONOMIEKOMPONENTE,
    TaphonomieChartaGeltung.PALAEONTOLOGISCH_AKTIV: TaphonomieChartaTyp.TAPHONOMIESYSTEM,
    TaphonomieChartaGeltung.PALAEONTOLOGIE_SOUVERAEN: TaphonomieChartaTyp.TAPHONOMIESYSTEM,
}

_PROZEDUR_MAP = {
    TaphonomieChartaGeltung.GESPERRT: TaphonomieChartaProzedur.TAPHONOMIEANALYSE,
    TaphonomieChartaGeltung.GRUNDLEGEND_PALAEONTOLOGISCH: TaphonomieChartaProzedur.TAPHONOMIEANALYSE,
    TaphonomieChartaGeltung.PALAEONTOLOGISCH: TaphonomieChartaProzedur.TAPHONOMIESYNTHESE,
    TaphonomieChartaGeltung.PALAEONTOLOGISCH_AKTIV: TaphonomieChartaProzedur.TAPHONOMIESYNTHESE,
    TaphonomieChartaGeltung.PALAEONTOLOGIE_SOUVERAEN: TaphonomieChartaProzedur.TAPHONOMIEBEWERTUNG,
}


@dataclass(frozen=True)
class TaphonomieChartaNorm:
    geltung: TaphonomieChartaGeltung
    palaeontologie_weight: float
    palaeontologie_tier: int
    palaeontologie_ids: tuple[str, ...]
    palaeontologie_tags: tuple[str, ...]
    typ: TaphonomieChartaTyp
    prozedur: TaphonomieChartaProzedur
    canonical: bool = True


@dataclass(frozen=True)
class TaphonomieCharta:
    normen: tuple[TaphonomieChartaNorm, ...]
    parent: Optional[PalaeontologieNormSatz] = None


def build_taphonomie_charta(parent: Optional[PalaeontologieNormSatz] = None) -> TaphonomieCharta:
    if parent is None:
        parent = build_palaeontologie_norm()
    base = sum(e.palaeontologie_norm_weight for e in parent.normen)
    tier_base = max(e.palaeontologie_norm_tier for e in parent.normen)
    normen = tuple(
        TaphonomieChartaNorm(
            geltung=g,
            palaeontologie_weight=round(base + _WEIGHT_DELTA[g], 4),
            palaeontologie_tier=tier_base + i + 1,
            palaeontologie_ids=(f"taphonomie-charta-{g.name.lower()}-001",),
            palaeontologie_tags=("palaeontologie", "taphonomie", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(TaphonomieChartaGeltung)
    )
    return TaphonomieCharta(normen=normen, parent=parent)
