"""#716 — ProgrammierparadigmenPakt: OOP, Funktional, Logisch & Reaktiv."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.berechnungstheorie_manifest import BerechnungstheorieManifest, build_berechnungstheorie_manifest


class ProgrammierparadigmenPaktGeltung(str, Enum):
    GESPERRT = "gesperrt"
    PARADIGMATISCH = "paradigmatisch"
    GRUNDLEGEND_PARADIGMATISCH = "grundlegend-paradigmatisch"


class ProgrammierparadigmenPaktTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class ProgrammierparadigmenPaktProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class ProgrammierparadigmenPaktEintrag:
    eintrag_id: str
    geltung: ProgrammierparadigmenPaktGeltung
    typ: ProgrammierparadigmenPaktTyp
    prozedur: ProgrammierparadigmenPaktProzedur
    info_weight: float
    info_tier: int
    info_ids: List[str]
    info_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class ProgrammierparadigmenPakt:
    pakt_id: str
    eintraege: List[ProgrammierparadigmenPaktEintrag]
    parent: BerechnungstheorieManifest


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        ProgrammierparadigmenPaktGeltung.GESPERRT: 0.0,
        ProgrammierparadigmenPaktGeltung.PARADIGMATISCH: 0.05,
        ProgrammierparadigmenPaktGeltung.GRUNDLEGEND_PARADIGMATISCH: 0.1,
    })
    _TIER_DELTA.update({
        ProgrammierparadigmenPaktGeltung.GESPERRT: 0,
        ProgrammierparadigmenPaktGeltung.PARADIGMATISCH: 1,
        ProgrammierparadigmenPaktGeltung.GRUNDLEGEND_PARADIGMATISCH: 2,
    })
    _TYP_MAP.update({
        ProgrammierparadigmenPaktGeltung.GESPERRT: ProgrammierparadigmenPaktTyp.BEOBACHTUNG,
        ProgrammierparadigmenPaktGeltung.PARADIGMATISCH: ProgrammierparadigmenPaktTyp.ANALYSE,
        ProgrammierparadigmenPaktGeltung.GRUNDLEGEND_PARADIGMATISCH: ProgrammierparadigmenPaktTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        ProgrammierparadigmenPaktGeltung.GESPERRT: ProgrammierparadigmenPaktProzedur.INITIALISIEREN,
        ProgrammierparadigmenPaktGeltung.PARADIGMATISCH: ProgrammierparadigmenPaktProzedur.AKTIVIEREN,
        ProgrammierparadigmenPaktGeltung.GRUNDLEGEND_PARADIGMATISCH: ProgrammierparadigmenPaktProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        ProgrammierparadigmenPaktGeltung.GESPERRT: [ProgrammierparadigmenPaktGeltung.GESPERRT],
        ProgrammierparadigmenPaktGeltung.PARADIGMATISCH: [ProgrammierparadigmenPaktGeltung.PARADIGMATISCH],
        ProgrammierparadigmenPaktGeltung.GRUNDLEGEND_PARADIGMATISCH: [ProgrammierparadigmenPaktGeltung.GRUNDLEGEND_PARADIGMATISCH],
    })


_init_map()


def build_programmierparadigmen_pakt(*, pakt_id: str = "programmierparadigmen-pakt") -> ProgrammierparadigmenPakt:
    parent = build_berechnungstheorie_manifest(manifest_id=f"{pakt_id}-parent")
    eintraege: List[ProgrammierparadigmenPaktEintrag] = []
    for g in ProgrammierparadigmenPaktGeltung:
        eintraege.append(ProgrammierparadigmenPaktEintrag(
            eintrag_id=f"{pakt_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            info_weight=round(sum(n.info_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            info_tier=max(n.info_tier for n in parent.normen) + _TIER_DELTA[g],
            info_ids=[f"pp-{pakt_id}-{g.value}-001", f"pp-{pakt_id}-{g.value}-002"],
            info_tags=["info", "programmierparadigmen", g.value],
        ))
    return ProgrammierparadigmenPakt(pakt_id=pakt_id, eintraege=eintraege, parent=parent)
