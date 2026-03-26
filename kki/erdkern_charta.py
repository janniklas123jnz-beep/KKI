from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .geophysik_norm import GeophysikNormSatz, build_geophysik_norm


class ErdkernChartaGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_GEOPHYSIKALISCH = auto()
    GEOPHYSIKALISCH = auto()
    GEOPHYSIKALISCH_AKTIV = auto()
    GEOPHYSIK_SOUVERAEN = auto()


class ErdkernChartaTyp(Enum):
    ERDKERN = auto()
    KERNSYSTEM = auto()
    KERNKOMPONENTE = auto()


class ErdkernChartaProzedur(Enum):
    KERNANALYSE = auto()
    KERNSYNTHESE = auto()
    KERNBEWERTUNG = auto()


_WEIGHT_DELTA: dict[ErdkernChartaGeltung, float] = {
    ErdkernChartaGeltung.GESPERRT: 0.0,
    ErdkernChartaGeltung.GRUNDLEGEND_GEOPHYSIKALISCH: 2.0,
    ErdkernChartaGeltung.GEOPHYSIKALISCH: 4.0,
    ErdkernChartaGeltung.GEOPHYSIKALISCH_AKTIV: 6.0,
    ErdkernChartaGeltung.GEOPHYSIK_SOUVERAEN: 8.0,
}

_TYP_MAP = {
    ErdkernChartaGeltung.GESPERRT: ErdkernChartaTyp.ERDKERN,
    ErdkernChartaGeltung.GRUNDLEGEND_GEOPHYSIKALISCH: ErdkernChartaTyp.KERNKOMPONENTE,
    ErdkernChartaGeltung.GEOPHYSIKALISCH: ErdkernChartaTyp.KERNKOMPONENTE,
    ErdkernChartaGeltung.GEOPHYSIKALISCH_AKTIV: ErdkernChartaTyp.KERNSYSTEM,
    ErdkernChartaGeltung.GEOPHYSIK_SOUVERAEN: ErdkernChartaTyp.KERNSYSTEM,
}

_PROZEDUR_MAP = {
    ErdkernChartaGeltung.GESPERRT: ErdkernChartaProzedur.KERNANALYSE,
    ErdkernChartaGeltung.GRUNDLEGEND_GEOPHYSIKALISCH: ErdkernChartaProzedur.KERNANALYSE,
    ErdkernChartaGeltung.GEOPHYSIKALISCH: ErdkernChartaProzedur.KERNSYNTHESE,
    ErdkernChartaGeltung.GEOPHYSIKALISCH_AKTIV: ErdkernChartaProzedur.KERNSYNTHESE,
    ErdkernChartaGeltung.GEOPHYSIK_SOUVERAEN: ErdkernChartaProzedur.KERNBEWERTUNG,
}


@dataclass(frozen=True)
class ErdkernChartaNorm:
    geltung: ErdkernChartaGeltung
    geophysik_weight: float
    geophysik_tier: int
    geophysik_ids: tuple[str, ...]
    geophysik_tags: tuple[str, ...]
    typ: ErdkernChartaTyp
    prozedur: ErdkernChartaProzedur
    canonical: bool = True


@dataclass(frozen=True)
class ErdkernCharta:
    normen: tuple[ErdkernChartaNorm, ...]
    parent: Optional[GeophysikNormSatz] = None


def build_erdkern_charta(parent: Optional[GeophysikNormSatz] = None) -> ErdkernCharta:
    if parent is None:
        parent = build_geophysik_norm()
    base = sum(e.geophysik_norm_weight for e in parent.normen)
    tier_base = max(e.geophysik_norm_tier for e in parent.normen)
    normen = tuple(
        ErdkernChartaNorm(
            geltung=g,
            geophysik_weight=round(base + _WEIGHT_DELTA[g], 4),
            geophysik_tier=tier_base + i + 1,
            geophysik_ids=(f"erdkern-{g.name.lower()}-001",),
            geophysik_tags=("geophysik", "erdkern", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(ErdkernChartaGeltung)
    )
    return ErdkernCharta(normen=normen, parent=parent)
