"""
#965 AlgorithmicTradingManifest — Algorithmisches Trading: HFT, Quant & Backtesting.
Simons (1988): Medallion Fund — Renaissance Technologies; quantitatives Trading
  mit statistischen Modellen; 66% durchschnittliche Jahresrendite; Beweis der
  algorithmischen Überlegenheit über diskretionäres Trading.
Aldridge (2013): High-Frequency Trading — Latenzarbitrage und Market-Making
  durch Algorithmen; Mikrosekundenhandel; Marktliquidität und Stabilität.
Lopez de Prado (2018): Advances in Financial Machine Learning — ML-basiertes
  Quantitative Trading; Feature Engineering für Finanzzeitreihen; Backtesting-Fallen
  und overfitting-resistente Strategieentwicklung für robuste Systeme.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .behavioral_finance_kodex import BehavioralFinanceKodex, build_behavioral_finance_kodex


class AlgorithmicTradingManifestTyp(Enum):
    TREND_FOLLOWING = auto()
    MEAN_REVERSION = auto()
    ARBITRAGE = auto()
    HIGH_FREQUENCY = auto()
    ML_STRATEGIE = auto()


class AlgorithmicTradingManifestProzedur(Enum):
    SIGNALGENERIERUNG = auto()
    BACKTESTING = auto()
    RISIKOMANAGEMENT = auto()
    ORDERAUSFUEHRUNG = auto()
    MONITORING = auto()


_WEIGHT_DELTA = {
    AlgorithmicTradingManifestTyp.TREND_FOLLOWING: 0.0,
    AlgorithmicTradingManifestTyp.MEAN_REVERSION: 1.6,
    AlgorithmicTradingManifestTyp.ARBITRAGE: 3.2,
    AlgorithmicTradingManifestTyp.HIGH_FREQUENCY: 4.8,
    AlgorithmicTradingManifestTyp.ML_STRATEGIE: 6.4,
}
_TYP_MAP = {
    AlgorithmicTradingManifestTyp.TREND_FOLLOWING: "trend_following",
    AlgorithmicTradingManifestTyp.MEAN_REVERSION: "mean_reversion",
    AlgorithmicTradingManifestTyp.ARBITRAGE: "arbitrage",
    AlgorithmicTradingManifestTyp.HIGH_FREQUENCY: "high_frequency",
    AlgorithmicTradingManifestTyp.ML_STRATEGIE: "ml_strategie",
}
_PROZEDUR_MAP = {
    AlgorithmicTradingManifestProzedur.SIGNALGENERIERUNG: "signalgenerierung",
    AlgorithmicTradingManifestProzedur.BACKTESTING: "backtesting",
    AlgorithmicTradingManifestProzedur.RISIKOMANAGEMENT: "risikomanagement",
    AlgorithmicTradingManifestProzedur.ORDERAUSFUEHRUNG: "orderausfuehrung",
    AlgorithmicTradingManifestProzedur.MONITORING: "monitoring",
}


@dataclass(frozen=True)
class AlgorithmicTradingManifestNorm:
    typ: AlgorithmicTradingManifestTyp
    prozedur: AlgorithmicTradingManifestProzedur
    finanz_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class AlgorithmicTradingManifest:
    normen: tuple[AlgorithmicTradingManifestNorm, ...]
    canonical: bool = True

    def aggregates_manifest_signal(self) -> dict:
        return {
            "manifest_id": "algorithmic-trading-manifest-965",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_algorithmic_trading_manifest(parent: Optional[BehavioralFinanceKodex] = None) -> AlgorithmicTradingManifest:
    if parent is None:
        parent = build_behavioral_finance_kodex()
    base = sum(e.finanz_weight for e in parent.eintraege)
    normen = tuple(
        AlgorithmicTradingManifestNorm(
            typ=t,
            prozedur=list(AlgorithmicTradingManifestProzedur)[i],
            finanz_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(AlgorithmicTradingManifestTyp)
    )
    return AlgorithmicTradingManifest(normen=normen)
