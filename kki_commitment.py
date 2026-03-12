"""Wiederverwendbare Commitment-Helfer fuer KKI."""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from typing import Optional


@dataclass
class Commitment:
    """Ein kryptografisches Commitment fuer eine geplante Aktion."""

    hash_wert: str
    nonce: str
    aktion: Optional[str] = None

    @staticmethod
    def erstelle(aktion: str) -> 'Commitment':
        nonce = hashlib.sha256(str(random.random()).encode()).hexdigest()[:16]
        hash_wert = hashlib.sha256(f"{aktion}:{nonce}".encode()).hexdigest()
        return Commitment(hash_wert=hash_wert, nonce=nonce, aktion=None)

    def reveal(self, aktion: str) -> bool:
        erwarteter_hash = hashlib.sha256(f"{aktion}:{self.nonce}".encode()).hexdigest()
        self.aktion = aktion
        return erwarteter_hash == self.hash_wert

    def verifiziere(self, behauptete_aktion: str) -> bool:
        erwarteter_hash = hashlib.sha256(f"{behauptete_aktion}:{self.nonce}".encode()).hexdigest()
        return erwarteter_hash == self.hash_wert
