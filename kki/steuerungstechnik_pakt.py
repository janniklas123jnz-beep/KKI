"""#736 — SteuerungstechnikPakt: Regelkreise, PID-Regler & Automatisierung."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.strukturtechnik_manifest import StrukturtechnikManifest, build_strukturtechnik_manifest


class SteuerungstechnikPaktGeltung(str, Enum):
    GESPERRT = "gesperrt"
    STEUERUNGSTECHNISCH = "steuerungstechnisch"
    GRUNDLEGEND_STEUERUNGSTECHNISCH = "grundlegend-steuerungstechnisch"


class SteuerungstechnikPaktTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class SteuerungstechnikPaktProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class SteuerungstechnikPaktEintrag:
    eintrag_id: str
    geltung: SteuerungstechnikPaktGeltung
    typ: SteuerungstechnikPaktTyp
    prozedur: SteuerungstechnikPaktProzedur
    ing_weight: float
    ing_tier: int
    ing_ids: List[str]
    ing_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class SteuerungstechnikPakt:
    pakt_id: str
    eintraege: List[SteuerungstechnikPaktEintrag]
    parent: StrukturtechnikManifest


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        SteuerungstechnikPaktGeltung.GESPERRT: 0.0,
        SteuerungstechnikPaktGeltung.STEUERUNGSTECHNISCH: 0.05,
        SteuerungstechnikPaktGeltung.GRUNDLEGEND_STEUERUNGSTECHNISCH: 0.1,
    })
    _TIER_DELTA.update({
        SteuerungstechnikPaktGeltung.GESPERRT: 0,
        SteuerungstechnikPaktGeltung.STEUERUNGSTECHNISCH: 1,
        SteuerungstechnikPaktGeltung.GRUNDLEGEND_STEUERUNGSTECHNISCH: 2,
    })
    _TYP_MAP.update({
        SteuerungstechnikPaktGeltung.GESPERRT: SteuerungstechnikPaktTyp.BEOBACHTUNG,
        SteuerungstechnikPaktGeltung.STEUERUNGSTECHNISCH: SteuerungstechnikPaktTyp.ANALYSE,
        SteuerungstechnikPaktGeltung.GRUNDLEGEND_STEUERUNGSTECHNISCH: SteuerungstechnikPaktTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        SteuerungstechnikPaktGeltung.GESPERRT: SteuerungstechnikPaktProzedur.INITIALISIEREN,
        SteuerungstechnikPaktGeltung.STEUERUNGSTECHNISCH: SteuerungstechnikPaktProzedur.AKTIVIEREN,
        SteuerungstechnikPaktGeltung.GRUNDLEGEND_STEUERUNGSTECHNISCH: SteuerungstechnikPaktProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        SteuerungstechnikPaktGeltung.GESPERRT: [SteuerungstechnikPaktGeltung.GESPERRT],
        SteuerungstechnikPaktGeltung.STEUERUNGSTECHNISCH: [SteuerungstechnikPaktGeltung.STEUERUNGSTECHNISCH],
        SteuerungstechnikPaktGeltung.GRUNDLEGEND_STEUERUNGSTECHNISCH: [SteuerungstechnikPaktGeltung.GRUNDLEGEND_STEUERUNGSTECHNISCH],
    })


_init_map()


def build_steuerungstechnik_pakt(*, pakt_id: str = "steuerungstechnik-pakt") -> SteuerungstechnikPakt:
    parent = build_strukturtechnik_manifest(manifest_id=f"{pakt_id}-parent")
    eintraege: List[SteuerungstechnikPaktEintrag] = []
    for g in SteuerungstechnikPaktGeltung:
        eintraege.append(SteuerungstechnikPaktEintrag(
            eintrag_id=f"{pakt_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            ing_weight=round(sum(n.ing_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            ing_tier=max(n.ing_tier for n in parent.normen) + _TIER_DELTA[g],
            ing_ids=[f"sp-{pakt_id}-{g.value}-001", f"sp-{pakt_id}-{g.value}-002"],
            ing_tags=["ing", "steuerungstechnik", g.value],
        ))
    return SteuerungstechnikPakt(pakt_id=pakt_id, eintraege=eintraege, parent=parent)
