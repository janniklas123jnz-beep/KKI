"""
#947 BioinformatikSenat — Bioinformatik: BLAST, AlphaFold & Systembiologie-Governance.
Altschul et al. (1990): Basic Local Alignment Search Tool (BLAST) — schnelle
  Sequenzähnlichkeitssuche; Grundlage aller Genomdatenbankanalysen weltweit.
Jumper et al./DeepMind (2021): AlphaFold2 — KI-basierte Proteinstrukturvorhersage;
  löst 50-jähriges Proteinfaltungsproblem; revolutioniert Strukturbiologie.
Kitano (2002): Systems Biology — integrative Analyse biologischer Systeme;
  mathematische Modellierung von Stoffwechselnetzwerken und Signalkaskaden.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .bioprozesstechnik_pakt import BioprozesstechnikPakt, build_bioprozesstechnik_pakt


class BioinformatikSenatTyp(Enum):
    SEQUENZANALYSE = auto()
    STRUKTURVORHERSAGE = auto()
    NETZWERKANALYSE = auto()
    PHYLOGENETIK = auto()
    SINGLE_CELL_ANALYSE = auto()


class BioinformatikSenatProzedur(Enum):
    DATENERHEBUNG = auto()
    ALIGNMENT = auto()
    MODELLIERUNG = auto()
    VISUALISIERUNG = auto()
    INTERPRETATION = auto()


_WEIGHT_DELTA = {
    BioinformatikSenatTyp.SEQUENZANALYSE: 0.0,
    BioinformatikSenatTyp.STRUKTURVORHERSAGE: 1.9,
    BioinformatikSenatTyp.NETZWERKANALYSE: 3.8,
    BioinformatikSenatTyp.PHYLOGENETIK: 5.7,
    BioinformatikSenatTyp.SINGLE_CELL_ANALYSE: 7.6,
}
_TYP_MAP = {
    BioinformatikSenatTyp.SEQUENZANALYSE: "sequenzanalyse",
    BioinformatikSenatTyp.STRUKTURVORHERSAGE: "strukturvorhersage",
    BioinformatikSenatTyp.NETZWERKANALYSE: "netzwerkanalyse",
    BioinformatikSenatTyp.PHYLOGENETIK: "phylogenetik",
    BioinformatikSenatTyp.SINGLE_CELL_ANALYSE: "single_cell_analyse",
}
_PROZEDUR_MAP = {
    BioinformatikSenatProzedur.DATENERHEBUNG: "datenerhebung",
    BioinformatikSenatProzedur.ALIGNMENT: "alignment",
    BioinformatikSenatProzedur.MODELLIERUNG: "modellierung",
    BioinformatikSenatProzedur.VISUALISIERUNG: "visualisierung",
    BioinformatikSenatProzedur.INTERPRETATION: "interpretation",
}


@dataclass(frozen=True)
class BioinformatikSenatNorm:
    typ: BioinformatikSenatTyp
    prozedur: BioinformatikSenatProzedur
    biotech_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class BioinformatikSenat:
    normen: tuple[BioinformatikSenatNorm, ...]
    canonical: bool = True

    def aggregates_senat_signal(self) -> dict:
        return {
            "senat_id": "bioinformatik-senat-947",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_bioinformatik_senat(parent: Optional[BioprozesstechnikPakt] = None) -> BioinformatikSenat:
    if parent is None:
        parent = build_bioprozesstechnik_pakt()
    base = sum(e.biotech_weight for e in parent.eintraege)
    normen = tuple(
        BioinformatikSenatNorm(
            typ=t,
            prozedur=list(BioinformatikSenatProzedur)[i],
            biotech_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(BioinformatikSenatTyp)
    )
    return BioinformatikSenat(normen=normen)
