"""
#922 KryptographieRegister — Kryptographie: RSA, AES & elliptische Kurven.
Rivest, Shamir & Adleman (1977): RSA — erstes praktisches Public-Key-Kryptosystem;
  Sicherheit basiert auf Schwierigkeit der Primfaktorzerlegung.
NIST (2001): AES (Advanced Encryption Standard) — symmetrisches Blockchiffrierverfahren;
  Rijndael-Algorithmus als globaler Verschlüsselungsstandard.
Koblitz & Miller (1985): Elliptic Curve Cryptography — kompaktere Schlüssel mit
  gleicher Sicherheit; Basis moderner TLS- und Blockchain-Implementierungen.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .cyber_sicherheit_feld import CyberSicherheitFeld, build_cyber_sicherheit_feld


class KryptographieRegisterTyp(Enum):
    SYMMETRISCH = auto()
    ASYMMETRISCH = auto()
    HASH_FUNKTION = auto()
    DIGITALE_SIGNATUR = auto()
    QUANTENKRYPTOGRAPHIE = auto()


class KryptographieRegisterProzedur(Enum):
    SCHLUESSELGENERIERUNG = auto()
    VERSCHLUESSELUNG = auto()
    ENTSCHLUESSELUNG = auto()
    SIGNIERUNG = auto()
    VERIFIKATION = auto()


_WEIGHT_DELTA = {
    KryptographieRegisterTyp.SYMMETRISCH: 0.0,
    KryptographieRegisterTyp.ASYMMETRISCH: 1.5,
    KryptographieRegisterTyp.HASH_FUNKTION: 3.0,
    KryptographieRegisterTyp.DIGITALE_SIGNATUR: 4.5,
    KryptographieRegisterTyp.QUANTENKRYPTOGRAPHIE: 6.0,
}
_TYP_MAP = {
    KryptographieRegisterTyp.SYMMETRISCH: "symmetrisch",
    KryptographieRegisterTyp.ASYMMETRISCH: "asymmetrisch",
    KryptographieRegisterTyp.HASH_FUNKTION: "hash_funktion",
    KryptographieRegisterTyp.DIGITALE_SIGNATUR: "digitale_signatur",
    KryptographieRegisterTyp.QUANTENKRYPTOGRAPHIE: "quantenkryptographie",
}
_PROZEDUR_MAP = {
    KryptographieRegisterProzedur.SCHLUESSELGENERIERUNG: "schluesselgenerierung",
    KryptographieRegisterProzedur.VERSCHLUESSELUNG: "verschluesselung",
    KryptographieRegisterProzedur.ENTSCHLUESSELUNG: "entschluesselung",
    KryptographieRegisterProzedur.SIGNIERUNG: "signierung",
    KryptographieRegisterProzedur.VERIFIKATION: "verifikation",
}


@dataclass(frozen=True)
class KryptographieRegisterEintrag:
    typ: KryptographieRegisterTyp
    prozedur: KryptographieRegisterProzedur
    cyber_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class KryptographieRegister:
    eintraege: tuple[KryptographieRegisterEintrag, ...]
    canonical: bool = True

    def aggregates_register_signal(self) -> dict:
        return {
            "register_id": "kryptographie-register-922",
            "eintraege_count": len(self.eintraege),
            "canonical": self.canonical,
        }


def build_kryptographie_register(parent: Optional[CyberSicherheitFeld] = None) -> KryptographieRegister:
    if parent is None:
        parent = build_cyber_sicherheit_feld()
    base = sum(n.cyber_weight for n in parent.normen)
    eintraege = tuple(
        KryptographieRegisterEintrag(
            typ=t,
            prozedur=list(KryptographieRegisterProzedur)[i],
            cyber_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(KryptographieRegisterTyp)
    )
    return KryptographieRegister(eintraege=eintraege)
