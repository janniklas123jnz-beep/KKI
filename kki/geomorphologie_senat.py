from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .flussmorphologie_pakt import FlussmorphologiePakt, build_flussmorphologie_pakt


class GeomorphologieSenatGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_GEOMORPHOLOGISCH = auto()
    GEOMORPHOLOGISCH = auto()
    GEOMORPHOLOGISCH_AKTIV = auto()
    GEOMORPHOLOGIE_SOUVERAEN = auto()


class GeomorphologieSenatTyp(Enum):
    GEOMORPHOLOGIESENAT = auto()
    GEOMORPHOLOGIEBEIRAT = auto()
    GEOMORPHOLOGIERAT = auto()


class GeomorphologieSenatProzedur(Enum):
    GEOMORPHOLOGIEBERATUNG = auto()
    GEOMORPHOLOGIEBESCHLUSSFASSUNG = auto()
    GEOMORPHOLOGIEAUFSICHT = auto()


_WEIGHT_DELTA: dict[GeomorphologieSenatGeltung, float] = {
    GeomorphologieSenatGeltung.GESPERRT: 0.0,
    GeomorphologieSenatGeltung.GRUNDLEGEND_GEOMORPHOLOGISCH: 1.8,
    GeomorphologieSenatGeltung.GEOMORPHOLOGISCH: 3.6,
    GeomorphologieSenatGeltung.GEOMORPHOLOGISCH_AKTIV: 5.4,
    GeomorphologieSenatGeltung.GEOMORPHOLOGIE_SOUVERAEN: 7.2,
}

_TYP_MAP = {
    GeomorphologieSenatGeltung.GESPERRT: GeomorphologieSenatTyp.GEOMORPHOLOGIESENAT,
    GeomorphologieSenatGeltung.GRUNDLEGEND_GEOMORPHOLOGISCH: GeomorphologieSenatTyp.GEOMORPHOLOGIERAT,
    GeomorphologieSenatGeltung.GEOMORPHOLOGISCH: GeomorphologieSenatTyp.GEOMORPHOLOGIERAT,
    GeomorphologieSenatGeltung.GEOMORPHOLOGISCH_AKTIV: GeomorphologieSenatTyp.GEOMORPHOLOGIEBEIRAT,
    GeomorphologieSenatGeltung.GEOMORPHOLOGIE_SOUVERAEN: GeomorphologieSenatTyp.GEOMORPHOLOGIEBEIRAT,
}

_PROZEDUR_MAP = {
    GeomorphologieSenatGeltung.GESPERRT: GeomorphologieSenatProzedur.GEOMORPHOLOGIEBERATUNG,
    GeomorphologieSenatGeltung.GRUNDLEGEND_GEOMORPHOLOGISCH: GeomorphologieSenatProzedur.GEOMORPHOLOGIEBERATUNG,
    GeomorphologieSenatGeltung.GEOMORPHOLOGISCH: GeomorphologieSenatProzedur.GEOMORPHOLOGIEBESCHLUSSFASSUNG,
    GeomorphologieSenatGeltung.GEOMORPHOLOGISCH_AKTIV: GeomorphologieSenatProzedur.GEOMORPHOLOGIEBESCHLUSSFASSUNG,
    GeomorphologieSenatGeltung.GEOMORPHOLOGIE_SOUVERAEN: GeomorphologieSenatProzedur.GEOMORPHOLOGIEAUFSICHT,
}


@dataclass(frozen=True)
class GeomorphologieSenatNorm:
    geltung: GeomorphologieSenatGeltung
    geomorphologie_weight: float
    geomorphologie_tier: int
    geomorphologie_ids: tuple[str, ...]
    geomorphologie_tags: tuple[str, ...]
    typ: GeomorphologieSenatTyp
    prozedur: GeomorphologieSenatProzedur
    canonical: bool = True


@dataclass(frozen=True)
class GeomorphologieSenat:
    normen: tuple[GeomorphologieSenatNorm, ...]
    parent: Optional[FlussmorphologiePakt] = None


def build_geomorphologie_senat(parent: Optional[FlussmorphologiePakt] = None) -> GeomorphologieSenat:
    if parent is None:
        parent = build_flussmorphologie_pakt()
    base = sum(e.geomorphologie_weight for e in parent.eintraege)
    normen = tuple(
        GeomorphologieSenatNorm(
            geltung=g,
            geomorphologie_weight=round(base + _WEIGHT_DELTA[g], 4),
            geomorphologie_tier=i + 1,
            geomorphologie_ids=(f"geomorphologie-senat-{g.name.lower()}-001",),
            geomorphologie_tags=("geomorphologie", "senat", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(GeomorphologieSenatGeltung)
    )
    return GeomorphologieSenat(normen=normen, parent=parent)
