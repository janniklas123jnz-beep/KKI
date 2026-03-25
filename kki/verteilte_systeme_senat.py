"""#717 — VerteilteSystemeSenat: Konsensus, CAP-Theorem & Fehlertoleranz."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.programmierparadigmen_pakt import ProgrammierparadigmenPakt, build_programmierparadigmen_pakt


class VerteilteSystemeSenatGeltung(str, Enum):
    GESPERRT = "gesperrt"
    VERTEILT_AKTIV = "verteilt-aktiv"
    GRUNDLEGEND_VERTEILT_AKTIV = "grundlegend-verteilt-aktiv"


class VerteilteSystemeSenatTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class VerteilteSystemeSenatProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class VerteilteSystemeSenatNorm:
    senat_id: str
    geltung: VerteilteSystemeSenatGeltung
    typ: VerteilteSystemeSenatTyp
    prozedur: VerteilteSystemeSenatProzedur
    info_weight: float
    info_tier: int
    info_ids: List[str]
    info_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class VerteilteSystemeSenat:
    senat_id: str
    normen: List[VerteilteSystemeSenatNorm]
    parent: ProgrammierparadigmenPakt


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        VerteilteSystemeSenatGeltung.GESPERRT: 0.0,
        VerteilteSystemeSenatGeltung.VERTEILT_AKTIV: 0.05,
        VerteilteSystemeSenatGeltung.GRUNDLEGEND_VERTEILT_AKTIV: 0.1,
    })
    _TIER_DELTA.update({
        VerteilteSystemeSenatGeltung.GESPERRT: 0,
        VerteilteSystemeSenatGeltung.VERTEILT_AKTIV: 1,
        VerteilteSystemeSenatGeltung.GRUNDLEGEND_VERTEILT_AKTIV: 2,
    })
    _TYP_MAP.update({
        VerteilteSystemeSenatGeltung.GESPERRT: VerteilteSystemeSenatTyp.BEOBACHTUNG,
        VerteilteSystemeSenatGeltung.VERTEILT_AKTIV: VerteilteSystemeSenatTyp.ANALYSE,
        VerteilteSystemeSenatGeltung.GRUNDLEGEND_VERTEILT_AKTIV: VerteilteSystemeSenatTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        VerteilteSystemeSenatGeltung.GESPERRT: VerteilteSystemeSenatProzedur.INITIALISIEREN,
        VerteilteSystemeSenatGeltung.VERTEILT_AKTIV: VerteilteSystemeSenatProzedur.AKTIVIEREN,
        VerteilteSystemeSenatGeltung.GRUNDLEGEND_VERTEILT_AKTIV: VerteilteSystemeSenatProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        VerteilteSystemeSenatGeltung.GESPERRT: [VerteilteSystemeSenatGeltung.GESPERRT],
        VerteilteSystemeSenatGeltung.VERTEILT_AKTIV: [VerteilteSystemeSenatGeltung.VERTEILT_AKTIV],
        VerteilteSystemeSenatGeltung.GRUNDLEGEND_VERTEILT_AKTIV: [VerteilteSystemeSenatGeltung.GRUNDLEGEND_VERTEILT_AKTIV],
    })


_init_map()


def build_verteilte_systeme_senat(*, senat_id: str = "verteilte-systeme-senat") -> VerteilteSystemeSenat:
    parent = build_programmierparadigmen_pakt(pakt_id=f"{senat_id}-parent")
    normen: List[VerteilteSystemeSenatNorm] = []
    for g in VerteilteSystemeSenatGeltung:
        normen.append(VerteilteSystemeSenatNorm(
            senat_id=f"{senat_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            info_weight=round(sum(e.info_weight for e in parent.eintraege) * (1.0 + _WEIGHT_DELTA[g]), 4),
            info_tier=max(e.info_tier for e in parent.eintraege) + _TIER_DELTA[g],
            info_ids=[f"vs-{senat_id}-{g.value}-001", f"vs-{senat_id}-{g.value}-002"],
            info_tags=["info", "verteilte-systeme", g.value],
        ))
    return VerteilteSystemeSenat(senat_id=senat_id, normen=normen, parent=parent)
