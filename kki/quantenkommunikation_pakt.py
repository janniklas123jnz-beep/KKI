"""
#936 QuantenkommunikationPakt — Quantenkommunikation: QKD, BB84 & Quanteninternet.
Bennett & Brassard (1984): Quantum Cryptography — BB84-Protokoll; erstes Quanten-
  schlüsselverteilungsprotokoll; physikalisch garantierte Abhörsicherheit.
Ekert (1991): Quantum Cryptography Based on Bell's Theorem — E91-Protokoll;
  Verschränkung als Ressource für quantensichere Schlüsselverteilung.
Kimble (2008): The Quantum Internet — Vision des Quanteninternets; Quantenrepeater
  und verschränkte Verbindungen zwischen Quantenknoten weltweit.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .quantensimulations_manifest import QuantensimulationsManifest, build_quantensimulations_manifest


class QuantenkommunikationPaktTyp(Enum):
    BB84_PROTOKOLL = auto()
    E91_PROTOKOLL = auto()
    QUANTENREPEATER = auto()
    QUANTENNETZWERK = auto()
    SATELLITEN_QKD = auto()


class QuantenkommunikationPaktProzedur(Enum):
    SCHLUESSELERZEUGUNG = auto()
    QUANTENUEBERTRAGUNG = auto()
    BELLTESTUNG = auto()
    FEHLERRAUSCHABSCHAETZUNG = auto()
    DATENSCHUTZVERSTAERKUNG = auto()


_WEIGHT_DELTA = {
    QuantenkommunikationPaktTyp.BB84_PROTOKOLL: 0.0,
    QuantenkommunikationPaktTyp.E91_PROTOKOLL: 1.7,
    QuantenkommunikationPaktTyp.QUANTENREPEATER: 3.4,
    QuantenkommunikationPaktTyp.QUANTENNETZWERK: 5.1,
    QuantenkommunikationPaktTyp.SATELLITEN_QKD: 6.8,
}
_TYP_MAP = {
    QuantenkommunikationPaktTyp.BB84_PROTOKOLL: "bb84_protokoll",
    QuantenkommunikationPaktTyp.E91_PROTOKOLL: "e91_protokoll",
    QuantenkommunikationPaktTyp.QUANTENREPEATER: "quantenrepeater",
    QuantenkommunikationPaktTyp.QUANTENNETZWERK: "quantennetzwerk",
    QuantenkommunikationPaktTyp.SATELLITEN_QKD: "satelliten_qkd",
}
_PROZEDUR_MAP = {
    QuantenkommunikationPaktProzedur.SCHLUESSELERZEUGUNG: "schluesselerzeugung",
    QuantenkommunikationPaktProzedur.QUANTENUEBERTRAGUNG: "quantenuebertragung",
    QuantenkommunikationPaktProzedur.BELLTESTUNG: "belltestung",
    QuantenkommunikationPaktProzedur.FEHLERRAUSCHABSCHAETZUNG: "fehlerrauschabschaetzung",
    QuantenkommunikationPaktProzedur.DATENSCHUTZVERSTAERKUNG: "datenschutzverstaerkung",
}


@dataclass(frozen=True)
class QuantenkommunikationPaktEintrag:
    typ: QuantenkommunikationPaktTyp
    prozedur: QuantenkommunikationPaktProzedur
    quanten_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class QuantenkommunikationPakt:
    eintraege: tuple[QuantenkommunikationPaktEintrag, ...]
    canonical: bool = True

    def aggregates_pakt_signal(self) -> dict:
        return {
            "pakt_id": "quantenkommunikation-pakt-936",
            "eintraege_count": len(self.eintraege),
            "canonical": self.canonical,
        }


def build_quantenkommunikation_pakt(parent: Optional[QuantensimulationsManifest] = None) -> QuantenkommunikationPakt:
    if parent is None:
        parent = build_quantensimulations_manifest()
    base = sum(n.quanten_weight for n in parent.normen)
    eintraege = tuple(
        QuantenkommunikationPaktEintrag(
            typ=t,
            prozedur=list(QuantenkommunikationPaktProzedur)[i],
            quanten_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(QuantenkommunikationPaktTyp)
    )
    return QuantenkommunikationPakt(eintraege=eintraege)
