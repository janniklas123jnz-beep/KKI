"""#621 MusikFeld — Wurzel Musikwissenschaft (parent: ReligionswissenschaftVerfassung)."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List
from .religionswissenschaft_verfassung import ReligionswissenschaftVerfassung, build_religionswissenschaft_verfassung

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class MusikFeldGeltung(str, Enum):
    GESPERRT = "gesperrt"
    MUSIKALISCH_SOUVERAEN = "musikalisch-souveraen"
    GRUNDLEGEND_MUSIKALISCH_SOUVERAEN = "grundlegend-musikalisch-souveraen"


class MusikFeldTyp(str, Enum):
    ANALYTISCH = "analytisch"
    SYNTHETISCH = "synthetisch"
    HISTORISCH = "historisch"
    KOMPARATIV = "komparativ"


class MusikFeldProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class MusikFeldNorm:
    musik_feld_id: str
    geltung: MusikFeldGeltung
    typ: MusikFeldTyp
    prozedur: MusikFeldProzedur
    musik_weight: float
    musik_tier: int
    musik_ids: List[str]
    musik_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class MusikFeld:
    feld_id: str
    normen: List[MusikFeldNorm]
    parent: ReligionswissenschaftVerfassung


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        MusikFeldGeltung.GESPERRT: 0.0,
        MusikFeldGeltung.MUSIKALISCH_SOUVERAEN: 0.05,
        MusikFeldGeltung.GRUNDLEGEND_MUSIKALISCH_SOUVERAEN: 0.1,
    })
    _TIER_DELTA.update({
        MusikFeldGeltung.GESPERRT: 0,
        MusikFeldGeltung.MUSIKALISCH_SOUVERAEN: 1,
        MusikFeldGeltung.GRUNDLEGEND_MUSIKALISCH_SOUVERAEN: 2,
    })
    _TYP_MAP.update({
        MusikFeldGeltung.GESPERRT: MusikFeldTyp.ANALYTISCH,
        MusikFeldGeltung.MUSIKALISCH_SOUVERAEN: MusikFeldTyp.SYNTHETISCH,
        MusikFeldGeltung.GRUNDLEGEND_MUSIKALISCH_SOUVERAEN: MusikFeldTyp.HISTORISCH,
    })
    _PROZEDUR_MAP.update({
        MusikFeldGeltung.GESPERRT: MusikFeldProzedur.INITIALISIEREN,
        MusikFeldGeltung.MUSIKALISCH_SOUVERAEN: MusikFeldProzedur.AKTIVIEREN,
        MusikFeldGeltung.GRUNDLEGEND_MUSIKALISCH_SOUVERAEN: MusikFeldProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        MusikFeldGeltung.GESPERRT: [MusikFeldGeltung.GESPERRT],
        MusikFeldGeltung.MUSIKALISCH_SOUVERAEN: [MusikFeldGeltung.MUSIKALISCH_SOUVERAEN],
        MusikFeldGeltung.GRUNDLEGEND_MUSIKALISCH_SOUVERAEN: [MusikFeldGeltung.GRUNDLEGEND_MUSIKALISCH_SOUVERAEN],
    })


_init_map()


def build_musik_feld(*, feld_id: str = "musik-feld") -> MusikFeld:
    parent = build_religionswissenschaft_verfassung(verfassung_id=f"{feld_id}-parent")
    normen: List[MusikFeldNorm] = []
    for g in MusikFeldGeltung:
        normen.append(MusikFeldNorm(
            musik_feld_id=f"{feld_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            musik_weight=round(sum(n.religions_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            musik_tier=max(n.religions_tier for n in parent.normen) + _TIER_DELTA[g],
            musik_ids=[f"mf-{feld_id}-{g.value}-001", f"mf-{feld_id}-{g.value}-002"],
            musik_tags=["musikwissenschaft", "feld", g.value],
        ))
    return MusikFeld(feld_id=feld_id, normen=normen, parent=parent)
