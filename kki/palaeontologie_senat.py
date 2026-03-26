from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .erdzeitalter_pakt import ErdzeitalterPakt, build_erdzeitalter_pakt


class PalaeontologieSenatGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_PALAEONTOLOGISCH = auto()
    PALAEONTOLOGISCH = auto()
    PALAEONTOLOGISCH_AKTIV = auto()
    PALAEONTOLOGIE_SOUVERAEN = auto()


class PalaeontologieSenatTyp(Enum):
    PALAEONTOLOGIESENAT = auto()
    PALAEONTOLOGIEBEIRAT = auto()
    PALAEONTOLOGIERAT = auto()


class PalaeontologieSenatProzedur(Enum):
    PALAEONTOLOGIEBERATUNG = auto()
    PALAEONTOLOGIEBESCHLUSSFASSUNG = auto()
    PALAEONTOLOGIEAUFSICHT = auto()


_WEIGHT_DELTA: dict[PalaeontologieSenatGeltung, float] = {
    PalaeontologieSenatGeltung.GESPERRT: 0.0,
    PalaeontologieSenatGeltung.GRUNDLEGEND_PALAEONTOLOGISCH: 1.8,
    PalaeontologieSenatGeltung.PALAEONTOLOGISCH: 3.6,
    PalaeontologieSenatGeltung.PALAEONTOLOGISCH_AKTIV: 5.4,
    PalaeontologieSenatGeltung.PALAEONTOLOGIE_SOUVERAEN: 7.2,
}

_TYP_MAP = {
    PalaeontologieSenatGeltung.GESPERRT: PalaeontologieSenatTyp.PALAEONTOLOGIESENAT,
    PalaeontologieSenatGeltung.GRUNDLEGEND_PALAEONTOLOGISCH: PalaeontologieSenatTyp.PALAEONTOLOGIERAT,
    PalaeontologieSenatGeltung.PALAEONTOLOGISCH: PalaeontologieSenatTyp.PALAEONTOLOGIERAT,
    PalaeontologieSenatGeltung.PALAEONTOLOGISCH_AKTIV: PalaeontologieSenatTyp.PALAEONTOLOGIEBEIRAT,
    PalaeontologieSenatGeltung.PALAEONTOLOGIE_SOUVERAEN: PalaeontologieSenatTyp.PALAEONTOLOGIEBEIRAT,
}

_PROZEDUR_MAP = {
    PalaeontologieSenatGeltung.GESPERRT: PalaeontologieSenatProzedur.PALAEONTOLOGIEBERATUNG,
    PalaeontologieSenatGeltung.GRUNDLEGEND_PALAEONTOLOGISCH: PalaeontologieSenatProzedur.PALAEONTOLOGIEBERATUNG,
    PalaeontologieSenatGeltung.PALAEONTOLOGISCH: PalaeontologieSenatProzedur.PALAEONTOLOGIEBESCHLUSSFASSUNG,
    PalaeontologieSenatGeltung.PALAEONTOLOGISCH_AKTIV: PalaeontologieSenatProzedur.PALAEONTOLOGIEBESCHLUSSFASSUNG,
    PalaeontologieSenatGeltung.PALAEONTOLOGIE_SOUVERAEN: PalaeontologieSenatProzedur.PALAEONTOLOGIEAUFSICHT,
}


@dataclass(frozen=True)
class PalaeontologieSenatNorm:
    geltung: PalaeontologieSenatGeltung
    palaeontologie_weight: float
    palaeontologie_tier: int
    palaeontologie_ids: tuple[str, ...]
    palaeontologie_tags: tuple[str, ...]
    typ: PalaeontologieSenatTyp
    prozedur: PalaeontologieSenatProzedur
    canonical: bool = True


@dataclass(frozen=True)
class PalaeontologieSenat:
    normen: tuple[PalaeontologieSenatNorm, ...]
    parent: Optional[ErdzeitalterPakt] = None


def build_palaeontologie_senat(parent: Optional[ErdzeitalterPakt] = None) -> PalaeontologieSenat:
    if parent is None:
        parent = build_erdzeitalter_pakt()
    base = sum(e.palaeontologie_weight for e in parent.eintraege)
    normen = tuple(
        PalaeontologieSenatNorm(
            geltung=g,
            palaeontologie_weight=round(base + _WEIGHT_DELTA[g], 4),
            palaeontologie_tier=i + 1,
            palaeontologie_ids=(f"palaeontologie-senat-{g.name.lower()}-001",),
            palaeontologie_tags=("palaeontologie", "senat", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(PalaeontologieSenatGeltung)
    )
    return PalaeontologieSenat(normen=normen, parent=parent)
