"""
#949 PharmakogenomikCharta — Pharmakogenomik: Personalisierte Medizin & Biomarker.
Evans & Relling (1999): Pharmacogenomics — genetische Variation in Arzneimittel-
  metabolismus; CYP450-Polymorphismen bestimmen individuelle Medikamentenwirkung.
Collins & McKusick (2001): Implications of the Human Genome Project for Medical
  Science — Roadmap personalisierter Medizin; genetische Risikoprofile und Therapie.
FDA (2020): Precision Medicine Initiative — Biomarker-basierte Zulassung;
  companion diagnostics als Vorstufe individualisierter Krebstherapie.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .biotechnologie_norm import BiotechnologieNorm, build_biotechnologie_norm


class PharmakogenomikChartaTyp(Enum):
    PHARMAKOGENETIK = auto()
    BIOMARKER = auto()
    COMPANION_DIAGNOSTICS = auto()
    PERSONALISIERTE_THERAPIE = auto()
    PRAEZISIONSONKOLOGIE = auto()


class PharmakogenomikChartaProzedur(Enum):
    GENOTYPISIERUNG = auto()
    PHAENOTYPISIERUNG = auto()
    BIOMARKERVALIDIERUNG = auto()
    THERAPIEAUSWAHL = auto()
    MONITORING = auto()


_WEIGHT_DELTA = {
    PharmakogenomikChartaTyp.PHARMAKOGENETIK: 0.0,
    PharmakogenomikChartaTyp.BIOMARKER: 2.0,
    PharmakogenomikChartaTyp.COMPANION_DIAGNOSTICS: 4.0,
    PharmakogenomikChartaTyp.PERSONALISIERTE_THERAPIE: 6.0,
    PharmakogenomikChartaTyp.PRAEZISIONSONKOLOGIE: 8.0,
}
_TYP_MAP = {
    PharmakogenomikChartaTyp.PHARMAKOGENETIK: "pharmakogenetik",
    PharmakogenomikChartaTyp.BIOMARKER: "biomarker",
    PharmakogenomikChartaTyp.COMPANION_DIAGNOSTICS: "companion_diagnostics",
    PharmakogenomikChartaTyp.PERSONALISIERTE_THERAPIE: "personalisierte_therapie",
    PharmakogenomikChartaTyp.PRAEZISIONSONKOLOGIE: "praezisionsonkologie",
}
_PROZEDUR_MAP = {
    PharmakogenomikChartaProzedur.GENOTYPISIERUNG: "genotypisierung",
    PharmakogenomikChartaProzedur.PHAENOTYPISIERUNG: "phaenotypisierung",
    PharmakogenomikChartaProzedur.BIOMARKERVALIDIERUNG: "biomarkervalidierung",
    PharmakogenomikChartaProzedur.THERAPIEAUSWAHL: "therapieauswahl",
    PharmakogenomikChartaProzedur.MONITORING: "monitoring",
}


@dataclass(frozen=True)
class PharmakogenomikChartaNorm:
    typ: PharmakogenomikChartaTyp
    prozedur: PharmakogenomikChartaProzedur
    biotech_weight: float
    biotech_tier: int
    canonical: bool = True


@dataclass(frozen=True)
class PharmakogenomikCharta:
    normen: tuple[PharmakogenomikChartaNorm, ...]
    canonical: bool = True

    def aggregates_charta_signal(self) -> dict:
        return {
            "charta_id": "pharmakogenomik-charta-949",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_pharmakogenomik_charta(parent: Optional[BiotechnologieNorm] = None) -> PharmakogenomikCharta:
    if parent is None:
        parent = build_biotechnologie_norm()
    base = sum(e.biotech_norm_weight for e in parent.normen)
    normen = tuple(
        PharmakogenomikChartaNorm(
            typ=t,
            prozedur=list(PharmakogenomikChartaProzedur)[i],
            biotech_weight=base + _WEIGHT_DELTA[t],
            biotech_tier=i + 1,
        )
        for i, t in enumerate(PharmakogenomikChartaTyp)
    )
    return PharmakogenomikCharta(normen=normen)
