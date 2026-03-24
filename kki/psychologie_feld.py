from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from kki.paedagogik_verfassung import (
    PaedagogikVerfassung,
    PaedagogikVerfassungsGeltung,
    build_paedagogik_verfassung,
)

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class PsychologieFeldGeltung(str, Enum):
    GESPERRT = "gesperrt"
    PSYCHOLOGISCH_SOUVERAEN = "psychologisch-souverän"
    GRUNDLEGEND_PSYCHOLOGISCH_SOUVERAEN = "grundlegend-psychologisch-souverän"


class PsychologieFeldTyp(str, Enum):
    SCHUTZ_PSYCHOLOGIEFELD = "schutz-psychologiefeld"
    ORDNUNGS_PSYCHOLOGIEFELD = "ordnungs-psychologiefeld"
    SOUVERAENITAETS_PSYCHOLOGIEFELD = "souveraenitaets-psychologiefeld"


class PsychologieFeldProzedur(str, Enum):
    PSYCHOLOGIEFELD_ANALYSE = "psychologiefeld-analyse"
    PSYCHOLOGIEFELD_INTEGRATION = "psychologiefeld-integration"
    PSYCHOLOGIEFELD_SYNTHESE = "psychologiefeld-synthese"


@dataclass(frozen=True)
class PsychologieFeldNorm:
    psychologie_feld_id: str
    psychologie_typ: PsychologieFeldTyp
    prozedur: PsychologieFeldProzedur
    geltung: PsychologieFeldGeltung
    psychologie_weight: float
    psychologie_tier: int
    canonical: bool
    psychologie_ids: tuple[str, ...]
    psychologie_tags: tuple[str, ...]


@dataclass(frozen=True)
class PsychologieFeld:
    feld_id: str
    paedagogik_verfassung: PaedagogikVerfassung
    normen: tuple[PsychologieFeldNorm, ...]


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        PsychologieFeldGeltung.GESPERRT: 0.0,
        PsychologieFeldGeltung.PSYCHOLOGISCH_SOUVERAEN: 0.05,
        PsychologieFeldGeltung.GRUNDLEGEND_PSYCHOLOGISCH_SOUVERAEN: 0.1,
    })
    _TIER_DELTA.update({
        PsychologieFeldGeltung.GESPERRT: 0,
        PsychologieFeldGeltung.PSYCHOLOGISCH_SOUVERAEN: 1,
        PsychologieFeldGeltung.GRUNDLEGEND_PSYCHOLOGISCH_SOUVERAEN: 2,
    })
    _TYP_MAP.update({
        PsychologieFeldGeltung.GESPERRT: PsychologieFeldTyp.SCHUTZ_PSYCHOLOGIEFELD,
        PsychologieFeldGeltung.PSYCHOLOGISCH_SOUVERAEN: PsychologieFeldTyp.ORDNUNGS_PSYCHOLOGIEFELD,
        PsychologieFeldGeltung.GRUNDLEGEND_PSYCHOLOGISCH_SOUVERAEN: PsychologieFeldTyp.SOUVERAENITAETS_PSYCHOLOGIEFELD,
    })
    _PROZEDUR_MAP.update({
        PsychologieFeldGeltung.GESPERRT: PsychologieFeldProzedur.PSYCHOLOGIEFELD_ANALYSE,
        PsychologieFeldGeltung.PSYCHOLOGISCH_SOUVERAEN: PsychologieFeldProzedur.PSYCHOLOGIEFELD_INTEGRATION,
        PsychologieFeldGeltung.GRUNDLEGEND_PSYCHOLOGISCH_SOUVERAEN: PsychologieFeldProzedur.PSYCHOLOGIEFELD_SYNTHESE,
    })
    _GELTUNG_MAP.update({
        PaedagogikVerfassungsGeltung.GESPERRT: PsychologieFeldGeltung.GESPERRT,
        PaedagogikVerfassungsGeltung.BILDUNGS_SOUVERAEN: PsychologieFeldGeltung.PSYCHOLOGISCH_SOUVERAEN,
        PaedagogikVerfassungsGeltung.GRUNDLEGEND_BILDUNGS_SOUVERAEN: PsychologieFeldGeltung.GRUNDLEGEND_PSYCHOLOGISCH_SOUVERAEN,
    })


_init_map()


def build_psychologie_feld(
    paedagogik_verfassung: PaedagogikVerfassung | None = None,
    *,
    feld_id: str = "psychologie-feld",
) -> PsychologieFeld:
    if paedagogik_verfassung is None:
        paedagogik_verfassung = build_paedagogik_verfassung(
            verfassung_id=f"{feld_id}-verfassung"
        )

    normen: list[PsychologieFeldNorm] = []
    for parent_norm in paedagogik_verfassung.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{feld_id}-{parent_norm.paedagogik_verfassung_id.removeprefix(f'{paedagogik_verfassung.verfassung_id}-')}"
        raw_weight = min(1.0, parent_norm.paedagogik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.paedagogik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is PsychologieFeldGeltung.GRUNDLEGEND_PSYCHOLOGISCH_SOUVERAEN)
        normen.append(
            PsychologieFeldNorm(
                psychologie_feld_id=new_id,
                psychologie_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                psychologie_weight=new_weight,
                psychologie_tier=new_tier,
                canonical=is_canonical,
                psychologie_ids=parent_norm.paedagogik_ids + (new_id,),
                psychologie_tags=parent_norm.paedagogik_tags + (f"psychologie-feld:{new_geltung.value}",),
            )
        )
    return PsychologieFeld(
        feld_id=feld_id,
        paedagogik_verfassung=paedagogik_verfassung,
        normen=tuple(normen),
    )
