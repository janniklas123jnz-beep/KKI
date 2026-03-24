"""#651 InternetFeld — Wurzel Internet & Wissensrecherche (parent: GesundheitswissenschaftVerfassung)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .gesundheitswissenschaft_verfassung import GesundheitswissenschaftVerfassung, build_gesundheitswissenschaft_verfassung

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class InternetFeldGeltung(str, Enum):
    GESPERRT = "gesperrt"
    INTERNET_SOUVERAEN = "internet-souveraen"
    GRUNDLEGEND_INTERNET_SOUVERAEN = "grundlegend-internet-souveraen"


class InternetFeldTyp(str, Enum):
    RECHERCHE = "recherche"
    VALIDIERUNG = "validierung"
    AGGREGATION = "aggregation"
    AUTONOME_ENTDECKUNG = "autonome-entdeckung"


class InternetFeldProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class InternetFeldNorm:
    internet_feld_id: str
    geltung: InternetFeldGeltung
    typ: InternetFeldTyp
    prozedur: InternetFeldProzedur
    internet_weight: float
    internet_tier: int
    internet_ids: List[str]
    internet_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class InternetFeld:
    feld_id: str
    normen: List[InternetFeldNorm]
    parent: GesundheitswissenschaftVerfassung


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        InternetFeldGeltung.GESPERRT: 0.0,
        InternetFeldGeltung.INTERNET_SOUVERAEN: 0.05,
        InternetFeldGeltung.GRUNDLEGEND_INTERNET_SOUVERAEN: 0.1,
    })
    _TIER_DELTA.update({
        InternetFeldGeltung.GESPERRT: 0,
        InternetFeldGeltung.INTERNET_SOUVERAEN: 1,
        InternetFeldGeltung.GRUNDLEGEND_INTERNET_SOUVERAEN: 2,
    })
    _TYP_MAP.update({
        InternetFeldGeltung.GESPERRT: InternetFeldTyp.RECHERCHE,
        InternetFeldGeltung.INTERNET_SOUVERAEN: InternetFeldTyp.VALIDIERUNG,
        InternetFeldGeltung.GRUNDLEGEND_INTERNET_SOUVERAEN: InternetFeldTyp.AGGREGATION,
    })
    _PROZEDUR_MAP.update({
        InternetFeldGeltung.GESPERRT: InternetFeldProzedur.INITIALISIEREN,
        InternetFeldGeltung.INTERNET_SOUVERAEN: InternetFeldProzedur.AKTIVIEREN,
        InternetFeldGeltung.GRUNDLEGEND_INTERNET_SOUVERAEN: InternetFeldProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        InternetFeldGeltung.GESPERRT: [InternetFeldGeltung.GESPERRT],
        InternetFeldGeltung.INTERNET_SOUVERAEN: [InternetFeldGeltung.INTERNET_SOUVERAEN],
        InternetFeldGeltung.GRUNDLEGEND_INTERNET_SOUVERAEN: [InternetFeldGeltung.GRUNDLEGEND_INTERNET_SOUVERAEN],
    })


_init_map()


def build_internet_feld(*, feld_id: str = "internet-feld") -> InternetFeld:
    parent = build_gesundheitswissenschaft_verfassung(verfassung_id=f"{feld_id}-parent")
    normen: List[InternetFeldNorm] = []
    for g in InternetFeldGeltung:
        normen.append(InternetFeldNorm(
            internet_feld_id=f"{feld_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            internet_weight=round(sum(n.medizin_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            internet_tier=max(n.medizin_tier for n in parent.normen) + _TIER_DELTA[g],
            internet_ids=[f"if-{feld_id}-{g.value}-001", f"if-{feld_id}-{g.value}-002"],
            internet_tags=["internet", "feld", g.value],
        ))
    return InternetFeld(feld_id=feld_id, normen=normen, parent=parent)
