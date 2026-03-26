"""
#927 CyberAbwehrSenat — Cyber-Abwehr: SOC, SIEM & Incident Response.
NIST (2012): Computer Security Incident Handling Guide — strukturierter
  Incident-Response-Prozess: Preparation, Detection, Containment, Recovery.
Gartner (2011): SIEM (Security Information and Event Management) — zentrale
  Log-Aggregation und Korrelation für Echtzeit-Bedrohungserkennung.
Mandiant (2013): APT1-Report — Aufdeckung staatlicher Cyber-Spionage;
  Threat Intelligence als strategische Abwehrkomponente.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .blockchain_pakt import BlockchainPakt, build_blockchain_pakt


class CyberAbwehrSenatTyp(Enum):
    SOC_BETRIEB = auto()
    THREAT_INTELLIGENCE = auto()
    INCIDENT_RESPONSE = auto()
    FORENSIK = auto()
    RED_TEAMING = auto()


class CyberAbwehrSenatProzedur(Enum):
    ERKENNUNG = auto()
    EINDAEMMUNG = auto()
    BESEITIGUNG = auto()
    WIEDERHERSTELLUNG = auto()
    NACHBEREITUNG = auto()


_WEIGHT_DELTA = {
    CyberAbwehrSenatTyp.SOC_BETRIEB: 0.0,
    CyberAbwehrSenatTyp.THREAT_INTELLIGENCE: 1.9,
    CyberAbwehrSenatTyp.INCIDENT_RESPONSE: 3.8,
    CyberAbwehrSenatTyp.FORENSIK: 5.7,
    CyberAbwehrSenatTyp.RED_TEAMING: 7.6,
}
_TYP_MAP = {
    CyberAbwehrSenatTyp.SOC_BETRIEB: "soc_betrieb",
    CyberAbwehrSenatTyp.THREAT_INTELLIGENCE: "threat_intelligence",
    CyberAbwehrSenatTyp.INCIDENT_RESPONSE: "incident_response",
    CyberAbwehrSenatTyp.FORENSIK: "forensik",
    CyberAbwehrSenatTyp.RED_TEAMING: "red_teaming",
}
_PROZEDUR_MAP = {
    CyberAbwehrSenatProzedur.ERKENNUNG: "erkennung",
    CyberAbwehrSenatProzedur.EINDAEMMUNG: "eindaemmung",
    CyberAbwehrSenatProzedur.BESEITIGUNG: "beseitigung",
    CyberAbwehrSenatProzedur.WIEDERHERSTELLUNG: "wiederherstellung",
    CyberAbwehrSenatProzedur.NACHBEREITUNG: "nachbereitung",
}


@dataclass(frozen=True)
class CyberAbwehrSenatNorm:
    typ: CyberAbwehrSenatTyp
    prozedur: CyberAbwehrSenatProzedur
    cyber_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class CyberAbwehrSenat:
    normen: tuple[CyberAbwehrSenatNorm, ...]
    canonical: bool = True

    def aggregates_senat_signal(self) -> dict:
        return {
            "senat_id": "cyber-abwehr-senat-927",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_cyber_abwehr_senat(parent: Optional[BlockchainPakt] = None) -> CyberAbwehrSenat:
    if parent is None:
        parent = build_blockchain_pakt()
    base = sum(e.cyber_weight for e in parent.eintraege)
    normen = tuple(
        CyberAbwehrSenatNorm(
            typ=t,
            prozedur=list(CyberAbwehrSenatProzedur)[i],
            cyber_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(CyberAbwehrSenatTyp)
    )
    return CyberAbwehrSenat(normen=normen)
