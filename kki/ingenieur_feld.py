"""#731 — IngenieurFeld: Ingenieurwissenschaften & Technikwissenschaften Wurzel."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.wirtschaft_verfassung import WirtschaftVerfassung, build_wirtschaft_verfassung


class IngenieurFeldGeltung(str, Enum):
    GESPERRT = "gesperrt"
    INGENIEURTECHNISCH = "ingenieurtechnisch"
    GRUNDLEGEND_INGENIEURTECHNISCH = "grundlegend-ingenieurtechnisch"


class IngenieurFeldTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class IngenieurFeldProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class IngenieurFeldNorm:
    ing_feld_id: str
    geltung: IngenieurFeldGeltung
    typ: IngenieurFeldTyp
    prozedur: IngenieurFeldProzedur
    ing_weight: float
    ing_tier: int
    ing_ids: List[str]
    ing_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class IngenieurFeld:
    feld_id: str
    normen: List[IngenieurFeldNorm]
    parent: WirtschaftVerfassung


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        IngenieurFeldGeltung.GESPERRT: 0.0,
        IngenieurFeldGeltung.INGENIEURTECHNISCH: 0.05,
        IngenieurFeldGeltung.GRUNDLEGEND_INGENIEURTECHNISCH: 0.1,
    })
    _TIER_DELTA.update({
        IngenieurFeldGeltung.GESPERRT: 0,
        IngenieurFeldGeltung.INGENIEURTECHNISCH: 1,
        IngenieurFeldGeltung.GRUNDLEGEND_INGENIEURTECHNISCH: 2,
    })
    _TYP_MAP.update({
        IngenieurFeldGeltung.GESPERRT: IngenieurFeldTyp.BEOBACHTUNG,
        IngenieurFeldGeltung.INGENIEURTECHNISCH: IngenieurFeldTyp.ANALYSE,
        IngenieurFeldGeltung.GRUNDLEGEND_INGENIEURTECHNISCH: IngenieurFeldTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        IngenieurFeldGeltung.GESPERRT: IngenieurFeldProzedur.INITIALISIEREN,
        IngenieurFeldGeltung.INGENIEURTECHNISCH: IngenieurFeldProzedur.AKTIVIEREN,
        IngenieurFeldGeltung.GRUNDLEGEND_INGENIEURTECHNISCH: IngenieurFeldProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        IngenieurFeldGeltung.GESPERRT: [IngenieurFeldGeltung.GESPERRT],
        IngenieurFeldGeltung.INGENIEURTECHNISCH: [IngenieurFeldGeltung.INGENIEURTECHNISCH],
        IngenieurFeldGeltung.GRUNDLEGEND_INGENIEURTECHNISCH: [IngenieurFeldGeltung.GRUNDLEGEND_INGENIEURTECHNISCH],
    })


_init_map()


def build_ingenieur_feld(*, feld_id: str = "ingenieur-feld") -> IngenieurFeld:
    parent = build_wirtschaft_verfassung(verfassung_id=f"{feld_id}-parent")
    normen: List[IngenieurFeldNorm] = []
    for g in IngenieurFeldGeltung:
        normen.append(IngenieurFeldNorm(
            ing_feld_id=f"{feld_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            ing_weight=round(sum(n.wirt_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            ing_tier=max(n.wirt_tier for n in parent.normen) + _TIER_DELTA[g],
            ing_ids=[f"if-{feld_id}-{g.value}-001", f"if-{feld_id}-{g.value}-002"],
            ing_tags=["ing", "ingenieur", g.value],
        ))
    return IngenieurFeld(feld_id=feld_id, normen=normen, parent=parent)
