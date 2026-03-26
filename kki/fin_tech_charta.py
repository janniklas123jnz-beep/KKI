"""
#969 FinTechCharta — FinTech: DeFi, Robo-Advisor & Open Banking.
Satoshi Nakamoto (2008) → DeFi Ecosystem (2020): Dezentrale Finanzen —
  Smart-Contract-basierte Finanzdienstleistungen ohne Intermediäre; DEX, Lending,
  Yield Farming; TVL >100 Mrd. $; direkte Brücke zu Leitsterns Trading-Vision.
Betterment/Wealthfront (2010): Robo-Advisor — algorithmisches Vermögensmanagement;
  ETF-basierte Portfolios; steuerliche Optimierung; Demokratisierung der Geldanlage.
EU PSD2 (2018): Open Banking — APIs für Kontodaten; Drittanbieterzugang;
  Finanzökosystem-Disruption; Grundlage von Banking-as-a-Service.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .finanz_norm import FinanzNorm, build_finanz_norm


class FinTechChartaTyp(Enum):
    DECENTRALIZED_FINANCE = auto()
    ROBO_ADVISOR = auto()
    OPEN_BANKING = auto()
    PAYMENT_INNOVATION = auto()
    INSURTECH = auto()


class FinTechChartaProzedur(Enum):
    PRODUKTENTWICKLUNG = auto()
    REGULATORISCHE_SANDBOX = auto()
    MARKTEINFUEHRUNG = auto()
    SKALIERUNG = auto()
    COMPLIANCE = auto()


_WEIGHT_DELTA = {
    FinTechChartaTyp.DECENTRALIZED_FINANCE: 0.0,
    FinTechChartaTyp.ROBO_ADVISOR: 2.0,
    FinTechChartaTyp.OPEN_BANKING: 4.0,
    FinTechChartaTyp.PAYMENT_INNOVATION: 6.0,
    FinTechChartaTyp.INSURTECH: 8.0,
}
_TYP_MAP = {
    FinTechChartaTyp.DECENTRALIZED_FINANCE: "decentralized_finance",
    FinTechChartaTyp.ROBO_ADVISOR: "robo_advisor",
    FinTechChartaTyp.OPEN_BANKING: "open_banking",
    FinTechChartaTyp.PAYMENT_INNOVATION: "payment_innovation",
    FinTechChartaTyp.INSURTECH: "insurtech",
}
_PROZEDUR_MAP = {
    FinTechChartaProzedur.PRODUKTENTWICKLUNG: "produktentwicklung",
    FinTechChartaProzedur.REGULATORISCHE_SANDBOX: "regulatorische_sandbox",
    FinTechChartaProzedur.MARKTEINFUEHRUNG: "markteinfuehrung",
    FinTechChartaProzedur.SKALIERUNG: "skalierung",
    FinTechChartaProzedur.COMPLIANCE: "compliance",
}


@dataclass(frozen=True)
class FinTechChartaNorm:
    typ: FinTechChartaTyp
    prozedur: FinTechChartaProzedur
    finanz_weight: float
    finanz_tier: int
    canonical: bool = True


@dataclass(frozen=True)
class FinTechCharta:
    normen: tuple[FinTechChartaNorm, ...]
    canonical: bool = True

    def aggregates_charta_signal(self) -> dict:
        return {
            "charta_id": "fin-tech-charta-969",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_fin_tech_charta(parent: Optional[FinanzNorm] = None) -> FinTechCharta:
    if parent is None:
        parent = build_finanz_norm()
    base = sum(e.finanz_norm_weight for e in parent.normen)
    normen = tuple(
        FinTechChartaNorm(
            typ=t,
            prozedur=list(FinTechChartaProzedur)[i],
            finanz_weight=base + _WEIGHT_DELTA[t],
            finanz_tier=i + 1,
        )
        for i, t in enumerate(FinTechChartaTyp)
    )
    return FinTechCharta(normen=normen)
