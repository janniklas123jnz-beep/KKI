"""
#945 mRNAManifest — mRNA-Technologie: Karikó, Weissman & Lipid-Nanopartikel.
Karikó & Weissman (2005): Suppression of RNA Recognition by Toll-like Receptors —
  modifizierte Nukleoside reduzieren mRNA-Immunogenität; Nobelpreis 2023;
  Schlüsselentdeckung für therapeutische mRNA.
Cullis & Hope (2017): Lipid Nanoparticles for Drug Delivery — LNP als Trägersystem
  für mRNA; effiziente Zellaufnahme und endosomale Freisetzung.
BioNTech/Pfizer & Moderna (2020): COVID-19 mRNA Vaccines — erste zugelassene
  mRNA-Vakzine; Beweis der Plattformtechnologie; neue Ära der Medizin.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .synthetische_biologie_kodex import SynthetischeBiologieKodex, build_synthetische_biologie_kodex


class mRNAManifestTyp(Enum):
    MRNA_VAKZIN = auto()
    MRNA_THERAPIE = auto()
    LIPID_NANOPARTIKEL = auto()
    SELBSTREPLIZIERENDE_MRNA = auto()
    MRNA_KREBSTHERAPIE = auto()


class mRNAManifestProzedur(Enum):
    SEQUENZDESIGN = auto()
    MODIFIKATION = auto()
    FORMULIERUNG = auto()
    VERABREICHUNG = auto()
    IMMUNANTWORT = auto()


_WEIGHT_DELTA = {
    mRNAManifestTyp.MRNA_VAKZIN: 0.0,
    mRNAManifestTyp.MRNA_THERAPIE: 1.6,
    mRNAManifestTyp.LIPID_NANOPARTIKEL: 3.2,
    mRNAManifestTyp.SELBSTREPLIZIERENDE_MRNA: 4.8,
    mRNAManifestTyp.MRNA_KREBSTHERAPIE: 6.4,
}
_TYP_MAP = {
    mRNAManifestTyp.MRNA_VAKZIN: "mrna_vakzin",
    mRNAManifestTyp.MRNA_THERAPIE: "mrna_therapie",
    mRNAManifestTyp.LIPID_NANOPARTIKEL: "lipid_nanopartikel",
    mRNAManifestTyp.SELBSTREPLIZIERENDE_MRNA: "selbstreplizierende_mrna",
    mRNAManifestTyp.MRNA_KREBSTHERAPIE: "mrna_krebstherapie",
}
_PROZEDUR_MAP = {
    mRNAManifestProzedur.SEQUENZDESIGN: "sequenzdesign",
    mRNAManifestProzedur.MODIFIKATION: "modifikation",
    mRNAManifestProzedur.FORMULIERUNG: "formulierung",
    mRNAManifestProzedur.VERABREICHUNG: "verabreichung",
    mRNAManifestProzedur.IMMUNANTWORT: "immunantwort",
}


@dataclass(frozen=True)
class mRNAManifestNorm:
    typ: mRNAManifestTyp
    prozedur: mRNAManifestProzedur
    biotech_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class mRNAManifest:
    normen: tuple[mRNAManifestNorm, ...]
    canonical: bool = True

    def aggregates_manifest_signal(self) -> dict:
        return {
            "manifest_id": "mrna-manifest-945",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_mrna_manifest(parent: Optional[SynthetischeBiologieKodex] = None) -> mRNAManifest:
    if parent is None:
        parent = build_synthetische_biologie_kodex()
    base = sum(e.biotech_weight for e in parent.eintraege)
    normen = tuple(
        mRNAManifestNorm(
            typ=t,
            prozedur=list(mRNAManifestProzedur)[i],
            biotech_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(mRNAManifestTyp)
    )
    return mRNAManifest(normen=normen)
