from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .mineralogie_norm import MineralogieNormSatz, build_mineralogie_norm


class EdelmineralChartaGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_MINERALOGISCH = auto()
    MINERALOGISCH = auto()
    MINERALOGISCH_AKTIV = auto()
    MINERALOGIE_SOUVERAEN = auto()


class EdelmineralChartaTyp(Enum):
    EDELMINERALCHARTA = auto()
    EDELMINERALSYSTEM = auto()
    EDELMINERALKOMPONENTE = auto()


class EdelmineralChartaProzedur(Enum):
    EDELMINERALANALYSE = auto()
    EDELMINERAL_SYNTHESE = auto()
    EDELMINERAL_BEWERTUNG = auto()


_WEIGHT_DELTA: dict[EdelmineralChartaGeltung, float] = {
    EdelmineralChartaGeltung.GESPERRT: 0.0,
    EdelmineralChartaGeltung.GRUNDLEGEND_MINERALOGISCH: 2.0,
    EdelmineralChartaGeltung.MINERALOGISCH: 4.0,
    EdelmineralChartaGeltung.MINERALOGISCH_AKTIV: 6.0,
    EdelmineralChartaGeltung.MINERALOGIE_SOUVERAEN: 8.0,
}

_TYP_MAP = {
    EdelmineralChartaGeltung.GESPERRT: EdelmineralChartaTyp.EDELMINERALCHARTA,
    EdelmineralChartaGeltung.GRUNDLEGEND_MINERALOGISCH: EdelmineralChartaTyp.EDELMINERALKOMPONENTE,
    EdelmineralChartaGeltung.MINERALOGISCH: EdelmineralChartaTyp.EDELMINERALKOMPONENTE,
    EdelmineralChartaGeltung.MINERALOGISCH_AKTIV: EdelmineralChartaTyp.EDELMINERALSYSTEM,
    EdelmineralChartaGeltung.MINERALOGIE_SOUVERAEN: EdelmineralChartaTyp.EDELMINERALSYSTEM,
}

_PROZEDUR_MAP = {
    EdelmineralChartaGeltung.GESPERRT: EdelmineralChartaProzedur.EDELMINERALANALYSE,
    EdelmineralChartaGeltung.GRUNDLEGEND_MINERALOGISCH: EdelmineralChartaProzedur.EDELMINERALANALYSE,
    EdelmineralChartaGeltung.MINERALOGISCH: EdelmineralChartaProzedur.EDELMINERAL_SYNTHESE,
    EdelmineralChartaGeltung.MINERALOGISCH_AKTIV: EdelmineralChartaProzedur.EDELMINERAL_SYNTHESE,
    EdelmineralChartaGeltung.MINERALOGIE_SOUVERAEN: EdelmineralChartaProzedur.EDELMINERAL_BEWERTUNG,
}


@dataclass(frozen=True)
class EdelmineralChartaNorm:
    geltung: EdelmineralChartaGeltung
    mineralogie_weight: float
    mineralogie_tier: int
    mineralogie_ids: tuple[str, ...]
    mineralogie_tags: tuple[str, ...]
    typ: EdelmineralChartaTyp
    prozedur: EdelmineralChartaProzedur
    canonical: bool = True


@dataclass(frozen=True)
class EdelmineralCharta:
    normen: tuple[EdelmineralChartaNorm, ...]
    parent: Optional[MineralogieNormSatz] = None


def build_edelmineral_charta(parent: Optional[MineralogieNormSatz] = None) -> EdelmineralCharta:
    if parent is None:
        parent = build_mineralogie_norm()
    base = sum(e.mineralogie_norm_weight for e in parent.normen)
    tier_base = max(e.mineralogie_norm_tier for e in parent.normen)
    normen = tuple(
        EdelmineralChartaNorm(
            geltung=g,
            mineralogie_weight=round(base + _WEIGHT_DELTA[g], 4),
            mineralogie_tier=tier_base + i + 1,
            mineralogie_ids=(f"edelmineral-charta-{g.name.lower()}-001",),
            mineralogie_tags=("mineralogie", "edelmineral", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(EdelmineralChartaGeltung)
    )
    return EdelmineralCharta(normen=normen, parent=parent)
