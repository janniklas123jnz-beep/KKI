"""#646 TherapiePakt — Therapie & Behandlungsmethoden (parent: DiagnostikManifest)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .diagnostik_manifest import DiagnostikManifest, build_diagnostik_manifest

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class TherapiePaktGeltung(str, Enum):
    GESPERRT = "gesperrt"
    THERAPEUTISCH = "therapeutisch"
    GRUNDLEGEND_THERAPEUTISCH = "grundlegend-therapeutisch"


class TherapiePaktTyp(str, Enum):
    KLINISCH = "klinisch"
    THEORETISCH = "theoretisch"
    ANGEWANDT = "angewandt"
    PRAEVENTIV = "praeventiv"


class TherapiePaktProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class TherapiePaktEintrag:
    pakt_id: str
    geltung: TherapiePaktGeltung
    typ: TherapiePaktTyp
    prozedur: TherapiePaktProzedur
    medizin_weight: float
    medizin_tier: int
    medizin_ids: List[str]
    medizin_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class TherapiePakt:
    pakt_id: str
    eintraege: List[TherapiePaktEintrag]
    parent: DiagnostikManifest


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        TherapiePaktGeltung.GESPERRT: 0.0,
        TherapiePaktGeltung.THERAPEUTISCH: 0.05,
        TherapiePaktGeltung.GRUNDLEGEND_THERAPEUTISCH: 0.1,
    })
    _TIER_DELTA.update({
        TherapiePaktGeltung.GESPERRT: 0,
        TherapiePaktGeltung.THERAPEUTISCH: 1,
        TherapiePaktGeltung.GRUNDLEGEND_THERAPEUTISCH: 2,
    })
    _TYP_MAP.update({
        TherapiePaktGeltung.GESPERRT: TherapiePaktTyp.KLINISCH,
        TherapiePaktGeltung.THERAPEUTISCH: TherapiePaktTyp.THEORETISCH,
        TherapiePaktGeltung.GRUNDLEGEND_THERAPEUTISCH: TherapiePaktTyp.ANGEWANDT,
    })
    _PROZEDUR_MAP.update({
        TherapiePaktGeltung.GESPERRT: TherapiePaktProzedur.INITIALISIEREN,
        TherapiePaktGeltung.THERAPEUTISCH: TherapiePaktProzedur.AKTIVIEREN,
        TherapiePaktGeltung.GRUNDLEGEND_THERAPEUTISCH: TherapiePaktProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        TherapiePaktGeltung.GESPERRT: [TherapiePaktGeltung.GESPERRT],
        TherapiePaktGeltung.THERAPEUTISCH: [TherapiePaktGeltung.THERAPEUTISCH],
        TherapiePaktGeltung.GRUNDLEGEND_THERAPEUTISCH: [TherapiePaktGeltung.GRUNDLEGEND_THERAPEUTISCH],
    })


_init_map()


def build_therapie_pakt(*, pakt_id: str = "therapie-pakt") -> TherapiePakt:
    parent = build_diagnostik_manifest(manifest_id=f"{pakt_id}-parent")
    eintraege: List[TherapiePaktEintrag] = []
    for g in TherapiePaktGeltung:
        eintraege.append(TherapiePaktEintrag(
            pakt_id=f"{pakt_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            medizin_weight=round(sum(n.medizin_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            medizin_tier=max(n.medizin_tier for n in parent.normen) + _TIER_DELTA[g],
            medizin_ids=[f"tp-{pakt_id}-{g.value}-001", f"tp-{pakt_id}-{g.value}-002"],
            medizin_tags=["medizin", "therapie", g.value],
        ))
    return TherapiePakt(pakt_id=pakt_id, eintraege=eintraege, parent=parent)
