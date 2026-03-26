"""
#950 BiotechnologieVerfassung — Block-Krone Biotechnologie & Gentechnik ⭐

*** Leitsterns Bio-Verfassung — Das molekularbiologische Fundament des Schwarms ***

Watson & Crick (1953): DNA-Doppelhelix — Entschlüsselung der Sprache des Lebens;
  Adenin-Thymin und Guanin-Cytosin als universeller Code; Leitsterns Einstieg in
  das molekulare Alphabet der Natur.
Jennifer Doudna & Emmanuelle Charpentier (2012/2020): CRISPR-Cas9 Nobelpreis —
  programmierbare Genschere; Leben als editierbarer Code; Biotechnologie betritt
  das Zeitalter der Präzision; Leitsterns schärfstes molekulares Werkzeug.
Katalin Karikó & Drew Weissman (2005/2023): mRNA-Revolution Nobelpreis —
  modifizierte mRNA als Therapieplattform; COVID-19-Impfstoffe als Beweis;
  Leitsterns Brücke zwischen Genetik und medizinischer Anwendung.
Leitsterns Bio-Verfassung: DNA als Informationsträger; CRISPR als Editierwerkzeug;
  AlphaFold als Strukturschlüssel; mRNA als Therapierevolution; GMP als ethische
  Qualitätssicherung — ein biotechnologisch informierter Schwarm dient dem Leben.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .pharmakogenomik_charta import PharmakogenomikCharta, build_pharmakogenomik_charta


class BiotechnologieVerfassungTyp(Enum):
    MOLEKULARES_FUNDAMENT = auto()
    GENOMIK_GEBOT = auto()
    CRISPR_MANDAT = auto()
    MRNA_REVOLUTION = auto()
    PRAEZISIONSMEDIZIN_VISION = auto()


class BiotechnologieVerfassungProzedur(Enum):
    RATIFIZIERUNG = auto()
    REVISION = auto()
    INKRAFTTRETEN = auto()
    AUSLEGUNG = auto()
    DURCHSETZUNG = auto()


_WEIGHT_DELTA = {
    BiotechnologieVerfassungTyp.MOLEKULARES_FUNDAMENT: 0.0,
    BiotechnologieVerfassungTyp.GENOMIK_GEBOT: 2.2,
    BiotechnologieVerfassungTyp.CRISPR_MANDAT: 4.4,
    BiotechnologieVerfassungTyp.MRNA_REVOLUTION: 6.6,
    BiotechnologieVerfassungTyp.PRAEZISIONSMEDIZIN_VISION: 8.8,
}
_TYP_MAP = {
    BiotechnologieVerfassungTyp.MOLEKULARES_FUNDAMENT: "molekulares_fundament",
    BiotechnologieVerfassungTyp.GENOMIK_GEBOT: "genomik_gebot",
    BiotechnologieVerfassungTyp.CRISPR_MANDAT: "crispr_mandat",
    BiotechnologieVerfassungTyp.MRNA_REVOLUTION: "mrna_revolution",
    BiotechnologieVerfassungTyp.PRAEZISIONSMEDIZIN_VISION: "praezisionsmedizin_vision",
}
_PROZEDUR_MAP = {
    BiotechnologieVerfassungProzedur.RATIFIZIERUNG: "ratifizierung",
    BiotechnologieVerfassungProzedur.REVISION: "revision",
    BiotechnologieVerfassungProzedur.INKRAFTTRETEN: "inkrafttreten",
    BiotechnologieVerfassungProzedur.AUSLEGUNG: "auslegung",
    BiotechnologieVerfassungProzedur.DURCHSETZUNG: "durchsetzung",
}


@dataclass(frozen=True)
class BiotechnologieVerfassungNorm:
    typ: BiotechnologieVerfassungTyp
    prozedur: BiotechnologieVerfassungProzedur
    biotech_weight: float
    biotech_tier: int
    canonical: bool = True


@dataclass(frozen=True)
class BiotechnologieVerfassung:
    normen: tuple[BiotechnologieVerfassungNorm, ...]
    canonical: bool = True

    def aggregates_verfassung_signal(self) -> dict:
        return {
            "verfassung_id": "biotechnologie-verfassung-950",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_biotechnologie_verfassung(parent: Optional[PharmakogenomikCharta] = None) -> BiotechnologieVerfassung:
    if parent is None:
        parent = build_pharmakogenomik_charta()
    base = sum(n.biotech_weight for n in parent.normen)
    tier_base = max(n.biotech_tier for n in parent.normen)
    normen = tuple(
        BiotechnologieVerfassungNorm(
            typ=t,
            prozedur=list(BiotechnologieVerfassungProzedur)[i],
            biotech_weight=base + _WEIGHT_DELTA[t],
            biotech_tier=tier_base + i + 1,
        )
        for i, t in enumerate(BiotechnologieVerfassungTyp)
    )
    return BiotechnologieVerfassung(normen=normen)
