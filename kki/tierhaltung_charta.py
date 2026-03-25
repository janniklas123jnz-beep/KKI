from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .pflanzenbau_register import PflanzenbauRegister, build_pflanzenbau_register


class TierhaltungChartaGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_TIERHALTEND = auto()
    TIERHALTEND = auto()
    TIERHALTEND_AKTIV = auto()
    TIERHALTUNG_SOUVERAEN = auto()


class TierhaltungChartaTyp(Enum):
    TIERHALTUNGCHARTA = auto()
    ZUCHTPROGRAMM = auto()
    TIERSCHUTZSTANDARD = auto()


class TierhaltungChartaProzedur(Enum):
    BESTANDSANALYSE = auto()
    ZUCHTZIELPLANUNG = auto()
    TIERWOHLEVALUIERUNG = auto()


_WEIGHT_DELTA: dict[TierhaltungChartaGeltung, float] = {
    TierhaltungChartaGeltung.GESPERRT: 0.0,
    TierhaltungChartaGeltung.GRUNDLEGEND_TIERHALTEND: 1.4,
    TierhaltungChartaGeltung.TIERHALTEND: 2.8,
    TierhaltungChartaGeltung.TIERHALTEND_AKTIV: 4.2,
    TierhaltungChartaGeltung.TIERHALTUNG_SOUVERAEN: 5.6,
}

_TYP_MAP = {
    TierhaltungChartaGeltung.GESPERRT: TierhaltungChartaTyp.TIERHALTUNGCHARTA,
    TierhaltungChartaGeltung.GRUNDLEGEND_TIERHALTEND: TierhaltungChartaTyp.TIERSCHUTZSTANDARD,
    TierhaltungChartaGeltung.TIERHALTEND: TierhaltungChartaTyp.TIERSCHUTZSTANDARD,
    TierhaltungChartaGeltung.TIERHALTEND_AKTIV: TierhaltungChartaTyp.ZUCHTPROGRAMM,
    TierhaltungChartaGeltung.TIERHALTUNG_SOUVERAEN: TierhaltungChartaTyp.ZUCHTPROGRAMM,
}

_PROZEDUR_MAP = {
    TierhaltungChartaGeltung.GESPERRT: TierhaltungChartaProzedur.BESTANDSANALYSE,
    TierhaltungChartaGeltung.GRUNDLEGEND_TIERHALTEND: TierhaltungChartaProzedur.BESTANDSANALYSE,
    TierhaltungChartaGeltung.TIERHALTEND: TierhaltungChartaProzedur.ZUCHTZIELPLANUNG,
    TierhaltungChartaGeltung.TIERHALTEND_AKTIV: TierhaltungChartaProzedur.ZUCHTZIELPLANUNG,
    TierhaltungChartaGeltung.TIERHALTUNG_SOUVERAEN: TierhaltungChartaProzedur.TIERWOHLEVALUIERUNG,
}


@dataclass(frozen=True)
class TierhaltungChartaNorm:
    geltung: TierhaltungChartaGeltung
    agrar_weight: float
    agrar_tier: int
    agrar_ids: tuple[str, ...]
    agrar_tags: tuple[str, ...]
    typ: TierhaltungChartaTyp
    prozedur: TierhaltungChartaProzedur
    canonical: bool = True


@dataclass(frozen=True)
class TierhaltungCharta:
    normen: tuple[TierhaltungChartaNorm, ...]
    parent: Optional[PflanzenbauRegister] = None


def build_tierhaltung_charta(parent: Optional[PflanzenbauRegister] = None) -> TierhaltungCharta:
    if parent is None:
        parent = build_pflanzenbau_register()
    base = sum(e.agrar_weight for e in parent.eintraege)
    normen = tuple(
        TierhaltungChartaNorm(
            geltung=g,
            agrar_weight=round(base + _WEIGHT_DELTA[g], 4),
            agrar_tier=i + 1,
            agrar_ids=(f"tierhaltung-{g.name.lower()}-001",),
            agrar_tags=("tierhaltung", "charta", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(TierhaltungChartaGeltung)
    )
    return TierhaltungCharta(normen=normen, parent=parent)
