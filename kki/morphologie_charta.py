from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from kki.sprachphonik_register import PhonologieRegister, PhonologieRegisterGeltung, build_phonologie_register

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class MorphologieChartaGeltung(str, Enum):
    GESPERRT = "gesperrt"
    MORPHOLOGISCH = "morphologisch"
    GRUNDLEGEND_MORPHOLOGISCH = "grundlegend-morphologisch"


class MorphologieChartaTyp(str, Enum):
    SCHUTZ_MORPHOLOGIECHARTA = "schutz-morphologiecharta"
    ORDNUNGS_MORPHOLOGIECHARTA = "ordnungs-morphologiecharta"
    SOUVERAENITAETS_MORPHOLOGIECHARTA = "souveraenitaets-morphologiecharta"


class MorphologieChartaProzedur(str, Enum):
    MORPHOLOGIECHARTA_ANALYSE = "morphologiecharta-analyse"
    MORPHOLOGIECHARTA_INTEGRATION = "morphologiecharta-integration"
    MORPHOLOGIECHARTA_SYNTHESE = "morphologiecharta-synthese"


@dataclass(frozen=True)
class MorphologieChartaNorm:
    morphologie_charta_id: str
    linguistik_typ: MorphologieChartaTyp
    prozedur: MorphologieChartaProzedur
    geltung: MorphologieChartaGeltung
    linguistik_weight: float
    linguistik_tier: int
    canonical: bool
    linguistik_ids: tuple[str, ...]
    linguistik_tags: tuple[str, ...]


@dataclass(frozen=True)
class MorphologieCharta:
    charta_id: str
    phonologie_register: PhonologieRegister
    normen: tuple[MorphologieChartaNorm, ...]


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        MorphologieChartaGeltung.GESPERRT: 0.0,
        MorphologieChartaGeltung.MORPHOLOGISCH: 0.05,
        MorphologieChartaGeltung.GRUNDLEGEND_MORPHOLOGISCH: 0.1,
    })
    _TIER_DELTA.update({
        MorphologieChartaGeltung.GESPERRT: 0,
        MorphologieChartaGeltung.MORPHOLOGISCH: 1,
        MorphologieChartaGeltung.GRUNDLEGEND_MORPHOLOGISCH: 2,
    })
    _TYP_MAP.update({
        MorphologieChartaGeltung.GESPERRT: MorphologieChartaTyp.SCHUTZ_MORPHOLOGIECHARTA,
        MorphologieChartaGeltung.MORPHOLOGISCH: MorphologieChartaTyp.ORDNUNGS_MORPHOLOGIECHARTA,
        MorphologieChartaGeltung.GRUNDLEGEND_MORPHOLOGISCH: MorphologieChartaTyp.SOUVERAENITAETS_MORPHOLOGIECHARTA,
    })
    _PROZEDUR_MAP.update({
        MorphologieChartaGeltung.GESPERRT: MorphologieChartaProzedur.MORPHOLOGIECHARTA_ANALYSE,
        MorphologieChartaGeltung.MORPHOLOGISCH: MorphologieChartaProzedur.MORPHOLOGIECHARTA_INTEGRATION,
        MorphologieChartaGeltung.GRUNDLEGEND_MORPHOLOGISCH: MorphologieChartaProzedur.MORPHOLOGIECHARTA_SYNTHESE,
    })
    _GELTUNG_MAP.update({
        PhonologieRegisterGeltung.GESPERRT: MorphologieChartaGeltung.GESPERRT,
        PhonologieRegisterGeltung.PHONOLOGISCH: MorphologieChartaGeltung.MORPHOLOGISCH,
        PhonologieRegisterGeltung.GRUNDLEGEND_PHONOLOGISCH: MorphologieChartaGeltung.GRUNDLEGEND_MORPHOLOGISCH,
    })


_init_map()


def build_morphologie_charta(
    phonologie_register: PhonologieRegister | None = None,
    *,
    charta_id: str = "morphologie-charta",
) -> MorphologieCharta:
    if phonologie_register is None:
        phonologie_register = build_phonologie_register(register_id=f"{charta_id}-register")

    normen: list[MorphologieChartaNorm] = []
    for parent_norm in phonologie_register.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.phonologie_register_id.removeprefix(f'{phonologie_register.register_id}-')}"
        raw_weight = min(1.0, parent_norm.linguistik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.linguistik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is MorphologieChartaGeltung.GRUNDLEGEND_MORPHOLOGISCH)
        normen.append(
            MorphologieChartaNorm(
                morphologie_charta_id=new_id,
                linguistik_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                linguistik_weight=new_weight,
                linguistik_tier=new_tier,
                canonical=is_canonical,
                linguistik_ids=parent_norm.linguistik_ids + (new_id,),
                linguistik_tags=parent_norm.linguistik_tags + (f"morphologie-charta:{new_geltung.value}",),
            )
        )
    return MorphologieCharta(
        charta_id=charta_id,
        phonologie_register=phonologie_register,
        normen=tuple(normen),
    )
