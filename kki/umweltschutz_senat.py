"""#667 UmweltschutzSenat — Umweltschutz & Nachhaltigkeitspolitik (parent: NahrungskettenPakt)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .nahrungsketten_pakt import NahrungskettenPakt, build_nahrungsketten_pakt

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class UmweltschutzSenatGeltung(str, Enum):
    GESPERRT = "gesperrt"
    UMWELTGESCHUETZT = "umweltgeschuetzt"
    GRUNDLEGEND_UMWELTGESCHUETZT = "grundlegend-umweltgeschuetzt"


class UmweltschutzSenatTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"
    SCHUTZ = "schutz"


class UmweltschutzSenatProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class UmweltschutzSenatNorm:
    umweltschutz_senat_id: str
    geltung: UmweltschutzSenatGeltung
    typ: UmweltschutzSenatTyp
    prozedur: UmweltschutzSenatProzedur
    oekologie_weight: float
    oekologie_tier: int
    oekologie_ids: List[str]
    oekologie_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class UmweltschutzSenat:
    senat_id: str
    normen: List[UmweltschutzSenatNorm]
    parent: NahrungskettenPakt


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        UmweltschutzSenatGeltung.GESPERRT: 0.0,
        UmweltschutzSenatGeltung.UMWELTGESCHUETZT: 0.05,
        UmweltschutzSenatGeltung.GRUNDLEGEND_UMWELTGESCHUETZT: 0.1,
    })
    _TIER_DELTA.update({
        UmweltschutzSenatGeltung.GESPERRT: 0,
        UmweltschutzSenatGeltung.UMWELTGESCHUETZT: 1,
        UmweltschutzSenatGeltung.GRUNDLEGEND_UMWELTGESCHUETZT: 2,
    })
    _TYP_MAP.update({
        UmweltschutzSenatGeltung.GESPERRT: UmweltschutzSenatTyp.BEOBACHTUNG,
        UmweltschutzSenatGeltung.UMWELTGESCHUETZT: UmweltschutzSenatTyp.ANALYSE,
        UmweltschutzSenatGeltung.GRUNDLEGEND_UMWELTGESCHUETZT: UmweltschutzSenatTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        UmweltschutzSenatGeltung.GESPERRT: UmweltschutzSenatProzedur.INITIALISIEREN,
        UmweltschutzSenatGeltung.UMWELTGESCHUETZT: UmweltschutzSenatProzedur.AKTIVIEREN,
        UmweltschutzSenatGeltung.GRUNDLEGEND_UMWELTGESCHUETZT: UmweltschutzSenatProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        UmweltschutzSenatGeltung.GESPERRT: [UmweltschutzSenatGeltung.GESPERRT],
        UmweltschutzSenatGeltung.UMWELTGESCHUETZT: [UmweltschutzSenatGeltung.UMWELTGESCHUETZT],
        UmweltschutzSenatGeltung.GRUNDLEGEND_UMWELTGESCHUETZT: [UmweltschutzSenatGeltung.GRUNDLEGEND_UMWELTGESCHUETZT],
    })


_init_map()


def build_umweltschutz_senat(*, senat_id: str = "umweltschutz-senat") -> UmweltschutzSenat:
    parent = build_nahrungsketten_pakt(pakt_id=f"{senat_id}-parent")
    normen: List[UmweltschutzSenatNorm] = []
    for g in UmweltschutzSenatGeltung:
        normen.append(UmweltschutzSenatNorm(
            umweltschutz_senat_id=f"{senat_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            oekologie_weight=round(sum(e.oekologie_weight for e in parent.eintraege) * (1.0 + _WEIGHT_DELTA[g]), 4),
            oekologie_tier=max(e.oekologie_tier for e in parent.eintraege) + _TIER_DELTA[g],
            oekologie_ids=[f"us-{senat_id}-{g.value}-001", f"us-{senat_id}-{g.value}-002"],
            oekologie_tags=["oekologie", "umweltschutz", "senat", g.value],
        ))
    return UmweltschutzSenat(senat_id=senat_id, normen=normen, parent=parent)
