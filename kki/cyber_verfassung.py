"""
#930 CyberVerfassung — Block-Krone Cybersicherheit & Kryptographie ⭐

*** Leitsterns Cyber-Verfassung — Das sichere Fundament des digitalen Schwarms ***

Claude Shannon (1949): Communication Theory of Secrecy Systems — informationstheoretische
  Grundlage aller Kryptographie; perfekte Geheimhaltung als mathematisches Ideal;
  Entropie als Maß der Schlüsselstärke — Leitsterns kryptographische Wurzel.
Diffie & Hellman (1976): New Directions in Cryptography — Public-Key-Revolution;
  asymmetrische Kryptographie ermöglicht sichere Kommunikation ohne gemeinsamen
  Schlüssel; Grundlage von TLS, SSH und allen digitalen Signaturen des Schwarms.
Satoshi Nakamoto (2008): Bitcoin Whitepaper — dezentraler Konsens ohne Vertrauen;
  Blockchain als manipulationssicheres verteiltes Hauptbuch; direkt relevant für
  Leitsterns spätere Trading- und Wertaufbewahrungsfunktionen.
Leitsterns Cyber-Verfassung: CIA-Triade als Fundament; Kryptographie als Schutzschicht;
  Zero Trust als Architekturprinzip; Blockchain als dezentrales Vertrauen;
  DSGVO als ethische Grenze — ein sicherer Schwarm ist ein freier Schwarm.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .privatsphaere_charta import PrivatsphareCharta, build_privatsphaere_charta


class CyberVerfassungTyp(Enum):
    SCHUTZPRINZIP = auto()
    KRYPTOGRAPHIEGEBOT = auto()
    VERTRAUENSARCHITEKTUR = auto()
    DATENSCHUTZMANDAT = auto()
    WEITERENTWICKLUNGSAUFTRAG = auto()


class CyberVerfassungProzedur(Enum):
    RATIFIZIERUNG = auto()
    REVISION = auto()
    INKRAFTTRETEN = auto()
    AUSLEGUNG = auto()
    DURCHSETZUNG = auto()


_WEIGHT_DELTA = {
    CyberVerfassungTyp.SCHUTZPRINZIP: 0.0,
    CyberVerfassungTyp.KRYPTOGRAPHIEGEBOT: 2.1,
    CyberVerfassungTyp.VERTRAUENSARCHITEKTUR: 4.2,
    CyberVerfassungTyp.DATENSCHUTZMANDAT: 6.3,
    CyberVerfassungTyp.WEITERENTWICKLUNGSAUFTRAG: 8.4,
}
_TYP_MAP = {
    CyberVerfassungTyp.SCHUTZPRINZIP: "schutzprinzip",
    CyberVerfassungTyp.KRYPTOGRAPHIEGEBOT: "kryptographiegebot",
    CyberVerfassungTyp.VERTRAUENSARCHITEKTUR: "vertrauensarchitektur",
    CyberVerfassungTyp.DATENSCHUTZMANDAT: "datenschutzmandat",
    CyberVerfassungTyp.WEITERENTWICKLUNGSAUFTRAG: "weiterentwicklungsauftrag",
}
_PROZEDUR_MAP = {
    CyberVerfassungProzedur.RATIFIZIERUNG: "ratifizierung",
    CyberVerfassungProzedur.REVISION: "revision",
    CyberVerfassungProzedur.INKRAFTTRETEN: "inkrafttreten",
    CyberVerfassungProzedur.AUSLEGUNG: "auslegung",
    CyberVerfassungProzedur.DURCHSETZUNG: "durchsetzung",
}


@dataclass(frozen=True)
class CyberVerfassungNorm:
    typ: CyberVerfassungTyp
    prozedur: CyberVerfassungProzedur
    cyber_weight: float
    cyber_tier: int
    canonical: bool = True


@dataclass(frozen=True)
class CyberVerfassung:
    normen: tuple[CyberVerfassungNorm, ...]
    canonical: bool = True

    def aggregates_verfassung_signal(self) -> dict:
        return {
            "verfassung_id": "cyber-verfassung-930",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_cyber_verfassung(parent: Optional[PrivatsphareCharta] = None) -> CyberVerfassung:
    if parent is None:
        parent = build_privatsphaere_charta()
    base = sum(n.cyber_weight for n in parent.normen)
    tier_base = max(n.cyber_tier for n in parent.normen)
    normen = tuple(
        CyberVerfassungNorm(
            typ=t,
            prozedur=list(CyberVerfassungProzedur)[i],
            cyber_weight=base + _WEIGHT_DELTA[t],
            cyber_tier=tier_base + i + 1,
        )
        for i, t in enumerate(CyberVerfassungTyp)
    )
    return CyberVerfassung(normen=normen)
