from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .landwirtschaft_pakt import LandwirtschaftPakt, build_landwirtschaft_pakt


class AgraroekologieSenatGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_AGRAROEKOLOGISCH = auto()
    AGRAROEKOLOGISCH = auto()
    AGRAROEKOLOGISCH_AKTIV = auto()
    AGRAOEKOLOGIE_SOUVERAEN = auto()


class AgraroekologieSenatTyp(Enum):
    AGRAROEKOLOGIESENAT = auto()
    OEKOSYSTEMRAT = auto()
    BIODIVERSITAETSAUSSCHUSS = auto()


class AgraroekologieSenatProzedur(Enum):
    OEKOSYSTEMANALYSE = auto()
    BIODIVERSITAETSBEWERTUNG = auto()
    AGRARUMWELTBEWERTUNG = auto()


_WEIGHT_DELTA: dict[AgraroekologieSenatGeltung, float] = {
    AgraroekologieSenatGeltung.GESPERRT: 0.0,
    AgraroekologieSenatGeltung.GRUNDLEGEND_AGRAROEKOLOGISCH: 1.8,
    AgraroekologieSenatGeltung.AGRAROEKOLOGISCH: 3.6,
    AgraroekologieSenatGeltung.AGRAROEKOLOGISCH_AKTIV: 5.4,
    AgraroekologieSenatGeltung.AGRAOEKOLOGIE_SOUVERAEN: 7.2,
}

_TYP_MAP = {
    AgraroekologieSenatGeltung.GESPERRT: AgraroekologieSenatTyp.AGRAROEKOLOGIESENAT,
    AgraroekologieSenatGeltung.GRUNDLEGEND_AGRAROEKOLOGISCH: AgraroekologieSenatTyp.OEKOSYSTEMRAT,
    AgraroekologieSenatGeltung.AGRAROEKOLOGISCH: AgraroekologieSenatTyp.OEKOSYSTEMRAT,
    AgraroekologieSenatGeltung.AGRAROEKOLOGISCH_AKTIV: AgraroekologieSenatTyp.BIODIVERSITAETSAUSSCHUSS,
    AgraroekologieSenatGeltung.AGRAOEKOLOGIE_SOUVERAEN: AgraroekologieSenatTyp.BIODIVERSITAETSAUSSCHUSS,
}

_PROZEDUR_MAP = {
    AgraroekologieSenatGeltung.GESPERRT: AgraroekologieSenatProzedur.OEKOSYSTEMANALYSE,
    AgraroekologieSenatGeltung.GRUNDLEGEND_AGRAROEKOLOGISCH: AgraroekologieSenatProzedur.OEKOSYSTEMANALYSE,
    AgraroekologieSenatGeltung.AGRAROEKOLOGISCH: AgraroekologieSenatProzedur.BIODIVERSITAETSBEWERTUNG,
    AgraroekologieSenatGeltung.AGRAROEKOLOGISCH_AKTIV: AgraroekologieSenatProzedur.BIODIVERSITAETSBEWERTUNG,
    AgraroekologieSenatGeltung.AGRAOEKOLOGIE_SOUVERAEN: AgraroekologieSenatProzedur.AGRARUMWELTBEWERTUNG,
}


@dataclass(frozen=True)
class AgraroekologieSenatNorm:
    geltung: AgraroekologieSenatGeltung
    agrar_weight: float
    agrar_tier: int
    agrar_ids: tuple[str, ...]
    agrar_tags: tuple[str, ...]
    typ: AgraroekologieSenatTyp
    prozedur: AgraroekologieSenatProzedur
    canonical: bool = True


@dataclass(frozen=True)
class AgraroekologieSenat:
    normen: tuple[AgraroekologieSenatNorm, ...]
    parent: Optional[LandwirtschaftPakt] = None


def build_agraoekologie_senat(parent: Optional[LandwirtschaftPakt] = None) -> AgraroekologieSenat:
    if parent is None:
        parent = build_landwirtschaft_pakt()
    base = sum(e.agrar_weight for e in parent.eintraege)
    normen = tuple(
        AgraroekologieSenatNorm(
            geltung=g,
            agrar_weight=round(base + _WEIGHT_DELTA[g], 4),
            agrar_tier=i + 1,
            agrar_ids=(f"agraroekologie-senat-{g.name.lower()}-001",),
            agrar_tags=("agraroekologie", "senat", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(AgraroekologieSenatGeltung)
    )
    return AgraroekologieSenat(normen=normen, parent=parent)
