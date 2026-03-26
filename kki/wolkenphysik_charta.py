from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .atmosphaere_dynamik_register import AtmosphaereDynamikRegister, build_atmosphaere_dynamik_register


class WolkenphysikChartaGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_METEOROLOGISCH = auto()
    METEOROLOGISCH = auto()
    METEOROLOGISCH_AKTIV = auto()
    METEOROLOGIE_SOUVERAEN = auto()


class WolkenphysikChartaTyp(Enum):
    WOLKENPHYSIKCHARTA = auto()
    WOLKENPHYSIKSYSTEM = auto()
    WOLKENPHYSIKKOMPONENTE = auto()


class WolkenphysikChartaProzedur(Enum):
    WOLKENPHYSIKANALYSE = auto()
    WOLKENPHYSIKSYNTHESE = auto()
    WOLKENPHYSIKBEWERTUNG = auto()


_WEIGHT_DELTA: dict[WolkenphysikChartaGeltung, float] = {
    WolkenphysikChartaGeltung.GESPERRT: 0.0,
    WolkenphysikChartaGeltung.GRUNDLEGEND_METEOROLOGISCH: 1.4,
    WolkenphysikChartaGeltung.METEOROLOGISCH: 2.8,
    WolkenphysikChartaGeltung.METEOROLOGISCH_AKTIV: 4.2,
    WolkenphysikChartaGeltung.METEOROLOGIE_SOUVERAEN: 5.6,
}

_TYP_MAP = {
    WolkenphysikChartaGeltung.GESPERRT: WolkenphysikChartaTyp.WOLKENPHYSIKCHARTA,
    WolkenphysikChartaGeltung.GRUNDLEGEND_METEOROLOGISCH: WolkenphysikChartaTyp.WOLKENPHYSIKKOMPONENTE,
    WolkenphysikChartaGeltung.METEOROLOGISCH: WolkenphysikChartaTyp.WOLKENPHYSIKKOMPONENTE,
    WolkenphysikChartaGeltung.METEOROLOGISCH_AKTIV: WolkenphysikChartaTyp.WOLKENPHYSIKSYSTEM,
    WolkenphysikChartaGeltung.METEOROLOGIE_SOUVERAEN: WolkenphysikChartaTyp.WOLKENPHYSIKSYSTEM,
}

_PROZEDUR_MAP = {
    WolkenphysikChartaGeltung.GESPERRT: WolkenphysikChartaProzedur.WOLKENPHYSIKANALYSE,
    WolkenphysikChartaGeltung.GRUNDLEGEND_METEOROLOGISCH: WolkenphysikChartaProzedur.WOLKENPHYSIKANALYSE,
    WolkenphysikChartaGeltung.METEOROLOGISCH: WolkenphysikChartaProzedur.WOLKENPHYSIKSYNTHESE,
    WolkenphysikChartaGeltung.METEOROLOGISCH_AKTIV: WolkenphysikChartaProzedur.WOLKENPHYSIKSYNTHESE,
    WolkenphysikChartaGeltung.METEOROLOGIE_SOUVERAEN: WolkenphysikChartaProzedur.WOLKENPHYSIKBEWERTUNG,
}


@dataclass(frozen=True)
class WolkenphysikChartaNorm:
    geltung: WolkenphysikChartaGeltung
    meteorologie_weight: float
    meteorologie_tier: int
    meteorologie_ids: tuple[str, ...]
    meteorologie_tags: tuple[str, ...]
    typ: WolkenphysikChartaTyp
    prozedur: WolkenphysikChartaProzedur
    canonical: bool = True


@dataclass(frozen=True)
class WolkenphysikCharta:
    normen: tuple[WolkenphysikChartaNorm, ...]
    parent: Optional[AtmosphaereDynamikRegister] = None


def build_wolkenphysik_charta(parent: Optional[AtmosphaereDynamikRegister] = None) -> WolkenphysikCharta:
    if parent is None:
        parent = build_atmosphaere_dynamik_register()
    base = sum(e.meteorologie_weight for e in parent.eintraege)
    normen = tuple(
        WolkenphysikChartaNorm(
            geltung=g,
            meteorologie_weight=round(base + _WEIGHT_DELTA[g], 4),
            meteorologie_tier=i + 1,
            meteorologie_ids=(f"wolkenphysik-charta-{g.name.lower()}-001",),
            meteorologie_tags=("meteorologie", "wolkenphysik", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(WolkenphysikChartaGeltung)
    )
    return WolkenphysikCharta(normen=normen, parent=parent)
