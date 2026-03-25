"""#682 — KristallstrukturRegister: Gitter, Elementarzellen & Kristallsysteme."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.material_feld import MaterialFeld, build_material_feld


class KristallstrukturRegisterGeltung(str, Enum):
    GESPERRT = "gesperrt"
    KRISTALLSTRUKTURIERT = "kristallstrukturiert"
    GRUNDLEGEND_KRISTALLSTRUKTURIERT = "grundlegend-kristallstrukturiert"


class KristallstrukturRegisterTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class KristallstrukturRegisterProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class KristallstrukturRegisterEintrag:
    eintrag_id: str
    geltung: KristallstrukturRegisterGeltung
    typ: KristallstrukturRegisterTyp
    prozedur: KristallstrukturRegisterProzedur
    material_weight: float
    material_tier: int
    material_ids: List[str]
    material_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class KristallstrukturRegister:
    register_id: str
    eintraege: List[KristallstrukturRegisterEintrag]
    parent: MaterialFeld


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        KristallstrukturRegisterGeltung.GESPERRT: 0.0,
        KristallstrukturRegisterGeltung.KRISTALLSTRUKTURIERT: 0.05,
        KristallstrukturRegisterGeltung.GRUNDLEGEND_KRISTALLSTRUKTURIERT: 0.1,
    })
    _TIER_DELTA.update({
        KristallstrukturRegisterGeltung.GESPERRT: 0,
        KristallstrukturRegisterGeltung.KRISTALLSTRUKTURIERT: 1,
        KristallstrukturRegisterGeltung.GRUNDLEGEND_KRISTALLSTRUKTURIERT: 2,
    })
    _TYP_MAP.update({
        KristallstrukturRegisterGeltung.GESPERRT: KristallstrukturRegisterTyp.BEOBACHTUNG,
        KristallstrukturRegisterGeltung.KRISTALLSTRUKTURIERT: KristallstrukturRegisterTyp.ANALYSE,
        KristallstrukturRegisterGeltung.GRUNDLEGEND_KRISTALLSTRUKTURIERT: KristallstrukturRegisterTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        KristallstrukturRegisterGeltung.GESPERRT: KristallstrukturRegisterProzedur.INITIALISIEREN,
        KristallstrukturRegisterGeltung.KRISTALLSTRUKTURIERT: KristallstrukturRegisterProzedur.AKTIVIEREN,
        KristallstrukturRegisterGeltung.GRUNDLEGEND_KRISTALLSTRUKTURIERT: KristallstrukturRegisterProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        KristallstrukturRegisterGeltung.GESPERRT: [KristallstrukturRegisterGeltung.GESPERRT],
        KristallstrukturRegisterGeltung.KRISTALLSTRUKTURIERT: [KristallstrukturRegisterGeltung.KRISTALLSTRUKTURIERT],
        KristallstrukturRegisterGeltung.GRUNDLEGEND_KRISTALLSTRUKTURIERT: [KristallstrukturRegisterGeltung.GRUNDLEGEND_KRISTALLSTRUKTURIERT],
    })


_init_map()


def build_kristallstruktur_register(*, register_id: str = "kristallstruktur-register") -> KristallstrukturRegister:
    parent = build_material_feld(feld_id=f"{register_id}-parent")
    eintraege: List[KristallstrukturRegisterEintrag] = []
    for g in KristallstrukturRegisterGeltung:
        eintraege.append(KristallstrukturRegisterEintrag(
            eintrag_id=f"{register_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            material_weight=round(sum(n.material_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            material_tier=max(n.material_tier for n in parent.normen) + _TIER_DELTA[g],
            material_ids=[f"kr-{register_id}-{g.value}-001", f"kr-{register_id}-{g.value}-002"],
            material_tags=["material", "kristallstruktur", g.value],
        ))
    return KristallstrukturRegister(register_id=register_id, eintraege=eintraege, parent=parent)
