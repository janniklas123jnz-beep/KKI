"""#690 — MaterialwissenschaftVerfassung ⭐: Block-Krone Materialwissenschaft & Nanotechnologie."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.bio_material_charta import BioMaterialCharta, build_bio_material_charta


class MaterialwissenschaftVerfassungGeltung(str, Enum):
    GESPERRT = "gesperrt"
    MATERIALWISS_SOUVERAEN = "materialwiss-souveraen"
    GRUNDLEGEND_MATERIALWISS_SOUVERAEN = "grundlegend-materialwiss-souveraen"


class MaterialwissenschaftVerfassungTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class MaterialwissenschaftVerfassungProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class MaterialwissenschaftVerfassungsNorm:
    materialwiss_verfassung_id: str
    geltung: MaterialwissenschaftVerfassungGeltung
    typ: MaterialwissenschaftVerfassungTyp
    prozedur: MaterialwissenschaftVerfassungProzedur
    material_weight: float
    material_tier: int
    material_ids: List[str]
    material_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class MaterialwissenschaftVerfassung:
    verfassung_id: str
    normen: List[MaterialwissenschaftVerfassungsNorm]
    parent: BioMaterialCharta

    def aggregates_verfassung_signal(self) -> dict:
        return {
            "verfassung_id": self.verfassung_id,
            "total_weight": round(sum(n.material_weight for n in self.normen), 4),
            "norm_count": len(self.normen),
        }


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        MaterialwissenschaftVerfassungGeltung.GESPERRT: 0.0,
        MaterialwissenschaftVerfassungGeltung.MATERIALWISS_SOUVERAEN: 0.05,
        MaterialwissenschaftVerfassungGeltung.GRUNDLEGEND_MATERIALWISS_SOUVERAEN: 0.1,
    })
    _TIER_DELTA.update({
        MaterialwissenschaftVerfassungGeltung.GESPERRT: 0,
        MaterialwissenschaftVerfassungGeltung.MATERIALWISS_SOUVERAEN: 1,
        MaterialwissenschaftVerfassungGeltung.GRUNDLEGEND_MATERIALWISS_SOUVERAEN: 2,
    })
    _TYP_MAP.update({
        MaterialwissenschaftVerfassungGeltung.GESPERRT: MaterialwissenschaftVerfassungTyp.BEOBACHTUNG,
        MaterialwissenschaftVerfassungGeltung.MATERIALWISS_SOUVERAEN: MaterialwissenschaftVerfassungTyp.ANALYSE,
        MaterialwissenschaftVerfassungGeltung.GRUNDLEGEND_MATERIALWISS_SOUVERAEN: MaterialwissenschaftVerfassungTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        MaterialwissenschaftVerfassungGeltung.GESPERRT: MaterialwissenschaftVerfassungProzedur.INITIALISIEREN,
        MaterialwissenschaftVerfassungGeltung.MATERIALWISS_SOUVERAEN: MaterialwissenschaftVerfassungProzedur.AKTIVIEREN,
        MaterialwissenschaftVerfassungGeltung.GRUNDLEGEND_MATERIALWISS_SOUVERAEN: MaterialwissenschaftVerfassungProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        MaterialwissenschaftVerfassungGeltung.GESPERRT: [MaterialwissenschaftVerfassungGeltung.GESPERRT],
        MaterialwissenschaftVerfassungGeltung.MATERIALWISS_SOUVERAEN: [MaterialwissenschaftVerfassungGeltung.MATERIALWISS_SOUVERAEN],
        MaterialwissenschaftVerfassungGeltung.GRUNDLEGEND_MATERIALWISS_SOUVERAEN: [MaterialwissenschaftVerfassungGeltung.GRUNDLEGEND_MATERIALWISS_SOUVERAEN],
    })


_init_map()


def build_materialwissenschaft_verfassung(*, verfassung_id: str = "materialwissenschaft-verfassung") -> MaterialwissenschaftVerfassung:
    parent = build_bio_material_charta(charta_id=f"{verfassung_id}-parent")
    normen: List[MaterialwissenschaftVerfassungsNorm] = []
    for g in MaterialwissenschaftVerfassungGeltung:
        normen.append(MaterialwissenschaftVerfassungsNorm(
            materialwiss_verfassung_id=f"{verfassung_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            material_weight=round(sum(n.material_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            material_tier=max(n.material_tier for n in parent.normen) + _TIER_DELTA[g],
            material_ids=[f"mv-{verfassung_id}-{g.value}-001", f"mv-{verfassung_id}-{g.value}-002"],
            material_tags=["material", "materialwissenschaft", "verfassung", g.value],
        ))
    return MaterialwissenschaftVerfassung(verfassung_id=verfassung_id, normen=normen, parent=parent)
