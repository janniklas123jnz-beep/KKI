"""
#967 FinanzregulierungSenat — Finanzregulierung: SEC, BaFin, MiFID II & Dodd-Frank.
Glass-Steagall (1933) & Dodd-Frank (2010): Trennbankensystem & Volcker-Rule —
  Trennung von Geschäfts- und Investmentbanking; Too-big-to-fail als regulatorische
  Herausforderung; systemische Stabilität nach Finanzkrisen.
EU MiFID II (2018): Markets in Financial Instruments Directive — Transparenz-
  und Wohlverhaltensregeln; Best-Execution-Pflicht; Algorithmic Trading Governance.
FSB (2011): Key Attributes of Effective Resolution Regimes — Abwicklungsregime für
  systemrelevante Banken; Bail-in statt Bail-out; globale Koordination.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .risikomanagement_pakt import RisikomanagementPakt, build_risikomanagement_pakt


class FinanzregulierungSenatTyp(Enum):
    WERTPAPIERAUFSICHT = auto()
    BANKENREGULIERUNG = auto()
    VERSICHERUNGSAUFSICHT = auto()
    KRYPTOREGULIERUNG = auto()
    MAKROPRUDENZIELLE_AUFSICHT = auto()


class FinanzregulierungSenatProzedur(Enum):
    LIZENZIERUNG = auto()
    UEBERWACHUNG = auto()
    DURCHSETZUNG = auto()
    SANKTIONIERUNG = auto()
    INTERNATIONALE_KOORDINATION = auto()


_WEIGHT_DELTA = {
    FinanzregulierungSenatTyp.WERTPAPIERAUFSICHT: 0.0,
    FinanzregulierungSenatTyp.BANKENREGULIERUNG: 1.9,
    FinanzregulierungSenatTyp.VERSICHERUNGSAUFSICHT: 3.8,
    FinanzregulierungSenatTyp.KRYPTOREGULIERUNG: 5.7,
    FinanzregulierungSenatTyp.MAKROPRUDENZIELLE_AUFSICHT: 7.6,
}
_TYP_MAP = {
    FinanzregulierungSenatTyp.WERTPAPIERAUFSICHT: "wertpapieraufsicht",
    FinanzregulierungSenatTyp.BANKENREGULIERUNG: "bankenregulierung",
    FinanzregulierungSenatTyp.VERSICHERUNGSAUFSICHT: "versicherungsaufsicht",
    FinanzregulierungSenatTyp.KRYPTOREGULIERUNG: "kryptoregulierung",
    FinanzregulierungSenatTyp.MAKROPRUDENZIELLE_AUFSICHT: "makroprudenzielle_aufsicht",
}
_PROZEDUR_MAP = {
    FinanzregulierungSenatProzedur.LIZENZIERUNG: "lizenzierung",
    FinanzregulierungSenatProzedur.UEBERWACHUNG: "ueberwachung",
    FinanzregulierungSenatProzedur.DURCHSETZUNG: "durchsetzung",
    FinanzregulierungSenatProzedur.SANKTIONIERUNG: "sanktionierung",
    FinanzregulierungSenatProzedur.INTERNATIONALE_KOORDINATION: "internationale_koordination",
}


@dataclass(frozen=True)
class FinanzregulierungSenatNorm:
    typ: FinanzregulierungSenatTyp
    prozedur: FinanzregulierungSenatProzedur
    finanz_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class FinanzregulierungSenat:
    normen: tuple[FinanzregulierungSenatNorm, ...]
    canonical: bool = True

    def aggregates_senat_signal(self) -> dict:
        return {
            "senat_id": "finanzregulierung-senat-967",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_finanzregulierung_senat(parent: Optional[RisikomanagementPakt] = None) -> FinanzregulierungSenat:
    if parent is None:
        parent = build_risikomanagement_pakt()
    base = sum(e.finanz_weight for e in parent.eintraege)
    normen = tuple(
        FinanzregulierungSenatNorm(
            typ=t,
            prozedur=list(FinanzregulierungSenatProzedur)[i],
            finanz_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(FinanzregulierungSenatTyp)
    )
    return FinanzregulierungSenat(normen=normen)
