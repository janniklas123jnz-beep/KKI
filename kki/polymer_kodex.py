"""#684 — PolymerKodex: Makromoleküle, Kettenlängen & Kunststoffeigenschaften."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.halbleiter_charta import HalbleiterCharta, build_halbleiter_charta


class PolymerKodexGeltung(str, Enum):
    GESPERRT = "gesperrt"
    POLYMER_VERNETZT = "polymer-vernetzt"
    GRUNDLEGEND_POLYMER_VERNETZT = "grundlegend-polymer-vernetzt"


class PolymerKodexTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class PolymerKodexProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class PolymerKodexEintrag:
    eintrag_id: str
    geltung: PolymerKodexGeltung
    typ: PolymerKodexTyp
    prozedur: PolymerKodexProzedur
    material_weight: float
    material_tier: int
    material_ids: List[str]
    material_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class PolymerKodex:
    kodex_id: str
    eintraege: List[PolymerKodexEintrag]
    parent: HalbleiterCharta


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        PolymerKodexGeltung.GESPERRT: 0.0,
        PolymerKodexGeltung.POLYMER_VERNETZT: 0.05,
        PolymerKodexGeltung.GRUNDLEGEND_POLYMER_VERNETZT: 0.1,
    })
    _TIER_DELTA.update({
        PolymerKodexGeltung.GESPERRT: 0,
        PolymerKodexGeltung.POLYMER_VERNETZT: 1,
        PolymerKodexGeltung.GRUNDLEGEND_POLYMER_VERNETZT: 2,
    })
    _TYP_MAP.update({
        PolymerKodexGeltung.GESPERRT: PolymerKodexTyp.BEOBACHTUNG,
        PolymerKodexGeltung.POLYMER_VERNETZT: PolymerKodexTyp.ANALYSE,
        PolymerKodexGeltung.GRUNDLEGEND_POLYMER_VERNETZT: PolymerKodexTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        PolymerKodexGeltung.GESPERRT: PolymerKodexProzedur.INITIALISIEREN,
        PolymerKodexGeltung.POLYMER_VERNETZT: PolymerKodexProzedur.AKTIVIEREN,
        PolymerKodexGeltung.GRUNDLEGEND_POLYMER_VERNETZT: PolymerKodexProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        PolymerKodexGeltung.GESPERRT: [PolymerKodexGeltung.GESPERRT],
        PolymerKodexGeltung.POLYMER_VERNETZT: [PolymerKodexGeltung.POLYMER_VERNETZT],
        PolymerKodexGeltung.GRUNDLEGEND_POLYMER_VERNETZT: [PolymerKodexGeltung.GRUNDLEGEND_POLYMER_VERNETZT],
    })


_init_map()


def build_polymer_kodex(*, kodex_id: str = "polymer-kodex") -> PolymerKodex:
    parent = build_halbleiter_charta(charta_id=f"{kodex_id}-parent")
    eintraege: List[PolymerKodexEintrag] = []
    for g in PolymerKodexGeltung:
        eintraege.append(PolymerKodexEintrag(
            eintrag_id=f"{kodex_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            material_weight=round(sum(n.material_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            material_tier=max(n.material_tier for n in parent.normen) + _TIER_DELTA[g],
            material_ids=[f"pk-{kodex_id}-{g.value}-001", f"pk-{kodex_id}-{g.value}-002"],
            material_tags=["material", "polymer", g.value],
        ))
    return PolymerKodex(kodex_id=kodex_id, eintraege=eintraege, parent=parent)
