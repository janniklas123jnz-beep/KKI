from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .meereis_pakt import MeereisPakt, build_meereis_pakt


class GlaziologieSenatTyp(Enum):
    MASSENHAUSHALT = auto()
    EISDYNAMIK = auto()
    KRYOSPHAERE = auto()
    KLIMAWECHSELWIRKUNG = auto()
    RESSOURCEN = auto()


class GlaziologieSenatProzedur(Enum):
    BERATUNG = auto()
    STANDARDISIERUNG = auto()
    FORSCHUNG = auto()
    KOORDINATION = auto()
    DOKUMENTATION = auto()


_WEIGHT_DELTA = {
    GlaziologieSenatTyp.MASSENHAUSHALT: 0.0,
    GlaziologieSenatTyp.EISDYNAMIK: 1.8,
    GlaziologieSenatTyp.KRYOSPHAERE: 3.6,
    GlaziologieSenatTyp.KLIMAWECHSELWIRKUNG: 5.4,
    GlaziologieSenatTyp.RESSOURCEN: 7.2,
}
_TYP_MAP = {
    GlaziologieSenatTyp.MASSENHAUSHALT: "massenhaushalt",
    GlaziologieSenatTyp.EISDYNAMIK: "eisdynamik",
    GlaziologieSenatTyp.KRYOSPHAERE: "kryosphaere",
    GlaziologieSenatTyp.KLIMAWECHSELWIRKUNG: "klimawechselwirkung",
    GlaziologieSenatTyp.RESSOURCEN: "ressourcen",
}
_PROZEDUR_MAP = {
    GlaziologieSenatProzedur.BERATUNG: "beratung",
    GlaziologieSenatProzedur.STANDARDISIERUNG: "standardisierung",
    GlaziologieSenatProzedur.FORSCHUNG: "forschung",
    GlaziologieSenatProzedur.KOORDINATION: "koordination",
    GlaziologieSenatProzedur.DOKUMENTATION: "dokumentation",
}


@dataclass(frozen=True)
class GlaziologieSenatNorm:
    typ: GlaziologieSenatTyp
    prozedur: GlaziologieSenatProzedur
    glaziologie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class GlaziologieSenat:
    normen: tuple[GlaziologieSenatNorm, ...]
    canonical: bool = True

    def aggregates_senat_signal(self) -> dict:
        return {
            "senat_id": "glaziologie-senat-897",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_glaziologie_senat(parent: Optional[MeereisPakt] = None) -> GlaziologieSenat:
    if parent is None:
        parent = build_meereis_pakt()
    base = sum(e.glaziologie_weight for e in parent.eintraege)
    normen = tuple(
        GlaziologieSenatNorm(
            typ=t,
            prozedur=list(GlaziologieSenatProzedur)[i],
            glaziologie_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(GlaziologieSenatTyp)
    )
    return GlaziologieSenat(normen=normen)
