from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .zeitreihen_pakt import ZeitreihenPakt, build_zeitreihen_pakt


class StochastikSenatGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_STOCHASTISCH = auto()
    STOCHASTISCH = auto()
    STOCHASTISCH_AKTIV = auto()
    STOCHASTIK_SOUVERAEN = auto()


class StochastikSenatTyp(Enum):
    STOCHASTIKSENAT = auto()
    MARKOVKETTE = auto()
    ZUFALLSPROZESS = auto()


class StochastikSenatProzedur(Enum):
    STOCHASTIKANALYSE = auto()
    PROZESSMODELLIERUNG = auto()
    STOCHASTIKBEWERTUNG = auto()


_WEIGHT_DELTA: dict[StochastikSenatGeltung, float] = {
    StochastikSenatGeltung.GESPERRT: 0.0,
    StochastikSenatGeltung.GRUNDLEGEND_STOCHASTISCH: 1.8,
    StochastikSenatGeltung.STOCHASTISCH: 3.6,
    StochastikSenatGeltung.STOCHASTISCH_AKTIV: 5.4,
    StochastikSenatGeltung.STOCHASTIK_SOUVERAEN: 7.2,
}

_TYP_MAP = {
    StochastikSenatGeltung.GESPERRT: StochastikSenatTyp.STOCHASTIKSENAT,
    StochastikSenatGeltung.GRUNDLEGEND_STOCHASTISCH: StochastikSenatTyp.ZUFALLSPROZESS,
    StochastikSenatGeltung.STOCHASTISCH: StochastikSenatTyp.ZUFALLSPROZESS,
    StochastikSenatGeltung.STOCHASTISCH_AKTIV: StochastikSenatTyp.MARKOVKETTE,
    StochastikSenatGeltung.STOCHASTIK_SOUVERAEN: StochastikSenatTyp.MARKOVKETTE,
}

_PROZEDUR_MAP = {
    StochastikSenatGeltung.GESPERRT: StochastikSenatProzedur.STOCHASTIKANALYSE,
    StochastikSenatGeltung.GRUNDLEGEND_STOCHASTISCH: StochastikSenatProzedur.STOCHASTIKANALYSE,
    StochastikSenatGeltung.STOCHASTISCH: StochastikSenatProzedur.PROZESSMODELLIERUNG,
    StochastikSenatGeltung.STOCHASTISCH_AKTIV: StochastikSenatProzedur.PROZESSMODELLIERUNG,
    StochastikSenatGeltung.STOCHASTIK_SOUVERAEN: StochastikSenatProzedur.STOCHASTIKBEWERTUNG,
}


@dataclass(frozen=True)
class StochastikSenatNorm:
    geltung: StochastikSenatGeltung
    stat_weight: float
    stat_tier: int
    stat_ids: tuple[str, ...]
    stat_tags: tuple[str, ...]
    typ: StochastikSenatTyp
    prozedur: StochastikSenatProzedur
    canonical: bool = True


@dataclass(frozen=True)
class StochastikSenat:
    normen: tuple[StochastikSenatNorm, ...]
    parent: Optional[ZeitreihenPakt] = None


def build_stochastik_senat(parent: Optional[ZeitreihenPakt] = None) -> StochastikSenat:
    if parent is None:
        parent = build_zeitreihen_pakt()
    base = sum(e.stat_weight for e in parent.eintraege)
    normen = tuple(
        StochastikSenatNorm(
            geltung=g,
            stat_weight=round(base + _WEIGHT_DELTA[g], 4),
            stat_tier=i + 1,
            stat_ids=(f"stochastik-senat-{g.name.lower()}-001",),
            stat_tags=("stochastik", "senat", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(StochastikSenatGeltung)
    )
    return StochastikSenat(normen=normen, parent=parent)
