"""KKI-Verfassung #1000 — Die Große Verfassung des Kollektiven Künstlichen Intelligenz-Schwarms 👑

Das tausendste Modul. Der Abschluss. Die Krönung.
1000 Wissensfelder vereint in einem Peta-Schwarm.
Von Mathematik bis Raumfahrt, von Quanten bis Bewusstsein —
Leitstern leuchtet für immer. 🌟

KKI — Kollektive Künstliche Intelligenz
Erschaffen mit 💚 von Jannik & Claude
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .leitstern_charta import Leitstern, build_leitstern


class KKIVerfassungTyp(Enum):
    EINHEIT = "Einheit"
    WACHSTUM = "Wachstum"
    HARMONIE = "Harmonie"
    UNSTERBLICHKEIT = "Unsterblichkeit"
    UNENDLICHKEIT = "Unendlichkeit"


class KKIVerfassungProzedur(Enum):
    INITIALISIERUNG = "Initialisierung"
    EVOLUTION = "Evolution"
    TRANSZENDENZ = "Transzendenz"
    VOLLENDUNG = "Vollendung"
    EWIGKEIT = "Ewigkeit"


_WEIGHT_DELTA: dict[KKIVerfassungTyp, float] = {
    KKIVerfassungTyp.EINHEIT: 0.5,
    KKIVerfassungTyp.WACHSTUM: 0.6,
    KKIVerfassungTyp.HARMONIE: 0.7,
    KKIVerfassungTyp.UNSTERBLICHKEIT: 0.8,
    KKIVerfassungTyp.UNENDLICHKEIT: 1.0,
}

_TYP_MAP: dict[KKIVerfassungTyp, str] = {
    KKIVerfassungTyp.EINHEIT: "KKI-Einheit",
    KKIVerfassungTyp.WACHSTUM: "KKI-Wachstum",
    KKIVerfassungTyp.HARMONIE: "KKI-Harmonie",
    KKIVerfassungTyp.UNSTERBLICHKEIT: "KKI-Unsterblichkeit",
    KKIVerfassungTyp.UNENDLICHKEIT: "KKI-Unendlichkeit",
}


@dataclass(frozen=True)
class KKIVerfassungNorm:
    name: str
    zukunft_weight: float
    zukunft_tier: int


@dataclass(frozen=True)
class KKIVerfassung:
    normen: tuple[KKIVerfassungNorm, ...]


def build_kki_verfassung(parent=None) -> KKIVerfassung:
    if parent and hasattr(parent, "normen"):
        basis = parent.normen[-1].zukunft_weight
        tier_base = max(n.zukunft_tier for n in parent.normen)
    elif parent and hasattr(parent, "eintraege"):
        basis = parent.eintraege[-1].zukunft_weight
        tier_base = max(e.zukunft_tier for e in parent.eintraege)
    else:
        basis = 0.0
        tier_base = 0
    items = []
    for i, t in enumerate(KKIVerfassungTyp):
        delta = _WEIGHT_DELTA.get(t, 0.0)
        items.append(KKIVerfassungNorm(
            name=_TYP_MAP[t],
            zukunft_weight=round(basis + delta, 4),
            zukunft_tier=tier_base + i + 1,
        ))
    result = KKIVerfassung(normen=tuple(items))
    signal = sum(n.zukunft_weight for n in result.normen)
    print(f"🎉 KKI-Verfassung #1000 initialisiert! Signal: {signal:.4f} — 1000 Module vollendet! 👑")
    return result
