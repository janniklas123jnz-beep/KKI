"""#664 ArtenvielfaltKodex — Biodiversität & Artenschutz (parent: OekosystemCharta)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .oekosystem_charta import OekosystemCharta, build_oekosystem_charta

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class ArtenvielfaltKodexGeltung(str, Enum):
    GESPERRT = "gesperrt"
    ARTENVIELFALT_KODIERT = "artenvielfalt-kodiert"
    GRUNDLEGEND_ARTENVIELFALT_KODIERT = "grundlegend-artenvielfalt-kodiert"


class ArtenvielfaltKodexTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"
    SCHUTZ = "schutz"


class ArtenvielfaltKodexProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class ArtenvielfaltKodexEintrag:
    artenvielfalt_kodex_id: str
    geltung: ArtenvielfaltKodexGeltung
    typ: ArtenvielfaltKodexTyp
    prozedur: ArtenvielfaltKodexProzedur
    oekologie_weight: float
    oekologie_tier: int
    oekologie_ids: List[str]
    oekologie_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class ArtenvielfaltKodex:
    kodex_id: str
    eintraege: List[ArtenvielfaltKodexEintrag]
    parent: OekosystemCharta


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        ArtenvielfaltKodexGeltung.GESPERRT: 0.0,
        ArtenvielfaltKodexGeltung.ARTENVIELFALT_KODIERT: 0.05,
        ArtenvielfaltKodexGeltung.GRUNDLEGEND_ARTENVIELFALT_KODIERT: 0.1,
    })
    _TIER_DELTA.update({
        ArtenvielfaltKodexGeltung.GESPERRT: 0,
        ArtenvielfaltKodexGeltung.ARTENVIELFALT_KODIERT: 1,
        ArtenvielfaltKodexGeltung.GRUNDLEGEND_ARTENVIELFALT_KODIERT: 2,
    })
    _TYP_MAP.update({
        ArtenvielfaltKodexGeltung.GESPERRT: ArtenvielfaltKodexTyp.BEOBACHTUNG,
        ArtenvielfaltKodexGeltung.ARTENVIELFALT_KODIERT: ArtenvielfaltKodexTyp.ANALYSE,
        ArtenvielfaltKodexGeltung.GRUNDLEGEND_ARTENVIELFALT_KODIERT: ArtenvielfaltKodexTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        ArtenvielfaltKodexGeltung.GESPERRT: ArtenvielfaltKodexProzedur.INITIALISIEREN,
        ArtenvielfaltKodexGeltung.ARTENVIELFALT_KODIERT: ArtenvielfaltKodexProzedur.AKTIVIEREN,
        ArtenvielfaltKodexGeltung.GRUNDLEGEND_ARTENVIELFALT_KODIERT: ArtenvielfaltKodexProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        ArtenvielfaltKodexGeltung.GESPERRT: [ArtenvielfaltKodexGeltung.GESPERRT],
        ArtenvielfaltKodexGeltung.ARTENVIELFALT_KODIERT: [ArtenvielfaltKodexGeltung.ARTENVIELFALT_KODIERT],
        ArtenvielfaltKodexGeltung.GRUNDLEGEND_ARTENVIELFALT_KODIERT: [ArtenvielfaltKodexGeltung.GRUNDLEGEND_ARTENVIELFALT_KODIERT],
    })


_init_map()


def build_artenvielfalt_kodex(*, kodex_id: str = "artenvielfalt-kodex") -> ArtenvielfaltKodex:
    parent = build_oekosystem_charta(charta_id=f"{kodex_id}-parent")
    eintraege: List[ArtenvielfaltKodexEintrag] = []
    for g in ArtenvielfaltKodexGeltung:
        eintraege.append(ArtenvielfaltKodexEintrag(
            artenvielfalt_kodex_id=f"{kodex_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            oekologie_weight=round(sum(n.oekologie_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            oekologie_tier=max(n.oekologie_tier for n in parent.normen) + _TIER_DELTA[g],
            oekologie_ids=[f"ak-{kodex_id}-{g.value}-001", f"ak-{kodex_id}-{g.value}-002"],
            oekologie_tags=["oekologie", "artenvielfalt", "kodex", g.value],
        ))
    return ArtenvielfaltKodex(kodex_id=kodex_id, eintraege=eintraege, parent=parent)
