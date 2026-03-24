"""#654 QuellenvalidierungKodex — Quellenvalidierung & Faktenprüfung (parent: DatenAbrufCharta)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .datenabruf_charta import DatenAbrufCharta, build_datenabruf_charta

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class QuellenvalidierungKodexGeltung(str, Enum):
    GESPERRT = "gesperrt"
    QUELLENVALIDIERT = "quellenvalidiert"
    GRUNDLEGEND_QUELLENVALIDIERT = "grundlegend-quellenvalidiert"


class QuellenvalidierungKodexTyp(str, Enum):
    RECHERCHE = "recherche"
    VALIDIERUNG = "validierung"
    AGGREGATION = "aggregation"
    AUTONOME_ENTDECKUNG = "autonome-entdeckung"


class QuellenvalidierungKodexProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class QuellenvalidierungKodexEintrag:
    kodex_id: str
    geltung: QuellenvalidierungKodexGeltung
    typ: QuellenvalidierungKodexTyp
    prozedur: QuellenvalidierungKodexProzedur
    internet_weight: float
    internet_tier: int
    internet_ids: List[str]
    internet_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class QuellenvalidierungKodex:
    kodex_id: str
    eintraege: List[QuellenvalidierungKodexEintrag]
    parent: DatenAbrufCharta


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        QuellenvalidierungKodexGeltung.GESPERRT: 0.0,
        QuellenvalidierungKodexGeltung.QUELLENVALIDIERT: 0.05,
        QuellenvalidierungKodexGeltung.GRUNDLEGEND_QUELLENVALIDIERT: 0.1,
    })
    _TIER_DELTA.update({
        QuellenvalidierungKodexGeltung.GESPERRT: 0,
        QuellenvalidierungKodexGeltung.QUELLENVALIDIERT: 1,
        QuellenvalidierungKodexGeltung.GRUNDLEGEND_QUELLENVALIDIERT: 2,
    })
    _TYP_MAP.update({
        QuellenvalidierungKodexGeltung.GESPERRT: QuellenvalidierungKodexTyp.RECHERCHE,
        QuellenvalidierungKodexGeltung.QUELLENVALIDIERT: QuellenvalidierungKodexTyp.VALIDIERUNG,
        QuellenvalidierungKodexGeltung.GRUNDLEGEND_QUELLENVALIDIERT: QuellenvalidierungKodexTyp.AGGREGATION,
    })
    _PROZEDUR_MAP.update({
        QuellenvalidierungKodexGeltung.GESPERRT: QuellenvalidierungKodexProzedur.INITIALISIEREN,
        QuellenvalidierungKodexGeltung.QUELLENVALIDIERT: QuellenvalidierungKodexProzedur.AKTIVIEREN,
        QuellenvalidierungKodexGeltung.GRUNDLEGEND_QUELLENVALIDIERT: QuellenvalidierungKodexProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        QuellenvalidierungKodexGeltung.GESPERRT: [QuellenvalidierungKodexGeltung.GESPERRT],
        QuellenvalidierungKodexGeltung.QUELLENVALIDIERT: [QuellenvalidierungKodexGeltung.QUELLENVALIDIERT],
        QuellenvalidierungKodexGeltung.GRUNDLEGEND_QUELLENVALIDIERT: [QuellenvalidierungKodexGeltung.GRUNDLEGEND_QUELLENVALIDIERT],
    })


_init_map()


def build_quellenvalidierung_kodex(*, kodex_id: str = "quellenvalidierung-kodex") -> QuellenvalidierungKodex:
    parent = build_datenabruf_charta(charta_id=f"{kodex_id}-parent")
    eintraege: List[QuellenvalidierungKodexEintrag] = []
    for g in QuellenvalidierungKodexGeltung:
        eintraege.append(QuellenvalidierungKodexEintrag(
            kodex_id=f"{kodex_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            internet_weight=round(sum(n.internet_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            internet_tier=max(n.internet_tier for n in parent.normen) + _TIER_DELTA[g],
            internet_ids=[f"qvk-{kodex_id}-{g.value}-001", f"qvk-{kodex_id}-{g.value}-002"],
            internet_tags=["internet", "quellenvalidierung", g.value],
        ))
    return QuellenvalidierungKodex(kodex_id=kodex_id, eintraege=eintraege, parent=parent)
