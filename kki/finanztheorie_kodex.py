"""#724 — FinanztheorieKodex: Optionen, Portfolios & Risikobewertung."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.makrooekonomie_charta import MakrooekonomieCharta, build_makrooekonomie_charta


class FinanztheorieKodexGeltung(str, Enum):
    GESPERRT = "gesperrt"
    FINANZTHEORETISCH = "finanztheoretisch"
    GRUNDLEGEND_FINANZTHEORETISCH = "grundlegend-finanztheoretisch"


class FinanztheorieKodexTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class FinanztheorieKodexProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class FinanztheorieKodexEintrag:
    eintrag_id: str
    geltung: FinanztheorieKodexGeltung
    typ: FinanztheorieKodexTyp
    prozedur: FinanztheorieKodexProzedur
    wirt_weight: float
    wirt_tier: int
    wirt_ids: List[str]
    wirt_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class FinanztheorieKodex:
    kodex_id: str
    eintraege: List[FinanztheorieKodexEintrag]
    parent: MakrooekonomieCharta


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        FinanztheorieKodexGeltung.GESPERRT: 0.0,
        FinanztheorieKodexGeltung.FINANZTHEORETISCH: 0.05,
        FinanztheorieKodexGeltung.GRUNDLEGEND_FINANZTHEORETISCH: 0.1,
    })
    _TIER_DELTA.update({
        FinanztheorieKodexGeltung.GESPERRT: 0,
        FinanztheorieKodexGeltung.FINANZTHEORETISCH: 1,
        FinanztheorieKodexGeltung.GRUNDLEGEND_FINANZTHEORETISCH: 2,
    })
    _TYP_MAP.update({
        FinanztheorieKodexGeltung.GESPERRT: FinanztheorieKodexTyp.BEOBACHTUNG,
        FinanztheorieKodexGeltung.FINANZTHEORETISCH: FinanztheorieKodexTyp.ANALYSE,
        FinanztheorieKodexGeltung.GRUNDLEGEND_FINANZTHEORETISCH: FinanztheorieKodexTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        FinanztheorieKodexGeltung.GESPERRT: FinanztheorieKodexProzedur.INITIALISIEREN,
        FinanztheorieKodexGeltung.FINANZTHEORETISCH: FinanztheorieKodexProzedur.AKTIVIEREN,
        FinanztheorieKodexGeltung.GRUNDLEGEND_FINANZTHEORETISCH: FinanztheorieKodexProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        FinanztheorieKodexGeltung.GESPERRT: [FinanztheorieKodexGeltung.GESPERRT],
        FinanztheorieKodexGeltung.FINANZTHEORETISCH: [FinanztheorieKodexGeltung.FINANZTHEORETISCH],
        FinanztheorieKodexGeltung.GRUNDLEGEND_FINANZTHEORETISCH: [FinanztheorieKodexGeltung.GRUNDLEGEND_FINANZTHEORETISCH],
    })


_init_map()


def build_finanztheorie_kodex(*, kodex_id: str = "finanztheorie-kodex") -> FinanztheorieKodex:
    parent = build_makrooekonomie_charta(charta_id=f"{kodex_id}-parent")
    eintraege: List[FinanztheorieKodexEintrag] = []
    for g in FinanztheorieKodexGeltung:
        eintraege.append(FinanztheorieKodexEintrag(
            eintrag_id=f"{kodex_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            wirt_weight=round(sum(n.wirt_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            wirt_tier=max(n.wirt_tier for n in parent.normen) + _TIER_DELTA[g],
            wirt_ids=[f"fk-{kodex_id}-{g.value}-001", f"fk-{kodex_id}-{g.value}-002"],
            wirt_tags=["wirt", "finanztheorie", g.value],
        ))
    return FinanztheorieKodex(kodex_id=kodex_id, eintraege=eintraege, parent=parent)
