"""
#909 KiEthikCharta — KI-Ethik: Alignment, Sicherheit & Verantwortung.
Bostrom (2014): Superintelligence — existenzielle Risiken durch KI; Alignment-Problem.
Russell (2019): Human Compatible — kooperative inverse Verstärkungslernen als Lösung.
Jobin et al. (2019): Global Landscape of AI Ethics Guidelines — 84 Richtlinien verglichen.
EU AI Act (2024): Risikobasierter Ansatz für KI-Regulierung — weltweit erstes KI-Gesetz.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .maschinenlernen_norm import MaschinenlernenNorm, build_maschinenlernen_norm


class KiEthikChartaTyp(Enum):
    ALIGNMENT = auto()
    SICHERHEIT = auto()
    TRANSPARENZ = auto()
    GERECHTIGKEIT = auto()
    NACHHALTIGKEIT = auto()


class KiEthikChartaProzedur(Enum):
    BEWERTUNG = auto()
    REGULIERUNG = auto()
    ZERTIFIZIERUNG = auto()
    UEBERWACHUNG = auto()
    DURCHSETZUNG = auto()


_WEIGHT_DELTA = {
    KiEthikChartaTyp.ALIGNMENT: 0.0,
    KiEthikChartaTyp.SICHERHEIT: 2.0,
    KiEthikChartaTyp.TRANSPARENZ: 4.0,
    KiEthikChartaTyp.GERECHTIGKEIT: 6.0,
    KiEthikChartaTyp.NACHHALTIGKEIT: 8.0,
}
_TYP_MAP = {
    KiEthikChartaTyp.ALIGNMENT: "alignment",
    KiEthikChartaTyp.SICHERHEIT: "sicherheit",
    KiEthikChartaTyp.TRANSPARENZ: "transparenz",
    KiEthikChartaTyp.GERECHTIGKEIT: "gerechtigkeit",
    KiEthikChartaTyp.NACHHALTIGKEIT: "nachhaltigkeit",
}
_PROZEDUR_MAP = {
    KiEthikChartaProzedur.BEWERTUNG: "bewertung",
    KiEthikChartaProzedur.REGULIERUNG: "regulierung",
    KiEthikChartaProzedur.ZERTIFIZIERUNG: "zertifizierung",
    KiEthikChartaProzedur.UEBERWACHUNG: "ueberwachung",
    KiEthikChartaProzedur.DURCHSETZUNG: "durchsetzung",
}


@dataclass(frozen=True)
class KiEthikChartaNorm:
    typ: KiEthikChartaTyp
    prozedur: KiEthikChartaProzedur
    maschinenlernen_weight: float
    maschinenlernen_tier: int
    canonical: bool = True


@dataclass(frozen=True)
class KiEthikCharta:
    normen: tuple[KiEthikChartaNorm, ...]
    canonical: bool = True

    def aggregates_charta_signal(self) -> dict:
        return {
            "charta_id": "ki-ethik-charta-909",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_ki_ethik_charta(parent: Optional[MaschinenlernenNorm] = None) -> KiEthikCharta:
    if parent is None:
        parent = build_maschinenlernen_norm()
    base = sum(e.maschinenlernen_norm_weight for e in parent.normen)
    normen = tuple(
        KiEthikChartaNorm(
            typ=t,
            prozedur=list(KiEthikChartaProzedur)[i],
            maschinenlernen_weight=base + _WEIGHT_DELTA[t],
            maschinenlernen_tier=i + 1,
        )
        for i, t in enumerate(KiEthikChartaTyp)
    )
    return KiEthikCharta(normen=normen)
