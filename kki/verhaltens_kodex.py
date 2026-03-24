from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from kki.bewusstseins_charta import (
    BewusstseinsCharta,
    BewusstseinsChartaGeltung,
    build_bewusstseins_charta,
)

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class VerhaltensKodexGeltung(str, Enum):
    GESPERRT = "gesperrt"
    VERHALTENSPSYCHOLOGISCH = "verhaltenspsychologisch"
    GRUNDLEGEND_VERHALTENSPSYCHOLOGISCH = "grundlegend-verhaltenspsychologisch"


class VerhaltensKodexTyp(str, Enum):
    SCHUTZ_VERHALTENSKODEX = "schutz-verhaltenskodex"
    ORDNUNGS_VERHALTENSKODEX = "ordnungs-verhaltenskodex"
    SOUVERAENITAETS_VERHALTENSKODEX = "souveraenitaets-verhaltenskodex"


class VerhaltensKodexProzedur(str, Enum):
    VERHALTENSKODEX_ANALYSE = "verhaltenskodex-analyse"
    VERHALTENSKODEX_INTEGRATION = "verhaltenskodex-integration"
    VERHALTENSKODEX_SYNTHESE = "verhaltenskodex-synthese"


@dataclass(frozen=True)
class VerhaltensKodexNorm:
    verhaltens_kodex_id: str
    psychologie_typ: VerhaltensKodexTyp
    prozedur: VerhaltensKodexProzedur
    geltung: VerhaltensKodexGeltung
    psychologie_weight: float
    psychologie_tier: int
    canonical: bool
    psychologie_ids: tuple[str, ...]
    psychologie_tags: tuple[str, ...]


@dataclass(frozen=True)
class VerhaltensKodex:
    kodex_id: str
    bewusstseins_charta: BewusstseinsCharta
    normen: tuple[VerhaltensKodexNorm, ...]


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        VerhaltensKodexGeltung.GESPERRT: 0.0,
        VerhaltensKodexGeltung.VERHALTENSPSYCHOLOGISCH: 0.05,
        VerhaltensKodexGeltung.GRUNDLEGEND_VERHALTENSPSYCHOLOGISCH: 0.1,
    })
    _TIER_DELTA.update({
        VerhaltensKodexGeltung.GESPERRT: 0,
        VerhaltensKodexGeltung.VERHALTENSPSYCHOLOGISCH: 1,
        VerhaltensKodexGeltung.GRUNDLEGEND_VERHALTENSPSYCHOLOGISCH: 2,
    })
    _TYP_MAP.update({
        VerhaltensKodexGeltung.GESPERRT: VerhaltensKodexTyp.SCHUTZ_VERHALTENSKODEX,
        VerhaltensKodexGeltung.VERHALTENSPSYCHOLOGISCH: VerhaltensKodexTyp.ORDNUNGS_VERHALTENSKODEX,
        VerhaltensKodexGeltung.GRUNDLEGEND_VERHALTENSPSYCHOLOGISCH: VerhaltensKodexTyp.SOUVERAENITAETS_VERHALTENSKODEX,
    })
    _PROZEDUR_MAP.update({
        VerhaltensKodexGeltung.GESPERRT: VerhaltensKodexProzedur.VERHALTENSKODEX_ANALYSE,
        VerhaltensKodexGeltung.VERHALTENSPSYCHOLOGISCH: VerhaltensKodexProzedur.VERHALTENSKODEX_INTEGRATION,
        VerhaltensKodexGeltung.GRUNDLEGEND_VERHALTENSPSYCHOLOGISCH: VerhaltensKodexProzedur.VERHALTENSKODEX_SYNTHESE,
    })
    _GELTUNG_MAP.update({
        BewusstseinsChartaGeltung.GESPERRT: VerhaltensKodexGeltung.GESPERRT,
        BewusstseinsChartaGeltung.BEWUSSTSEINSWISSENSCHAFTLICH: VerhaltensKodexGeltung.VERHALTENSPSYCHOLOGISCH,
        BewusstseinsChartaGeltung.GRUNDLEGEND_BEWUSSTSEINSWISSENSCHAFTLICH: VerhaltensKodexGeltung.GRUNDLEGEND_VERHALTENSPSYCHOLOGISCH,
    })


_init_map()


def build_verhaltens_kodex(
    bewusstseins_charta: BewusstseinsCharta | None = None,
    *,
    kodex_id: str = "verhaltens-kodex",
) -> VerhaltensKodex:
    if bewusstseins_charta is None:
        bewusstseins_charta = build_bewusstseins_charta(
            charta_id=f"{kodex_id}-charta"
        )

    normen: list[VerhaltensKodexNorm] = []
    for parent_norm in bewusstseins_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{kodex_id}-{parent_norm.bewusstseins_charta_id.removeprefix(f'{bewusstseins_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.psychologie_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.psychologie_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is VerhaltensKodexGeltung.GRUNDLEGEND_VERHALTENSPSYCHOLOGISCH)
        normen.append(
            VerhaltensKodexNorm(
                verhaltens_kodex_id=new_id,
                psychologie_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                psychologie_weight=new_weight,
                psychologie_tier=new_tier,
                canonical=is_canonical,
                psychologie_ids=parent_norm.psychologie_ids + (new_id,),
                psychologie_tags=parent_norm.psychologie_tags + (f"verhaltens-kodex:{new_geltung.value}",),
            )
        )
    return VerhaltensKodex(
        kodex_id=kodex_id,
        bewusstseins_charta=bewusstseins_charta,
        normen=tuple(normen),
    )
