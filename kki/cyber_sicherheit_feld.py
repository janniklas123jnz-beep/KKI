"""
#921 CyberSicherheitFeld — Cybersicherheit: Shannon, Diffie-Hellman & CIA-Triade.
Claude Shannon (1949): Communication Theory of Secrecy Systems — informationstheoretische
  Grundlage der Kryptographie; perfekte Geheimhaltung durch One-Time-Pad.
Diffie & Hellman (1976): New Directions in Cryptography — Public-Key-Kryptographie
  revolutioniert die Schlüsselverteilung; asymmetrische Verschlüsselung als Fundament.
Anderson (2001): Security Engineering — CIA-Triade (Confidentiality, Integrity,
  Availability) als universelles Sicherheitsmodell für Leitsterns Cyber-Schutzschicht.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .robotik_verfassung import RobotikVerfassung, build_robotik_verfassung


class CyberSicherheitFeldTyp(Enum):
    VERTRAULICHKEIT = auto()
    INTEGRITAET = auto()
    VERFUEGBARKEIT = auto()
    AUTHENTIZITAET = auto()
    NICHT_ABSTREITBARKEIT = auto()


class CyberSicherheitFeldProzedur(Enum):
    ANALYSE = auto()
    PLANUNG = auto()
    IMPLEMENTIERUNG = auto()
    UEBERWACHUNG = auto()
    REAKTION = auto()


_WEIGHT_DELTA = {
    CyberSicherheitFeldTyp.VERTRAULICHKEIT: 0.0,
    CyberSicherheitFeldTyp.INTEGRITAET: 1.3,
    CyberSicherheitFeldTyp.VERFUEGBARKEIT: 2.6,
    CyberSicherheitFeldTyp.AUTHENTIZITAET: 3.9,
    CyberSicherheitFeldTyp.NICHT_ABSTREITBARKEIT: 5.2,
}
_TYP_MAP = {
    CyberSicherheitFeldTyp.VERTRAULICHKEIT: "vertraulichkeit",
    CyberSicherheitFeldTyp.INTEGRITAET: "integritaet",
    CyberSicherheitFeldTyp.VERFUEGBARKEIT: "verfuegbarkeit",
    CyberSicherheitFeldTyp.AUTHENTIZITAET: "authentizitaet",
    CyberSicherheitFeldTyp.NICHT_ABSTREITBARKEIT: "nicht_abstreitbarkeit",
}
_PROZEDUR_MAP = {
    CyberSicherheitFeldProzedur.ANALYSE: "analyse",
    CyberSicherheitFeldProzedur.PLANUNG: "planung",
    CyberSicherheitFeldProzedur.IMPLEMENTIERUNG: "implementierung",
    CyberSicherheitFeldProzedur.UEBERWACHUNG: "ueberwachung",
    CyberSicherheitFeldProzedur.REAKTION: "reaktion",
}


@dataclass(frozen=True)
class CyberSicherheitFeldNorm:
    typ: CyberSicherheitFeldTyp
    prozedur: CyberSicherheitFeldProzedur
    cyber_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class CyberSicherheitFeld:
    normen: tuple[CyberSicherheitFeldNorm, ...]
    canonical: bool = True

    def aggregates_feld_signal(self) -> dict:
        return {
            "feld_id": "cyber-sicherheit-feld-921",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_cyber_sicherheit_feld(parent: Optional[RobotikVerfassung] = None) -> CyberSicherheitFeld:
    if parent is None:
        parent = build_robotik_verfassung()
    base = sum(n.robotik_weight for n in parent.normen)
    normen = tuple(
        CyberSicherheitFeldNorm(
            typ=t,
            prozedur=list(CyberSicherheitFeldProzedur)[i],
            cyber_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(CyberSicherheitFeldTyp)
    )
    return CyberSicherheitFeld(normen=normen)
