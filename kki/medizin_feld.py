"""#641 MedizinFeld — Wurzel Medizin & Gesundheitswissenschaften (parent: LiteraturwissenschaftVerfassung)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .literaturwissenschaft_verfassung import LiteraturwissenschaftVerfassung, build_literaturwissenschaft_verfassung

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class MedizinFeldGeltung(str, Enum):
    GESPERRT = "gesperrt"
    MEDIZINISCH_SOUVERAEN = "medizinisch-souveraen"
    GRUNDLEGEND_MEDIZINISCH_SOUVERAEN = "grundlegend-medizinisch-souveraen"


class MedizinFeldTyp(str, Enum):
    KLINISCH = "klinisch"
    THEORETISCH = "theoretisch"
    ANGEWANDT = "angewandt"
    PRAEVENTIV = "praeventiv"


class MedizinFeldProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class MedizinFeldNorm:
    medizin_feld_id: str
    geltung: MedizinFeldGeltung
    typ: MedizinFeldTyp
    prozedur: MedizinFeldProzedur
    medizin_weight: float
    medizin_tier: int
    medizin_ids: List[str]
    medizin_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class MedizinFeld:
    feld_id: str
    normen: List[MedizinFeldNorm]
    parent: LiteraturwissenschaftVerfassung


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        MedizinFeldGeltung.GESPERRT: 0.0,
        MedizinFeldGeltung.MEDIZINISCH_SOUVERAEN: 0.05,
        MedizinFeldGeltung.GRUNDLEGEND_MEDIZINISCH_SOUVERAEN: 0.1,
    })
    _TIER_DELTA.update({
        MedizinFeldGeltung.GESPERRT: 0,
        MedizinFeldGeltung.MEDIZINISCH_SOUVERAEN: 1,
        MedizinFeldGeltung.GRUNDLEGEND_MEDIZINISCH_SOUVERAEN: 2,
    })
    _TYP_MAP.update({
        MedizinFeldGeltung.GESPERRT: MedizinFeldTyp.KLINISCH,
        MedizinFeldGeltung.MEDIZINISCH_SOUVERAEN: MedizinFeldTyp.THEORETISCH,
        MedizinFeldGeltung.GRUNDLEGEND_MEDIZINISCH_SOUVERAEN: MedizinFeldTyp.ANGEWANDT,
    })
    _PROZEDUR_MAP.update({
        MedizinFeldGeltung.GESPERRT: MedizinFeldProzedur.INITIALISIEREN,
        MedizinFeldGeltung.MEDIZINISCH_SOUVERAEN: MedizinFeldProzedur.AKTIVIEREN,
        MedizinFeldGeltung.GRUNDLEGEND_MEDIZINISCH_SOUVERAEN: MedizinFeldProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        MedizinFeldGeltung.GESPERRT: [MedizinFeldGeltung.GESPERRT],
        MedizinFeldGeltung.MEDIZINISCH_SOUVERAEN: [MedizinFeldGeltung.MEDIZINISCH_SOUVERAEN],
        MedizinFeldGeltung.GRUNDLEGEND_MEDIZINISCH_SOUVERAEN: [MedizinFeldGeltung.GRUNDLEGEND_MEDIZINISCH_SOUVERAEN],
    })


_init_map()


def build_medizin_feld(*, feld_id: str = "medizin-feld") -> MedizinFeld:
    parent = build_literaturwissenschaft_verfassung(verfassung_id=f"{feld_id}-parent")
    normen: List[MedizinFeldNorm] = []
    for g in MedizinFeldGeltung:
        normen.append(MedizinFeldNorm(
            medizin_feld_id=f"{feld_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            medizin_weight=round(sum(n.literatur_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            medizin_tier=max(n.literatur_tier for n in parent.normen) + _TIER_DELTA[g],
            medizin_ids=[f"mf-{feld_id}-{g.value}-001", f"mf-{feld_id}-{g.value}-002"],
            medizin_tags=["medizin", "feld", g.value],
        ))
    return MedizinFeld(feld_id=feld_id, normen=normen, parent=parent)
