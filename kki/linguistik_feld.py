from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from kki.psychologie_verfassung import (
    PsychologieVerfassung,
    PsychologieVerfassungsGeltung,
    build_psychologie_verfassung,
)

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class LinguistikFeldGeltung(str, Enum):
    GESPERRT = "gesperrt"
    LINGUISTISCH_SOUVERAEN = "linguistisch-souverän"
    GRUNDLEGEND_LINGUISTISCH_SOUVERAEN = "grundlegend-linguistisch-souverän"


class LinguistikFeldTyp(str, Enum):
    SCHUTZ_LINGUISTIKFELD = "schutz-linguistikfeld"
    ORDNUNGS_LINGUISTIKFELD = "ordnungs-linguistikfeld"
    SOUVERAENITAETS_LINGUISTIKFELD = "souveraenitaets-linguistikfeld"


class LinguistikFeldProzedur(str, Enum):
    LINGUISTIKFELD_ANALYSE = "linguistikfeld-analyse"
    LINGUISTIKFELD_INTEGRATION = "linguistikfeld-integration"
    LINGUISTIKFELD_SYNTHESE = "linguistikfeld-synthese"


@dataclass(frozen=True)
class LinguistikFeldNorm:
    linguistik_feld_id: str
    linguistik_typ: LinguistikFeldTyp
    prozedur: LinguistikFeldProzedur
    geltung: LinguistikFeldGeltung
    linguistik_weight: float
    linguistik_tier: int
    canonical: bool
    linguistik_ids: tuple[str, ...]
    linguistik_tags: tuple[str, ...]


@dataclass(frozen=True)
class LinguistikFeld:
    feld_id: str
    psychologie_verfassung: PsychologieVerfassung
    normen: tuple[LinguistikFeldNorm, ...]


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        LinguistikFeldGeltung.GESPERRT: 0.0,
        LinguistikFeldGeltung.LINGUISTISCH_SOUVERAEN: 0.05,
        LinguistikFeldGeltung.GRUNDLEGEND_LINGUISTISCH_SOUVERAEN: 0.1,
    })
    _TIER_DELTA.update({
        LinguistikFeldGeltung.GESPERRT: 0,
        LinguistikFeldGeltung.LINGUISTISCH_SOUVERAEN: 1,
        LinguistikFeldGeltung.GRUNDLEGEND_LINGUISTISCH_SOUVERAEN: 2,
    })
    _TYP_MAP.update({
        LinguistikFeldGeltung.GESPERRT: LinguistikFeldTyp.SCHUTZ_LINGUISTIKFELD,
        LinguistikFeldGeltung.LINGUISTISCH_SOUVERAEN: LinguistikFeldTyp.ORDNUNGS_LINGUISTIKFELD,
        LinguistikFeldGeltung.GRUNDLEGEND_LINGUISTISCH_SOUVERAEN: LinguistikFeldTyp.SOUVERAENITAETS_LINGUISTIKFELD,
    })
    _PROZEDUR_MAP.update({
        LinguistikFeldGeltung.GESPERRT: LinguistikFeldProzedur.LINGUISTIKFELD_ANALYSE,
        LinguistikFeldGeltung.LINGUISTISCH_SOUVERAEN: LinguistikFeldProzedur.LINGUISTIKFELD_INTEGRATION,
        LinguistikFeldGeltung.GRUNDLEGEND_LINGUISTISCH_SOUVERAEN: LinguistikFeldProzedur.LINGUISTIKFELD_SYNTHESE,
    })
    _GELTUNG_MAP.update({
        PsychologieVerfassungsGeltung.GESPERRT: LinguistikFeldGeltung.GESPERRT,
        PsychologieVerfassungsGeltung.PSYCHE_SOUVERAEN: LinguistikFeldGeltung.LINGUISTISCH_SOUVERAEN,
        PsychologieVerfassungsGeltung.GRUNDLEGEND_PSYCHE_SOUVERAEN: LinguistikFeldGeltung.GRUNDLEGEND_LINGUISTISCH_SOUVERAEN,
    })


_init_map()


def build_linguistik_feld(
    psychologie_verfassung: PsychologieVerfassung | None = None,
    *,
    feld_id: str = "linguistik-feld",
) -> LinguistikFeld:
    if psychologie_verfassung is None:
        psychologie_verfassung = build_psychologie_verfassung(
            verfassung_id=f"{feld_id}-verfassung"
        )

    normen: list[LinguistikFeldNorm] = []
    for parent_norm in psychologie_verfassung.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{feld_id}-{parent_norm.psychologie_verfassung_id.removeprefix(f'{psychologie_verfassung.verfassung_id}-')}"
        raw_weight = min(1.0, parent_norm.psychologie_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.psychologie_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is LinguistikFeldGeltung.GRUNDLEGEND_LINGUISTISCH_SOUVERAEN)
        normen.append(
            LinguistikFeldNorm(
                linguistik_feld_id=new_id,
                linguistik_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                linguistik_weight=new_weight,
                linguistik_tier=new_tier,
                canonical=is_canonical,
                linguistik_ids=parent_norm.psychologie_ids + (new_id,),
                linguistik_tags=parent_norm.psychologie_tags + (f"linguistik-feld:{new_geltung.value}",),
            )
        )
    return LinguistikFeld(
        feld_id=feld_id,
        psychologie_verfassung=psychologie_verfassung,
        normen=tuple(normen),
    )
