"""
#905 NaturalLanguageManifest — Natural Language Processing: Von n-Grammen zu Transformern.
Chomsky (1957): Syntaktische Strukturen — formale Grammatiken als Sprachfundament.
Shannon (1948): Informationstheorie — Sprachmodelle als Wahrscheinlichkeitsverteilungen.
Vaswani et al. (2017): Attention is All You Need — Transformer-Architektur revolutioniert NLP.
Brown et al. (2020): GPT-3 — Few-Shot-Learning durch skalierte Sprachmodelle.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .verstaerkungslernen_kodex import VerstaerkungslernenKodex, build_verstaerkungslernen_kodex


class NaturalLanguageManifestTyp(Enum):
    TOKENISIERUNG = auto()
    SPRACHMODELL = auto()
    SEQUENCE2SEQUENCE = auto()
    KLASSIFIKATION = auto()
    GENERIERUNG = auto()


class NaturalLanguageManifestProzedur(Enum):
    PREPROCESSING = auto()
    EMBEDDING = auto()
    ENCODING = auto()
    DECODING = auto()
    POSTPROCESSING = auto()


_WEIGHT_DELTA = {
    NaturalLanguageManifestTyp.TOKENISIERUNG: 0.0,
    NaturalLanguageManifestTyp.SPRACHMODELL: 1.6,
    NaturalLanguageManifestTyp.SEQUENCE2SEQUENCE: 3.2,
    NaturalLanguageManifestTyp.KLASSIFIKATION: 4.8,
    NaturalLanguageManifestTyp.GENERIERUNG: 6.4,
}
_TYP_MAP = {
    NaturalLanguageManifestTyp.TOKENISIERUNG: "tokenisierung",
    NaturalLanguageManifestTyp.SPRACHMODELL: "sprachmodell",
    NaturalLanguageManifestTyp.SEQUENCE2SEQUENCE: "sequence2sequence",
    NaturalLanguageManifestTyp.KLASSIFIKATION: "klassifikation",
    NaturalLanguageManifestTyp.GENERIERUNG: "generierung",
}
_PROZEDUR_MAP = {
    NaturalLanguageManifestProzedur.PREPROCESSING: "preprocessing",
    NaturalLanguageManifestProzedur.EMBEDDING: "embedding",
    NaturalLanguageManifestProzedur.ENCODING: "encoding",
    NaturalLanguageManifestProzedur.DECODING: "decoding",
    NaturalLanguageManifestProzedur.POSTPROCESSING: "postprocessing",
}


@dataclass(frozen=True)
class NaturalLanguageManifestNorm:
    typ: NaturalLanguageManifestTyp
    prozedur: NaturalLanguageManifestProzedur
    maschinenlernen_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class NaturalLanguageManifest:
    normen: tuple[NaturalLanguageManifestNorm, ...]
    canonical: bool = True

    def aggregates_manifest_signal(self) -> dict:
        return {
            "manifest_id": "natural-language-manifest-905",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_natural_language_manifest(parent: Optional[VerstaerkungslernenKodex] = None) -> NaturalLanguageManifest:
    if parent is None:
        parent = build_verstaerkungslernen_kodex()
    base = sum(e.maschinenlernen_weight for e in parent.eintraege)
    normen = tuple(
        NaturalLanguageManifestNorm(
            typ=t,
            prozedur=list(NaturalLanguageManifestProzedur)[i],
            maschinenlernen_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(NaturalLanguageManifestTyp)
    )
    return NaturalLanguageManifest(normen=normen)
