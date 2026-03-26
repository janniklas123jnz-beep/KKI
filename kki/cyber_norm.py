"""
#928 CyberNorm — Cybersicherheits-Standards: ISO 27001, NIST & BSI (*_norm-Muster).
ISO/IEC 27001 (2022): Information Security Management — weltweit führende Norm
  für Informationssicherheits-Managementsysteme (ISMS).
NIST Cybersecurity Framework (2014): Identify, Protect, Detect, Respond, Recover —
  fünf Kernfunktionen als universeller Sicherheitsrahmen.
BSI IT-Grundschutz (1994): Bundesamt für Sicherheit in der Informationstechnik —
  systematischer Schutzbedarfsfeststellung und Maßnahmenkatalog.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .cyber_abwehr_senat import CyberAbwehrSenat, build_cyber_abwehr_senat


class CyberNormTyp(Enum):
    ISO_NORM = auto()
    NIST_STANDARD = auto()
    BSI_GRUNDSCHUTZ = auto()
    BRANCHENSTANDARD = auto()
    REGULATORISCH = auto()


class CyberNormProzedur(Enum):
    NORMIERUNG = auto()
    STANDARDISIERUNG = auto()
    VALIDIERUNG = auto()
    ZERTIFIZIERUNG = auto()
    AKKREDITIERUNG = auto()


_WEIGHT_DELTA = {
    "ISO_NORM": 0.0,
    "NIST_STANDARD": 1.9,
    "BSI_GRUNDSCHUTZ": 3.8,
    "BRANCHENSTANDARD": 5.7,
    "REGULATORISCH": 7.6,
}
_TYP_MAP = {
    "ISO_NORM": "iso_norm",
    "NIST_STANDARD": "nist_standard",
    "BSI_GRUNDSCHUTZ": "bsi_grundschutz",
    "BRANCHENSTANDARD": "branchenstandard",
    "REGULATORISCH": "regulatorisch",
}
_PROZEDUR_MAP = {
    "NORMIERUNG": "normierung",
    "STANDARDISIERUNG": "standardisierung",
    "VALIDIERUNG": "validierung",
    "ZERTIFIZIERUNG": "zertifizierung",
    "AKKREDITIERUNG": "akkreditierung",
}


@dataclass(frozen=True)
class CyberNormEintrag:
    typ: CyberNormTyp
    prozedur: CyberNormProzedur
    cyber_norm_weight: float
    cyber_norm_tier: int
    canonical: bool = True


@dataclass(frozen=True)
class CyberNorm:
    normen: tuple[CyberNormEintrag, ...]
    canonical: bool = True

    def aggregates_norm_signal(self) -> dict:
        return {
            "norm_id": "cyber-norm-928",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_cyber_norm(parent: Optional[CyberAbwehrSenat] = None) -> CyberNorm:
    if parent is None:
        parent = build_cyber_abwehr_senat()
    base = sum(n.cyber_weight for n in parent.normen)
    normen = tuple(
        CyberNormEintrag(
            typ=t,
            prozedur=list(CyberNormProzedur)[i],
            cyber_norm_weight=base + _WEIGHT_DELTA[t.name],
            cyber_norm_tier=i + 1,
        )
        for i, t in enumerate(CyberNormTyp)
    )
    return CyberNorm(normen=normen)
