"""
#964 BehavioralFinanceKodex — Verhaltensökonomie: Kahneman, Tversky & Prospect Theory.
Kahneman & Tversky (1979): Prospect Theory — Verluste wiegen schwerer als Gewinne
  (Verlustaversion); S-förmige Wertfunktion; Nobelpreis Wirtschaft 2002 (Kahneman).
Thaler & Sunstein (2008): Nudge — Verhaltensarchitektur; sanfte Stupser als
  Entscheidungshilfe; libertärer Paternalismus; Nobelpreis Wirtschaft 2017 (Thaler).
Shiller (2000): Irrational Exuberance — irrationaler Überschwang als Blasenursache;
  narrative Ökonomie; Nobelpreis Wirtschaft 2013; Basis für contrarian Strategien.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .portfolio_charta import PortfolioCharta, build_portfolio_charta


class BehavioralFinanceKodexTyp(Enum):
    PROSPECT_THEORY = auto()
    VERLUSTAVERSION = auto()
    HERDENVERHALTEN = auto()
    ANKEREFFEKT = auto()
    UEBERKONFIDENZ = auto()


class BehavioralFinanceKodexProzedur(Enum):
    BIASIDENTIFIKATION = auto()
    ENTSCHEIDUNGSANALYSE = auto()
    NUDGE_DESIGN = auto()
    DEBIASING = auto()
    VERHALTENSMONITORING = auto()


_WEIGHT_DELTA = {
    BehavioralFinanceKodexTyp.PROSPECT_THEORY: 0.0,
    BehavioralFinanceKodexTyp.VERLUSTAVERSION: 1.8,
    BehavioralFinanceKodexTyp.HERDENVERHALTEN: 3.6,
    BehavioralFinanceKodexTyp.ANKEREFFEKT: 5.4,
    BehavioralFinanceKodexTyp.UEBERKONFIDENZ: 7.2,
}
_TYP_MAP = {
    BehavioralFinanceKodexTyp.PROSPECT_THEORY: "prospect_theory",
    BehavioralFinanceKodexTyp.VERLUSTAVERSION: "verlustaversion",
    BehavioralFinanceKodexTyp.HERDENVERHALTEN: "herdenverhalten",
    BehavioralFinanceKodexTyp.ANKEREFFEKT: "ankereffekt",
    BehavioralFinanceKodexTyp.UEBERKONFIDENZ: "ueberkonfidenz",
}
_PROZEDUR_MAP = {
    BehavioralFinanceKodexProzedur.BIASIDENTIFIKATION: "biasidentifikation",
    BehavioralFinanceKodexProzedur.ENTSCHEIDUNGSANALYSE: "entscheidungsanalyse",
    BehavioralFinanceKodexProzedur.NUDGE_DESIGN: "nudge_design",
    BehavioralFinanceKodexProzedur.DEBIASING: "debiasing",
    BehavioralFinanceKodexProzedur.VERHALTENSMONITORING: "verhaltensmonitoring",
}


@dataclass(frozen=True)
class BehavioralFinanceKodexEintrag:
    typ: BehavioralFinanceKodexTyp
    prozedur: BehavioralFinanceKodexProzedur
    finanz_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class BehavioralFinanceKodex:
    eintraege: tuple[BehavioralFinanceKodexEintrag, ...]
    canonical: bool = True

    def aggregates_kodex_signal(self) -> dict:
        return {
            "kodex_id": "behavioral-finance-kodex-964",
            "eintraege_count": len(self.eintraege),
            "canonical": self.canonical,
        }


def build_behavioral_finance_kodex(parent: Optional[PortfolioCharta] = None) -> BehavioralFinanceKodex:
    if parent is None:
        parent = build_portfolio_charta()
    base = sum(n.finanz_weight for n in parent.normen)
    eintraege = tuple(
        BehavioralFinanceKodexEintrag(
            typ=t,
            prozedur=list(BehavioralFinanceKodexProzedur)[i],
            finanz_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(BehavioralFinanceKodexTyp)
    )
    return BehavioralFinanceKodex(eintraege=eintraege)
