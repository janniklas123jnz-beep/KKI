"""#656 RecherchePakt — Recherche-Koordination & Wissensintegration (parent: InformationsextraktorManifest)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .informationsextraktor_manifest import InformationsextraktorManifest, build_informationsextraktor_manifest

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class RecherchePaktGeltung(str, Enum):
    GESPERRT = "gesperrt"
    RECHERCHIERT = "recherchiert"
    GRUNDLEGEND_RECHERCHIERT = "grundlegend-recherchiert"


class RecherchePaktTyp(str, Enum):
    RECHERCHE = "recherche"
    VALIDIERUNG = "validierung"
    AGGREGATION = "aggregation"
    AUTONOME_ENTDECKUNG = "autonome-entdeckung"


class RecherchePaktProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class RecherchePaktEintrag:
    pakt_id: str
    geltung: RecherchePaktGeltung
    typ: RecherchePaktTyp
    prozedur: RecherchePaktProzedur
    internet_weight: float
    internet_tier: int
    internet_ids: List[str]
    internet_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class RecherchePakt:
    pakt_id: str
    eintraege: List[RecherchePaktEintrag]
    parent: InformationsextraktorManifest


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        RecherchePaktGeltung.GESPERRT: 0.0,
        RecherchePaktGeltung.RECHERCHIERT: 0.05,
        RecherchePaktGeltung.GRUNDLEGEND_RECHERCHIERT: 0.1,
    })
    _TIER_DELTA.update({
        RecherchePaktGeltung.GESPERRT: 0,
        RecherchePaktGeltung.RECHERCHIERT: 1,
        RecherchePaktGeltung.GRUNDLEGEND_RECHERCHIERT: 2,
    })
    _TYP_MAP.update({
        RecherchePaktGeltung.GESPERRT: RecherchePaktTyp.RECHERCHE,
        RecherchePaktGeltung.RECHERCHIERT: RecherchePaktTyp.VALIDIERUNG,
        RecherchePaktGeltung.GRUNDLEGEND_RECHERCHIERT: RecherchePaktTyp.AGGREGATION,
    })
    _PROZEDUR_MAP.update({
        RecherchePaktGeltung.GESPERRT: RecherchePaktProzedur.INITIALISIEREN,
        RecherchePaktGeltung.RECHERCHIERT: RecherchePaktProzedur.AKTIVIEREN,
        RecherchePaktGeltung.GRUNDLEGEND_RECHERCHIERT: RecherchePaktProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        RecherchePaktGeltung.GESPERRT: [RecherchePaktGeltung.GESPERRT],
        RecherchePaktGeltung.RECHERCHIERT: [RecherchePaktGeltung.RECHERCHIERT],
        RecherchePaktGeltung.GRUNDLEGEND_RECHERCHIERT: [RecherchePaktGeltung.GRUNDLEGEND_RECHERCHIERT],
    })


_init_map()


def build_recherche_pakt(*, pakt_id: str = "recherche-pakt") -> RecherchePakt:
    parent = build_informationsextraktor_manifest(manifest_id=f"{pakt_id}-parent")
    eintraege: List[RecherchePaktEintrag] = []
    for g in RecherchePaktGeltung:
        eintraege.append(RecherchePaktEintrag(
            pakt_id=f"{pakt_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            internet_weight=round(sum(n.internet_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            internet_tier=max(n.internet_tier for n in parent.normen) + _TIER_DELTA[g],
            internet_ids=[f"rp-{pakt_id}-{g.value}-001", f"rp-{pakt_id}-{g.value}-002"],
            internet_tags=["internet", "recherche", g.value],
        ))
    return RecherchePakt(pakt_id=pakt_id, eintraege=eintraege, parent=parent)
