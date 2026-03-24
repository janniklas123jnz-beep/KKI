from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from kki.linguistik_feld import LinguistikFeld, LinguistikFeldGeltung, build_linguistik_feld

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class PhonologieRegisterGeltung(str, Enum):
    GESPERRT = "gesperrt"
    PHONOLOGISCH = "phonologisch"
    GRUNDLEGEND_PHONOLOGISCH = "grundlegend-phonologisch"


class PhonologieRegisterTyp(str, Enum):
    SCHUTZ_PHONOLOGIE = "schutz-phonologie"
    ORDNUNGS_PHONOLOGIE = "ordnungs-phonologie"
    SOUVERAENITAETS_PHONOLOGIE = "souveraenitaets-phonologie"


class PhonologieRegisterProzedur(str, Enum):
    PHONOLOGIE_ANALYSE = "phonologie-analyse"
    PHONOLOGIE_INTEGRATION = "phonologie-integration"
    PHONOLOGIE_SYNTHESE = "phonologie-synthese"


@dataclass(frozen=True)
class PhonologieRegisterNorm:
    phonologie_register_id: str
    linguistik_typ: PhonologieRegisterTyp
    prozedur: PhonologieRegisterProzedur
    geltung: PhonologieRegisterGeltung
    linguistik_weight: float
    linguistik_tier: int
    canonical: bool
    linguistik_ids: tuple[str, ...]
    linguistik_tags: tuple[str, ...]


@dataclass(frozen=True)
class PhonologieRegister:
    register_id: str
    linguistik_feld: LinguistikFeld
    normen: tuple[PhonologieRegisterNorm, ...]


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        PhonologieRegisterGeltung.GESPERRT: 0.0,
        PhonologieRegisterGeltung.PHONOLOGISCH: 0.05,
        PhonologieRegisterGeltung.GRUNDLEGEND_PHONOLOGISCH: 0.1,
    })
    _TIER_DELTA.update({
        PhonologieRegisterGeltung.GESPERRT: 0,
        PhonologieRegisterGeltung.PHONOLOGISCH: 1,
        PhonologieRegisterGeltung.GRUNDLEGEND_PHONOLOGISCH: 2,
    })
    _TYP_MAP.update({
        PhonologieRegisterGeltung.GESPERRT: PhonologieRegisterTyp.SCHUTZ_PHONOLOGIE,
        PhonologieRegisterGeltung.PHONOLOGISCH: PhonologieRegisterTyp.ORDNUNGS_PHONOLOGIE,
        PhonologieRegisterGeltung.GRUNDLEGEND_PHONOLOGISCH: PhonologieRegisterTyp.SOUVERAENITAETS_PHONOLOGIE,
    })
    _PROZEDUR_MAP.update({
        PhonologieRegisterGeltung.GESPERRT: PhonologieRegisterProzedur.PHONOLOGIE_ANALYSE,
        PhonologieRegisterGeltung.PHONOLOGISCH: PhonologieRegisterProzedur.PHONOLOGIE_INTEGRATION,
        PhonologieRegisterGeltung.GRUNDLEGEND_PHONOLOGISCH: PhonologieRegisterProzedur.PHONOLOGIE_SYNTHESE,
    })
    _GELTUNG_MAP.update({
        LinguistikFeldGeltung.GESPERRT: PhonologieRegisterGeltung.GESPERRT,
        LinguistikFeldGeltung.LINGUISTISCH_SOUVERAEN: PhonologieRegisterGeltung.PHONOLOGISCH,
        LinguistikFeldGeltung.GRUNDLEGEND_LINGUISTISCH_SOUVERAEN: PhonologieRegisterGeltung.GRUNDLEGEND_PHONOLOGISCH,
    })


_init_map()


def build_phonologie_register(
    linguistik_feld: LinguistikFeld | None = None,
    *,
    register_id: str = "phonologie-register",
) -> PhonologieRegister:
    if linguistik_feld is None:
        linguistik_feld = build_linguistik_feld(feld_id=f"{register_id}-feld")

    normen: list[PhonologieRegisterNorm] = []
    for parent_norm in linguistik_feld.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{register_id}-{parent_norm.linguistik_feld_id.removeprefix(f'{linguistik_feld.feld_id}-')}"
        raw_weight = min(1.0, parent_norm.linguistik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.linguistik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is PhonologieRegisterGeltung.GRUNDLEGEND_PHONOLOGISCH)
        normen.append(
            PhonologieRegisterNorm(
                phonologie_register_id=new_id,
                linguistik_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                linguistik_weight=new_weight,
                linguistik_tier=new_tier,
                canonical=is_canonical,
                linguistik_ids=parent_norm.linguistik_ids + (new_id,),
                linguistik_tags=parent_norm.linguistik_tags + (f"phonologie-register:{new_geltung.value}",),
            )
        )
    return PhonologieRegister(
        register_id=register_id,
        linguistik_feld=linguistik_feld,
        normen=tuple(normen),
    )
