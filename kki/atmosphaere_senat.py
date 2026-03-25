"""#697 — AtmosphaereSenat: Atmosphärenschichten, Wetterdynamik & Klimasystem."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.ozeanographie_pakt import OzeanographiePakt, build_ozeanographie_pakt


class AtmosphaereSenatGeltung(str, Enum):
    GESPERRT = "gesperrt"
    ATMOSPHAERISCH_AKTIV = "atmosphaerisch-aktiv"
    GRUNDLEGEND_ATMOSPHAERISCH_AKTIV = "grundlegend-atmosphaerisch-aktiv"


class AtmosphaereSenatTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class AtmosphaereSenatProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class AtmosphaereSenatNorm:
    norm_id: str
    geltung: AtmosphaereSenatGeltung
    typ: AtmosphaereSenatTyp
    prozedur: AtmosphaereSenatProzedur
    geo_weight: float
    geo_tier: int
    geo_ids: List[str]
    geo_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class AtmosphaereSenat:
    senat_id: str
    normen: List[AtmosphaereSenatNorm]
    parent: OzeanographiePakt


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        AtmosphaereSenatGeltung.GESPERRT: 0.0,
        AtmosphaereSenatGeltung.ATMOSPHAERISCH_AKTIV: 0.05,
        AtmosphaereSenatGeltung.GRUNDLEGEND_ATMOSPHAERISCH_AKTIV: 0.1,
    })
    _TIER_DELTA.update({
        AtmosphaereSenatGeltung.GESPERRT: 0,
        AtmosphaereSenatGeltung.ATMOSPHAERISCH_AKTIV: 1,
        AtmosphaereSenatGeltung.GRUNDLEGEND_ATMOSPHAERISCH_AKTIV: 2,
    })
    _TYP_MAP.update({
        AtmosphaereSenatGeltung.GESPERRT: AtmosphaereSenatTyp.BEOBACHTUNG,
        AtmosphaereSenatGeltung.ATMOSPHAERISCH_AKTIV: AtmosphaereSenatTyp.ANALYSE,
        AtmosphaereSenatGeltung.GRUNDLEGEND_ATMOSPHAERISCH_AKTIV: AtmosphaereSenatTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        AtmosphaereSenatGeltung.GESPERRT: AtmosphaereSenatProzedur.INITIALISIEREN,
        AtmosphaereSenatGeltung.ATMOSPHAERISCH_AKTIV: AtmosphaereSenatProzedur.AKTIVIEREN,
        AtmosphaereSenatGeltung.GRUNDLEGEND_ATMOSPHAERISCH_AKTIV: AtmosphaereSenatProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        AtmosphaereSenatGeltung.GESPERRT: [AtmosphaereSenatGeltung.GESPERRT],
        AtmosphaereSenatGeltung.ATMOSPHAERISCH_AKTIV: [AtmosphaereSenatGeltung.ATMOSPHAERISCH_AKTIV],
        AtmosphaereSenatGeltung.GRUNDLEGEND_ATMOSPHAERISCH_AKTIV: [AtmosphaereSenatGeltung.GRUNDLEGEND_ATMOSPHAERISCH_AKTIV],
    })


_init_map()


def build_atmosphaere_senat(*, senat_id: str = "atmosphaere-senat") -> AtmosphaereSenat:
    parent = build_ozeanographie_pakt(pakt_id=f"{senat_id}-parent")
    normen: List[AtmosphaereSenatNorm] = []
    for g in AtmosphaereSenatGeltung:
        normen.append(AtmosphaereSenatNorm(
            norm_id=f"{senat_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            geo_weight=round(sum(e.geo_weight for e in parent.eintraege) * (1.0 + _WEIGHT_DELTA[g]), 4),
            geo_tier=max(e.geo_tier for e in parent.eintraege) + _TIER_DELTA[g],
            geo_ids=[f"as-{senat_id}-{g.value}-001", f"as-{senat_id}-{g.value}-002"],
            geo_tags=["geo", "atmosphaere", g.value],
        ))
    return AtmosphaereSenat(senat_id=senat_id, normen=normen, parent=parent)
