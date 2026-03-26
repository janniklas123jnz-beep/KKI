from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .meteorologie_norm import MeteorologieNormSatz, build_meteorologie_norm


class WettervorhersageChartaGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_METEOROLOGISCH = auto()
    METEOROLOGISCH = auto()
    METEOROLOGISCH_AKTIV = auto()
    METEOROLOGIE_SOUVERAEN = auto()


class WettervorhersageChartaTyp(Enum):
    WETTERVORHERSAGECHARTA = auto()
    WETTERVORHERSAGESYSTEM = auto()
    WETTERVORHERSAGEKOMPONENTE = auto()


class WettervorhersageChartaProzedur(Enum):
    WETTERVORHERSAGEANALYSE = auto()
    WETTERVORHERSAGESYNTHESE = auto()
    WETTERVORHERSAGEBEWERTUNG = auto()


_WEIGHT_DELTA: dict[WettervorhersageChartaGeltung, float] = {
    WettervorhersageChartaGeltung.GESPERRT: 0.0,
    WettervorhersageChartaGeltung.GRUNDLEGEND_METEOROLOGISCH: 2.0,
    WettervorhersageChartaGeltung.METEOROLOGISCH: 4.0,
    WettervorhersageChartaGeltung.METEOROLOGISCH_AKTIV: 6.0,
    WettervorhersageChartaGeltung.METEOROLOGIE_SOUVERAEN: 8.0,
}

_TYP_MAP = {
    WettervorhersageChartaGeltung.GESPERRT: WettervorhersageChartaTyp.WETTERVORHERSAGECHARTA,
    WettervorhersageChartaGeltung.GRUNDLEGEND_METEOROLOGISCH: WettervorhersageChartaTyp.WETTERVORHERSAGEKOMPONENTE,
    WettervorhersageChartaGeltung.METEOROLOGISCH: WettervorhersageChartaTyp.WETTERVORHERSAGEKOMPONENTE,
    WettervorhersageChartaGeltung.METEOROLOGISCH_AKTIV: WettervorhersageChartaTyp.WETTERVORHERSAGESYSTEM,
    WettervorhersageChartaGeltung.METEOROLOGIE_SOUVERAEN: WettervorhersageChartaTyp.WETTERVORHERSAGESYSTEM,
}

_PROZEDUR_MAP = {
    WettervorhersageChartaGeltung.GESPERRT: WettervorhersageChartaProzedur.WETTERVORHERSAGEANALYSE,
    WettervorhersageChartaGeltung.GRUNDLEGEND_METEOROLOGISCH: WettervorhersageChartaProzedur.WETTERVORHERSAGEANALYSE,
    WettervorhersageChartaGeltung.METEOROLOGISCH: WettervorhersageChartaProzedur.WETTERVORHERSAGESYNTHESE,
    WettervorhersageChartaGeltung.METEOROLOGISCH_AKTIV: WettervorhersageChartaProzedur.WETTERVORHERSAGESYNTHESE,
    WettervorhersageChartaGeltung.METEOROLOGIE_SOUVERAEN: WettervorhersageChartaProzedur.WETTERVORHERSAGEBEWERTUNG,
}


@dataclass(frozen=True)
class WettervorhersageChartaNorm:
    geltung: WettervorhersageChartaGeltung
    meteorologie_weight: float
    meteorologie_tier: int
    meteorologie_ids: tuple[str, ...]
    meteorologie_tags: tuple[str, ...]
    typ: WettervorhersageChartaTyp
    prozedur: WettervorhersageChartaProzedur
    canonical: bool = True


@dataclass(frozen=True)
class WettervorhersageCharta:
    normen: tuple[WettervorhersageChartaNorm, ...]
    parent: Optional[MeteorologieNormSatz] = None


def build_wettervorhersage_charta(parent: Optional[MeteorologieNormSatz] = None) -> WettervorhersageCharta:
    if parent is None:
        parent = build_meteorologie_norm()
    base = sum(e.meteorologie_norm_weight for e in parent.normen)
    tier_base = max(e.meteorologie_norm_tier for e in parent.normen)
    normen = tuple(
        WettervorhersageChartaNorm(
            geltung=g,
            meteorologie_weight=round(base + _WEIGHT_DELTA[g], 4),
            meteorologie_tier=tier_base + i + 1,
            meteorologie_ids=(f"wettervorhersage-charta-{g.name.lower()}-001",),
            meteorologie_tags=("meteorologie", "wettervorhersage", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(WettervorhersageChartaGeltung)
    )
    return WettervorhersageCharta(normen=normen, parent=parent)
