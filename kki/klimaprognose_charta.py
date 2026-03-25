from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .klima_norm import KlimaNormSatz, build_klima_norm


class KlimaprognoseChartaGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_KLIMAPROGNOSTISCH = auto()
    KLIMAPROGNOSTISCH = auto()
    KLIMAPROGNOSTISCH_AKTIV = auto()
    KLIMAPROGNOSE_SOUVERAEN = auto()


class KlimaprognoseChartaTyp(Enum):
    KLIMAPROGNOSECHARTA = auto()
    KLIMASZENARIO = auto()
    KLIMAPROJEKION = auto()


class KlimaprognoseChartaProzedur(Enum):
    KLIMAPROGNOSEANALYSE = auto()
    KLIMAPROGNOSESYNTHESE = auto()
    KLIMAPROGNOSEBEWERTUNG = auto()


_WEIGHT_DELTA: dict[KlimaprognoseChartaGeltung, float] = {
    KlimaprognoseChartaGeltung.GESPERRT: 0.0,
    KlimaprognoseChartaGeltung.GRUNDLEGEND_KLIMAPROGNOSTISCH: 2.0,
    KlimaprognoseChartaGeltung.KLIMAPROGNOSTISCH: 4.0,
    KlimaprognoseChartaGeltung.KLIMAPROGNOSTISCH_AKTIV: 6.0,
    KlimaprognoseChartaGeltung.KLIMAPROGNOSE_SOUVERAEN: 8.0,
}

_TYP_MAP = {
    KlimaprognoseChartaGeltung.GESPERRT: KlimaprognoseChartaTyp.KLIMAPROGNOSECHARTA,
    KlimaprognoseChartaGeltung.GRUNDLEGEND_KLIMAPROGNOSTISCH: KlimaprognoseChartaTyp.KLIMAPROJEKION,
    KlimaprognoseChartaGeltung.KLIMAPROGNOSTISCH: KlimaprognoseChartaTyp.KLIMAPROJEKION,
    KlimaprognoseChartaGeltung.KLIMAPROGNOSTISCH_AKTIV: KlimaprognoseChartaTyp.KLIMASZENARIO,
    KlimaprognoseChartaGeltung.KLIMAPROGNOSE_SOUVERAEN: KlimaprognoseChartaTyp.KLIMASZENARIO,
}

_PROZEDUR_MAP = {
    KlimaprognoseChartaGeltung.GESPERRT: KlimaprognoseChartaProzedur.KLIMAPROGNOSEANALYSE,
    KlimaprognoseChartaGeltung.GRUNDLEGEND_KLIMAPROGNOSTISCH: KlimaprognoseChartaProzedur.KLIMAPROGNOSEANALYSE,
    KlimaprognoseChartaGeltung.KLIMAPROGNOSTISCH: KlimaprognoseChartaProzedur.KLIMAPROGNOSESYNTHESE,
    KlimaprognoseChartaGeltung.KLIMAPROGNOSTISCH_AKTIV: KlimaprognoseChartaProzedur.KLIMAPROGNOSESYNTHESE,
    KlimaprognoseChartaGeltung.KLIMAPROGNOSE_SOUVERAEN: KlimaprognoseChartaProzedur.KLIMAPROGNOSEBEWERTUNG,
}


@dataclass(frozen=True)
class KlimaprognoseChartaNorm:
    geltung: KlimaprognoseChartaGeltung
    klima_weight: float
    klima_tier: int
    klima_ids: tuple[str, ...]
    klima_tags: tuple[str, ...]
    typ: KlimaprognoseChartaTyp
    prozedur: KlimaprognoseChartaProzedur
    canonical: bool = True


@dataclass(frozen=True)
class KlimaprognoseCharta:
    normen: tuple[KlimaprognoseChartaNorm, ...]
    parent: Optional[KlimaNormSatz] = None


def build_klimaprognose_charta(parent: Optional[KlimaNormSatz] = None) -> KlimaprognoseCharta:
    if parent is None:
        parent = build_klima_norm()
    base = sum(e.klima_norm_weight for e in parent.normen)
    tier_base = max(e.klima_norm_tier for e in parent.normen)
    normen = tuple(
        KlimaprognoseChartaNorm(
            geltung=g,
            klima_weight=round(base + _WEIGHT_DELTA[g], 4),
            klima_tier=tier_base + i + 1,
            klima_ids=(f"klimaprognose-charta-{g.name.lower()}-001",),
            klima_tags=("klimaprognose", "charta", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(KlimaprognoseChartaGeltung)
    )
    return KlimaprognoseCharta(normen=normen, parent=parent)
