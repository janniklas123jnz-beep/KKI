"""
#943 CRISPRCharta — Genomeditierung: CRISPR-Cas9, Basisschnitt & ethische Grenzen.
Doudna & Charpentier (2012): A Programmable Dual-RNA-Guided DNA Endonuclease —
  CRISPR-Cas9 als universelles Genscherensystem; Nobelpreis 2020; Revolution in
  Präzisionsmedizin, Landwirtschaft und synthetischer Biologie.
David Liu (2016): Base Editing — präzise Einzelbasen-Korrektur ohne Doppelstrangbruch;
  sicherere Alternative zu klassischem CRISPR; therapeutisch nutzbar.
He Jiankui (2018): CRISPR-Babys — erste keimbahnbearbeiteten Menschen; globaler Skandal;
  Notwendigkeit ethischer Rahmenbedingungen für Genomeditierung am Menschen.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .genomik_register import GenomikRegister, build_genomik_register


class CRISPRChartaTyp(Enum):
    CRISPR_CAS9 = auto()
    BASE_EDITING = auto()
    PRIME_EDITING = auto()
    EPIGENETISCHES_EDITING = auto()
    KEIMBAHNTHERAPIE = auto()


class CRISPRChartaProzedur(Enum):
    GUIDE_RNA_DESIGN = auto()
    DELIVERY = auto()
    SCHNITT = auto()
    REPARATUR = auto()
    VERIFIKATION = auto()


_WEIGHT_DELTA = {
    CRISPRChartaTyp.CRISPR_CAS9: 0.0,
    CRISPRChartaTyp.BASE_EDITING: 1.7,
    CRISPRChartaTyp.PRIME_EDITING: 3.4,
    CRISPRChartaTyp.EPIGENETISCHES_EDITING: 5.1,
    CRISPRChartaTyp.KEIMBAHNTHERAPIE: 6.8,
}
_TYP_MAP = {
    CRISPRChartaTyp.CRISPR_CAS9: "crispr_cas9",
    CRISPRChartaTyp.BASE_EDITING: "base_editing",
    CRISPRChartaTyp.PRIME_EDITING: "prime_editing",
    CRISPRChartaTyp.EPIGENETISCHES_EDITING: "epigenetisches_editing",
    CRISPRChartaTyp.KEIMBAHNTHERAPIE: "keimbahntherapie",
}
_PROZEDUR_MAP = {
    CRISPRChartaProzedur.GUIDE_RNA_DESIGN: "guide_rna_design",
    CRISPRChartaProzedur.DELIVERY: "delivery",
    CRISPRChartaProzedur.SCHNITT: "schnitt",
    CRISPRChartaProzedur.REPARATUR: "reparatur",
    CRISPRChartaProzedur.VERIFIKATION: "verifikation",
}


@dataclass(frozen=True)
class CRISPRChartaNorm:
    typ: CRISPRChartaTyp
    prozedur: CRISPRChartaProzedur
    biotech_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class CRISPRCharta:
    normen: tuple[CRISPRChartaNorm, ...]
    canonical: bool = True

    def aggregates_charta_signal(self) -> dict:
        return {
            "charta_id": "crispr-charta-943",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_crispr_charta(parent: Optional[GenomikRegister] = None) -> CRISPRCharta:
    if parent is None:
        parent = build_genomik_register()
    base = sum(e.biotech_weight for e in parent.eintraege)
    normen = tuple(
        CRISPRChartaNorm(
            typ=t,
            prozedur=list(CRISPRChartaProzedur)[i],
            biotech_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(CRISPRChartaTyp)
    )
    return CRISPRCharta(normen=normen)
