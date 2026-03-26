"""
#963 PortfolioCharta — Portfoliotheorie: Markowitz, CAPM & Faktor-Investing.
Markowitz (1952): Portfolio Selection — Mean-Variance-Optimierung; Diversifikation
  als risikoreduzierendes Prinzip; Effizienzfrontier; Nobelpreis Wirtschaft 1990.
Sharpe (1964): Capital Asset Prices — CAPM (Capital Asset Pricing Model);
  Beta als Risikomaß; Marktportfolio als optimales Referenzportfolio; Nobelpreis 1990.
Fama & French (1993): Common Risk Factors in the Returns on Stocks and Bonds —
  Drei-Faktoren-Modell; Size und Value als systematische Risikoprämien über Beta hinaus.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .finanzmarkt_register import FinanzmarktRegister, build_finanzmarkt_register


class PortfolioChartaTyp(Enum):
    MEAN_VARIANCE = auto()
    CAPM_PORTFOLIO = auto()
    FAKTOREN_INVESTING = auto()
    RISIKOPARITAET = auto()
    DYNAMISCHE_ALLOCATION = auto()


class PortfolioChartaProzedur(Enum):
    ZIELRENDITE = auto()
    RISIKOANALYSE = auto()
    OPTIMIERUNG = auto()
    REBALANCING = auto()
    PERFORMANCE_MESSUNG = auto()


_WEIGHT_DELTA = {
    PortfolioChartaTyp.MEAN_VARIANCE: 0.0,
    PortfolioChartaTyp.CAPM_PORTFOLIO: 1.7,
    PortfolioChartaTyp.FAKTOREN_INVESTING: 3.4,
    PortfolioChartaTyp.RISIKOPARITAET: 5.1,
    PortfolioChartaTyp.DYNAMISCHE_ALLOCATION: 6.8,
}
_TYP_MAP = {
    PortfolioChartaTyp.MEAN_VARIANCE: "mean_variance",
    PortfolioChartaTyp.CAPM_PORTFOLIO: "capm_portfolio",
    PortfolioChartaTyp.FAKTOREN_INVESTING: "faktoren_investing",
    PortfolioChartaTyp.RISIKOPARITAET: "risikoparitaet",
    PortfolioChartaTyp.DYNAMISCHE_ALLOCATION: "dynamische_allocation",
}
_PROZEDUR_MAP = {
    PortfolioChartaProzedur.ZIELRENDITE: "zielrendite",
    PortfolioChartaProzedur.RISIKOANALYSE: "risikoanalyse",
    PortfolioChartaProzedur.OPTIMIERUNG: "optimierung",
    PortfolioChartaProzedur.REBALANCING: "rebalancing",
    PortfolioChartaProzedur.PERFORMANCE_MESSUNG: "performance_messung",
}


@dataclass(frozen=True)
class PortfolioChartaNorm:
    typ: PortfolioChartaTyp
    prozedur: PortfolioChartaProzedur
    finanz_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class PortfolioCharta:
    normen: tuple[PortfolioChartaNorm, ...]
    canonical: bool = True

    def aggregates_charta_signal(self) -> dict:
        return {
            "charta_id": "portfolio-charta-963",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_portfolio_charta(parent: Optional[FinanzmarktRegister] = None) -> PortfolioCharta:
    if parent is None:
        parent = build_finanzmarkt_register()
    base = sum(e.finanz_weight for e in parent.eintraege)
    normen = tuple(
        PortfolioChartaNorm(
            typ=t,
            prozedur=list(PortfolioChartaProzedur)[i],
            finanz_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(PortfolioChartaTyp)
    )
    return PortfolioCharta(normen=normen)
