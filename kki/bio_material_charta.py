"""#689 — BioMaterialCharta: Biomimetik, Hydrogele & biokompatible Werkstoffe."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.material_norm import MaterialNormSatz, build_material_norm


class BioMaterialChartaGeltung(str, Enum):
    GESPERRT = "gesperrt"
    BIOMATERIAL_INTEGRIERT = "biomaterial-integriert"
    GRUNDLEGEND_BIOMATERIAL_INTEGRIERT = "grundlegend-biomaterial-integriert"


class BioMaterialChartaTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class BioMaterialChartaProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class BioMaterialChartaNorm:
    norm_id: str
    geltung: BioMaterialChartaGeltung
    typ: BioMaterialChartaTyp
    prozedur: BioMaterialChartaProzedur
    material_weight: float
    material_tier: int
    material_ids: List[str]
    material_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class BioMaterialCharta:
    charta_id: str
    normen: List[BioMaterialChartaNorm]
    parent: MaterialNormSatz


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        BioMaterialChartaGeltung.GESPERRT: 0.0,
        BioMaterialChartaGeltung.BIOMATERIAL_INTEGRIERT: 0.05,
        BioMaterialChartaGeltung.GRUNDLEGEND_BIOMATERIAL_INTEGRIERT: 0.1,
    })
    _TIER_DELTA.update({
        BioMaterialChartaGeltung.GESPERRT: 0,
        BioMaterialChartaGeltung.BIOMATERIAL_INTEGRIERT: 1,
        BioMaterialChartaGeltung.GRUNDLEGEND_BIOMATERIAL_INTEGRIERT: 2,
    })
    _TYP_MAP.update({
        BioMaterialChartaGeltung.GESPERRT: BioMaterialChartaTyp.BEOBACHTUNG,
        BioMaterialChartaGeltung.BIOMATERIAL_INTEGRIERT: BioMaterialChartaTyp.ANALYSE,
        BioMaterialChartaGeltung.GRUNDLEGEND_BIOMATERIAL_INTEGRIERT: BioMaterialChartaTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        BioMaterialChartaGeltung.GESPERRT: BioMaterialChartaProzedur.INITIALISIEREN,
        BioMaterialChartaGeltung.BIOMATERIAL_INTEGRIERT: BioMaterialChartaProzedur.AKTIVIEREN,
        BioMaterialChartaGeltung.GRUNDLEGEND_BIOMATERIAL_INTEGRIERT: BioMaterialChartaProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        BioMaterialChartaGeltung.GESPERRT: [BioMaterialChartaGeltung.GESPERRT],
        BioMaterialChartaGeltung.BIOMATERIAL_INTEGRIERT: [BioMaterialChartaGeltung.BIOMATERIAL_INTEGRIERT],
        BioMaterialChartaGeltung.GRUNDLEGEND_BIOMATERIAL_INTEGRIERT: [BioMaterialChartaGeltung.GRUNDLEGEND_BIOMATERIAL_INTEGRIERT],
    })


_init_map()


def build_bio_material_charta(*, charta_id: str = "bio-material-charta") -> BioMaterialCharta:
    parent = build_material_norm(norm_id=f"{charta_id}-parent")
    normen: List[BioMaterialChartaNorm] = []
    for g in BioMaterialChartaGeltung:
        normen.append(BioMaterialChartaNorm(
            norm_id=f"{charta_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            material_weight=round(sum(e.material_norm_weight for e in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            material_tier=max(e.material_norm_tier for e in parent.normen) + _TIER_DELTA[g],
            material_ids=[f"bmc-{charta_id}-{g.value}-001", f"bmc-{charta_id}-{g.value}-002"],
            material_tags=["material", "biomaterial", g.value],
        ))
    return BioMaterialCharta(charta_id=charta_id, normen=normen, parent=parent)
