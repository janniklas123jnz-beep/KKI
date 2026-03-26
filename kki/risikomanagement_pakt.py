"""
#966 RisikomanagementPakt — Risikomanagement: VaR, CVaR & Basel III.
Jorion (1997): Value at Risk — VaR als Standardrisikomaß; maximaler erwarteter
  Verlust mit gegebener Wahrscheinlichkeit über definierten Zeithorizont;
  Grundlage aller regulatorischen Eigenkapitalanforderungen.
Rockafellar & Uryasev (2000): Optimization of Conditional Value-at-Risk —
  CVaR als kohärentes Risikomaß; berücksichtigt Tail-Risiken jenseits des VaR;
  mathematisch überlegenes Optimierungsinstrument.
Basel Committee (2010/2017): Basel III/IV — Eigenkapitalanforderungen für Banken;
  Leverage Ratio, LCR, NSFR als systemische Stabilitätspuffer; G20-Reaktion auf 2008.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .algorithmic_trading_manifest import AlgorithmicTradingManifest, build_algorithmic_trading_manifest


class RisikomanagementPaktTyp(Enum):
    MARKTRISIKO = auto()
    KREDITRISIKO = auto()
    LIQUIDITAETSRISIKO = auto()
    OPERATIONELLES_RISIKO = auto()
    SYSTEMRISIKO = auto()


class RisikomanagementPaktProzedur(Enum):
    RISIKOIDENTIFIKATION = auto()
    MESSUNG = auto()
    STEUERUNG = auto()
    UEBERWACHUNG = auto()
    REPORTING = auto()


_WEIGHT_DELTA = {
    RisikomanagementPaktTyp.MARKTRISIKO: 0.0,
    RisikomanagementPaktTyp.KREDITRISIKO: 1.7,
    RisikomanagementPaktTyp.LIQUIDITAETSRISIKO: 3.4,
    RisikomanagementPaktTyp.OPERATIONELLES_RISIKO: 5.1,
    RisikomanagementPaktTyp.SYSTEMRISIKO: 6.8,
}
_TYP_MAP = {
    RisikomanagementPaktTyp.MARKTRISIKO: "marktrisiko",
    RisikomanagementPaktTyp.KREDITRISIKO: "kreditrisiko",
    RisikomanagementPaktTyp.LIQUIDITAETSRISIKO: "liquiditaetsrisiko",
    RisikomanagementPaktTyp.OPERATIONELLES_RISIKO: "operationelles_risiko",
    RisikomanagementPaktTyp.SYSTEMRISIKO: "systemrisiko",
}
_PROZEDUR_MAP = {
    RisikomanagementPaktProzedur.RISIKOIDENTIFIKATION: "risikoidentifikation",
    RisikomanagementPaktProzedur.MESSUNG: "messung",
    RisikomanagementPaktProzedur.STEUERUNG: "steuerung",
    RisikomanagementPaktProzedur.UEBERWACHUNG: "ueberwachung",
    RisikomanagementPaktProzedur.REPORTING: "reporting",
}


@dataclass(frozen=True)
class RisikomanagementPaktEintrag:
    typ: RisikomanagementPaktTyp
    prozedur: RisikomanagementPaktProzedur
    finanz_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class RisikomanagementPakt:
    eintraege: tuple[RisikomanagementPaktEintrag, ...]
    canonical: bool = True

    def aggregates_pakt_signal(self) -> dict:
        return {
            "pakt_id": "risikomanagement-pakt-966",
            "eintraege_count": len(self.eintraege),
            "canonical": self.canonical,
        }


def build_risikomanagement_pakt(parent: Optional[AlgorithmicTradingManifest] = None) -> RisikomanagementPakt:
    if parent is None:
        parent = build_algorithmic_trading_manifest()
    base = sum(n.finanz_weight for n in parent.normen)
    eintraege = tuple(
        RisikomanagementPaktEintrag(
            typ=t,
            prozedur=list(RisikomanagementPaktProzedur)[i],
            finanz_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(RisikomanagementPaktTyp)
    )
    return RisikomanagementPakt(eintraege=eintraege)
