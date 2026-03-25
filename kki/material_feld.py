"""#681 — MaterialFeld: Materialwissenschaft & Nanotechnologie Wurzel."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.molekularwissenschaft_verfassung import MolekularwissenschaftVerfassung, build_molekularwissenschaft_verfassung


class MaterialFeldGeltung(str, Enum):
    GESPERRT = "gesperrt"
    MATERIAL_AKTIV = "material-aktiv"
    GRUNDLEGEND_MATERIAL_AKTIV = "grundlegend-material-aktiv"


class MaterialFeldTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class MaterialFeldProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class MaterialFeldNorm:
    material_feld_id: str
    geltung: MaterialFeldGeltung
    typ: MaterialFeldTyp
    prozedur: MaterialFeldProzedur
    material_weight: float
    material_tier: int
    material_ids: List[str]
    material_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class MaterialFeld:
    feld_id: str
    normen: List[MaterialFeldNorm]
    parent: MolekularwissenschaftVerfassung


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        MaterialFeldGeltung.GESPERRT: 0.0,
        MaterialFeldGeltung.MATERIAL_AKTIV: 0.05,
        MaterialFeldGeltung.GRUNDLEGEND_MATERIAL_AKTIV: 0.1,
    })
    _TIER_DELTA.update({
        MaterialFeldGeltung.GESPERRT: 0,
        MaterialFeldGeltung.MATERIAL_AKTIV: 1,
        MaterialFeldGeltung.GRUNDLEGEND_MATERIAL_AKTIV: 2,
    })
    _TYP_MAP.update({
        MaterialFeldGeltung.GESPERRT: MaterialFeldTyp.BEOBACHTUNG,
        MaterialFeldGeltung.MATERIAL_AKTIV: MaterialFeldTyp.ANALYSE,
        MaterialFeldGeltung.GRUNDLEGEND_MATERIAL_AKTIV: MaterialFeldTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        MaterialFeldGeltung.GESPERRT: MaterialFeldProzedur.INITIALISIEREN,
        MaterialFeldGeltung.MATERIAL_AKTIV: MaterialFeldProzedur.AKTIVIEREN,
        MaterialFeldGeltung.GRUNDLEGEND_MATERIAL_AKTIV: MaterialFeldProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        MaterialFeldGeltung.GESPERRT: [MaterialFeldGeltung.GESPERRT],
        MaterialFeldGeltung.MATERIAL_AKTIV: [MaterialFeldGeltung.MATERIAL_AKTIV],
        MaterialFeldGeltung.GRUNDLEGEND_MATERIAL_AKTIV: [MaterialFeldGeltung.GRUNDLEGEND_MATERIAL_AKTIV],
    })


_init_map()


def build_material_feld(*, feld_id: str = "material-feld") -> MaterialFeld:
    parent = build_molekularwissenschaft_verfassung(verfassung_id=f"{feld_id}-parent")
    normen: List[MaterialFeldNorm] = []
    for g in MaterialFeldGeltung:
        normen.append(MaterialFeldNorm(
            material_feld_id=f"{feld_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            material_weight=round(sum(n.chemie_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            material_tier=max(n.chemie_tier for n in parent.normen) + _TIER_DELTA[g],
            material_ids=[f"mf-{feld_id}-{g.value}-001", f"mf-{feld_id}-{g.value}-002"],
            material_tags=["material", "feld", g.value],
        ))
    return MaterialFeld(feld_id=feld_id, normen=normen, parent=parent)
