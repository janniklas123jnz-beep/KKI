"""
#944 SynthetischeBiologieKodex — Synthetische Biologie: BioBricks, Minimalzelle & iGEM.
Endy (2005): Foundations for Engineering Biology — synthetische Biologie als
  Ingenieursdisziplin; standardisierte BioBrick-Teile als genetische Bausteine.
Gibson et al. (2010): Creation of a Bacterial Cell Controlled by Chemically Synthesized
  Genome — erste vollsynthetische Zelle; Mycoplasma mycoides JCVI-syn1.0.
Venter (2016): Design and Synthesis of a Minimal Bacterial Genome — JCVI-syn3.0
  mit nur 473 Genen; Minimalzelle als Grundlage des Lebens definiert.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .crispr_charta import CRISPRCharta, build_crispr_charta


class SynthetischeBiologieKodexTyp(Enum):
    BIOBRICK_STANDARD = auto()
    METABOLIC_ENGINEERING = auto()
    SYNTHETISCHE_ZELLE = auto()
    BIOSENSOR = auto()
    ZELLFABRIK = auto()


class SynthetischeBiologieKodexProzedur(Enum):
    DESIGN = auto()
    BUILD = auto()
    TEST = auto()
    LEARN = auto()
    OPTIMIERUNG = auto()


_WEIGHT_DELTA = {
    SynthetischeBiologieKodexTyp.BIOBRICK_STANDARD: 0.0,
    SynthetischeBiologieKodexTyp.METABOLIC_ENGINEERING: 1.8,
    SynthetischeBiologieKodexTyp.SYNTHETISCHE_ZELLE: 3.6,
    SynthetischeBiologieKodexTyp.BIOSENSOR: 5.4,
    SynthetischeBiologieKodexTyp.ZELLFABRIK: 7.2,
}
_TYP_MAP = {
    SynthetischeBiologieKodexTyp.BIOBRICK_STANDARD: "biobrick_standard",
    SynthetischeBiologieKodexTyp.METABOLIC_ENGINEERING: "metabolic_engineering",
    SynthetischeBiologieKodexTyp.SYNTHETISCHE_ZELLE: "synthetische_zelle",
    SynthetischeBiologieKodexTyp.BIOSENSOR: "biosensor",
    SynthetischeBiologieKodexTyp.ZELLFABRIK: "zellfabrik",
}
_PROZEDUR_MAP = {
    SynthetischeBiologieKodexProzedur.DESIGN: "design",
    SynthetischeBiologieKodexProzedur.BUILD: "build",
    SynthetischeBiologieKodexProzedur.TEST: "test",
    SynthetischeBiologieKodexProzedur.LEARN: "learn",
    SynthetischeBiologieKodexProzedur.OPTIMIERUNG: "optimierung",
}


@dataclass(frozen=True)
class SynthetischeBiologieKodexEintrag:
    typ: SynthetischeBiologieKodexTyp
    prozedur: SynthetischeBiologieKodexProzedur
    biotech_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class SynthetischeBiologieKodex:
    eintraege: tuple[SynthetischeBiologieKodexEintrag, ...]
    canonical: bool = True

    def aggregates_kodex_signal(self) -> dict:
        return {
            "kodex_id": "synthetische-biologie-kodex-944",
            "eintraege_count": len(self.eintraege),
            "canonical": self.canonical,
        }


def build_synthetische_biologie_kodex(parent: Optional[CRISPRCharta] = None) -> SynthetischeBiologieKodex:
    if parent is None:
        parent = build_crispr_charta()
    base = sum(n.biotech_weight for n in parent.normen)
    eintraege = tuple(
        SynthetischeBiologieKodexEintrag(
            typ=t,
            prozedur=list(SynthetischeBiologieKodexProzedur)[i],
            biotech_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(SynthetischeBiologieKodexTyp)
    )
    return SynthetischeBiologieKodex(eintraege=eintraege)
