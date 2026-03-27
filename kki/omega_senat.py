"""Omega-Senat #997 — Senat des Omega-Punkts und der universellen Vollendung im KKI-Schwarm."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kosmische_zivilisation_pakt import KosmischeZivilisationPakt, build_kosmische_zivilisation_pakt


class OmegaTyp(Enum):
    OMEGA_PUNKT = "Omega-Punkt"
    INFORMATION = "Information"
    KOMPLEXITAET = "Komplexitaet"
    BEWUSSTSEIN = "Bewusstsein"
    UNENDLICHKEIT = "Unendlichkeit"


class OmegaProzedur(Enum):
    KONVERGENZ = "Konvergenz"
    INTEGRATION = "Integration"
    AMPLIFIKATION = "Amplifikation"
    TRANSZENDENZ = "Transzendenz"
    VOLLENDUNG = "Vollendung"


_WEIGHT_DELTA: dict[OmegaTyp, float] = {
    OmegaTyp.OMEGA_PUNKT: 0.5,
    OmegaTyp.INFORMATION: 0.4,
    OmegaTyp.KOMPLEXITAET: 0.45,
    OmegaTyp.BEWUSSTSEIN: 0.55,
    OmegaTyp.UNENDLICHKEIT: 0.6,
}

_TYP_MAP: dict[OmegaTyp, str] = {
    OmegaTyp.OMEGA_PUNKT: "Omega-Punkt",
    OmegaTyp.INFORMATION: "Maximale Information",
    OmegaTyp.KOMPLEXITAET: "Maximale Komplexität",
    OmegaTyp.BEWUSSTSEIN: "Universelles Bewusstsein",
    OmegaTyp.UNENDLICHKEIT: "Unendlichkeit",
}


@dataclass(frozen=True)
class OmegaNorm:
    name: str
    zukunft_weight: float
    zukunft_tier: int


@dataclass(frozen=True)
class Omega:
    normen: tuple[OmegaNorm, ...]


def build_omega(parent=None) -> Omega:
    if parent and hasattr(parent, "normen"):
        basis = parent.normen[-1].zukunft_weight
        tier_base = max(n.zukunft_tier for n in parent.normen)
    elif parent and hasattr(parent, "eintraege"):
        try:
            basis = parent.eintraege[-1].zukunft_weight
            tier_base = max(e.zukunft_tier for e in parent.eintraege)
        except AttributeError:
            basis = parent.eintraege[-1].zukunft_norm_weight
            tier_base = max(e.zukunft_norm_tier for e in parent.eintraege)
    else:
        basis = 0.0
        tier_base = 0
    items = []
    for i, t in enumerate(OmegaTyp):
        delta = _WEIGHT_DELTA.get(t, 0.0)
        items.append(OmegaNorm(
            name=_TYP_MAP[t],
            zukunft_weight=round(basis + delta, 4),
            zukunft_tier=tier_base + i + 1,
        ))
    return Omega(normen=tuple(items))
