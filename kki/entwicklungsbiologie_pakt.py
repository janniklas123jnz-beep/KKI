"""#706 — EntwicklungsbiologiePakt: Embryogenese, Stammzellen & Differenzierung."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.genomik_manifest import GenomikManifest, build_genomik_manifest


class EntwicklungsbiologiePaktGeltung(str, Enum):
    GESPERRT = "gesperrt"
    ENTWICKLUNGSBIOLOGISCH = "entwicklungsbiologisch"
    GRUNDLEGEND_ENTWICKLUNGSBIOLOGISCH = "grundlegend-entwicklungsbiologisch"


class EntwicklungsbiologiePaktTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class EntwicklungsbiologiePaktProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class EntwicklungsbiologiePaktEintrag:
    eintrag_id: str
    geltung: EntwicklungsbiologiePaktGeltung
    typ: EntwicklungsbiologiePaktTyp
    prozedur: EntwicklungsbiologiePaktProzedur
    bio_weight: float
    bio_tier: int
    bio_ids: List[str]
    bio_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class EntwicklungsbiologiePakt:
    pakt_id: str
    eintraege: List[EntwicklungsbiologiePaktEintrag]
    parent: GenomikManifest


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        EntwicklungsbiologiePaktGeltung.GESPERRT: 0.0,
        EntwicklungsbiologiePaktGeltung.ENTWICKLUNGSBIOLOGISCH: 0.05,
        EntwicklungsbiologiePaktGeltung.GRUNDLEGEND_ENTWICKLUNGSBIOLOGISCH: 0.1,
    })
    _TIER_DELTA.update({
        EntwicklungsbiologiePaktGeltung.GESPERRT: 0,
        EntwicklungsbiologiePaktGeltung.ENTWICKLUNGSBIOLOGISCH: 1,
        EntwicklungsbiologiePaktGeltung.GRUNDLEGEND_ENTWICKLUNGSBIOLOGISCH: 2,
    })
    _TYP_MAP.update({
        EntwicklungsbiologiePaktGeltung.GESPERRT: EntwicklungsbiologiePaktTyp.BEOBACHTUNG,
        EntwicklungsbiologiePaktGeltung.ENTWICKLUNGSBIOLOGISCH: EntwicklungsbiologiePaktTyp.ANALYSE,
        EntwicklungsbiologiePaktGeltung.GRUNDLEGEND_ENTWICKLUNGSBIOLOGISCH: EntwicklungsbiologiePaktTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        EntwicklungsbiologiePaktGeltung.GESPERRT: EntwicklungsbiologiePaktProzedur.INITIALISIEREN,
        EntwicklungsbiologiePaktGeltung.ENTWICKLUNGSBIOLOGISCH: EntwicklungsbiologiePaktProzedur.AKTIVIEREN,
        EntwicklungsbiologiePaktGeltung.GRUNDLEGEND_ENTWICKLUNGSBIOLOGISCH: EntwicklungsbiologiePaktProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        EntwicklungsbiologiePaktGeltung.GESPERRT: [EntwicklungsbiologiePaktGeltung.GESPERRT],
        EntwicklungsbiologiePaktGeltung.ENTWICKLUNGSBIOLOGISCH: [EntwicklungsbiologiePaktGeltung.ENTWICKLUNGSBIOLOGISCH],
        EntwicklungsbiologiePaktGeltung.GRUNDLEGEND_ENTWICKLUNGSBIOLOGISCH: [EntwicklungsbiologiePaktGeltung.GRUNDLEGEND_ENTWICKLUNGSBIOLOGISCH],
    })


_init_map()


def build_entwicklungsbiologie_pakt(*, pakt_id: str = "entwicklungsbiologie-pakt") -> EntwicklungsbiologiePakt:
    parent = build_genomik_manifest(manifest_id=f"{pakt_id}-parent")
    eintraege: List[EntwicklungsbiologiePaktEintrag] = []
    for g in EntwicklungsbiologiePaktGeltung:
        eintraege.append(EntwicklungsbiologiePaktEintrag(
            eintrag_id=f"{pakt_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            bio_weight=round(sum(n.bio_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            bio_tier=max(n.bio_tier for n in parent.normen) + _TIER_DELTA[g],
            bio_ids=[f"ep-{pakt_id}-{g.value}-001", f"ep-{pakt_id}-{g.value}-002"],
            bio_tags=["bio", "entwicklungsbiologie", g.value],
        ))
    return EntwicklungsbiologiePakt(pakt_id=pakt_id, eintraege=eintraege, parent=parent)
