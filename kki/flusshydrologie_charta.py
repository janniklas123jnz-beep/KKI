from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .grundwasser_register import GrundwasserRegister, build_grundwasser_register


class FlusshydrologieChartaGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_HYDROLOGISCH = auto()
    HYDROLOGISCH = auto()
    HYDROLOGISCH_AKTIV = auto()
    HYDROLOGIE_SOUVERAEN = auto()


class FlusshydrologieChartaTyp(Enum):
    FLUSSHYDROLOGIECHARTA = auto()
    FLUSSHYDROLOGIESYSTEM = auto()
    FLUSSHYDROLOGIEKOMPONENTE = auto()


class FlusshydrologieChartaProzedur(Enum):
    FLUSSHYDROLOGIEANALYSE = auto()
    FLUSSHYDROLOGIESYNTHESE = auto()
    FLUSSHYDROLOGIEBEWERTUNG = auto()


_WEIGHT_DELTA: dict[FlusshydrologieChartaGeltung, float] = {
    FlusshydrologieChartaGeltung.GESPERRT: 0.0,
    FlusshydrologieChartaGeltung.GRUNDLEGEND_HYDROLOGISCH: 1.4,
    FlusshydrologieChartaGeltung.HYDROLOGISCH: 2.8,
    FlusshydrologieChartaGeltung.HYDROLOGISCH_AKTIV: 4.2,
    FlusshydrologieChartaGeltung.HYDROLOGIE_SOUVERAEN: 5.6,
}

_TYP_MAP = {
    FlusshydrologieChartaGeltung.GESPERRT: FlusshydrologieChartaTyp.FLUSSHYDROLOGIECHARTA,
    FlusshydrologieChartaGeltung.GRUNDLEGEND_HYDROLOGISCH: FlusshydrologieChartaTyp.FLUSSHYDROLOGIEKOMPONENTE,
    FlusshydrologieChartaGeltung.HYDROLOGISCH: FlusshydrologieChartaTyp.FLUSSHYDROLOGIEKOMPONENTE,
    FlusshydrologieChartaGeltung.HYDROLOGISCH_AKTIV: FlusshydrologieChartaTyp.FLUSSHYDROLOGIESYSTEM,
    FlusshydrologieChartaGeltung.HYDROLOGIE_SOUVERAEN: FlusshydrologieChartaTyp.FLUSSHYDROLOGIESYSTEM,
}

_PROZEDUR_MAP = {
    FlusshydrologieChartaGeltung.GESPERRT: FlusshydrologieChartaProzedur.FLUSSHYDROLOGIEANALYSE,
    FlusshydrologieChartaGeltung.GRUNDLEGEND_HYDROLOGISCH: FlusshydrologieChartaProzedur.FLUSSHYDROLOGIEANALYSE,
    FlusshydrologieChartaGeltung.HYDROLOGISCH: FlusshydrologieChartaProzedur.FLUSSHYDROLOGIESYNTHESE,
    FlusshydrologieChartaGeltung.HYDROLOGISCH_AKTIV: FlusshydrologieChartaProzedur.FLUSSHYDROLOGIESYNTHESE,
    FlusshydrologieChartaGeltung.HYDROLOGIE_SOUVERAEN: FlusshydrologieChartaProzedur.FLUSSHYDROLOGIEBEWERTUNG,
}


@dataclass(frozen=True)
class FlusshydrologieChartaNorm:
    geltung: FlusshydrologieChartaGeltung
    hydrologie_weight: float
    hydrologie_tier: int
    hydrologie_ids: tuple[str, ...]
    hydrologie_tags: tuple[str, ...]
    typ: FlusshydrologieChartaTyp
    prozedur: FlusshydrologieChartaProzedur
    canonical: bool = True


@dataclass(frozen=True)
class FlusshydrologieCharta:
    normen: tuple[FlusshydrologieChartaNorm, ...]
    parent: Optional[GrundwasserRegister] = None


def build_flusshydrologie_charta(parent: Optional[GrundwasserRegister] = None) -> FlusshydrologieCharta:
    if parent is None:
        parent = build_grundwasser_register()
    base = sum(e.hydrologie_weight for e in parent.eintraege)
    normen = tuple(
        FlusshydrologieChartaNorm(
            geltung=g,
            hydrologie_weight=round(base + _WEIGHT_DELTA[g], 4),
            hydrologie_tier=i + 1,
            hydrologie_ids=(f"flusshydrologie-charta-{g.name.lower()}-001",),
            hydrologie_tags=("hydrologie", "flusshydrologie", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(FlusshydrologieChartaGeltung)
    )
    return FlusshydrologieCharta(normen=normen, parent=parent)
