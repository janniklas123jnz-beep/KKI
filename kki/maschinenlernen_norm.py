"""
#908 MaschinenlernenNorm — ML-Standards: Bias, Fairness & Evaluation (*_norm-Muster).
Barocas & Hardt (2017): Fairness in Machine Learning — Gruppen- vs. individuelle Fairness.
Gebru et al. (2018): Datasheets for Datasets — Transparenzstandards für ML-Daten.
Mitchell et al. (2019): Model Cards — Dokumentationsstandards für ML-Modelle.
ISO/IEC 42001 (2023): KI-Managementsysteme — internationaler Standard für verantwortungsvolle KI.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .maschinenlernen_senat import MaschinenlernenSenat, build_maschinenlernen_senat


class MaschinenlernenNormTyp(Enum):
    BIAS_NORM = auto()
    FAIRNESS_NORM = auto()
    EVALUATIONS_NORM = auto()
    DATENSCHUTZ_NORM = auto()
    ERKLAERBARKKEITS_NORM = auto()


class MaschinenlernenNormProzedur(Enum):
    NORMIERUNG = auto()
    STANDARDISIERUNG = auto()
    VALIDIERUNG = auto()
    ZERTIFIZIERUNG = auto()
    AKKREDITIERUNG = auto()


_WEIGHT_DELTA = {
    "BIAS_NORM": 0.0,
    "FAIRNESS_NORM": 1.9,
    "EVALUATIONS_NORM": 3.8,
    "DATENSCHUTZ_NORM": 5.7,
    "ERKLAERBARKKEITS_NORM": 7.6,
}
_TYP_MAP = {
    "BIAS_NORM": "bias_norm",
    "FAIRNESS_NORM": "fairness_norm",
    "EVALUATIONS_NORM": "evaluations_norm",
    "DATENSCHUTZ_NORM": "datenschutz_norm",
    "ERKLAERBARKKEITS_NORM": "erklaerbarkkeits_norm",
}
_PROZEDUR_MAP = {
    "NORMIERUNG": "normierung",
    "STANDARDISIERUNG": "standardisierung",
    "VALIDIERUNG": "validierung",
    "ZERTIFIZIERUNG": "zertifizierung",
    "AKKREDITIERUNG": "akkreditierung",
}


@dataclass(frozen=True)
class MaschinenlernenNormEintrag:
    typ: MaschinenlernenNormTyp
    prozedur: MaschinenlernenNormProzedur
    maschinenlernen_norm_weight: float
    maschinenlernen_norm_tier: int
    canonical: bool = True


@dataclass(frozen=True)
class MaschinenlernenNorm:
    normen: tuple[MaschinenlernenNormEintrag, ...]
    canonical: bool = True

    def aggregates_norm_signal(self) -> dict:
        return {
            "norm_id": "maschinenlernen-norm-908",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_maschinenlernen_norm(parent: Optional[MaschinenlernenSenat] = None) -> MaschinenlernenNorm:
    if parent is None:
        parent = build_maschinenlernen_senat()
    base = sum(n.maschinenlernen_weight for n in parent.normen)
    normen = tuple(
        MaschinenlernenNormEintrag(
            typ=t,
            prozedur=list(MaschinenlernenNormProzedur)[i],
            maschinenlernen_norm_weight=base + _WEIGHT_DELTA[t.name],
            maschinenlernen_norm_tier=i + 1,
        )
        for i, t in enumerate(MaschinenlernenNormTyp)
    )
    return MaschinenlernenNorm(normen=normen)
