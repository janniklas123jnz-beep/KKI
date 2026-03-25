from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .kuestenoekologie_pakt import KuestenoekologiePakt, build_kuestenoekologie_pakt


class OzeanographieSenatGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_OZEANOGRAPHISCH = auto()
    OZEANOGRAPHISCH = auto()
    OZEANOGRAPHISCH_AKTIV = auto()
    OZEAN_SOUVERAEN = auto()


class OzeanographieSenatTyp(Enum):
    OZEANOGRAPHIESENAT = auto()
    OZEANRATSYSTEM = auto()
    OZEANRATKOMPONENTE = auto()


class OzeanographieSenatProzedur(Enum):
    OZEANRATANALYSE = auto()
    OZEANRATSYNTHESE = auto()
    OZEANRATBEWERTUNG = auto()


_WEIGHT_DELTA: dict[OzeanographieSenatGeltung, float] = {
    OzeanographieSenatGeltung.GESPERRT: 0.0,
    OzeanographieSenatGeltung.GRUNDLEGEND_OZEANOGRAPHISCH: 1.8,
    OzeanographieSenatGeltung.OZEANOGRAPHISCH: 3.6,
    OzeanographieSenatGeltung.OZEANOGRAPHISCH_AKTIV: 5.4,
    OzeanographieSenatGeltung.OZEAN_SOUVERAEN: 7.2,
}

_TYP_MAP = {
    OzeanographieSenatGeltung.GESPERRT: OzeanographieSenatTyp.OZEANOGRAPHIESENAT,
    OzeanographieSenatGeltung.GRUNDLEGEND_OZEANOGRAPHISCH: OzeanographieSenatTyp.OZEANRATKOMPONENTE,
    OzeanographieSenatGeltung.OZEANOGRAPHISCH: OzeanographieSenatTyp.OZEANRATKOMPONENTE,
    OzeanographieSenatGeltung.OZEANOGRAPHISCH_AKTIV: OzeanographieSenatTyp.OZEANRATSYSTEM,
    OzeanographieSenatGeltung.OZEAN_SOUVERAEN: OzeanographieSenatTyp.OZEANRATSYSTEM,
}

_PROZEDUR_MAP = {
    OzeanographieSenatGeltung.GESPERRT: OzeanographieSenatProzedur.OZEANRATANALYSE,
    OzeanographieSenatGeltung.GRUNDLEGEND_OZEANOGRAPHISCH: OzeanographieSenatProzedur.OZEANRATANALYSE,
    OzeanographieSenatGeltung.OZEANOGRAPHISCH: OzeanographieSenatProzedur.OZEANRATSYNTHESE,
    OzeanographieSenatGeltung.OZEANOGRAPHISCH_AKTIV: OzeanographieSenatProzedur.OZEANRATSYNTHESE,
    OzeanographieSenatGeltung.OZEAN_SOUVERAEN: OzeanographieSenatProzedur.OZEANRATBEWERTUNG,
}


@dataclass(frozen=True)
class OzeanographieSenatNorm:
    geltung: OzeanographieSenatGeltung
    ozean_weight: float
    ozean_tier: int
    ozean_ids: tuple[str, ...]
    ozean_tags: tuple[str, ...]
    typ: OzeanographieSenatTyp
    prozedur: OzeanographieSenatProzedur
    canonical: bool = True


@dataclass(frozen=True)
class OzeanographieSenat:
    normen: tuple[OzeanographieSenatNorm, ...]
    parent: Optional[KuestenoekologiePakt] = None


def build_ozeanographie_senat(parent: Optional[KuestenoekologiePakt] = None) -> OzeanographieSenat:
    if parent is None:
        parent = build_kuestenoekologie_pakt()
    base = sum(e.ozean_weight for e in parent.eintraege)
    normen = tuple(
        OzeanographieSenatNorm(
            geltung=g,
            ozean_weight=round(base + _WEIGHT_DELTA[g], 4),
            ozean_tier=i + 1,
            ozean_ids=(f"ozeanographie-senat-{g.name.lower()}-001",),
            ozean_tags=("ozean", "ozeanographie", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(OzeanographieSenatGeltung)
    )
    return OzeanographieSenat(normen=normen, parent=parent)
