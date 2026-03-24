from __future__ import annotations

# Leitsterns MythosRegister: GESPERRT schützt mythologische Grundprinzipien,
# MYTHOLOGISCH aktiviert mythologische Souveränität,
# GRUNDLEGEND_MYTHOLOGISCH verankert universelles Mythosfundament.
# Geltungsstufen: GESPERRT / MYTHOLOGISCH / GRUNDLEGEND_MYTHOLOGISCH

from dataclasses import dataclass
from enum import Enum

from kki.religions_feld import (
    ReligionsFeld,
    ReligionsFeldGeltung,
    build_religions_feld,
)

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class MythosRegisterGeltung(str, Enum):
    GESPERRT = "gesperrt"
    MYTHOLOGISCH = "mythologisch"
    GRUNDLEGEND_MYTHOLOGISCH = "grundlegend-mythologisch"


class MythosRegisterTyp(str, Enum):
    SCHUTZ_MYTHOSREGISTER = "schutz-mythosregister"
    ORDNUNGS_MYTHOSREGISTER = "ordnungs-mythosregister"
    SOUVERAENITAETS_MYTHOSREGISTER = "souveraenitaets-mythosregister"


class MythosRegisterProzedur(str, Enum):
    MYTHOS_ANALYSE = "mythos-analyse"
    MYTHOS_INTEGRATION = "mythos-integration"
    MYTHOS_SYNTHESE = "mythos-synthese"


@dataclass(frozen=True)
class MythosRegisterNorm:
    mythos_register_id: str
    religions_typ: MythosRegisterTyp
    prozedur: MythosRegisterProzedur
    geltung: MythosRegisterGeltung
    religions_weight: float
    religions_tier: int
    canonical: bool
    religions_ids: tuple[str, ...]
    religions_tags: tuple[str, ...]


@dataclass(frozen=True)
class MythosRegister:
    register_id: str
    religions_feld: ReligionsFeld
    normen: tuple[MythosRegisterNorm, ...]


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        MythosRegisterGeltung.GESPERRT: 0.0,
        MythosRegisterGeltung.MYTHOLOGISCH: 0.05,
        MythosRegisterGeltung.GRUNDLEGEND_MYTHOLOGISCH: 0.1,
    })
    _TIER_DELTA.update({
        MythosRegisterGeltung.GESPERRT: 0,
        MythosRegisterGeltung.MYTHOLOGISCH: 1,
        MythosRegisterGeltung.GRUNDLEGEND_MYTHOLOGISCH: 2,
    })
    _TYP_MAP.update({
        MythosRegisterGeltung.GESPERRT: MythosRegisterTyp.SCHUTZ_MYTHOSREGISTER,
        MythosRegisterGeltung.MYTHOLOGISCH: MythosRegisterTyp.ORDNUNGS_MYTHOSREGISTER,
        MythosRegisterGeltung.GRUNDLEGEND_MYTHOLOGISCH: MythosRegisterTyp.SOUVERAENITAETS_MYTHOSREGISTER,
    })
    _PROZEDUR_MAP.update({
        MythosRegisterGeltung.GESPERRT: MythosRegisterProzedur.MYTHOS_ANALYSE,
        MythosRegisterGeltung.MYTHOLOGISCH: MythosRegisterProzedur.MYTHOS_INTEGRATION,
        MythosRegisterGeltung.GRUNDLEGEND_MYTHOLOGISCH: MythosRegisterProzedur.MYTHOS_SYNTHESE,
    })
    _GELTUNG_MAP.update({
        ReligionsFeldGeltung.GESPERRT: MythosRegisterGeltung.GESPERRT,
        ReligionsFeldGeltung.RELIGIOES_SOUVERAEN: MythosRegisterGeltung.MYTHOLOGISCH,
        ReligionsFeldGeltung.GRUNDLEGEND_RELIGIOES_SOUVERAEN: MythosRegisterGeltung.GRUNDLEGEND_MYTHOLOGISCH,
    })


_init_map()


def build_mythos_register(
    religions_feld: ReligionsFeld | None = None,
    *,
    register_id: str = "mythos-register",
) -> MythosRegister:
    if religions_feld is None:
        religions_feld = build_religions_feld(feld_id=f"{register_id}-religions-feld")

    normen: list[MythosRegisterNorm] = []
    for parent_norm in religions_feld.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{register_id}-{parent_norm.religions_feld_id.removeprefix(f'{religions_feld.feld_id}-')}"
        raw_weight = min(1.0, parent_norm.religions_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.religions_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is MythosRegisterGeltung.GRUNDLEGEND_MYTHOLOGISCH)
        normen.append(
            MythosRegisterNorm(
                mythos_register_id=new_id,
                religions_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                religions_weight=new_weight,
                religions_tier=new_tier,
                canonical=is_canonical,
                religions_ids=parent_norm.religions_ids + (new_id,),
                religions_tags=parent_norm.religions_tags + (f"mythos-register:{new_geltung.value}",),
            )
        )
    return MythosRegister(
        register_id=register_id,
        religions_feld=religions_feld,
        normen=tuple(normen),
    )
