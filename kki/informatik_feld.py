"""#711 — InformatikFeld: Informatik & Algorithmik Wurzel."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.biologie_verfassung import BiologieVerfassung, build_biologie_verfassung


class InformatikFeldGeltung(str, Enum):
    GESPERRT = "gesperrt"
    INFO_AKTIV = "info-aktiv"
    GRUNDLEGEND_INFO_AKTIV = "grundlegend-info-aktiv"


class InformatikFeldTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class InformatikFeldProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class InformatikFeldNorm:
    info_feld_id: str
    geltung: InformatikFeldGeltung
    typ: InformatikFeldTyp
    prozedur: InformatikFeldProzedur
    info_weight: float
    info_tier: int
    info_ids: List[str]
    info_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class InformatikFeld:
    feld_id: str
    normen: List[InformatikFeldNorm]
    parent: BiologieVerfassung


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        InformatikFeldGeltung.GESPERRT: 0.0,
        InformatikFeldGeltung.INFO_AKTIV: 0.05,
        InformatikFeldGeltung.GRUNDLEGEND_INFO_AKTIV: 0.1,
    })
    _TIER_DELTA.update({
        InformatikFeldGeltung.GESPERRT: 0,
        InformatikFeldGeltung.INFO_AKTIV: 1,
        InformatikFeldGeltung.GRUNDLEGEND_INFO_AKTIV: 2,
    })
    _TYP_MAP.update({
        InformatikFeldGeltung.GESPERRT: InformatikFeldTyp.BEOBACHTUNG,
        InformatikFeldGeltung.INFO_AKTIV: InformatikFeldTyp.ANALYSE,
        InformatikFeldGeltung.GRUNDLEGEND_INFO_AKTIV: InformatikFeldTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        InformatikFeldGeltung.GESPERRT: InformatikFeldProzedur.INITIALISIEREN,
        InformatikFeldGeltung.INFO_AKTIV: InformatikFeldProzedur.AKTIVIEREN,
        InformatikFeldGeltung.GRUNDLEGEND_INFO_AKTIV: InformatikFeldProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        InformatikFeldGeltung.GESPERRT: [InformatikFeldGeltung.GESPERRT],
        InformatikFeldGeltung.INFO_AKTIV: [InformatikFeldGeltung.INFO_AKTIV],
        InformatikFeldGeltung.GRUNDLEGEND_INFO_AKTIV: [InformatikFeldGeltung.GRUNDLEGEND_INFO_AKTIV],
    })


_init_map()


def build_informatik_feld(*, feld_id: str = "informatik-feld") -> InformatikFeld:
    parent = build_biologie_verfassung(verfassung_id=f"{feld_id}-parent")
    normen: List[InformatikFeldNorm] = []
    for g in InformatikFeldGeltung:
        normen.append(InformatikFeldNorm(
            info_feld_id=f"{feld_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            info_weight=round(sum(n.bio_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            info_tier=max(n.bio_tier for n in parent.normen) + _TIER_DELTA[g],
            info_ids=[f"if-{feld_id}-{g.value}-001", f"if-{feld_id}-{g.value}-002"],
            info_tags=["info", "feld", g.value],
        ))
    return InformatikFeld(feld_id=feld_id, normen=normen, parent=parent)
