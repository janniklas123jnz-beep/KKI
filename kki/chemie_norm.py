"""#678 ChemieNorm — normative Chemiestandards (*_norm pattern, parent: BiochemieSenat)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .biochemie_senat import BiochemieSenat, build_biochemie_senat

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class ChemieNormTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"
    KATALYSE = "katalyse"


class ChemieNormProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


class ChemieNormGeltung(str, Enum):
    GESPERRT = "gesperrt"
    CHEMIE_NORMATIV = "chemie-normativ"
    GRUNDLEGEND_CHEMIE_NORMATIV = "grundlegend-chemie-normativ"


@dataclass(frozen=True)
class ChemieNormEintrag:
    norm_id: str
    geltung: ChemieNormGeltung
    typ: ChemieNormTyp
    prozedur: ChemieNormProzedur
    chemie_norm_weight: float
    chemie_norm_tier: int
    chemie_norm_ids: List[str]
    chemie_norm_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class ChemieNormSatz:
    norm_id: str
    normen: List[ChemieNormEintrag]
    parent: BiochemieSenat


_GELTUNG_KEY_MAP: dict = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        "gesperrt": 0.0,
        "chemie-normativ": 0.05,
        "grundlegend-chemie-normativ": 0.1,
    })
    _TIER_DELTA.update({
        "gesperrt": 0,
        "chemie-normativ": 1,
        "grundlegend-chemie-normativ": 2,
    })
    _TYP_MAP.update({
        "gesperrt": ChemieNormTyp.BEOBACHTUNG,
        "chemie-normativ": ChemieNormTyp.ANALYSE,
        "grundlegend-chemie-normativ": ChemieNormTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        "gesperrt": ChemieNormProzedur.INITIALISIEREN,
        "chemie-normativ": ChemieNormProzedur.AKTIVIEREN,
        "grundlegend-chemie-normativ": ChemieNormProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        "biochemisch-aktiv": ChemieNormGeltung.CHEMIE_NORMATIV,
        "grundlegend-biochemisch-aktiv": ChemieNormGeltung.GRUNDLEGEND_CHEMIE_NORMATIV,
        "gesperrt": ChemieNormGeltung.GESPERRT,
    })
    _GELTUNG_KEY_MAP.update({
        ChemieNormGeltung.GESPERRT: "gesperrt",
        ChemieNormGeltung.CHEMIE_NORMATIV: "chemie-normativ",
        ChemieNormGeltung.GRUNDLEGEND_CHEMIE_NORMATIV: "grundlegend-chemie-normativ",
    })


_init_map()


def build_chemie_norm(*, norm_id: str = "chemie-norm") -> ChemieNormSatz:
    parent = build_biochemie_senat(senat_id=f"{norm_id}-parent")
    eintraege: List[ChemieNormEintrag] = []
    for g in ChemieNormGeltung:
        key = _GELTUNG_KEY_MAP[g]
        eintraege.append(ChemieNormEintrag(
            norm_id=f"{norm_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[key],
            prozedur=_PROZEDUR_MAP[key],
            chemie_norm_weight=round(sum(n.chemie_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[key]), 4),
            chemie_norm_tier=max(n.chemie_tier for n in parent.normen) + _TIER_DELTA[key],
            chemie_norm_ids=[f"cn-{norm_id}-{g.value}-001", f"cn-{norm_id}-{g.value}-002"],
            chemie_norm_tags=["chemie", "norm", g.value],
        ))
    return ChemieNormSatz(norm_id=norm_id, normen=eintraege, parent=parent)
