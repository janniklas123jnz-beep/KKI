"""#738 — IngenieurNorm: Normative Technikstandards (*_norm)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.nachhaltigkeitstechnik_senat import NachhaltigkeitstechnikSenat, build_nachhaltigkeitstechnik_senat


class IngenieurNormGeltung(str, Enum):
    GESPERRT = "gesperrt"
    ING_NORMATIV = "ing-normativ"
    GRUNDLEGEND_ING_NORMATIV = "grundlegend-ing-normativ"


class IngenieurNormTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class IngenieurNormProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}
_GELTUNG_KEY_MAP: dict = {}


@dataclass(frozen=True)
class IngenieurNormEintrag:
    norm_id: str
    geltung: IngenieurNormGeltung
    typ: IngenieurNormTyp
    prozedur: IngenieurNormProzedur
    ing_norm_weight: float
    ing_norm_tier: int
    ing_norm_ids: List[str]
    ing_norm_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class IngenieurNormSatz:
    norm_id: str
    normen: List[IngenieurNormEintrag]
    parent: NachhaltigkeitstechnikSenat


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        "gesperrt": 0.0,
        "ing-normativ": 0.05,
        "grundlegend-ing-normativ": 0.1,
    })
    _TIER_DELTA.update({
        "gesperrt": 0,
        "ing-normativ": 1,
        "grundlegend-ing-normativ": 2,
    })
    _TYP_MAP.update({
        "gesperrt": IngenieurNormTyp.BEOBACHTUNG,
        "ing-normativ": IngenieurNormTyp.ANALYSE,
        "grundlegend-ing-normativ": IngenieurNormTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        "gesperrt": IngenieurNormProzedur.INITIALISIEREN,
        "ing-normativ": IngenieurNormProzedur.AKTIVIEREN,
        "grundlegend-ing-normativ": IngenieurNormProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        "nachhaltigkeitstechnisch": IngenieurNormGeltung.ING_NORMATIV,
        "grundlegend-nachhaltigkeitstechnisch": IngenieurNormGeltung.GRUNDLEGEND_ING_NORMATIV,
        "gesperrt": IngenieurNormGeltung.GESPERRT,
    })
    _GELTUNG_KEY_MAP.update({
        IngenieurNormGeltung.GESPERRT: "gesperrt",
        IngenieurNormGeltung.ING_NORMATIV: "ing-normativ",
        IngenieurNormGeltung.GRUNDLEGEND_ING_NORMATIV: "grundlegend-ing-normativ",
    })


_init_map()


def build_ingenieur_norm(*, norm_id: str = "ingenieur-norm") -> IngenieurNormSatz:
    parent = build_nachhaltigkeitstechnik_senat(senat_id=f"{norm_id}-parent")
    eintraege: List[IngenieurNormEintrag] = []
    for g in IngenieurNormGeltung:
        key = _GELTUNG_KEY_MAP[g]
        eintraege.append(IngenieurNormEintrag(
            norm_id=f"{norm_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[key],
            prozedur=_PROZEDUR_MAP[key],
            ing_norm_weight=round(sum(n.ing_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[key]), 4),
            ing_norm_tier=max(n.ing_tier for n in parent.normen) + _TIER_DELTA[key],
            ing_norm_ids=[f"in-{norm_id}-{g.value}-001", f"in-{norm_id}-{g.value}-002"],
            ing_norm_tags=["ing", "norm", g.value],
        ))
    return IngenieurNormSatz(norm_id=norm_id, normen=eintraege, parent=parent)
