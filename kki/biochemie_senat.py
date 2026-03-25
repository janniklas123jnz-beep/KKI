"""#677 BiochemieSenat — Biochemie & Molekularbiologie (parent: OrganischeChemiePakt)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .organische_chemie_pakt import OrganischeChemiePakt, build_organische_chemie_pakt

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class BiochemieSenatGeltung(str, Enum):
    GESPERRT = "gesperrt"
    BIOCHEMISCH_AKTIV = "biochemisch-aktiv"
    GRUNDLEGEND_BIOCHEMISCH_AKTIV = "grundlegend-biochemisch-aktiv"


class BiochemieSenatTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"
    KATALYSE = "katalyse"


class BiochemieSenatProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class BiochemieSenatNorm:
    biochemie_senat_id: str
    geltung: BiochemieSenatGeltung
    typ: BiochemieSenatTyp
    prozedur: BiochemieSenatProzedur
    chemie_weight: float
    chemie_tier: int
    chemie_ids: List[str]
    chemie_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class BiochemieSenat:
    senat_id: str
    normen: List[BiochemieSenatNorm]
    parent: OrganischeChemiePakt


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        BiochemieSenatGeltung.GESPERRT: 0.0,
        BiochemieSenatGeltung.BIOCHEMISCH_AKTIV: 0.05,
        BiochemieSenatGeltung.GRUNDLEGEND_BIOCHEMISCH_AKTIV: 0.1,
    })
    _TIER_DELTA.update({
        BiochemieSenatGeltung.GESPERRT: 0,
        BiochemieSenatGeltung.BIOCHEMISCH_AKTIV: 1,
        BiochemieSenatGeltung.GRUNDLEGEND_BIOCHEMISCH_AKTIV: 2,
    })
    _TYP_MAP.update({
        BiochemieSenatGeltung.GESPERRT: BiochemieSenatTyp.BEOBACHTUNG,
        BiochemieSenatGeltung.BIOCHEMISCH_AKTIV: BiochemieSenatTyp.ANALYSE,
        BiochemieSenatGeltung.GRUNDLEGEND_BIOCHEMISCH_AKTIV: BiochemieSenatTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        BiochemieSenatGeltung.GESPERRT: BiochemieSenatProzedur.INITIALISIEREN,
        BiochemieSenatGeltung.BIOCHEMISCH_AKTIV: BiochemieSenatProzedur.AKTIVIEREN,
        BiochemieSenatGeltung.GRUNDLEGEND_BIOCHEMISCH_AKTIV: BiochemieSenatProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        BiochemieSenatGeltung.GESPERRT: [BiochemieSenatGeltung.GESPERRT],
        BiochemieSenatGeltung.BIOCHEMISCH_AKTIV: [BiochemieSenatGeltung.BIOCHEMISCH_AKTIV],
        BiochemieSenatGeltung.GRUNDLEGEND_BIOCHEMISCH_AKTIV: [BiochemieSenatGeltung.GRUNDLEGEND_BIOCHEMISCH_AKTIV],
    })


_init_map()


def build_biochemie_senat(*, senat_id: str = "biochemie-senat") -> BiochemieSenat:
    parent = build_organische_chemie_pakt(pakt_id=f"{senat_id}-parent")
    normen: List[BiochemieSenatNorm] = []
    for g in BiochemieSenatGeltung:
        normen.append(BiochemieSenatNorm(
            biochemie_senat_id=f"{senat_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            chemie_weight=round(sum(e.chemie_weight for e in parent.eintraege) * (1.0 + _WEIGHT_DELTA[g]), 4),
            chemie_tier=max(e.chemie_tier for e in parent.eintraege) + _TIER_DELTA[g],
            chemie_ids=[f"bs-{senat_id}-{g.value}-001", f"bs-{senat_id}-{g.value}-002"],
            chemie_tags=["chemie", "biochemie", "senat", g.value],
        ))
    return BiochemieSenat(senat_id=senat_id, normen=normen, parent=parent)
