"""
#942 GenomikRegister — Genomik: Humangenomprojekt, NGS & Epigenetik.
Collins et al. (2003): The Human Genome Project — vollständige Sequenzierung des
  menschlichen Genoms; 3 Milliarden Basenpaare als Buch des Lebens entschlüsselt.
Metzker (2010): Sequencing Technologies — Next-Generation Sequencing (NGS);
  massive parallele Sequenzierung reduziert Kosten von 3 Mrd. $ auf unter 1.000 $.
Waddington (1942): Epigenetics — Genexpression ohne DNA-Veränderung; Methylierung
  und Histonmodifikation als epigenetische Schalter; Umwelt formt Genaktivität.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .biotechnologie_feld import BiotechnologieFeld, build_biotechnologie_feld


class GenomikRegisterTyp(Enum):
    GENOMSEQUENZIERUNG = auto()
    TRANSKRIPTOMIK = auto()
    PROTEOMIK = auto()
    EPIGENOMIK = auto()
    METAGENOMIK = auto()


class GenomikRegisterProzedur(Enum):
    PROBENAUFBEREITUNG = auto()
    SEQUENZIERUNG = auto()
    ASSEMBLY = auto()
    ANNOTATION = auto()
    INTERPRETATION = auto()


_WEIGHT_DELTA = {
    GenomikRegisterTyp.GENOMSEQUENZIERUNG: 0.0,
    GenomikRegisterTyp.TRANSKRIPTOMIK: 1.5,
    GenomikRegisterTyp.PROTEOMIK: 3.0,
    GenomikRegisterTyp.EPIGENOMIK: 4.5,
    GenomikRegisterTyp.METAGENOMIK: 6.0,
}
_TYP_MAP = {
    GenomikRegisterTyp.GENOMSEQUENZIERUNG: "genomsequenzierung",
    GenomikRegisterTyp.TRANSKRIPTOMIK: "transkriptomik",
    GenomikRegisterTyp.PROTEOMIK: "proteomik",
    GenomikRegisterTyp.EPIGENOMIK: "epigenomik",
    GenomikRegisterTyp.METAGENOMIK: "metagenomik",
}
_PROZEDUR_MAP = {
    GenomikRegisterProzedur.PROBENAUFBEREITUNG: "probenaufbereitung",
    GenomikRegisterProzedur.SEQUENZIERUNG: "sequenzierung",
    GenomikRegisterProzedur.ASSEMBLY: "assembly",
    GenomikRegisterProzedur.ANNOTATION: "annotation",
    GenomikRegisterProzedur.INTERPRETATION: "interpretation",
}


@dataclass(frozen=True)
class GenomikRegisterEintrag:
    typ: GenomikRegisterTyp
    prozedur: GenomikRegisterProzedur
    biotech_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class GenomikRegister:
    eintraege: tuple[GenomikRegisterEintrag, ...]
    canonical: bool = True

    def aggregates_register_signal(self) -> dict:
        return {
            "register_id": "genomik-register-942",
            "eintraege_count": len(self.eintraege),
            "canonical": self.canonical,
        }


def build_genomik_register(parent: Optional[BiotechnologieFeld] = None) -> GenomikRegister:
    if parent is None:
        parent = build_biotechnologie_feld()
    base = sum(n.biotech_weight for n in parent.normen)
    eintraege = tuple(
        GenomikRegisterEintrag(
            typ=t,
            prozedur=list(GenomikRegisterProzedur)[i],
            biotech_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(GenomikRegisterTyp)
    )
    return GenomikRegister(eintraege=eintraege)
