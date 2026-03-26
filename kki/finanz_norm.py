"""
#968 FinanzNorm — Finanzstandards: IFRS, Basel III/IV & FATF (*_norm-Muster).
IASB (2001): International Financial Reporting Standards (IFRS) — globale
  Rechnungslegungsstandards; Fair-Value-Bewertung; Vergleichbarkeit über Grenzen.
Basel Committee (2017): Basel IV — überarbeitete Standardansätze; Output Floor
  bei 72,5%; Kapitaluntergrenze für interne Modelle; globale Bankenstabilität.
FATF (1989): Financial Action Task Force — Anti-Geldwäsche-Standards (AML/CFT);
  40 Empfehlungen als globaler Standard; Grundlage aller KYC-Pflichten.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .finanzregulierung_senat import FinanzregulierungSenat, build_finanzregulierung_senat


class FinanzNormTyp(Enum):
    IFRS_STANDARD = auto()
    BASEL_STANDARD = auto()
    FATF_EMPFEHLUNG = auto()
    SOLVENCY_NORM = auto()
    ESG_BERICHTSPFLICHT = auto()


class FinanzNormProzedur(Enum):
    NORMIERUNG = auto()
    STANDARDISIERUNG = auto()
    VALIDIERUNG = auto()
    ZERTIFIZIERUNG = auto()
    AKKREDITIERUNG = auto()


_WEIGHT_DELTA = {
    "IFRS_STANDARD": 0.0,
    "BASEL_STANDARD": 2.0,
    "FATF_EMPFEHLUNG": 4.0,
    "SOLVENCY_NORM": 6.0,
    "ESG_BERICHTSPFLICHT": 8.0,
}
_TYP_MAP = {
    "IFRS_STANDARD": "ifrs_standard",
    "BASEL_STANDARD": "basel_standard",
    "FATF_EMPFEHLUNG": "fatf_empfehlung",
    "SOLVENCY_NORM": "solvency_norm",
    "ESG_BERICHTSPFLICHT": "esg_berichtspflicht",
}
_PROZEDUR_MAP = {
    "NORMIERUNG": "normierung",
    "STANDARDISIERUNG": "standardisierung",
    "VALIDIERUNG": "validierung",
    "ZERTIFIZIERUNG": "zertifizierung",
    "AKKREDITIERUNG": "akkreditierung",
}


@dataclass(frozen=True)
class FinanzNormEintrag:
    typ: FinanzNormTyp
    prozedur: FinanzNormProzedur
    finanz_norm_weight: float
    finanz_norm_tier: int
    canonical: bool = True


@dataclass(frozen=True)
class FinanzNorm:
    normen: tuple[FinanzNormEintrag, ...]
    canonical: bool = True

    def aggregates_norm_signal(self) -> dict:
        return {
            "norm_id": "finanz-norm-968",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_finanz_norm(parent: Optional[FinanzregulierungSenat] = None) -> FinanzNorm:
    if parent is None:
        parent = build_finanzregulierung_senat()
    base = sum(n.finanz_weight for n in parent.normen)
    normen = tuple(
        FinanzNormEintrag(
            typ=t,
            prozedur=list(FinanzNormProzedur)[i],
            finanz_norm_weight=base + _WEIGHT_DELTA[t.name],
            finanz_norm_tier=i + 1,
        )
        for i, t in enumerate(FinanzNormTyp)
    )
    return FinanzNorm(normen=normen)
