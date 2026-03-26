"""
#923 NetzwerksicherheitCharta — Netzwerksicherheit: Firewalls, IDS & Zero Trust.
Cheswick & Bellovin (1994): Firewalls and Internet Security — erste systematische
  Firewall-Architektur; Paketfilterung als Netzwerkperimeter-Schutz.
Anderson (1980): Computer Security Threat Monitoring — Intrusion Detection als
  Konzept; verhaltensbasierte Anomalieerkennung für Netzwerke.
Kindervag (2010): Zero Trust Architecture — "Never trust, always verify";
  Mikrosegmentierung ersetzt perimeterbasierte Sicherheitsmodelle.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .kryptographie_register import KryptographieRegister, build_kryptographie_register


class NetzwerksicherheitChartaTyp(Enum):
    FIREWALL = auto()
    IDS_IPS = auto()
    VPN = auto()
    ZERO_TRUST = auto()
    MICROSEGMENTIERUNG = auto()


class NetzwerksicherheitChartaProzedur(Enum):
    PAKETFILTERUNG = auto()
    ANOMALIEERKENNUNG = auto()
    TUNNELING = auto()
    AUTHENTIFIZIERUNG = auto()
    SEGMENTIERUNG = auto()


_WEIGHT_DELTA = {
    NetzwerksicherheitChartaTyp.FIREWALL: 0.0,
    NetzwerksicherheitChartaTyp.IDS_IPS: 1.7,
    NetzwerksicherheitChartaTyp.VPN: 3.4,
    NetzwerksicherheitChartaTyp.ZERO_TRUST: 5.1,
    NetzwerksicherheitChartaTyp.MICROSEGMENTIERUNG: 6.8,
}
_TYP_MAP = {
    NetzwerksicherheitChartaTyp.FIREWALL: "firewall",
    NetzwerksicherheitChartaTyp.IDS_IPS: "ids_ips",
    NetzwerksicherheitChartaTyp.VPN: "vpn",
    NetzwerksicherheitChartaTyp.ZERO_TRUST: "zero_trust",
    NetzwerksicherheitChartaTyp.MICROSEGMENTIERUNG: "microsegmentierung",
}
_PROZEDUR_MAP = {
    NetzwerksicherheitChartaProzedur.PAKETFILTERUNG: "paketfilterung",
    NetzwerksicherheitChartaProzedur.ANOMALIEERKENNUNG: "anomalieerkennung",
    NetzwerksicherheitChartaProzedur.TUNNELING: "tunneling",
    NetzwerksicherheitChartaProzedur.AUTHENTIFIZIERUNG: "authentifizierung",
    NetzwerksicherheitChartaProzedur.SEGMENTIERUNG: "segmentierung",
}


@dataclass(frozen=True)
class NetzwerksicherheitChartaNorm:
    typ: NetzwerksicherheitChartaTyp
    prozedur: NetzwerksicherheitChartaProzedur
    cyber_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class NetzwerksicherheitCharta:
    normen: tuple[NetzwerksicherheitChartaNorm, ...]
    canonical: bool = True

    def aggregates_charta_signal(self) -> dict:
        return {
            "charta_id": "netzwerksicherheit-charta-923",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_netzwerksicherheit_charta(parent: Optional[KryptographieRegister] = None) -> NetzwerksicherheitCharta:
    if parent is None:
        parent = build_kryptographie_register()
    base = sum(e.cyber_weight for e in parent.eintraege)
    normen = tuple(
        NetzwerksicherheitChartaNorm(
            typ=t,
            prozedur=list(NetzwerksicherheitChartaProzedur)[i],
            cyber_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(NetzwerksicherheitChartaTyp)
    )
    return NetzwerksicherheitCharta(normen=normen)
