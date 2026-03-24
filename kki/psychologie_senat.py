from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from kki.sozialpsychologie_pakt import (
    SozialpsychologiePakt,
    SozialpsychologiePaktGeltung,
    build_sozialpsychologie_pakt,
)

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class PsychologieSenatGeltung(str, Enum):
    GESPERRT = "gesperrt"
    PSYCHOLOGISCH_SENATORISCH = "psychologisch-senatorisch"
    GRUNDLEGEND_PSYCHOLOGISCH_SENATORISCH = "grundlegend-psychologisch-senatorisch"


class PsychologieSenatTyp(str, Enum):
    SCHUTZ_PSYCHOLOGIESENAT = "schutz-psychologiesenat"
    ORDNUNGS_PSYCHOLOGIESENAT = "ordnungs-psychologiesenat"
    SOUVERAENITAETS_PSYCHOLOGIESENAT = "souveraenitaets-psychologiesenat"


class PsychologieSenatProzedur(str, Enum):
    PSYCHOLOGIESENAT_ANALYSE = "psychologiesenat-analyse"
    PSYCHOLOGIESENAT_INTEGRATION = "psychologiesenat-integration"
    PSYCHOLOGIESENAT_SYNTHESE = "psychologiesenat-synthese"


@dataclass(frozen=True)
class PsychologieSenatNorm:
    psychologie_senat_id: str
    psychologie_typ: PsychologieSenatTyp
    prozedur: PsychologieSenatProzedur
    geltung: PsychologieSenatGeltung
    psychologie_weight: float
    psychologie_tier: int
    canonical: bool
    psychologie_ids: tuple[str, ...]
    psychologie_tags: tuple[str, ...]


@dataclass(frozen=True)
class PsychologieSenat:
    senat_id: str
    sozialpsychologie_pakt: SozialpsychologiePakt
    normen: tuple[PsychologieSenatNorm, ...]


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        PsychologieSenatGeltung.GESPERRT: 0.0,
        PsychologieSenatGeltung.PSYCHOLOGISCH_SENATORISCH: 0.05,
        PsychologieSenatGeltung.GRUNDLEGEND_PSYCHOLOGISCH_SENATORISCH: 0.1,
    })
    _TIER_DELTA.update({
        PsychologieSenatGeltung.GESPERRT: 0,
        PsychologieSenatGeltung.PSYCHOLOGISCH_SENATORISCH: 1,
        PsychologieSenatGeltung.GRUNDLEGEND_PSYCHOLOGISCH_SENATORISCH: 2,
    })
    _TYP_MAP.update({
        PsychologieSenatGeltung.GESPERRT: PsychologieSenatTyp.SCHUTZ_PSYCHOLOGIESENAT,
        PsychologieSenatGeltung.PSYCHOLOGISCH_SENATORISCH: PsychologieSenatTyp.ORDNUNGS_PSYCHOLOGIESENAT,
        PsychologieSenatGeltung.GRUNDLEGEND_PSYCHOLOGISCH_SENATORISCH: PsychologieSenatTyp.SOUVERAENITAETS_PSYCHOLOGIESENAT,
    })
    _PROZEDUR_MAP.update({
        PsychologieSenatGeltung.GESPERRT: PsychologieSenatProzedur.PSYCHOLOGIESENAT_ANALYSE,
        PsychologieSenatGeltung.PSYCHOLOGISCH_SENATORISCH: PsychologieSenatProzedur.PSYCHOLOGIESENAT_INTEGRATION,
        PsychologieSenatGeltung.GRUNDLEGEND_PSYCHOLOGISCH_SENATORISCH: PsychologieSenatProzedur.PSYCHOLOGIESENAT_SYNTHESE,
    })
    _GELTUNG_MAP.update({
        SozialpsychologiePaktGeltung.GESPERRT: PsychologieSenatGeltung.GESPERRT,
        SozialpsychologiePaktGeltung.SOZIALPSYCHOLOGISCH: PsychologieSenatGeltung.PSYCHOLOGISCH_SENATORISCH,
        SozialpsychologiePaktGeltung.GRUNDLEGEND_SOZIALPSYCHOLOGISCH: PsychologieSenatGeltung.GRUNDLEGEND_PSYCHOLOGISCH_SENATORISCH,
    })


_init_map()


def build_psychologie_senat(
    sozialpsychologie_pakt: SozialpsychologiePakt | None = None,
    *,
    senat_id: str = "psychologie-senat",
) -> PsychologieSenat:
    if sozialpsychologie_pakt is None:
        sozialpsychologie_pakt = build_sozialpsychologie_pakt(
            pakt_id=f"{senat_id}-pakt"
        )

    normen: list[PsychologieSenatNorm] = []
    for parent_norm in sozialpsychologie_pakt.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{senat_id}-{parent_norm.sozialpsychologie_pakt_id.removeprefix(f'{sozialpsychologie_pakt.pakt_id}-')}"
        raw_weight = min(1.0, parent_norm.psychologie_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.psychologie_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is PsychologieSenatGeltung.GRUNDLEGEND_PSYCHOLOGISCH_SENATORISCH)
        normen.append(
            PsychologieSenatNorm(
                psychologie_senat_id=new_id,
                psychologie_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                psychologie_weight=new_weight,
                psychologie_tier=new_tier,
                canonical=is_canonical,
                psychologie_ids=parent_norm.psychologie_ids + (new_id,),
                psychologie_tags=parent_norm.psychologie_tags + (f"psychologie-senat:{new_geltung.value}",),
            )
        )
    return PsychologieSenat(
        senat_id=senat_id,
        sozialpsychologie_pakt=sozialpsychologie_pakt,
        normen=tuple(normen),
    )
