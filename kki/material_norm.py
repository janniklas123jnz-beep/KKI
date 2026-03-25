"""#688 — MaterialNorm: Normative Materialwissenschafts-Standards (*_norm)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.quantenmaterial_senat import QuantenmaterialSenat, build_quantenmaterial_senat


class MaterialNormGeltung(str, Enum):
    GESPERRT = "gesperrt"
    MATERIAL_NORMATIV = "material-normativ"
    GRUNDLEGEND_MATERIAL_NORMATIV = "grundlegend-material-normativ"


class MaterialNormTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class MaterialNormProzedur(str, Enum):
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
class MaterialNormEintrag:
    norm_id: str
    geltung: MaterialNormGeltung
    typ: MaterialNormTyp
    prozedur: MaterialNormProzedur
    material_norm_weight: float
    material_norm_tier: int
    material_norm_ids: List[str]
    material_norm_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class MaterialNormSatz:
    norm_id: str
    normen: List[MaterialNormEintrag]
    parent: QuantenmaterialSenat


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        "gesperrt": 0.0,
        "material-normativ": 0.05,
        "grundlegend-material-normativ": 0.1,
    })
    _TIER_DELTA.update({
        "gesperrt": 0,
        "material-normativ": 1,
        "grundlegend-material-normativ": 2,
    })
    _TYP_MAP.update({
        "gesperrt": MaterialNormTyp.BEOBACHTUNG,
        "material-normativ": MaterialNormTyp.ANALYSE,
        "grundlegend-material-normativ": MaterialNormTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        "gesperrt": MaterialNormProzedur.INITIALISIEREN,
        "material-normativ": MaterialNormProzedur.AKTIVIEREN,
        "grundlegend-material-normativ": MaterialNormProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        "quantenmaterial-aktiv": MaterialNormGeltung.MATERIAL_NORMATIV,
        "grundlegend-quantenmaterial-aktiv": MaterialNormGeltung.GRUNDLEGEND_MATERIAL_NORMATIV,
        "gesperrt": MaterialNormGeltung.GESPERRT,
    })
    _GELTUNG_KEY_MAP.update({
        MaterialNormGeltung.GESPERRT: "gesperrt",
        MaterialNormGeltung.MATERIAL_NORMATIV: "material-normativ",
        MaterialNormGeltung.GRUNDLEGEND_MATERIAL_NORMATIV: "grundlegend-material-normativ",
    })


_init_map()


def build_material_norm(*, norm_id: str = "material-norm") -> MaterialNormSatz:
    parent = build_quantenmaterial_senat(senat_id=f"{norm_id}-parent")
    eintraege: List[MaterialNormEintrag] = []
    for g in MaterialNormGeltung:
        key = _GELTUNG_KEY_MAP[g]
        eintraege.append(MaterialNormEintrag(
            norm_id=f"{norm_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[key],
            prozedur=_PROZEDUR_MAP[key],
            material_norm_weight=round(sum(n.material_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[key]), 4),
            material_norm_tier=max(n.material_tier for n in parent.normen) + _TIER_DELTA[key],
            material_norm_ids=[f"mn-{norm_id}-{g.value}-001", f"mn-{norm_id}-{g.value}-002"],
            material_norm_tags=["material", "norm", g.value],
        ))
    return MaterialNormSatz(norm_id=norm_id, normen=eintraege, parent=parent)
