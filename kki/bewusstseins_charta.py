from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from kki.kognitionswissenschaft_register import (
    KognitionswissenschaftRegister,
    KognitionswissenschaftRegisterGeltung,
    build_kognitionswissenschaft_register,
)

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class BewusstseinsChartaGeltung(str, Enum):
    GESPERRT = "gesperrt"
    BEWUSSTSEINSWISSENSCHAFTLICH = "bewusstseinswissenschaftlich"
    GRUNDLEGEND_BEWUSSTSEINSWISSENSCHAFTLICH = "grundlegend-bewusstseinswissenschaftlich"


class BewusstseinsChartaTyp(str, Enum):
    SCHUTZ_BEWUSSTSEINSCHARTA = "schutz-bewusstseinscharta"
    ORDNUNGS_BEWUSSTSEINSCHARTA = "ordnungs-bewusstseinscharta"
    SOUVERAENITAETS_BEWUSSTSEINSCHARTA = "souveraenitaets-bewusstseinscharta"


class BewusstseinsChartaProzedur(str, Enum):
    BEWUSSTSEINSCHARTA_ANALYSE = "bewusstseinscharta-analyse"
    BEWUSSTSEINSCHARTA_INTEGRATION = "bewusstseinscharta-integration"
    BEWUSSTSEINSCHARTA_SYNTHESE = "bewusstseinscharta-synthese"


@dataclass(frozen=True)
class BewusstseinsChartaNorm:
    bewusstseins_charta_id: str
    psychologie_typ: BewusstseinsChartaTyp
    prozedur: BewusstseinsChartaProzedur
    geltung: BewusstseinsChartaGeltung
    psychologie_weight: float
    psychologie_tier: int
    canonical: bool
    psychologie_ids: tuple[str, ...]
    psychologie_tags: tuple[str, ...]


@dataclass(frozen=True)
class BewusstseinsCharta:
    charta_id: str
    kognitionswissenschaft_register: KognitionswissenschaftRegister
    normen: tuple[BewusstseinsChartaNorm, ...]


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        BewusstseinsChartaGeltung.GESPERRT: 0.0,
        BewusstseinsChartaGeltung.BEWUSSTSEINSWISSENSCHAFTLICH: 0.05,
        BewusstseinsChartaGeltung.GRUNDLEGEND_BEWUSSTSEINSWISSENSCHAFTLICH: 0.1,
    })
    _TIER_DELTA.update({
        BewusstseinsChartaGeltung.GESPERRT: 0,
        BewusstseinsChartaGeltung.BEWUSSTSEINSWISSENSCHAFTLICH: 1,
        BewusstseinsChartaGeltung.GRUNDLEGEND_BEWUSSTSEINSWISSENSCHAFTLICH: 2,
    })
    _TYP_MAP.update({
        BewusstseinsChartaGeltung.GESPERRT: BewusstseinsChartaTyp.SCHUTZ_BEWUSSTSEINSCHARTA,
        BewusstseinsChartaGeltung.BEWUSSTSEINSWISSENSCHAFTLICH: BewusstseinsChartaTyp.ORDNUNGS_BEWUSSTSEINSCHARTA,
        BewusstseinsChartaGeltung.GRUNDLEGEND_BEWUSSTSEINSWISSENSCHAFTLICH: BewusstseinsChartaTyp.SOUVERAENITAETS_BEWUSSTSEINSCHARTA,
    })
    _PROZEDUR_MAP.update({
        BewusstseinsChartaGeltung.GESPERRT: BewusstseinsChartaProzedur.BEWUSSTSEINSCHARTA_ANALYSE,
        BewusstseinsChartaGeltung.BEWUSSTSEINSWISSENSCHAFTLICH: BewusstseinsChartaProzedur.BEWUSSTSEINSCHARTA_INTEGRATION,
        BewusstseinsChartaGeltung.GRUNDLEGEND_BEWUSSTSEINSWISSENSCHAFTLICH: BewusstseinsChartaProzedur.BEWUSSTSEINSCHARTA_SYNTHESE,
    })
    _GELTUNG_MAP.update({
        KognitionswissenschaftRegisterGeltung.GESPERRT: BewusstseinsChartaGeltung.GESPERRT,
        KognitionswissenschaftRegisterGeltung.KOGNITIONSWISSENSCHAFTLICH: BewusstseinsChartaGeltung.BEWUSSTSEINSWISSENSCHAFTLICH,
        KognitionswissenschaftRegisterGeltung.GRUNDLEGEND_KOGNITIONSWISSENSCHAFTLICH: BewusstseinsChartaGeltung.GRUNDLEGEND_BEWUSSTSEINSWISSENSCHAFTLICH,
    })


_init_map()


def build_bewusstseins_charta(
    kognitionswissenschaft_register: KognitionswissenschaftRegister | None = None,
    *,
    charta_id: str = "bewusstseins-charta",
) -> BewusstseinsCharta:
    if kognitionswissenschaft_register is None:
        kognitionswissenschaft_register = build_kognitionswissenschaft_register(
            register_id=f"{charta_id}-register"
        )

    normen: list[BewusstseinsChartaNorm] = []
    for parent_norm in kognitionswissenschaft_register.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.kognitionswissenschaft_register_id.removeprefix(f'{kognitionswissenschaft_register.register_id}-')}"
        raw_weight = min(1.0, parent_norm.psychologie_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.psychologie_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is BewusstseinsChartaGeltung.GRUNDLEGEND_BEWUSSTSEINSWISSENSCHAFTLICH)
        normen.append(
            BewusstseinsChartaNorm(
                bewusstseins_charta_id=new_id,
                psychologie_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                psychologie_weight=new_weight,
                psychologie_tier=new_tier,
                canonical=is_canonical,
                psychologie_ids=parent_norm.psychologie_ids + (new_id,),
                psychologie_tags=parent_norm.psychologie_tags + (f"bewusstseins-charta:{new_geltung.value}",),
            )
        )
    return BewusstseinsCharta(
        charta_id=charta_id,
        kognitionswissenschaft_register=kognitionswissenschaft_register,
        normen=tuple(normen),
    )
