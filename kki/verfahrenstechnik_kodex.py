"""#734 — VerfahrenstechnikKodex: Prozesse, Reaktoren & Trenntechnik."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.elektrotechnik_charta import ElektrotechnikCharta, build_elektrotechnik_charta


class VerfahrenstechnikKodexGeltung(str, Enum):
    GESPERRT = "gesperrt"
    VERFAHRENSTECHNISCH = "verfahrenstechnisch"
    GRUNDLEGEND_VERFAHRENSTECHNISCH = "grundlegend-verfahrenstechnisch"


class VerfahrenstechnikKodexTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class VerfahrenstechnikKodexProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class VerfahrenstechnikKodexEintrag:
    eintrag_id: str
    geltung: VerfahrenstechnikKodexGeltung
    typ: VerfahrenstechnikKodexTyp
    prozedur: VerfahrenstechnikKodexProzedur
    ing_weight: float
    ing_tier: int
    ing_ids: List[str]
    ing_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class VerfahrenstechnikKodex:
    kodex_id: str
    eintraege: List[VerfahrenstechnikKodexEintrag]
    parent: ElektrotechnikCharta


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        VerfahrenstechnikKodexGeltung.GESPERRT: 0.0,
        VerfahrenstechnikKodexGeltung.VERFAHRENSTECHNISCH: 0.05,
        VerfahrenstechnikKodexGeltung.GRUNDLEGEND_VERFAHRENSTECHNISCH: 0.1,
    })
    _TIER_DELTA.update({
        VerfahrenstechnikKodexGeltung.GESPERRT: 0,
        VerfahrenstechnikKodexGeltung.VERFAHRENSTECHNISCH: 1,
        VerfahrenstechnikKodexGeltung.GRUNDLEGEND_VERFAHRENSTECHNISCH: 2,
    })
    _TYP_MAP.update({
        VerfahrenstechnikKodexGeltung.GESPERRT: VerfahrenstechnikKodexTyp.BEOBACHTUNG,
        VerfahrenstechnikKodexGeltung.VERFAHRENSTECHNISCH: VerfahrenstechnikKodexTyp.ANALYSE,
        VerfahrenstechnikKodexGeltung.GRUNDLEGEND_VERFAHRENSTECHNISCH: VerfahrenstechnikKodexTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        VerfahrenstechnikKodexGeltung.GESPERRT: VerfahrenstechnikKodexProzedur.INITIALISIEREN,
        VerfahrenstechnikKodexGeltung.VERFAHRENSTECHNISCH: VerfahrenstechnikKodexProzedur.AKTIVIEREN,
        VerfahrenstechnikKodexGeltung.GRUNDLEGEND_VERFAHRENSTECHNISCH: VerfahrenstechnikKodexProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        VerfahrenstechnikKodexGeltung.GESPERRT: [VerfahrenstechnikKodexGeltung.GESPERRT],
        VerfahrenstechnikKodexGeltung.VERFAHRENSTECHNISCH: [VerfahrenstechnikKodexGeltung.VERFAHRENSTECHNISCH],
        VerfahrenstechnikKodexGeltung.GRUNDLEGEND_VERFAHRENSTECHNISCH: [VerfahrenstechnikKodexGeltung.GRUNDLEGEND_VERFAHRENSTECHNISCH],
    })


_init_map()


def build_verfahrenstechnik_kodex(*, kodex_id: str = "verfahrenstechnik-kodex") -> VerfahrenstechnikKodex:
    parent = build_elektrotechnik_charta(charta_id=f"{kodex_id}-parent")
    eintraege: List[VerfahrenstechnikKodexEintrag] = []
    for g in VerfahrenstechnikKodexGeltung:
        eintraege.append(VerfahrenstechnikKodexEintrag(
            eintrag_id=f"{kodex_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            ing_weight=round(sum(n.ing_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            ing_tier=max(n.ing_tier for n in parent.normen) + _TIER_DELTA[g],
            ing_ids=[f"vk-{kodex_id}-{g.value}-001", f"vk-{kodex_id}-{g.value}-002"],
            ing_tags=["ing", "verfahrenstechnik", g.value],
        ))
    return VerfahrenstechnikKodex(kodex_id=kodex_id, eintraege=eintraege, parent=parent)
