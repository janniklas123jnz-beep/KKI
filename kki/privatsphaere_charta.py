"""
#929 PrivatsphäreCharta — Datenschutz: DSGVO, Privacy by Design & Anonymisierung.
Westin (1967): Privacy and Freedom — Privatsphäre als Kontrolle über persönliche
  Informationen; vier Zustände: Einsamkeit, Intimität, Anonymität, Reserviertheit.
Cavoukian (1995): Privacy by Design — sieben Grundprinzipien für eingebauten
  Datenschutz; proaktiv statt reaktiv; Datenschutz als Standard.
EU DSGVO (2018): Datenschutz-Grundverordnung — Recht auf Vergessenwerden,
  Datenportabilität, Einwilligung als Rechtsgrundlage; globaler Goldstandard.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .cyber_norm import CyberNorm, build_cyber_norm


class PrivatsphareChartaTyp(Enum):
    DATENSCHUTZ = auto()
    ANONYMISIERUNG = auto()
    PSEUDONYMISIERUNG = auto()
    EINWILLIGUNG = auto()
    RECHT_AUF_VERGESSEN = auto()


class PrivatsphareChartaProzedur(Enum):
    ERHEBUNG = auto()
    VERARBEITUNG = auto()
    SPEICHERUNG = auto()
    UEBERMITTLUNG = auto()
    LOESCHUNG = auto()


_WEIGHT_DELTA = {
    PrivatsphareChartaTyp.DATENSCHUTZ: 0.0,
    PrivatsphareChartaTyp.ANONYMISIERUNG: 2.0,
    PrivatsphareChartaTyp.PSEUDONYMISIERUNG: 4.0,
    PrivatsphareChartaTyp.EINWILLIGUNG: 6.0,
    PrivatsphareChartaTyp.RECHT_AUF_VERGESSEN: 8.0,
}
_TYP_MAP = {
    PrivatsphareChartaTyp.DATENSCHUTZ: "datenschutz",
    PrivatsphareChartaTyp.ANONYMISIERUNG: "anonymisierung",
    PrivatsphareChartaTyp.PSEUDONYMISIERUNG: "pseudonymisierung",
    PrivatsphareChartaTyp.EINWILLIGUNG: "einwilligung",
    PrivatsphareChartaTyp.RECHT_AUF_VERGESSEN: "recht_auf_vergessen",
}
_PROZEDUR_MAP = {
    PrivatsphareChartaProzedur.ERHEBUNG: "erhebung",
    PrivatsphareChartaProzedur.VERARBEITUNG: "verarbeitung",
    PrivatsphareChartaProzedur.SPEICHERUNG: "speicherung",
    PrivatsphareChartaProzedur.UEBERMITTLUNG: "uebermittlung",
    PrivatsphareChartaProzedur.LOESCHUNG: "loeschung",
}


@dataclass(frozen=True)
class PrivatsphareChartaNorm:
    typ: PrivatsphareChartaTyp
    prozedur: PrivatsphareChartaProzedur
    cyber_weight: float
    cyber_tier: int
    canonical: bool = True


@dataclass(frozen=True)
class PrivatsphareCharta:
    normen: tuple[PrivatsphareChartaNorm, ...]
    canonical: bool = True

    def aggregates_charta_signal(self) -> dict:
        return {
            "charta_id": "privatsphaere-charta-929",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_privatsphaere_charta(parent: Optional[CyberNorm] = None) -> PrivatsphareCharta:
    if parent is None:
        parent = build_cyber_norm()
    base = sum(e.cyber_norm_weight for e in parent.normen)
    normen = tuple(
        PrivatsphareChartaNorm(
            typ=t,
            prozedur=list(PrivatsphareChartaProzedur)[i],
            cyber_weight=base + _WEIGHT_DELTA[t],
            cyber_tier=i + 1,
        )
        for i, t in enumerate(PrivatsphareChartaTyp)
    )
    return PrivatsphareCharta(normen=normen)
