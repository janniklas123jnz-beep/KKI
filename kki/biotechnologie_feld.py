"""
#941 BiotechnologieFeld — Biotechnologie: Watson/Crick, Zentrales Dogma & PCR.
Watson & Crick (1953): Molecular Structure of Nucleic Acids — Doppelhelix der DNA;
  Strukturaufklärung als Startschuss der Molekularbiologie und Biotechnologie.
Crick (1958): The Central Dogma of Molecular Biology — DNA → RNA → Protein;
  fundamentaler Informationsfluss des Lebens; Basis aller gentechnischen Eingriffe.
Mullis (1983): Polymerase Chain Reaction — PCR als Amplifizierungswerkzeug;
  exponentielles Vervielfältigen von DNA-Sequenzen; Grundlage aller Biotech-Diagnostik.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .quanten_verfassung import QuantenVerfassung, build_quanten_verfassung


class BiotechnologieFeldTyp(Enum):
    MOLEKULARBIOLOGIE = auto()
    ZELLBIOLOGIE = auto()
    MIKROBIOLOGIE = auto()
    BIOCHEMIE = auto()
    SYSTEMBIOLOGIE = auto()


class BiotechnologieFeldProzedur(Enum):
    KLONIERUNG = auto()
    EXPRESSION = auto()
    SEQUENZIERUNG = auto()
    ANALYSE = auto()
    OPTIMIERUNG = auto()


_WEIGHT_DELTA = {
    BiotechnologieFeldTyp.MOLEKULARBIOLOGIE: 0.0,
    BiotechnologieFeldTyp.ZELLBIOLOGIE: 1.4,
    BiotechnologieFeldTyp.MIKROBIOLOGIE: 2.8,
    BiotechnologieFeldTyp.BIOCHEMIE: 4.2,
    BiotechnologieFeldTyp.SYSTEMBIOLOGIE: 5.6,
}
_TYP_MAP = {
    BiotechnologieFeldTyp.MOLEKULARBIOLOGIE: "molekularbiologie",
    BiotechnologieFeldTyp.ZELLBIOLOGIE: "zellbiologie",
    BiotechnologieFeldTyp.MIKROBIOLOGIE: "mikrobiologie",
    BiotechnologieFeldTyp.BIOCHEMIE: "biochemie",
    BiotechnologieFeldTyp.SYSTEMBIOLOGIE: "systembiologie",
}
_PROZEDUR_MAP = {
    BiotechnologieFeldProzedur.KLONIERUNG: "klonierung",
    BiotechnologieFeldProzedur.EXPRESSION: "expression",
    BiotechnologieFeldProzedur.SEQUENZIERUNG: "sequenzierung",
    BiotechnologieFeldProzedur.ANALYSE: "analyse",
    BiotechnologieFeldProzedur.OPTIMIERUNG: "optimierung",
}


@dataclass(frozen=True)
class BiotechnologieFeldNorm:
    typ: BiotechnologieFeldTyp
    prozedur: BiotechnologieFeldProzedur
    biotech_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class BiotechnologieFeld:
    normen: tuple[BiotechnologieFeldNorm, ...]
    canonical: bool = True

    def aggregates_feld_signal(self) -> dict:
        return {
            "feld_id": "biotechnologie-feld-941",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_biotechnologie_feld(parent: Optional[QuantenVerfassung] = None) -> BiotechnologieFeld:
    if parent is None:
        parent = build_quanten_verfassung()
    base = sum(n.quanten_weight for n in parent.normen)
    normen = tuple(
        BiotechnologieFeldNorm(
            typ=t,
            prozedur=list(BiotechnologieFeldProzedur)[i],
            biotech_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(BiotechnologieFeldTyp)
    )
    return BiotechnologieFeld(normen=normen)
