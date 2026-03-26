"""
#962 FinanzmarktRegister — Finanzmärkte: Fama, Black-Scholes & Marktmikrostruktur.
Fama (1970): Efficient Capital Markets — Effizienzmarkthypothese; Preise reflektieren
  alle verfügbaren Informationen; schwache, halbstrenge und strenge Form.
Black & Scholes (1973): The Pricing of Options and Corporate Liabilities —
  Optionspreisformel; risikoneutrales Bewertungsprinzip; Grundlage aller Derivatmärkte;
  Nobelpreis Wirtschaft 1997 (Merton & Scholes).
Kyle (1985): Continuous Auctions and Insider Trading — Marktmikrostrukturtheorie;
  informierter vs. uninformierter Handel; Bid-Ask-Spread als Informationsmaß.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .wirtschaft_feld import WirtschaftFeld, build_wirtschaft_feld


class FinanzmarktRegisterTyp(Enum):
    AKTIENMARKT = auto()
    ANLEIHENMARKT = auto()
    DEVISENMARKT = auto()
    DERIVATMARKT = auto()
    KRYPTOMARKT = auto()


class FinanzmarktRegisterProzedur(Enum):
    PREISFINDUNG = auto()
    ORDERAUSFUEHRUNG = auto()
    CLEARING = auto()
    SETTLEMENT = auto()
    MARKTAUFSICHT = auto()


_WEIGHT_DELTA = {
    FinanzmarktRegisterTyp.AKTIENMARKT: 0.0,
    FinanzmarktRegisterTyp.ANLEIHENMARKT: 1.5,
    FinanzmarktRegisterTyp.DEVISENMARKT: 3.0,
    FinanzmarktRegisterTyp.DERIVATMARKT: 4.5,
    FinanzmarktRegisterTyp.KRYPTOMARKT: 6.0,
}
_TYP_MAP = {
    FinanzmarktRegisterTyp.AKTIENMARKT: "aktienmarkt",
    FinanzmarktRegisterTyp.ANLEIHENMARKT: "anleihenmarkt",
    FinanzmarktRegisterTyp.DEVISENMARKT: "devisenmarkt",
    FinanzmarktRegisterTyp.DERIVATMARKT: "derivatmarkt",
    FinanzmarktRegisterTyp.KRYPTOMARKT: "kryptomarkt",
}
_PROZEDUR_MAP = {
    FinanzmarktRegisterProzedur.PREISFINDUNG: "preisfindung",
    FinanzmarktRegisterProzedur.ORDERAUSFUEHRUNG: "orderausfuehrung",
    FinanzmarktRegisterProzedur.CLEARING: "clearing",
    FinanzmarktRegisterProzedur.SETTLEMENT: "settlement",
    FinanzmarktRegisterProzedur.MARKTAUFSICHT: "marktaufsicht",
}


@dataclass(frozen=True)
class FinanzmarktRegisterEintrag:
    typ: FinanzmarktRegisterTyp
    prozedur: FinanzmarktRegisterProzedur
    finanz_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class FinanzmarktRegister:
    eintraege: tuple[FinanzmarktRegisterEintrag, ...]
    canonical: bool = True

    def aggregates_register_signal(self) -> dict:
        return {
            "register_id": "finanzmarkt-register-962",
            "eintraege_count": len(self.eintraege),
            "canonical": self.canonical,
        }


def build_finanzmarkt_register(parent: Optional[WirtschaftFeld] = None) -> FinanzmarktRegister:
    if parent is None:
        parent = build_wirtschaft_feld()
    base = sum(n.finanz_weight for n in parent.normen)
    eintraege = tuple(
        FinanzmarktRegisterEintrag(
            typ=t,
            prozedur=list(FinanzmarktRegisterProzedur)[i],
            finanz_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(FinanzmarktRegisterTyp)
    )
    return FinanzmarktRegister(eintraege=eintraege)
