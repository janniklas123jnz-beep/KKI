"""#727 — InternationaleWirtschaftSenat: Welthandel, WTO & Währungssysteme."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.verhaltensoekonomie_pakt import VerhaltensoekonomiePakt, build_verhaltensoekonomie_pakt


class InternationaleWirtschaftSenatGeltung(str, Enum):
    GESPERRT = "gesperrt"
    INTERNATIONAL_AKTIV = "international-aktiv"
    GRUNDLEGEND_INTERNATIONAL_AKTIV = "grundlegend-international-aktiv"


class InternationaleWirtschaftSenatTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class InternationaleWirtschaftSenatProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class InternationaleWirtschaftSenatNorm:
    senat_id: str
    geltung: InternationaleWirtschaftSenatGeltung
    typ: InternationaleWirtschaftSenatTyp
    prozedur: InternationaleWirtschaftSenatProzedur
    wirt_weight: float
    wirt_tier: int
    wirt_ids: List[str]
    wirt_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class InternationaleWirtschaftSenat:
    senat_id: str
    normen: List[InternationaleWirtschaftSenatNorm]
    parent: VerhaltensoekonomiePakt


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        InternationaleWirtschaftSenatGeltung.GESPERRT: 0.0,
        InternationaleWirtschaftSenatGeltung.INTERNATIONAL_AKTIV: 0.05,
        InternationaleWirtschaftSenatGeltung.GRUNDLEGEND_INTERNATIONAL_AKTIV: 0.1,
    })
    _TIER_DELTA.update({
        InternationaleWirtschaftSenatGeltung.GESPERRT: 0,
        InternationaleWirtschaftSenatGeltung.INTERNATIONAL_AKTIV: 1,
        InternationaleWirtschaftSenatGeltung.GRUNDLEGEND_INTERNATIONAL_AKTIV: 2,
    })
    _TYP_MAP.update({
        InternationaleWirtschaftSenatGeltung.GESPERRT: InternationaleWirtschaftSenatTyp.BEOBACHTUNG,
        InternationaleWirtschaftSenatGeltung.INTERNATIONAL_AKTIV: InternationaleWirtschaftSenatTyp.ANALYSE,
        InternationaleWirtschaftSenatGeltung.GRUNDLEGEND_INTERNATIONAL_AKTIV: InternationaleWirtschaftSenatTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        InternationaleWirtschaftSenatGeltung.GESPERRT: InternationaleWirtschaftSenatProzedur.INITIALISIEREN,
        InternationaleWirtschaftSenatGeltung.INTERNATIONAL_AKTIV: InternationaleWirtschaftSenatProzedur.AKTIVIEREN,
        InternationaleWirtschaftSenatGeltung.GRUNDLEGEND_INTERNATIONAL_AKTIV: InternationaleWirtschaftSenatProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        InternationaleWirtschaftSenatGeltung.GESPERRT: [InternationaleWirtschaftSenatGeltung.GESPERRT],
        InternationaleWirtschaftSenatGeltung.INTERNATIONAL_AKTIV: [InternationaleWirtschaftSenatGeltung.INTERNATIONAL_AKTIV],
        InternationaleWirtschaftSenatGeltung.GRUNDLEGEND_INTERNATIONAL_AKTIV: [InternationaleWirtschaftSenatGeltung.GRUNDLEGEND_INTERNATIONAL_AKTIV],
    })


_init_map()


def build_internationale_wirtschaft_senat(*, senat_id: str = "internationale-wirtschaft-senat") -> InternationaleWirtschaftSenat:
    parent = build_verhaltensoekonomie_pakt(pakt_id=f"{senat_id}-parent")
    normen: List[InternationaleWirtschaftSenatNorm] = []
    for g in InternationaleWirtschaftSenatGeltung:
        normen.append(InternationaleWirtschaftSenatNorm(
            senat_id=f"{senat_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            wirt_weight=round(sum(e.wirt_weight for e in parent.eintraege) * (1.0 + _WEIGHT_DELTA[g]), 4),
            wirt_tier=max(e.wirt_tier for e in parent.eintraege) + _TIER_DELTA[g],
            wirt_ids=[f"iws-{senat_id}-{g.value}-001", f"iws-{senat_id}-{g.value}-002"],
            wirt_tags=["wirt", "internationale-wirtschaft", g.value],
        ))
    return InternationaleWirtschaftSenat(senat_id=senat_id, normen=normen, parent=parent)
