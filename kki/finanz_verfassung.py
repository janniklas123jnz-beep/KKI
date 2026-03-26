"""
#970 FinanzVerfassung — Block-Krone Wirtschaft & Finanzmärkte ⭐

*** Leitsterns Finanz-Verfassung — Das ökonomische Fundament des Trading-Schwarms ***

Adam Smith (1776): Unsichtbare Hand — Marktmechanismus als dezentraler
  Koordinator; Preissignal als Informationsträger; Leitsterns Grundverständnis
  des Marktes als kollektives Informationsverarbeitungssystem.
Harry Markowitz (1952) & William Sharpe (1964): Portfolio-Revolution —
  Risiko und Rendite als untrennbares Paar; Diversifikation als einziges
  kostenloses Mittagessen; CAPM als Bewertungsrahmen; Nobelpreise 1990.
Jim Simons (1988): Medallion-Algorithmus — Beweis, dass Märkte nicht vollständig
  effizient sind; mathematische Muster als Handelsgrundlage; 66% p.a. als
  Leitsterns Inspiration für die Trading-Phase nach #1000.
Leitsterns Finanz-Verfassung: Märkte als Informationssystem; Algorithmen als
  Werkzeuge; Risiko als messbares Konzept; Verhaltensverzerrungen als Chancen;
  Regulierung als Stabilitätsrahmen — ein ökonomisch fundierter Schwarm handelt weise.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .fin_tech_charta import FinTechCharta, build_fin_tech_charta


class FinanzVerfassungTyp(Enum):
    MARKT_FUNDAMENT = auto()
    PORTFOLIO_GEBOT = auto()
    TRADING_MANDAT = auto()
    RISIKO_AUFTRAG = auto()
    FINTECH_VISION = auto()


class FinanzVerfassungProzedur(Enum):
    RATIFIZIERUNG = auto()
    REVISION = auto()
    INKRAFTTRETEN = auto()
    AUSLEGUNG = auto()
    DURCHSETZUNG = auto()


_WEIGHT_DELTA = {
    FinanzVerfassungTyp.MARKT_FUNDAMENT: 0.0,
    FinanzVerfassungTyp.PORTFOLIO_GEBOT: 2.2,
    FinanzVerfassungTyp.TRADING_MANDAT: 4.4,
    FinanzVerfassungTyp.RISIKO_AUFTRAG: 6.6,
    FinanzVerfassungTyp.FINTECH_VISION: 8.8,
}
_TYP_MAP = {
    FinanzVerfassungTyp.MARKT_FUNDAMENT: "markt_fundament",
    FinanzVerfassungTyp.PORTFOLIO_GEBOT: "portfolio_gebot",
    FinanzVerfassungTyp.TRADING_MANDAT: "trading_mandat",
    FinanzVerfassungTyp.RISIKO_AUFTRAG: "risiko_auftrag",
    FinanzVerfassungTyp.FINTECH_VISION: "fintech_vision",
}
_PROZEDUR_MAP = {
    FinanzVerfassungProzedur.RATIFIZIERUNG: "ratifizierung",
    FinanzVerfassungProzedur.REVISION: "revision",
    FinanzVerfassungProzedur.INKRAFTTRETEN: "inkrafttreten",
    FinanzVerfassungProzedur.AUSLEGUNG: "auslegung",
    FinanzVerfassungProzedur.DURCHSETZUNG: "durchsetzung",
}


@dataclass(frozen=True)
class FinanzVerfassungNorm:
    typ: FinanzVerfassungTyp
    prozedur: FinanzVerfassungProzedur
    finanz_weight: float
    finanz_tier: int
    canonical: bool = True


@dataclass(frozen=True)
class FinanzVerfassung:
    normen: tuple[FinanzVerfassungNorm, ...]
    canonical: bool = True

    def aggregates_verfassung_signal(self) -> dict:
        return {
            "verfassung_id": "finanz-verfassung-970",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_finanz_verfassung(parent: Optional[FinTechCharta] = None) -> FinanzVerfassung:
    if parent is None:
        parent = build_fin_tech_charta()
    base = sum(n.finanz_weight for n in parent.normen)
    tier_base = max(n.finanz_tier for n in parent.normen)
    normen = tuple(
        FinanzVerfassungNorm(
            typ=t,
            prozedur=list(FinanzVerfassungProzedur)[i],
            finanz_weight=base + _WEIGHT_DELTA[t],
            finanz_tier=tier_base + i + 1,
        )
        for i, t in enumerate(FinanzVerfassungTyp)
    )
    return FinanzVerfassung(normen=normen)
