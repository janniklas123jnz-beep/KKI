from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .hydrologie_norm import HydrologieNormSatz, build_hydrologie_norm


class WasserressourcenChartaGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_HYDROLOGISCH = auto()
    HYDROLOGISCH = auto()
    HYDROLOGISCH_AKTIV = auto()
    HYDROLOGIE_SOUVERAEN = auto()


class WasserressourcenChartaTyp(Enum):
    WASSERRESSOURCENCHARTA = auto()
    WASSERRESSOURCENSYSTEM = auto()
    WASSERRESSOURCENKOMPONENTE = auto()


class WasserressourcenChartaProzedur(Enum):
    WASSERRESSOURCENANALYSE = auto()
    WASSERRESSOURCENSYNTHESE = auto()
    WASSERRESSOURCENBEWERTUNG = auto()


_WEIGHT_DELTA: dict[WasserressourcenChartaGeltung, float] = {
    WasserressourcenChartaGeltung.GESPERRT: 0.0,
    WasserressourcenChartaGeltung.GRUNDLEGEND_HYDROLOGISCH: 2.0,
    WasserressourcenChartaGeltung.HYDROLOGISCH: 4.0,
    WasserressourcenChartaGeltung.HYDROLOGISCH_AKTIV: 6.0,
    WasserressourcenChartaGeltung.HYDROLOGIE_SOUVERAEN: 8.0,
}

_TYP_MAP = {
    WasserressourcenChartaGeltung.GESPERRT: WasserressourcenChartaTyp.WASSERRESSOURCENCHARTA,
    WasserressourcenChartaGeltung.GRUNDLEGEND_HYDROLOGISCH: WasserressourcenChartaTyp.WASSERRESSOURCENKOMPONENTE,
    WasserressourcenChartaGeltung.HYDROLOGISCH: WasserressourcenChartaTyp.WASSERRESSOURCENKOMPONENTE,
    WasserressourcenChartaGeltung.HYDROLOGISCH_AKTIV: WasserressourcenChartaTyp.WASSERRESSOURCENSYSTEM,
    WasserressourcenChartaGeltung.HYDROLOGIE_SOUVERAEN: WasserressourcenChartaTyp.WASSERRESSOURCENSYSTEM,
}

_PROZEDUR_MAP = {
    WasserressourcenChartaGeltung.GESPERRT: WasserressourcenChartaProzedur.WASSERRESSOURCENANALYSE,
    WasserressourcenChartaGeltung.GRUNDLEGEND_HYDROLOGISCH: WasserressourcenChartaProzedur.WASSERRESSOURCENANALYSE,
    WasserressourcenChartaGeltung.HYDROLOGISCH: WasserressourcenChartaProzedur.WASSERRESSOURCENSYNTHESE,
    WasserressourcenChartaGeltung.HYDROLOGISCH_AKTIV: WasserressourcenChartaProzedur.WASSERRESSOURCENSYNTHESE,
    WasserressourcenChartaGeltung.HYDROLOGIE_SOUVERAEN: WasserressourcenChartaProzedur.WASSERRESSOURCENBEWERTUNG,
}


@dataclass(frozen=True)
class WasserressourcenChartaNorm:
    geltung: WasserressourcenChartaGeltung
    hydrologie_weight: float
    hydrologie_tier: int
    hydrologie_ids: tuple[str, ...]
    hydrologie_tags: tuple[str, ...]
    typ: WasserressourcenChartaTyp
    prozedur: WasserressourcenChartaProzedur
    canonical: bool = True


@dataclass(frozen=True)
class WasserressourcenCharta:
    normen: tuple[WasserressourcenChartaNorm, ...]
    parent: Optional[HydrologieNormSatz] = None


def build_wasserressourcen_charta(parent: Optional[HydrologieNormSatz] = None) -> WasserressourcenCharta:
    if parent is None:
        parent = build_hydrologie_norm()
    base = sum(e.hydrologie_norm_weight for e in parent.normen)
    tier_base = max(e.hydrologie_norm_tier for e in parent.normen)
    normen = tuple(
        WasserressourcenChartaNorm(
            geltung=g,
            hydrologie_weight=round(base + _WEIGHT_DELTA[g], 4),
            hydrologie_tier=tier_base + i + 1,
            hydrologie_ids=(f"wasserressourcen-charta-{g.name.lower()}-001",),
            hydrologie_tags=("hydrologie", "wasserressourcen", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(WasserressourcenChartaGeltung)
    )
    return WasserressourcenCharta(normen=normen, parent=parent)
