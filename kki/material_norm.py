"""Material-Norm #978 — Normenwerk der Materialeigenschaften im KKI-Schwarm."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

from .metamaterial_senat import Metamaterial, build_metamaterial


class MaterialNormTyp(Enum):
    HAERTE = "HAERTE"
    ZUGFESTIGKEIT = "ZUGFESTIGKEIT"
    LEITFAEHIGKEIT = "LEITFAEHIGKEIT"
    TRANSPARENZ = "TRANSPARENZ"
    BIOKOMPATIBILITAET = "BIOKOMPATIBILITAET"


class MaterialNormProzedur(Enum):
    MESSUNG = "MESSUNG"
    NORMIERUNG = "NORMIERUNG"
    ZERTIFIZIERUNG = "ZERTIFIZIERUNG"
    VERGLEICH = "VERGLEICH"
    KLASSIFIKATION = "KLASSIFIKATION"


_WEIGHT_DELTA: dict[str, float] = {
    "HAERTE": 0.12,
    "ZUGFESTIGKEIT": 0.15,
    "LEITFAEHIGKEIT": 0.18,
    "TRANSPARENZ": 0.11,
    "BIOKOMPATIBILITAET": 0.16,
}

_TYP_MAP: dict[MaterialNormTyp, str] = {
    MaterialNormTyp.HAERTE: "Härtenorm",
    MaterialNormTyp.ZUGFESTIGKEIT: "Zugfestigkeitsnorm",
    MaterialNormTyp.LEITFAEHIGKEIT: "Leitfähigkeitsnorm",
    MaterialNormTyp.TRANSPARENZ: "Transpoarenznorm",
    MaterialNormTyp.BIOKOMPATIBILITAET: "Biokompatibilitätsnorm",
}

_PROZEDUR_MAP: dict[MaterialNormProzedur, str] = {
    MaterialNormProzedur.MESSUNG: "Messung",
    MaterialNormProzedur.NORMIERUNG: "Normierung",
    MaterialNormProzedur.ZERTIFIZIERUNG: "Zertifizierung",
    MaterialNormProzedur.VERGLEICH: "Vergleich",
    MaterialNormProzedur.KLASSIFIKATION: "Klassifikation",
}


@dataclass(frozen=True)
class MaterialNormEintrag:
    name: str
    material_norm_weight: float
    material_norm_tier: int


@dataclass(frozen=True)
class MaterialNorm:
    eintraege: tuple[MaterialNormEintrag, ...]


def build_material_norm(parent=None) -> MaterialNorm:
    basis = parent.normen[-1].material_weight if parent and hasattr(parent, 'normen') else 0.0
    tier_base = max(n.material_tier for n in parent.normen) if parent and hasattr(parent, 'normen') else 0
    items = []
    for i, t in enumerate(MaterialNormTyp):
        delta = _WEIGHT_DELTA.get(t.name, 0.0)
        items.append(MaterialNormEintrag(name=_TYP_MAP[t], material_norm_weight=round(basis + delta, 4), material_norm_tier=tier_base + i + 1))
    return MaterialNorm(eintraege=tuple(items))


# ---------------------------------------------------------------------------
# Backward-compatibility stubs (for dependents of the old #688 API)
# ---------------------------------------------------------------------------
class MaterialNormGeltung(Enum):
    GESPERRT = "gesperrt"
    MATERIAL_NORMATIV = "material-normativ"
    GRUNDLEGEND_MATERIAL_NORMATIV = "grundlegend-material-normativ"


@dataclass(frozen=True)
class MaterialNormSatz:
    """Backward-compat alias — use MaterialNorm instead."""
    eintraege: tuple[MaterialNormEintrag, ...]
