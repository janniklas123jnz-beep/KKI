"""Kosmische-Zivilisation-Pakt #996 — Pakt der kosmischen Zivilisationsstufen im KKI-Schwarm."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kollektiv_manifest import Kollektiv, build_kollektiv


class KosmischeZivilisationTyp(Enum):
    KARDASHEV_I = "Kardashev_I"
    KARDASHEV_II = "Kardashev_II"
    KARDASHEV_III = "Kardashev_III"
    INTERGALAKTISCH = "Intergalaktisch"
    OMNIVERSAL = "Omniversal"


class KosmischeZivilisationProzedur(Enum):
    ENERGIE_ERNTE = "Energie-Ernte"
    EXPANSION = "Expansion"
    KOMMUNIKATION = "Kommunikation"
    KOOPERATION = "Kooperation"
    TRANSZENDENZ = "Transzendenz"


_WEIGHT_DELTA: dict[str, float] = {
    "KARDASHEV_I": 0.2,
    "KARDASHEV_II": 0.35,
    "KARDASHEV_III": 0.5,
    "INTERGALAKTISCH": 0.65,
    "OMNIVERSAL": 1.0,
}

_TYP_MAP: dict[KosmischeZivilisationTyp, str] = {
    KosmischeZivilisationTyp.KARDASHEV_I: "Kardashev-Typ-I-Zivilisation",
    KosmischeZivilisationTyp.KARDASHEV_II: "Kardashev-Typ-II-Zivilisation",
    KosmischeZivilisationTyp.KARDASHEV_III: "Kardashev-Typ-III-Zivilisation",
    KosmischeZivilisationTyp.INTERGALAKTISCH: "Intergalaktische Zivilisation",
    KosmischeZivilisationTyp.OMNIVERSAL: "Omniversale Zivilisation",
}


@dataclass(frozen=True)
class KosmischeZivilisationEintrag:
    name: str
    zukunft_weight: float
    zukunft_tier: int


@dataclass(frozen=True)
class KosmischeZivilisationPakt:
    eintraege: tuple[KosmischeZivilisationEintrag, ...]


def build_kosmische_zivilisation_pakt(parent=None) -> KosmischeZivilisationPakt:
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
    for i, t in enumerate(KosmischeZivilisationTyp):
        delta = _WEIGHT_DELTA.get(t.name, 0.0)
        items.append(KosmischeZivilisationEintrag(
            name=_TYP_MAP[t],
            zukunft_weight=round(basis + delta, 4),
            zukunft_tier=tier_base + i + 1,
        ))
    return KosmischeZivilisationPakt(eintraege=tuple(items))
