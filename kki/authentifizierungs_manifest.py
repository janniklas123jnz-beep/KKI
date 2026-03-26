"""
#925 AuthentifizierungsManifest — Authentifizierung: OAuth, MFA & Zero-Trust-Identity.
Lamport (1981): Password Authentication with Insecure Communication — Hashketten
  als One-Time-Password-Grundlage; sichere Passwortübertragung ohne verschlüsselte Kanäle.
Hardt (2012): OAuth 2.0 Authorization Framework — delegierte Autorisierung;
  Token-basierter Zugang als Standard für Web-APIs und Cloud-Services.
NIST SP 800-63 (2017): Digital Identity Guidelines — Multi-Faktor-Authentifizierung
  als Mindeststandard; Biometrie, Hardware-Token und Wissensbasierung.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .angriffsvektor_kodex import AngriffsvektorKodex, build_angriffsvektor_kodex


class AuthentifizierungsManifestTyp(Enum):
    PASSWORT = auto()
    MULTI_FAKTOR = auto()
    BIOMETRIE = auto()
    ZERTIFIKAT = auto()
    HARDWARE_TOKEN = auto()


class AuthentifizierungsManifestProzedur(Enum):
    REGISTRIERUNG = auto()
    VERIFIKATION = auto()
    AUTORISIERUNG = auto()
    SITZUNGSVERWALTUNG = auto()
    ABMELDUNG = auto()


_WEIGHT_DELTA = {
    AuthentifizierungsManifestTyp.PASSWORT: 0.0,
    AuthentifizierungsManifestTyp.MULTI_FAKTOR: 1.6,
    AuthentifizierungsManifestTyp.BIOMETRIE: 3.2,
    AuthentifizierungsManifestTyp.ZERTIFIKAT: 4.8,
    AuthentifizierungsManifestTyp.HARDWARE_TOKEN: 6.4,
}
_TYP_MAP = {
    AuthentifizierungsManifestTyp.PASSWORT: "passwort",
    AuthentifizierungsManifestTyp.MULTI_FAKTOR: "multi_faktor",
    AuthentifizierungsManifestTyp.BIOMETRIE: "biometrie",
    AuthentifizierungsManifestTyp.ZERTIFIKAT: "zertifikat",
    AuthentifizierungsManifestTyp.HARDWARE_TOKEN: "hardware_token",
}
_PROZEDUR_MAP = {
    AuthentifizierungsManifestProzedur.REGISTRIERUNG: "registrierung",
    AuthentifizierungsManifestProzedur.VERIFIKATION: "verifikation",
    AuthentifizierungsManifestProzedur.AUTORISIERUNG: "autorisierung",
    AuthentifizierungsManifestProzedur.SITZUNGSVERWALTUNG: "sitzungsverwaltung",
    AuthentifizierungsManifestProzedur.ABMELDUNG: "abmeldung",
}


@dataclass(frozen=True)
class AuthentifizierungsManifestNorm:
    typ: AuthentifizierungsManifestTyp
    prozedur: AuthentifizierungsManifestProzedur
    cyber_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class AuthentifizierungsManifest:
    normen: tuple[AuthentifizierungsManifestNorm, ...]
    canonical: bool = True

    def aggregates_manifest_signal(self) -> dict:
        return {
            "manifest_id": "authentifizierungs-manifest-925",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_authentifizierungs_manifest(parent: Optional[AngriffsvektorKodex] = None) -> AuthentifizierungsManifest:
    if parent is None:
        parent = build_angriffsvektor_kodex()
    base = sum(e.cyber_weight for e in parent.eintraege)
    normen = tuple(
        AuthentifizierungsManifestNorm(
            typ=t,
            prozedur=list(AuthentifizierungsManifestProzedur)[i],
            cyber_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(AuthentifizierungsManifestTyp)
    )
    return AuthentifizierungsManifest(normen=normen)
