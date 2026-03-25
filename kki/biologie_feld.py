"""#701 — BiologieFeld: Biologie & Genetik Wurzel."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.geowissenschaft_verfassung import GeowissenschaftVerfassung, build_geowissenschaft_verfassung


class BiologieFeldGeltung(str, Enum):
    GESPERRT = "gesperrt"
    BIO_AKTIV = "bio-aktiv"
    GRUNDLEGEND_BIO_AKTIV = "grundlegend-bio-aktiv"


class BiologieFeldTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class BiologieFeldProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class BiologieFeldNorm:
    bio_feld_id: str
    geltung: BiologieFeldGeltung
    typ: BiologieFeldTyp
    prozedur: BiologieFeldProzedur
    bio_weight: float
    bio_tier: int
    bio_ids: List[str]
    bio_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class BiologieFeld:
    feld_id: str
    normen: List[BiologieFeldNorm]
    parent: GeowissenschaftVerfassung


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        BiologieFeldGeltung.GESPERRT: 0.0,
        BiologieFeldGeltung.BIO_AKTIV: 0.05,
        BiologieFeldGeltung.GRUNDLEGEND_BIO_AKTIV: 0.1,
    })
    _TIER_DELTA.update({
        BiologieFeldGeltung.GESPERRT: 0,
        BiologieFeldGeltung.BIO_AKTIV: 1,
        BiologieFeldGeltung.GRUNDLEGEND_BIO_AKTIV: 2,
    })
    _TYP_MAP.update({
        BiologieFeldGeltung.GESPERRT: BiologieFeldTyp.BEOBACHTUNG,
        BiologieFeldGeltung.BIO_AKTIV: BiologieFeldTyp.ANALYSE,
        BiologieFeldGeltung.GRUNDLEGEND_BIO_AKTIV: BiologieFeldTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        BiologieFeldGeltung.GESPERRT: BiologieFeldProzedur.INITIALISIEREN,
        BiologieFeldGeltung.BIO_AKTIV: BiologieFeldProzedur.AKTIVIEREN,
        BiologieFeldGeltung.GRUNDLEGEND_BIO_AKTIV: BiologieFeldProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        BiologieFeldGeltung.GESPERRT: [BiologieFeldGeltung.GESPERRT],
        BiologieFeldGeltung.BIO_AKTIV: [BiologieFeldGeltung.BIO_AKTIV],
        BiologieFeldGeltung.GRUNDLEGEND_BIO_AKTIV: [BiologieFeldGeltung.GRUNDLEGEND_BIO_AKTIV],
    })


_init_map()


def build_biologie_feld(*, feld_id: str = "biologie-feld") -> BiologieFeld:
    parent = build_geowissenschaft_verfassung(verfassung_id=f"{feld_id}-parent")
    normen: List[BiologieFeldNorm] = []
    for g in BiologieFeldGeltung:
        normen.append(BiologieFeldNorm(
            bio_feld_id=f"{feld_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            bio_weight=round(sum(n.geo_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            bio_tier=max(n.geo_tier for n in parent.normen) + _TIER_DELTA[g],
            bio_ids=[f"bf-{feld_id}-{g.value}-001", f"bf-{feld_id}-{g.value}-002"],
            bio_tags=["bio", "feld", g.value],
        ))
    return BiologieFeld(feld_id=feld_id, normen=normen, parent=parent)
