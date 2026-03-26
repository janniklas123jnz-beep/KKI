from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .vulkanismus_pakt import VulkanismusPakt, build_vulkanismus_pakt


class GeophysikSenatGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_GEOPHYSIKALISCH = auto()
    GEOPHYSIKALISCH = auto()
    GEOPHYSIKALISCH_AKTIV = auto()
    GEOPHYSIK_SOUVERAEN = auto()


class GeophysikSenatTyp(Enum):
    GEOPHYSIKSENAT = auto()
    GEOPHYSIKRATSYSTEM = auto()
    GEOPHYSIKRATKOMPONENTE = auto()


class GeophysikSenatProzedur(Enum):
    GEOPHYSIKRATANALYSE = auto()
    GEOPHYSIKSYNTHESE = auto()
    GEOPHYSIKRATBEWERTUNG = auto()


_WEIGHT_DELTA: dict[GeophysikSenatGeltung, float] = {
    GeophysikSenatGeltung.GESPERRT: 0.0,
    GeophysikSenatGeltung.GRUNDLEGEND_GEOPHYSIKALISCH: 1.8,
    GeophysikSenatGeltung.GEOPHYSIKALISCH: 3.6,
    GeophysikSenatGeltung.GEOPHYSIKALISCH_AKTIV: 5.4,
    GeophysikSenatGeltung.GEOPHYSIK_SOUVERAEN: 7.2,
}

_TYP_MAP = {
    GeophysikSenatGeltung.GESPERRT: GeophysikSenatTyp.GEOPHYSIKSENAT,
    GeophysikSenatGeltung.GRUNDLEGEND_GEOPHYSIKALISCH: GeophysikSenatTyp.GEOPHYSIKRATKOMPONENTE,
    GeophysikSenatGeltung.GEOPHYSIKALISCH: GeophysikSenatTyp.GEOPHYSIKRATKOMPONENTE,
    GeophysikSenatGeltung.GEOPHYSIKALISCH_AKTIV: GeophysikSenatTyp.GEOPHYSIKRATSYSTEM,
    GeophysikSenatGeltung.GEOPHYSIK_SOUVERAEN: GeophysikSenatTyp.GEOPHYSIKRATSYSTEM,
}

_PROZEDUR_MAP = {
    GeophysikSenatGeltung.GESPERRT: GeophysikSenatProzedur.GEOPHYSIKRATANALYSE,
    GeophysikSenatGeltung.GRUNDLEGEND_GEOPHYSIKALISCH: GeophysikSenatProzedur.GEOPHYSIKRATANALYSE,
    GeophysikSenatGeltung.GEOPHYSIKALISCH: GeophysikSenatProzedur.GEOPHYSIKSYNTHESE,
    GeophysikSenatGeltung.GEOPHYSIKALISCH_AKTIV: GeophysikSenatProzedur.GEOPHYSIKSYNTHESE,
    GeophysikSenatGeltung.GEOPHYSIK_SOUVERAEN: GeophysikSenatProzedur.GEOPHYSIKRATBEWERTUNG,
}


@dataclass(frozen=True)
class GeophysikSenatNorm:
    geltung: GeophysikSenatGeltung
    geophysik_weight: float
    geophysik_tier: int
    geophysik_ids: tuple[str, ...]
    geophysik_tags: tuple[str, ...]
    typ: GeophysikSenatTyp
    prozedur: GeophysikSenatProzedur
    canonical: bool = True


@dataclass(frozen=True)
class GeophysikSenat:
    normen: tuple[GeophysikSenatNorm, ...]
    parent: Optional[VulkanismusPakt] = None


def build_geophysik_senat(parent: Optional[VulkanismusPakt] = None) -> GeophysikSenat:
    if parent is None:
        parent = build_vulkanismus_pakt()
    base = sum(e.geophysik_weight for e in parent.eintraege)
    normen = tuple(
        GeophysikSenatNorm(
            geltung=g,
            geophysik_weight=round(base + _WEIGHT_DELTA[g], 4),
            geophysik_tier=i + 1,
            geophysik_ids=(f"geophysik-senat-{g.name.lower()}-001",),
            geophysik_tags=("geophysik", "senat", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(GeophysikSenatGeltung)
    )
    return GeophysikSenat(normen=normen, parent=parent)
