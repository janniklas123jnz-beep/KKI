"""#694 — TektonikKodex: Plattentektonik, Erdbebenforschung & Gebirgsbildung."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.gesteins_charta import GesteinsCharta, build_gesteins_charta


class TektonikKodexGeltung(str, Enum):
    GESPERRT = "gesperrt"
    TEKTONISCH_AKTIV = "tektonisch-aktiv"
    GRUNDLEGEND_TEKTONISCH_AKTIV = "grundlegend-tektonisch-aktiv"


class TektonikKodexTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class TektonikKodexProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class TektonikKodexEintrag:
    eintrag_id: str
    geltung: TektonikKodexGeltung
    typ: TektonikKodexTyp
    prozedur: TektonikKodexProzedur
    geo_weight: float
    geo_tier: int
    geo_ids: List[str]
    geo_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class TektonikKodex:
    kodex_id: str
    eintraege: List[TektonikKodexEintrag]
    parent: GesteinsCharta


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        TektonikKodexGeltung.GESPERRT: 0.0,
        TektonikKodexGeltung.TEKTONISCH_AKTIV: 0.05,
        TektonikKodexGeltung.GRUNDLEGEND_TEKTONISCH_AKTIV: 0.1,
    })
    _TIER_DELTA.update({
        TektonikKodexGeltung.GESPERRT: 0,
        TektonikKodexGeltung.TEKTONISCH_AKTIV: 1,
        TektonikKodexGeltung.GRUNDLEGEND_TEKTONISCH_AKTIV: 2,
    })
    _TYP_MAP.update({
        TektonikKodexGeltung.GESPERRT: TektonikKodexTyp.BEOBACHTUNG,
        TektonikKodexGeltung.TEKTONISCH_AKTIV: TektonikKodexTyp.ANALYSE,
        TektonikKodexGeltung.GRUNDLEGEND_TEKTONISCH_AKTIV: TektonikKodexTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        TektonikKodexGeltung.GESPERRT: TektonikKodexProzedur.INITIALISIEREN,
        TektonikKodexGeltung.TEKTONISCH_AKTIV: TektonikKodexProzedur.AKTIVIEREN,
        TektonikKodexGeltung.GRUNDLEGEND_TEKTONISCH_AKTIV: TektonikKodexProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        TektonikKodexGeltung.GESPERRT: [TektonikKodexGeltung.GESPERRT],
        TektonikKodexGeltung.TEKTONISCH_AKTIV: [TektonikKodexGeltung.TEKTONISCH_AKTIV],
        TektonikKodexGeltung.GRUNDLEGEND_TEKTONISCH_AKTIV: [TektonikKodexGeltung.GRUNDLEGEND_TEKTONISCH_AKTIV],
    })


_init_map()


def build_tektonik_kodex(*, kodex_id: str = "tektonik-kodex") -> TektonikKodex:
    parent = build_gesteins_charta(charta_id=f"{kodex_id}-parent")
    eintraege: List[TektonikKodexEintrag] = []
    for g in TektonikKodexGeltung:
        eintraege.append(TektonikKodexEintrag(
            eintrag_id=f"{kodex_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            geo_weight=round(sum(n.geo_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            geo_tier=max(n.geo_tier for n in parent.normen) + _TIER_DELTA[g],
            geo_ids=[f"tk-{kodex_id}-{g.value}-001", f"tk-{kodex_id}-{g.value}-002"],
            geo_tags=["geo", "tektonik", g.value],
        ))
    return TektonikKodex(kodex_id=kodex_id, eintraege=eintraege, parent=parent)
