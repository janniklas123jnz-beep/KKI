"""#674 ReaktionskinetikKodex — Reaktionskinetik & Gleichgewicht (parent: ChemischeBindungsCharta)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .chemische_bindungs_charta import ChemischeBindungsCharta, build_chemische_bindungs_charta

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class ReaktionskinetikKodexGeltung(str, Enum):
    GESPERRT = "gesperrt"
    REAKTIONSKINETISCH = "reaktionskinetisch"
    GRUNDLEGEND_REAKTIONSKINETISCH = "grundlegend-reaktionskinetisch"


class ReaktionskinetikKodexTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"
    KATALYSE = "katalyse"


class ReaktionskinetikKodexProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class ReaktionskinetikKodexEintrag:
    reaktionskinetik_kodex_id: str
    geltung: ReaktionskinetikKodexGeltung
    typ: ReaktionskinetikKodexTyp
    prozedur: ReaktionskinetikKodexProzedur
    chemie_weight: float
    chemie_tier: int
    chemie_ids: List[str]
    chemie_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class ReaktionskinetikKodex:
    kodex_id: str
    eintraege: List[ReaktionskinetikKodexEintrag]
    parent: ChemischeBindungsCharta


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        ReaktionskinetikKodexGeltung.GESPERRT: 0.0,
        ReaktionskinetikKodexGeltung.REAKTIONSKINETISCH: 0.05,
        ReaktionskinetikKodexGeltung.GRUNDLEGEND_REAKTIONSKINETISCH: 0.1,
    })
    _TIER_DELTA.update({
        ReaktionskinetikKodexGeltung.GESPERRT: 0,
        ReaktionskinetikKodexGeltung.REAKTIONSKINETISCH: 1,
        ReaktionskinetikKodexGeltung.GRUNDLEGEND_REAKTIONSKINETISCH: 2,
    })
    _TYP_MAP.update({
        ReaktionskinetikKodexGeltung.GESPERRT: ReaktionskinetikKodexTyp.BEOBACHTUNG,
        ReaktionskinetikKodexGeltung.REAKTIONSKINETISCH: ReaktionskinetikKodexTyp.ANALYSE,
        ReaktionskinetikKodexGeltung.GRUNDLEGEND_REAKTIONSKINETISCH: ReaktionskinetikKodexTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        ReaktionskinetikKodexGeltung.GESPERRT: ReaktionskinetikKodexProzedur.INITIALISIEREN,
        ReaktionskinetikKodexGeltung.REAKTIONSKINETISCH: ReaktionskinetikKodexProzedur.AKTIVIEREN,
        ReaktionskinetikKodexGeltung.GRUNDLEGEND_REAKTIONSKINETISCH: ReaktionskinetikKodexProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        ReaktionskinetikKodexGeltung.GESPERRT: [ReaktionskinetikKodexGeltung.GESPERRT],
        ReaktionskinetikKodexGeltung.REAKTIONSKINETISCH: [ReaktionskinetikKodexGeltung.REAKTIONSKINETISCH],
        ReaktionskinetikKodexGeltung.GRUNDLEGEND_REAKTIONSKINETISCH: [ReaktionskinetikKodexGeltung.GRUNDLEGEND_REAKTIONSKINETISCH],
    })


_init_map()


def build_reaktionskinetik_kodex(*, kodex_id: str = "reaktionskinetik-kodex") -> ReaktionskinetikKodex:
    parent = build_chemische_bindungs_charta(charta_id=f"{kodex_id}-parent")
    eintraege: List[ReaktionskinetikKodexEintrag] = []
    for g in ReaktionskinetikKodexGeltung:
        eintraege.append(ReaktionskinetikKodexEintrag(
            reaktionskinetik_kodex_id=f"{kodex_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            chemie_weight=round(sum(n.chemie_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            chemie_tier=max(n.chemie_tier for n in parent.normen) + _TIER_DELTA[g],
            chemie_ids=[f"rk-{kodex_id}-{g.value}-001", f"rk-{kodex_id}-{g.value}-002"],
            chemie_tags=["chemie", "reaktionskinetik", "kodex", g.value],
        ))
    return ReaktionskinetikKodex(kodex_id=kodex_id, eintraege=eintraege, parent=parent)
