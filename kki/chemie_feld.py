"""#671 ChemieFeld — Wurzel Chemie & Molekularwissenschaft (parent: UmweltwissenschaftVerfassung)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .umweltwissenschaft_verfassung import UmweltwissenschaftVerfassung, build_umweltwissenschaft_verfassung

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class ChemieFeldGeltung(str, Enum):
    GESPERRT = "gesperrt"
    CHEMISCH_AKTIV = "chemisch-aktiv"
    GRUNDLEGEND_CHEMISCH_AKTIV = "grundlegend-chemisch-aktiv"


class ChemieFeldTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"
    KATALYSE = "katalyse"


class ChemieFeldProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class ChemieFeldNorm:
    chemie_feld_id: str
    geltung: ChemieFeldGeltung
    typ: ChemieFeldTyp
    prozedur: ChemieFeldProzedur
    chemie_weight: float
    chemie_tier: int
    chemie_ids: List[str]
    chemie_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class ChemieFeld:
    feld_id: str
    normen: List[ChemieFeldNorm]
    parent: UmweltwissenschaftVerfassung


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        ChemieFeldGeltung.GESPERRT: 0.0,
        ChemieFeldGeltung.CHEMISCH_AKTIV: 0.05,
        ChemieFeldGeltung.GRUNDLEGEND_CHEMISCH_AKTIV: 0.1,
    })
    _TIER_DELTA.update({
        ChemieFeldGeltung.GESPERRT: 0,
        ChemieFeldGeltung.CHEMISCH_AKTIV: 1,
        ChemieFeldGeltung.GRUNDLEGEND_CHEMISCH_AKTIV: 2,
    })
    _TYP_MAP.update({
        ChemieFeldGeltung.GESPERRT: ChemieFeldTyp.BEOBACHTUNG,
        ChemieFeldGeltung.CHEMISCH_AKTIV: ChemieFeldTyp.ANALYSE,
        ChemieFeldGeltung.GRUNDLEGEND_CHEMISCH_AKTIV: ChemieFeldTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        ChemieFeldGeltung.GESPERRT: ChemieFeldProzedur.INITIALISIEREN,
        ChemieFeldGeltung.CHEMISCH_AKTIV: ChemieFeldProzedur.AKTIVIEREN,
        ChemieFeldGeltung.GRUNDLEGEND_CHEMISCH_AKTIV: ChemieFeldProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        ChemieFeldGeltung.GESPERRT: [ChemieFeldGeltung.GESPERRT],
        ChemieFeldGeltung.CHEMISCH_AKTIV: [ChemieFeldGeltung.CHEMISCH_AKTIV],
        ChemieFeldGeltung.GRUNDLEGEND_CHEMISCH_AKTIV: [ChemieFeldGeltung.GRUNDLEGEND_CHEMISCH_AKTIV],
    })


_init_map()


def build_chemie_feld(*, feld_id: str = "chemie-feld") -> ChemieFeld:
    parent = build_umweltwissenschaft_verfassung(verfassung_id=f"{feld_id}-parent")
    normen: List[ChemieFeldNorm] = []
    for g in ChemieFeldGeltung:
        normen.append(ChemieFeldNorm(
            chemie_feld_id=f"{feld_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            chemie_weight=round(sum(n.oekologie_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            chemie_tier=max(n.oekologie_tier for n in parent.normen) + _TIER_DELTA[g],
            chemie_ids=[f"cf-{feld_id}-{g.value}-001", f"cf-{feld_id}-{g.value}-002"],
            chemie_tags=["chemie", "feld", g.value],
        ))
    return ChemieFeld(feld_id=feld_id, normen=normen, parent=parent)
