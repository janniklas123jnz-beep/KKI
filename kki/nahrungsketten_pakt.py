"""#666 NahrungskettenPakt — Trophische Ebenen & Nahrungsnetze (parent: StoffkreislaufManifest)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .stoffkreislauf_manifest import StoffkreislaufManifest, build_stoffkreislauf_manifest

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class NahrungskettenPaktGeltung(str, Enum):
    GESPERRT = "gesperrt"
    NAHRUNGSKETTE_VERBUNDEN = "nahrungskette-verbunden"
    GRUNDLEGEND_NAHRUNGSKETTE_VERBUNDEN = "grundlegend-nahrungskette-verbunden"


class NahrungskettenPaktTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"
    SCHUTZ = "schutz"


class NahrungskettenPaktProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class NahrungskettenPaktEintrag:
    nahrungsketten_pakt_id: str
    geltung: NahrungskettenPaktGeltung
    typ: NahrungskettenPaktTyp
    prozedur: NahrungskettenPaktProzedur
    oekologie_weight: float
    oekologie_tier: int
    oekologie_ids: List[str]
    oekologie_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class NahrungskettenPakt:
    pakt_id: str
    eintraege: List[NahrungskettenPaktEintrag]
    parent: StoffkreislaufManifest


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        NahrungskettenPaktGeltung.GESPERRT: 0.0,
        NahrungskettenPaktGeltung.NAHRUNGSKETTE_VERBUNDEN: 0.05,
        NahrungskettenPaktGeltung.GRUNDLEGEND_NAHRUNGSKETTE_VERBUNDEN: 0.1,
    })
    _TIER_DELTA.update({
        NahrungskettenPaktGeltung.GESPERRT: 0,
        NahrungskettenPaktGeltung.NAHRUNGSKETTE_VERBUNDEN: 1,
        NahrungskettenPaktGeltung.GRUNDLEGEND_NAHRUNGSKETTE_VERBUNDEN: 2,
    })
    _TYP_MAP.update({
        NahrungskettenPaktGeltung.GESPERRT: NahrungskettenPaktTyp.BEOBACHTUNG,
        NahrungskettenPaktGeltung.NAHRUNGSKETTE_VERBUNDEN: NahrungskettenPaktTyp.ANALYSE,
        NahrungskettenPaktGeltung.GRUNDLEGEND_NAHRUNGSKETTE_VERBUNDEN: NahrungskettenPaktTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        NahrungskettenPaktGeltung.GESPERRT: NahrungskettenPaktProzedur.INITIALISIEREN,
        NahrungskettenPaktGeltung.NAHRUNGSKETTE_VERBUNDEN: NahrungskettenPaktProzedur.AKTIVIEREN,
        NahrungskettenPaktGeltung.GRUNDLEGEND_NAHRUNGSKETTE_VERBUNDEN: NahrungskettenPaktProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        NahrungskettenPaktGeltung.GESPERRT: [NahrungskettenPaktGeltung.GESPERRT],
        NahrungskettenPaktGeltung.NAHRUNGSKETTE_VERBUNDEN: [NahrungskettenPaktGeltung.NAHRUNGSKETTE_VERBUNDEN],
        NahrungskettenPaktGeltung.GRUNDLEGEND_NAHRUNGSKETTE_VERBUNDEN: [NahrungskettenPaktGeltung.GRUNDLEGEND_NAHRUNGSKETTE_VERBUNDEN],
    })


_init_map()


def build_nahrungsketten_pakt(*, pakt_id: str = "nahrungsketten-pakt") -> NahrungskettenPakt:
    parent = build_stoffkreislauf_manifest(manifest_id=f"{pakt_id}-parent")
    eintraege: List[NahrungskettenPaktEintrag] = []
    for g in NahrungskettenPaktGeltung:
        eintraege.append(NahrungskettenPaktEintrag(
            nahrungsketten_pakt_id=f"{pakt_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            oekologie_weight=round(sum(n.oekologie_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            oekologie_tier=max(n.oekologie_tier for n in parent.normen) + _TIER_DELTA[g],
            oekologie_ids=[f"np-{pakt_id}-{g.value}-001", f"np-{pakt_id}-{g.value}-002"],
            oekologie_tags=["oekologie", "nahrungskette", "pakt", g.value],
        ))
    return NahrungskettenPakt(pakt_id=pakt_id, eintraege=eintraege, parent=parent)
