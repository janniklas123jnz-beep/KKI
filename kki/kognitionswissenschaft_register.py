from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from kki.psychologie_feld import (
    PsychologieFeld,
    PsychologieFeldGeltung,
    build_psychologie_feld,
)

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class KognitionswissenschaftRegisterGeltung(str, Enum):
    GESPERRT = "gesperrt"
    KOGNITIONSWISSENSCHAFTLICH = "kognitionswissenschaftlich"
    GRUNDLEGEND_KOGNITIONSWISSENSCHAFTLICH = "grundlegend-kognitionswissenschaftlich"


class KognitionswissenschaftRegisterTyp(str, Enum):
    SCHUTZ_KOGNITIONSWISSENSCHAFT = "schutz-kognitionswissenschaft"
    ORDNUNGS_KOGNITIONSWISSENSCHAFT = "ordnungs-kognitionswissenschaft"
    SOUVERAENITAETS_KOGNITIONSWISSENSCHAFT = "souveraenitaets-kognitionswissenschaft"


class KognitionswissenschaftRegisterProzedur(str, Enum):
    KOGNITIONSWISSENSCHAFT_ANALYSE = "kognitionswissenschaft-analyse"
    KOGNITIONSWISSENSCHAFT_INTEGRATION = "kognitionswissenschaft-integration"
    KOGNITIONSWISSENSCHAFT_SYNTHESE = "kognitionswissenschaft-synthese"


@dataclass(frozen=True)
class KognitionswissenschaftRegisterNorm:
    kognitionswissenschaft_register_id: str
    psychologie_typ: KognitionswissenschaftRegisterTyp
    prozedur: KognitionswissenschaftRegisterProzedur
    geltung: KognitionswissenschaftRegisterGeltung
    psychologie_weight: float
    psychologie_tier: int
    canonical: bool
    psychologie_ids: tuple[str, ...]
    psychologie_tags: tuple[str, ...]


@dataclass(frozen=True)
class KognitionswissenschaftRegister:
    register_id: str
    psychologie_feld: PsychologieFeld
    normen: tuple[KognitionswissenschaftRegisterNorm, ...]


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        KognitionswissenschaftRegisterGeltung.GESPERRT: 0.0,
        KognitionswissenschaftRegisterGeltung.KOGNITIONSWISSENSCHAFTLICH: 0.05,
        KognitionswissenschaftRegisterGeltung.GRUNDLEGEND_KOGNITIONSWISSENSCHAFTLICH: 0.1,
    })
    _TIER_DELTA.update({
        KognitionswissenschaftRegisterGeltung.GESPERRT: 0,
        KognitionswissenschaftRegisterGeltung.KOGNITIONSWISSENSCHAFTLICH: 1,
        KognitionswissenschaftRegisterGeltung.GRUNDLEGEND_KOGNITIONSWISSENSCHAFTLICH: 2,
    })
    _TYP_MAP.update({
        KognitionswissenschaftRegisterGeltung.GESPERRT: KognitionswissenschaftRegisterTyp.SCHUTZ_KOGNITIONSWISSENSCHAFT,
        KognitionswissenschaftRegisterGeltung.KOGNITIONSWISSENSCHAFTLICH: KognitionswissenschaftRegisterTyp.ORDNUNGS_KOGNITIONSWISSENSCHAFT,
        KognitionswissenschaftRegisterGeltung.GRUNDLEGEND_KOGNITIONSWISSENSCHAFTLICH: KognitionswissenschaftRegisterTyp.SOUVERAENITAETS_KOGNITIONSWISSENSCHAFT,
    })
    _PROZEDUR_MAP.update({
        KognitionswissenschaftRegisterGeltung.GESPERRT: KognitionswissenschaftRegisterProzedur.KOGNITIONSWISSENSCHAFT_ANALYSE,
        KognitionswissenschaftRegisterGeltung.KOGNITIONSWISSENSCHAFTLICH: KognitionswissenschaftRegisterProzedur.KOGNITIONSWISSENSCHAFT_INTEGRATION,
        KognitionswissenschaftRegisterGeltung.GRUNDLEGEND_KOGNITIONSWISSENSCHAFTLICH: KognitionswissenschaftRegisterProzedur.KOGNITIONSWISSENSCHAFT_SYNTHESE,
    })
    _GELTUNG_MAP.update({
        PsychologieFeldGeltung.GESPERRT: KognitionswissenschaftRegisterGeltung.GESPERRT,
        PsychologieFeldGeltung.PSYCHOLOGISCH_SOUVERAEN: KognitionswissenschaftRegisterGeltung.KOGNITIONSWISSENSCHAFTLICH,
        PsychologieFeldGeltung.GRUNDLEGEND_PSYCHOLOGISCH_SOUVERAEN: KognitionswissenschaftRegisterGeltung.GRUNDLEGEND_KOGNITIONSWISSENSCHAFTLICH,
    })


_init_map()


def build_kognitionswissenschaft_register(
    psychologie_feld: PsychologieFeld | None = None,
    *,
    register_id: str = "kognitionswissenschaft-register",
) -> KognitionswissenschaftRegister:
    if psychologie_feld is None:
        psychologie_feld = build_psychologie_feld(
            feld_id=f"{register_id}-feld"
        )

    normen: list[KognitionswissenschaftRegisterNorm] = []
    for parent_norm in psychologie_feld.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{register_id}-{parent_norm.psychologie_feld_id.removeprefix(f'{psychologie_feld.feld_id}-')}"
        raw_weight = min(1.0, parent_norm.psychologie_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.psychologie_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KognitionswissenschaftRegisterGeltung.GRUNDLEGEND_KOGNITIONSWISSENSCHAFTLICH)
        normen.append(
            KognitionswissenschaftRegisterNorm(
                kognitionswissenschaft_register_id=new_id,
                psychologie_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                psychologie_weight=new_weight,
                psychologie_tier=new_tier,
                canonical=is_canonical,
                psychologie_ids=parent_norm.psychologie_ids + (new_id,),
                psychologie_tags=parent_norm.psychologie_tags + (f"kognitionswissenschaft-register:{new_geltung.value}",),
            )
        )
    return KognitionswissenschaftRegister(
        register_id=register_id,
        psychologie_feld=psychologie_feld,
        normen=tuple(normen),
    )
