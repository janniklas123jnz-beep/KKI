from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .seehydrologie_pakt import SeehydrologiePakt, build_seehydrologie_pakt


class HydrologieSenatGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_HYDROLOGISCH = auto()
    HYDROLOGISCH = auto()
    HYDROLOGISCH_AKTIV = auto()
    HYDROLOGIE_SOUVERAEN = auto()


class HydrologieSenatTyp(Enum):
    HYDROLOGIESENAT = auto()
    HYDROLOGIESENATSSYSTEM = auto()
    HYDROLOGIESENAATSKOMPONENTE = auto()


class HydrologieSenatProzedur(Enum):
    HYDROLOGIESENATANALYSE = auto()
    HYDROLOGIESENATSYNTHESE = auto()
    HYDROLOGIESENATBEWERTUNG = auto()


_WEIGHT_DELTA: dict[HydrologieSenatGeltung, float] = {
    HydrologieSenatGeltung.GESPERRT: 0.0,
    HydrologieSenatGeltung.GRUNDLEGEND_HYDROLOGISCH: 1.8,
    HydrologieSenatGeltung.HYDROLOGISCH: 3.6,
    HydrologieSenatGeltung.HYDROLOGISCH_AKTIV: 5.4,
    HydrologieSenatGeltung.HYDROLOGIE_SOUVERAEN: 7.2,
}

_TYP_MAP = {
    HydrologieSenatGeltung.GESPERRT: HydrologieSenatTyp.HYDROLOGIESENAT,
    HydrologieSenatGeltung.GRUNDLEGEND_HYDROLOGISCH: HydrologieSenatTyp.HYDROLOGIESENAATSKOMPONENTE,
    HydrologieSenatGeltung.HYDROLOGISCH: HydrologieSenatTyp.HYDROLOGIESENAATSKOMPONENTE,
    HydrologieSenatGeltung.HYDROLOGISCH_AKTIV: HydrologieSenatTyp.HYDROLOGIESENATSSYSTEM,
    HydrologieSenatGeltung.HYDROLOGIE_SOUVERAEN: HydrologieSenatTyp.HYDROLOGIESENATSSYSTEM,
}

_PROZEDUR_MAP = {
    HydrologieSenatGeltung.GESPERRT: HydrologieSenatProzedur.HYDROLOGIESENATANALYSE,
    HydrologieSenatGeltung.GRUNDLEGEND_HYDROLOGISCH: HydrologieSenatProzedur.HYDROLOGIESENATANALYSE,
    HydrologieSenatGeltung.HYDROLOGISCH: HydrologieSenatProzedur.HYDROLOGIESENATSYNTHESE,
    HydrologieSenatGeltung.HYDROLOGISCH_AKTIV: HydrologieSenatProzedur.HYDROLOGIESENATSYNTHESE,
    HydrologieSenatGeltung.HYDROLOGIE_SOUVERAEN: HydrologieSenatProzedur.HYDROLOGIESENATBEWERTUNG,
}


@dataclass(frozen=True)
class HydrologieSenatNorm:
    geltung: HydrologieSenatGeltung
    hydrologie_weight: float
    hydrologie_tier: int
    hydrologie_ids: tuple[str, ...]
    hydrologie_tags: tuple[str, ...]
    typ: HydrologieSenatTyp
    prozedur: HydrologieSenatProzedur
    canonical: bool = True


@dataclass(frozen=True)
class HydrologieSenat:
    normen: tuple[HydrologieSenatNorm, ...]
    parent: Optional[SeehydrologiePakt] = None


def build_hydrologie_senat(parent: Optional[SeehydrologiePakt] = None) -> HydrologieSenat:
    if parent is None:
        parent = build_seehydrologie_pakt()
    base = sum(e.hydrologie_weight for e in parent.eintraege)
    normen = tuple(
        HydrologieSenatNorm(
            geltung=g,
            hydrologie_weight=round(base + _WEIGHT_DELTA[g], 4),
            hydrologie_tier=i + 1,
            hydrologie_ids=(f"hydrologie-senat-{g.name.lower()}-001",),
            hydrologie_tags=("hydrologie", "senat", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(HydrologieSenatGeltung)
    )
    return HydrologieSenat(normen=normen, parent=parent)
