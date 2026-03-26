"""
#924 AngriffsvektorKodex — Angriffsvektoren: OWASP, CVE & Penetration Testing.
OWASP (2003): Open Web Application Security Project — Top-10 Schwachstellen als
  Industriestandard; SQL-Injection, XSS, CSRF als häufigste Angriffsvektoren.
MITRE (1999): CVE (Common Vulnerabilities and Exposures) — einheitliche
  Schwachstellendatenbank; standardisierte Identifikatoren für bekannte Lücken.
Shostack (2014): Threat Modeling — STRIDE-Methodik: Spoofing, Tampering, Repudiation,
  Information Disclosure, Denial of Service, Elevation of Privilege.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .netzwerksicherheit_charta import NetzwerksicherheitCharta, build_netzwerksicherheit_charta


class AngriffsvektorKodexTyp(Enum):
    SOCIAL_ENGINEERING = auto()
    MALWARE = auto()
    NETZWERKANGRIFF = auto()
    WEBANGRIFF = auto()
    INSIDER_BEDROHUNG = auto()


class AngriffsvektorKodexProzedur(Enum):
    RECONNAISSANCE = auto()
    EXPLOITATION = auto()
    PRIVILEGE_ESCALATION = auto()
    LATERAL_MOVEMENT = auto()
    EXFILTRATION = auto()


_WEIGHT_DELTA = {
    AngriffsvektorKodexTyp.SOCIAL_ENGINEERING: 0.0,
    AngriffsvektorKodexTyp.MALWARE: 1.8,
    AngriffsvektorKodexTyp.NETZWERKANGRIFF: 3.6,
    AngriffsvektorKodexTyp.WEBANGRIFF: 5.4,
    AngriffsvektorKodexTyp.INSIDER_BEDROHUNG: 7.2,
}
_TYP_MAP = {
    AngriffsvektorKodexTyp.SOCIAL_ENGINEERING: "social_engineering",
    AngriffsvektorKodexTyp.MALWARE: "malware",
    AngriffsvektorKodexTyp.NETZWERKANGRIFF: "netzwerkangriff",
    AngriffsvektorKodexTyp.WEBANGRIFF: "webangriff",
    AngriffsvektorKodexTyp.INSIDER_BEDROHUNG: "insider_bedrohung",
}
_PROZEDUR_MAP = {
    AngriffsvektorKodexProzedur.RECONNAISSANCE: "reconnaissance",
    AngriffsvektorKodexProzedur.EXPLOITATION: "exploitation",
    AngriffsvektorKodexProzedur.PRIVILEGE_ESCALATION: "privilege_escalation",
    AngriffsvektorKodexProzedur.LATERAL_MOVEMENT: "lateral_movement",
    AngriffsvektorKodexProzedur.EXFILTRATION: "exfiltration",
}


@dataclass(frozen=True)
class AngriffsvektorKodexEintrag:
    typ: AngriffsvektorKodexTyp
    prozedur: AngriffsvektorKodexProzedur
    cyber_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class AngriffsvektorKodex:
    eintraege: tuple[AngriffsvektorKodexEintrag, ...]
    canonical: bool = True

    def aggregates_kodex_signal(self) -> dict:
        return {
            "kodex_id": "angriffsvektor-kodex-924",
            "eintraege_count": len(self.eintraege),
            "canonical": self.canonical,
        }


def build_angriffsvektor_kodex(parent: Optional[NetzwerksicherheitCharta] = None) -> AngriffsvektorKodex:
    if parent is None:
        parent = build_netzwerksicherheit_charta()
    base = sum(n.cyber_weight for n in parent.normen)
    eintraege = tuple(
        AngriffsvektorKodexEintrag(
            typ=t,
            prozedur=list(AngriffsvektorKodexProzedur)[i],
            cyber_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(AngriffsvektorKodexTyp)
    )
    return AngriffsvektorKodex(eintraege=eintraege)
