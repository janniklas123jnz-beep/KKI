"""#714 — KomplexitaetstheorieKodex: P vs NP, Komplexitätsklassen & Reduktionen."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.datenstrukturen_charta import DatenstrukturenCharta, build_datenstrukturen_charta


class KomplexitaetstheorieKodexGeltung(str, Enum):
    GESPERRT = "gesperrt"
    KOMPLEXITAETSTHEORETISCH = "komplexitaetstheoretisch"
    GRUNDLEGEND_KOMPLEXITAETSTHEORETISCH = "grundlegend-komplexitaetstheoretisch"


class KomplexitaetstheorieKodexTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class KomplexitaetstheorieKodexProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class KomplexitaetstheorieKodexEintrag:
    eintrag_id: str
    geltung: KomplexitaetstheorieKodexGeltung
    typ: KomplexitaetstheorieKodexTyp
    prozedur: KomplexitaetstheorieKodexProzedur
    info_weight: float
    info_tier: int
    info_ids: List[str]
    info_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class KomplexitaetstheorieKodex:
    kodex_id: str
    eintraege: List[KomplexitaetstheorieKodexEintrag]
    parent: DatenstrukturenCharta


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        KomplexitaetstheorieKodexGeltung.GESPERRT: 0.0,
        KomplexitaetstheorieKodexGeltung.KOMPLEXITAETSTHEORETISCH: 0.05,
        KomplexitaetstheorieKodexGeltung.GRUNDLEGEND_KOMPLEXITAETSTHEORETISCH: 0.1,
    })
    _TIER_DELTA.update({
        KomplexitaetstheorieKodexGeltung.GESPERRT: 0,
        KomplexitaetstheorieKodexGeltung.KOMPLEXITAETSTHEORETISCH: 1,
        KomplexitaetstheorieKodexGeltung.GRUNDLEGEND_KOMPLEXITAETSTHEORETISCH: 2,
    })
    _TYP_MAP.update({
        KomplexitaetstheorieKodexGeltung.GESPERRT: KomplexitaetstheorieKodexTyp.BEOBACHTUNG,
        KomplexitaetstheorieKodexGeltung.KOMPLEXITAETSTHEORETISCH: KomplexitaetstheorieKodexTyp.ANALYSE,
        KomplexitaetstheorieKodexGeltung.GRUNDLEGEND_KOMPLEXITAETSTHEORETISCH: KomplexitaetstheorieKodexTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        KomplexitaetstheorieKodexGeltung.GESPERRT: KomplexitaetstheorieKodexProzedur.INITIALISIEREN,
        KomplexitaetstheorieKodexGeltung.KOMPLEXITAETSTHEORETISCH: KomplexitaetstheorieKodexProzedur.AKTIVIEREN,
        KomplexitaetstheorieKodexGeltung.GRUNDLEGEND_KOMPLEXITAETSTHEORETISCH: KomplexitaetstheorieKodexProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        KomplexitaetstheorieKodexGeltung.GESPERRT: [KomplexitaetstheorieKodexGeltung.GESPERRT],
        KomplexitaetstheorieKodexGeltung.KOMPLEXITAETSTHEORETISCH: [KomplexitaetstheorieKodexGeltung.KOMPLEXITAETSTHEORETISCH],
        KomplexitaetstheorieKodexGeltung.GRUNDLEGEND_KOMPLEXITAETSTHEORETISCH: [KomplexitaetstheorieKodexGeltung.GRUNDLEGEND_KOMPLEXITAETSTHEORETISCH],
    })


_init_map()


def build_komplexitaetstheorie_kodex(*, kodex_id: str = "komplexitaetstheorie-kodex") -> KomplexitaetstheorieKodex:
    parent = build_datenstrukturen_charta(charta_id=f"{kodex_id}-parent")
    eintraege: List[KomplexitaetstheorieKodexEintrag] = []
    for g in KomplexitaetstheorieKodexGeltung:
        eintraege.append(KomplexitaetstheorieKodexEintrag(
            eintrag_id=f"{kodex_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            info_weight=round(sum(n.info_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            info_tier=max(n.info_tier for n in parent.normen) + _TIER_DELTA[g],
            info_ids=[f"kt-{kodex_id}-{g.value}-001", f"kt-{kodex_id}-{g.value}-002"],
            info_tags=["info", "komplexitaetstheorie", g.value],
        ))
    return KomplexitaetstheorieKodex(kodex_id=kodex_id, eintraege=eintraege, parent=parent)
