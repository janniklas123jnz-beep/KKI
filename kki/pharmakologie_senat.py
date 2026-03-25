from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .drug_target_pakt import DrugTargetPakt, build_drug_target_pakt


class PharmakologieSanatGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_PHARMAKOLOGISCH = auto()
    PHARMAKOLOGISCH = auto()
    PHARMAKOLOGISCH_AKTIV = auto()
    PHARMAKOLOGIE_SOUVERAEN = auto()


class PharmakologieSanatTyp(Enum):
    PHARMAKOLOGIESENAT = auto()
    PHARMAKOLOGIEAUSSCHUSS = auto()
    PHARMAKOLOGIERAT = auto()


class PharmakologieSanatProzedur(Enum):
    PHARMAKOLOGIEBEWERTUNG = auto()
    NUTZENBEWERTUNG = auto()
    SICHERHEITSEINSTUFUNG = auto()


_WEIGHT_DELTA: dict[PharmakologieSanatGeltung, float] = {
    PharmakologieSanatGeltung.GESPERRT: 0.0,
    PharmakologieSanatGeltung.GRUNDLEGEND_PHARMAKOLOGISCH: 1.9,
    PharmakologieSanatGeltung.PHARMAKOLOGISCH: 3.8,
    PharmakologieSanatGeltung.PHARMAKOLOGISCH_AKTIV: 5.7,
    PharmakologieSanatGeltung.PHARMAKOLOGIE_SOUVERAEN: 7.6,
}

_TYP_MAP = {
    PharmakologieSanatGeltung.GESPERRT: PharmakologieSanatTyp.PHARMAKOLOGIESENAT,
    PharmakologieSanatGeltung.GRUNDLEGEND_PHARMAKOLOGISCH: PharmakologieSanatTyp.PHARMAKOLOGIEAUSSCHUSS,
    PharmakologieSanatGeltung.PHARMAKOLOGISCH: PharmakologieSanatTyp.PHARMAKOLOGIEAUSSCHUSS,
    PharmakologieSanatGeltung.PHARMAKOLOGISCH_AKTIV: PharmakologieSanatTyp.PHARMAKOLOGIERAT,
    PharmakologieSanatGeltung.PHARMAKOLOGIE_SOUVERAEN: PharmakologieSanatTyp.PHARMAKOLOGIERAT,
}

_PROZEDUR_MAP = {
    PharmakologieSanatGeltung.GESPERRT: PharmakologieSanatProzedur.PHARMAKOLOGIEBEWERTUNG,
    PharmakologieSanatGeltung.GRUNDLEGEND_PHARMAKOLOGISCH: PharmakologieSanatProzedur.PHARMAKOLOGIEBEWERTUNG,
    PharmakologieSanatGeltung.PHARMAKOLOGISCH: PharmakologieSanatProzedur.NUTZENBEWERTUNG,
    PharmakologieSanatGeltung.PHARMAKOLOGISCH_AKTIV: PharmakologieSanatProzedur.NUTZENBEWERTUNG,
    PharmakologieSanatGeltung.PHARMAKOLOGIE_SOUVERAEN: PharmakologieSanatProzedur.SICHERHEITSEINSTUFUNG,
}


@dataclass(frozen=True)
class PharmakologieSanatNorm:
    geltung: PharmakologieSanatGeltung
    pharma_weight: float
    pharma_tier: int
    pharma_ids: tuple[str, ...]
    pharma_tags: tuple[str, ...]
    typ: PharmakologieSanatTyp
    prozedur: PharmakologieSanatProzedur
    canonical: bool = True


@dataclass(frozen=True)
class PharmakologieSenat:
    normen: tuple[PharmakologieSanatNorm, ...]
    parent: Optional[DrugTargetPakt] = None


def build_pharmakologie_senat(parent: Optional[DrugTargetPakt] = None) -> PharmakologieSenat:
    if parent is None:
        parent = build_drug_target_pakt()
    base = sum(e.pharma_weight for e in parent.eintraege)
    normen = tuple(
        PharmakologieSanatNorm(
            geltung=g,
            pharma_weight=round(base + _WEIGHT_DELTA[g], 4),
            pharma_tier=i + 1,
            pharma_ids=(f"pharmakologie-senat-{g.name.lower()}-001",),
            pharma_tags=("pharmakologie", "senat", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(PharmakologieSanatGeltung)
    )
    return PharmakologieSenat(normen=normen, parent=parent)
