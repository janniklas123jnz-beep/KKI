from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .lagerstaettenkunde_pakt import LagerstättenkundePakt, build_lagerstaettenkunde_pakt


class MineralogieSenatGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_MINERALOGISCH = auto()
    MINERALOGISCH = auto()
    MINERALOGISCH_AKTIV = auto()
    MINERALOGIE_SOUVERAEN = auto()


class MineralogieSenatTyp(Enum):
    MINERALOGIESENAT = auto()
    MINERALOGIESENATSSYSTEM = auto()
    MINERALOGIESENAATSKOMPONENTE = auto()


class MineralogieSenatProzedur(Enum):
    MINERALOGIESENATANALYSE = auto()
    MINERALOGIESENATSYNTHESE = auto()
    MINERALOGIESENATBEWERTUNG = auto()


_WEIGHT_DELTA: dict[MineralogieSenatGeltung, float] = {
    MineralogieSenatGeltung.GESPERRT: 0.0,
    MineralogieSenatGeltung.GRUNDLEGEND_MINERALOGISCH: 1.8,
    MineralogieSenatGeltung.MINERALOGISCH: 3.6,
    MineralogieSenatGeltung.MINERALOGISCH_AKTIV: 5.4,
    MineralogieSenatGeltung.MINERALOGIE_SOUVERAEN: 7.2,
}

_TYP_MAP = {
    MineralogieSenatGeltung.GESPERRT: MineralogieSenatTyp.MINERALOGIESENAT,
    MineralogieSenatGeltung.GRUNDLEGEND_MINERALOGISCH: MineralogieSenatTyp.MINERALOGIESENAATSKOMPONENTE,
    MineralogieSenatGeltung.MINERALOGISCH: MineralogieSenatTyp.MINERALOGIESENAATSKOMPONENTE,
    MineralogieSenatGeltung.MINERALOGISCH_AKTIV: MineralogieSenatTyp.MINERALOGIESENATSSYSTEM,
    MineralogieSenatGeltung.MINERALOGIE_SOUVERAEN: MineralogieSenatTyp.MINERALOGIESENATSSYSTEM,
}

_PROZEDUR_MAP = {
    MineralogieSenatGeltung.GESPERRT: MineralogieSenatProzedur.MINERALOGIESENATANALYSE,
    MineralogieSenatGeltung.GRUNDLEGEND_MINERALOGISCH: MineralogieSenatProzedur.MINERALOGIESENATANALYSE,
    MineralogieSenatGeltung.MINERALOGISCH: MineralogieSenatProzedur.MINERALOGIESENATSYNTHESE,
    MineralogieSenatGeltung.MINERALOGISCH_AKTIV: MineralogieSenatProzedur.MINERALOGIESENATSYNTHESE,
    MineralogieSenatGeltung.MINERALOGIE_SOUVERAEN: MineralogieSenatProzedur.MINERALOGIESENATBEWERTUNG,
}


@dataclass(frozen=True)
class MineralogieSenatNorm:
    geltung: MineralogieSenatGeltung
    mineralogie_weight: float
    mineralogie_tier: int
    mineralogie_ids: tuple[str, ...]
    mineralogie_tags: tuple[str, ...]
    typ: MineralogieSenatTyp
    prozedur: MineralogieSenatProzedur
    canonical: bool = True


@dataclass(frozen=True)
class MineralogieSenat:
    normen: tuple[MineralogieSenatNorm, ...]
    parent: Optional[LagerstättenkundePakt] = None


def build_mineralogie_senat(parent: Optional[LagerstättenkundePakt] = None) -> MineralogieSenat:
    if parent is None:
        parent = build_lagerstaettenkunde_pakt()
    base = sum(e.mineralogie_weight for e in parent.eintraege)
    normen = tuple(
        MineralogieSenatNorm(
            geltung=g,
            mineralogie_weight=round(base + _WEIGHT_DELTA[g], 4),
            mineralogie_tier=i + 1,
            mineralogie_ids=(f"mineralogie-senat-{g.name.lower()}-001",),
            mineralogie_tags=("mineralogie", "senat", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(MineralogieSenatGeltung)
    )
    return MineralogieSenat(normen=normen, parent=parent)
