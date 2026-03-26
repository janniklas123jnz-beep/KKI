"""MatWiss-Verfassung #980 — Verfassung der Materialwissenschaften im KKI-Schwarm ⭐."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

from .nanofabrik_charta import Nanofabrik, build_nanofabrik


class MatwissVerfassungTyp(Enum):
    GRUNDPRINZIP = "GRUNDPRINZIP"
    SYNTHESIS = "SYNTHESIS"
    CHARAKTERISIERUNG = "CHARAKTERISIERUNG"
    ANWENDUNG = "ANWENDUNG"
    ZUKUNFT = "ZUKUNFT"


class MatwissVerfassungProzedur(Enum):
    FORSCHUNG = "FORSCHUNG"
    ENTWICKLUNG = "ENTWICKLUNG"
    NORMIERUNG = "NORMIERUNG"
    TRANSFER = "TRANSFER"
    VISION = "VISION"


_WEIGHT_DELTA: dict[MatwissVerfassungTyp, float] = {
    MatwissVerfassungTyp.GRUNDPRINZIP: 0.1,
    MatwissVerfassungTyp.SYNTHESIS: 0.15,
    MatwissVerfassungTyp.CHARAKTERISIERUNG: 0.2,
    MatwissVerfassungTyp.ANWENDUNG: 0.25,
    MatwissVerfassungTyp.ZUKUNFT: 0.3,
}

_TYP_MAP: dict[MatwissVerfassungTyp, str] = {
    MatwissVerfassungTyp.GRUNDPRINZIP: "Materialwiss.-Grundprinzip",
    MatwissVerfassungTyp.SYNTHESIS: "Materialsynthese",
    MatwissVerfassungTyp.CHARAKTERISIERUNG: "Materialcharakterisierung",
    MatwissVerfassungTyp.ANWENDUNG: "Materialanwendung",
    MatwissVerfassungTyp.ZUKUNFT: "Zukunft der Materialwiss.",
}

_PROZEDUR_MAP: dict[MatwissVerfassungProzedur, str] = {
    MatwissVerfassungProzedur.FORSCHUNG: "Forschung",
    MatwissVerfassungProzedur.ENTWICKLUNG: "Entwicklung",
    MatwissVerfassungProzedur.NORMIERUNG: "Normierung",
    MatwissVerfassungProzedur.TRANSFER: "Transfer",
    MatwissVerfassungProzedur.VISION: "Vision",
}


@dataclass(frozen=True)
class MatwissVerfassungNorm:
    name: str
    material_weight: float
    material_tier: int


@dataclass(frozen=True)
class MatwissVerfassung:
    normen: tuple[MatwissVerfassungNorm, ...]


def build_matwiss_verfassung(parent=None) -> MatwissVerfassung:
    basis = parent.normen[-1].material_weight if parent and hasattr(parent, 'normen') else 0.0
    tier_base = max(n.material_tier for n in parent.normen) if parent and hasattr(parent, 'normen') else 0
    items = []
    for i, t in enumerate(MatwissVerfassungTyp):
        delta = _WEIGHT_DELTA.get(t, 0.0)
        items.append(MatwissVerfassungNorm(name=_TYP_MAP[t], material_weight=round(basis + delta, 4), material_tier=tier_base + i + 1))
    result = MatwissVerfassung(normen=tuple(items))
    signal = sum(n.material_weight for n in result.normen)
    print(f"# signal: {signal:.4f}")
    return result
