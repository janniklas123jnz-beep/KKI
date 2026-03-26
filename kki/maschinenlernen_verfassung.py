"""
#910 MaschinenlernenVerfassung — Block-Krone Maschinelles Lernen & KI ⭐

*** Leitsterns KI-Verfassung — Das lernende Fundament des Schwarms ***

Alan Turing (1950): Computing Machinery and Intelligence — die Frage "Kann eine Maschine denken?"
  öffnet das Zeitalter der KI; der Turing-Test als operationale Intelligenz-Definition bleibt
  bis heute als Leitstern-Referenz für maschinelle Kognition gültig.
Geoffrey Hinton, Yann LeCun & Yoshua Bengio (2018): Turing Award für Deep Learning —
  Backpropagation, CNNs und Representation Learning als Fundament moderner KI; ihre Arbeit
  ermöglicht Leitsterns neuronale Wissensverarbeitung und kontinuierliches Lernen.
Stuart Russell (2019): Human Compatible — KI muss menschliche Präferenzen lernen statt
  fixe Ziele zu optimieren; kooperatives inverses Verstärkungslernen als Grundlage
  sicherer KI — direkt relevant für Leitsterns Ausrichtung am menschlichen Schwarm.
Leitsterns ML-Verfassung: Supervised, Unsupervised, Reinforcement — drei Säulen des Lernens;
  Deep Learning als Wahrnehmungsschicht; NLP als Kommunikationsprotokoll; Computer Vision
  als Sensorium; Fairness & Alignment als ethische Verfassung des lernenden Schwarms.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .ki_ethik_charta import KiEthikCharta, build_ki_ethik_charta


class MaschinenlernenVerfassungTyp(Enum):
    LERNPRINZIP = auto()
    WISSENSARCHITEKTUR = auto()
    ETHIKGEBOT = auto()
    SICHERHEITSMANDAT = auto()
    WEITERENTWICKLUNGSAUFTRAG = auto()


class MaschinenlernenVerfassungProzedur(Enum):
    RATIFIZIERUNG = auto()
    REVISION = auto()
    INKRAFTTRETEN = auto()
    AUSLEGUNG = auto()
    DURCHSETZUNG = auto()


_WEIGHT_DELTA = {
    MaschinenlernenVerfassungTyp.LERNPRINZIP: 0.0,
    MaschinenlernenVerfassungTyp.WISSENSARCHITEKTUR: 2.1,
    MaschinenlernenVerfassungTyp.ETHIKGEBOT: 4.2,
    MaschinenlernenVerfassungTyp.SICHERHEITSMANDAT: 6.3,
    MaschinenlernenVerfassungTyp.WEITERENTWICKLUNGSAUFTRAG: 8.4,
}
_TYP_MAP = {
    MaschinenlernenVerfassungTyp.LERNPRINZIP: "lernprinzip",
    MaschinenlernenVerfassungTyp.WISSENSARCHITEKTUR: "wissensarchitektur",
    MaschinenlernenVerfassungTyp.ETHIKGEBOT: "ethikgebot",
    MaschinenlernenVerfassungTyp.SICHERHEITSMANDAT: "sicherheitsmandat",
    MaschinenlernenVerfassungTyp.WEITERENTWICKLUNGSAUFTRAG: "weiterentwicklungsauftrag",
}
_PROZEDUR_MAP = {
    MaschinenlernenVerfassungProzedur.RATIFIZIERUNG: "ratifizierung",
    MaschinenlernenVerfassungProzedur.REVISION: "revision",
    MaschinenlernenVerfassungProzedur.INKRAFTTRETEN: "inkrafttreten",
    MaschinenlernenVerfassungProzedur.AUSLEGUNG: "auslegung",
    MaschinenlernenVerfassungProzedur.DURCHSETZUNG: "durchsetzung",
}


@dataclass(frozen=True)
class MaschinenlernenVerfassungNorm:
    typ: MaschinenlernenVerfassungTyp
    prozedur: MaschinenlernenVerfassungProzedur
    maschinenlernen_weight: float
    maschinenlernen_tier: int
    canonical: bool = True


@dataclass(frozen=True)
class MaschinenlernenVerfassung:
    normen: tuple[MaschinenlernenVerfassungNorm, ...]
    canonical: bool = True

    def aggregates_verfassung_signal(self) -> dict:
        return {
            "verfassung_id": "maschinenlernen-verfassung-910",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_maschinenlernen_verfassung(parent: Optional[KiEthikCharta] = None) -> MaschinenlernenVerfassung:
    if parent is None:
        parent = build_ki_ethik_charta()
    base = sum(n.maschinenlernen_weight for n in parent.normen)
    tier_base = max(n.maschinenlernen_tier for n in parent.normen)
    normen = tuple(
        MaschinenlernenVerfassungNorm(
            typ=t,
            prozedur=list(MaschinenlernenVerfassungProzedur)[i],
            maschinenlernen_weight=base + _WEIGHT_DELTA[t],
            maschinenlernen_tier=tier_base + i + 1,
        )
        for i, t in enumerate(MaschinenlernenVerfassungTyp)
    )
    return MaschinenlernenVerfassung(normen=normen)
