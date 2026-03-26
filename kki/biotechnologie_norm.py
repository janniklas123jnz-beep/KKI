"""
#948 BiotechnologieNorm — Biotech-Regulierung: GMP, ISO 13485 & FDA (*_norm-Muster).
ICH Q10 (2008): Pharmaceutical Quality System — Good Manufacturing Practice (GMP)
  als internationaler Qualitätsstandard für pharmazeutische Produktion.
ISO 13485 (2016): Medical Devices Quality Management — Qualitätsmanagementsystem
  für Medizinprodukte; harmonisierter Standard für globale Zulassungen.
FDA 21 CFR Part 11 (1997): Electronic Records and Signatures — digitale Compliance
  in regulierten Biotech-Umgebungen; Grundlage für GxP-Validierung.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .bioinformatik_senat import BioinformatikSenat, build_bioinformatik_senat


class BiotechnologieNormTyp(Enum):
    GMP_STANDARD = auto()
    ISO_MEDIZINPRODUKTE = auto()
    FDA_REGULIERUNG = auto()
    EMA_ZULASSUNG = auto()
    BIOSICHERHEITSKLASSE = auto()


class BiotechnologieNormProzedur(Enum):
    NORMIERUNG = auto()
    VALIDIERUNG = auto()
    ZERTIFIZIERUNG = auto()
    INSPEKTION = auto()
    AKKREDITIERUNG = auto()


_WEIGHT_DELTA = {
    "GMP_STANDARD": 0.0,
    "ISO_MEDIZINPRODUKTE": 2.0,
    "FDA_REGULIERUNG": 4.0,
    "EMA_ZULASSUNG": 6.0,
    "BIOSICHERHEITSKLASSE": 8.0,
}
_TYP_MAP = {
    "GMP_STANDARD": "gmp_standard",
    "ISO_MEDIZINPRODUKTE": "iso_medizinprodukte",
    "FDA_REGULIERUNG": "fda_regulierung",
    "EMA_ZULASSUNG": "ema_zulassung",
    "BIOSICHERHEITSKLASSE": "biosicherheitsklasse",
}
_PROZEDUR_MAP = {
    "NORMIERUNG": "normierung",
    "VALIDIERUNG": "validierung",
    "ZERTIFIZIERUNG": "zertifizierung",
    "INSPEKTION": "inspektion",
    "AKKREDITIERUNG": "akkreditierung",
}


@dataclass(frozen=True)
class BiotechnologieNormEintrag:
    typ: BiotechnologieNormTyp
    prozedur: BiotechnologieNormProzedur
    biotech_norm_weight: float
    biotech_norm_tier: int
    canonical: bool = True


@dataclass(frozen=True)
class BiotechnologieNorm:
    normen: tuple[BiotechnologieNormEintrag, ...]
    canonical: bool = True

    def aggregates_norm_signal(self) -> dict:
        return {
            "norm_id": "biotechnologie-norm-948",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_biotechnologie_norm(parent: Optional[BioinformatikSenat] = None) -> BiotechnologieNorm:
    if parent is None:
        parent = build_bioinformatik_senat()
    base = sum(n.biotech_weight for n in parent.normen)
    normen = tuple(
        BiotechnologieNormEintrag(
            typ=t,
            prozedur=list(BiotechnologieNormProzedur)[i],
            biotech_norm_weight=base + _WEIGHT_DELTA[t.name],
            biotech_norm_tier=i + 1,
        )
        for i, t in enumerate(BiotechnologieNormTyp)
    )
    return BiotechnologieNorm(normen=normen)
