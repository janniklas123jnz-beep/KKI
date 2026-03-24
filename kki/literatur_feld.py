"""#631 LiteraturFeld — Wurzel Literaturwissenschaft (parent: MusikwissenschaftVerfassung)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .musikwissenschaft_verfassung import MusikwissenschaftVerfassung, build_musikwissenschaft_verfassung

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class LiteraturFeldGeltung(str, Enum):
    GESPERRT = "gesperrt"
    LITERARISCH_SOUVERAEN = "literarisch-souveraen"
    GRUNDLEGEND_LITERARISCH_SOUVERAEN = "grundlegend-literarisch-souveraen"


class LiteraturFeldTyp(str, Enum):
    ANALYTISCH = "analytisch"
    SYNTHETISCH = "synthetisch"
    HISTORISCH = "historisch"
    KOMPARATIV = "komparativ"


class LiteraturFeldProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class LiteraturFeldNorm:
    literatur_feld_id: str
    geltung: LiteraturFeldGeltung
    typ: LiteraturFeldTyp
    prozedur: LiteraturFeldProzedur
    literatur_weight: float
    literatur_tier: int
    literatur_ids: List[str]
    literatur_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class LiteraturFeld:
    feld_id: str
    normen: List[LiteraturFeldNorm]
    parent: MusikwissenschaftVerfassung


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        LiteraturFeldGeltung.GESPERRT: 0.0,
        LiteraturFeldGeltung.LITERARISCH_SOUVERAEN: 0.05,
        LiteraturFeldGeltung.GRUNDLEGEND_LITERARISCH_SOUVERAEN: 0.1,
    })
    _TIER_DELTA.update({
        LiteraturFeldGeltung.GESPERRT: 0,
        LiteraturFeldGeltung.LITERARISCH_SOUVERAEN: 1,
        LiteraturFeldGeltung.GRUNDLEGEND_LITERARISCH_SOUVERAEN: 2,
    })
    _TYP_MAP.update({
        LiteraturFeldGeltung.GESPERRT: LiteraturFeldTyp.ANALYTISCH,
        LiteraturFeldGeltung.LITERARISCH_SOUVERAEN: LiteraturFeldTyp.SYNTHETISCH,
        LiteraturFeldGeltung.GRUNDLEGEND_LITERARISCH_SOUVERAEN: LiteraturFeldTyp.HISTORISCH,
    })
    _PROZEDUR_MAP.update({
        LiteraturFeldGeltung.GESPERRT: LiteraturFeldProzedur.INITIALISIEREN,
        LiteraturFeldGeltung.LITERARISCH_SOUVERAEN: LiteraturFeldProzedur.AKTIVIEREN,
        LiteraturFeldGeltung.GRUNDLEGEND_LITERARISCH_SOUVERAEN: LiteraturFeldProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        LiteraturFeldGeltung.GESPERRT: [LiteraturFeldGeltung.GESPERRT],
        LiteraturFeldGeltung.LITERARISCH_SOUVERAEN: [LiteraturFeldGeltung.LITERARISCH_SOUVERAEN],
        LiteraturFeldGeltung.GRUNDLEGEND_LITERARISCH_SOUVERAEN: [LiteraturFeldGeltung.GRUNDLEGEND_LITERARISCH_SOUVERAEN],
    })


_init_map()


def build_literatur_feld(*, feld_id: str = "literatur-feld") -> LiteraturFeld:
    parent = build_musikwissenschaft_verfassung(verfassung_id=f"{feld_id}-parent")
    normen: List[LiteraturFeldNorm] = []
    for g in LiteraturFeldGeltung:
        normen.append(LiteraturFeldNorm(
            literatur_feld_id=f"{feld_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            literatur_weight=round(sum(n.musik_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            literatur_tier=max(n.musik_tier for n in parent.normen) + _TIER_DELTA[g],
            literatur_ids=[f"lf-{feld_id}-{g.value}-001", f"lf-{feld_id}-{g.value}-002"],
            literatur_tags=["literaturwissenschaft", "feld", g.value],
        ))
    return LiteraturFeld(feld_id=feld_id, normen=normen, parent=parent)
