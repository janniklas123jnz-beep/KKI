from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .geomorphologie_norm import GeomorphologieNormSatz, build_geomorphologie_norm


class KarstsystemChartaGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_GEOMORPHOLOGISCH = auto()
    GEOMORPHOLOGISCH = auto()
    GEOMORPHOLOGISCH_AKTIV = auto()
    GEOMORPHOLOGIE_SOUVERAEN = auto()


class KarstsystemChartaTyp(Enum):
    KARSTSYSTEMCHARTA = auto()
    KARSTSYSTEMSYSTEM = auto()
    KARSTSYSTEMKOMPONENTE = auto()


class KarstsystemChartaProzedur(Enum):
    KARSTSYSTEMANALYSE = auto()
    KARSTSYSTEMSYNTHESE = auto()
    KARSTSYSTEMBEWERTUNG = auto()


_WEIGHT_DELTA: dict[KarstsystemChartaGeltung, float] = {
    KarstsystemChartaGeltung.GESPERRT: 0.0,
    KarstsystemChartaGeltung.GRUNDLEGEND_GEOMORPHOLOGISCH: 2.0,
    KarstsystemChartaGeltung.GEOMORPHOLOGISCH: 4.0,
    KarstsystemChartaGeltung.GEOMORPHOLOGISCH_AKTIV: 6.0,
    KarstsystemChartaGeltung.GEOMORPHOLOGIE_SOUVERAEN: 8.0,
}

_TYP_MAP = {
    KarstsystemChartaGeltung.GESPERRT: KarstsystemChartaTyp.KARSTSYSTEMCHARTA,
    KarstsystemChartaGeltung.GRUNDLEGEND_GEOMORPHOLOGISCH: KarstsystemChartaTyp.KARSTSYSTEMKOMPONENTE,
    KarstsystemChartaGeltung.GEOMORPHOLOGISCH: KarstsystemChartaTyp.KARSTSYSTEMKOMPONENTE,
    KarstsystemChartaGeltung.GEOMORPHOLOGISCH_AKTIV: KarstsystemChartaTyp.KARSTSYSTEMSYSTEM,
    KarstsystemChartaGeltung.GEOMORPHOLOGIE_SOUVERAEN: KarstsystemChartaTyp.KARSTSYSTEMSYSTEM,
}

_PROZEDUR_MAP = {
    KarstsystemChartaGeltung.GESPERRT: KarstsystemChartaProzedur.KARSTSYSTEMANALYSE,
    KarstsystemChartaGeltung.GRUNDLEGEND_GEOMORPHOLOGISCH: KarstsystemChartaProzedur.KARSTSYSTEMANALYSE,
    KarstsystemChartaGeltung.GEOMORPHOLOGISCH: KarstsystemChartaProzedur.KARSTSYSTEMSYNTHESE,
    KarstsystemChartaGeltung.GEOMORPHOLOGISCH_AKTIV: KarstsystemChartaProzedur.KARSTSYSTEMSYNTHESE,
    KarstsystemChartaGeltung.GEOMORPHOLOGIE_SOUVERAEN: KarstsystemChartaProzedur.KARSTSYSTEMBEWERTUNG,
}


@dataclass(frozen=True)
class KarstsystemChartaNorm:
    geltung: KarstsystemChartaGeltung
    geomorphologie_weight: float
    geomorphologie_tier: int
    geomorphologie_ids: tuple[str, ...]
    geomorphologie_tags: tuple[str, ...]
    typ: KarstsystemChartaTyp
    prozedur: KarstsystemChartaProzedur
    canonical: bool = True


@dataclass(frozen=True)
class KarstsystemCharta:
    normen: tuple[KarstsystemChartaNorm, ...]
    parent: Optional[GeomorphologieNormSatz] = None


def build_karstsystem_charta(parent: Optional[GeomorphologieNormSatz] = None) -> KarstsystemCharta:
    if parent is None:
        parent = build_geomorphologie_norm()
    base = sum(e.geomorphologie_norm_weight for e in parent.normen)
    tier_base = max(e.geomorphologie_norm_tier for e in parent.normen)
    normen = tuple(
        KarstsystemChartaNorm(
            geltung=g,
            geomorphologie_weight=round(base + _WEIGHT_DELTA[g], 4),
            geomorphologie_tier=tier_base + i + 1,
            geomorphologie_ids=(f"karstsystem-charta-{g.name.lower()}-001",),
            geomorphologie_tags=("geomorphologie", "karstsystem", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(KarstsystemChartaGeltung)
    )
    return KarstsystemCharta(normen=normen, parent=parent)
