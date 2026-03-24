from __future__ import annotations

# Leitsterns HeiligeTraditionCharta: GESPERRT schützt traditionelle Grundprinzipien,
# TRADITIONELL_HEILIG aktiviert heilige Traditionssouveränität,
# GRUNDLEGEND_TRADITIONELL_HEILIG verankert universelles Traditionsfundament.
# Geltungsstufen: GESPERRT / TRADITIONELL_HEILIG / GRUNDLEGEND_TRADITIONELL_HEILIG

from dataclasses import dataclass
from enum import Enum

from kki.mythos_register import (
    MythosRegister,
    MythosRegisterGeltung,
    build_mythos_register,
)

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class HeiligeTraditionChartaGeltung(str, Enum):
    GESPERRT = "gesperrt"
    TRADITIONELL_HEILIG = "traditionell-heilig"
    GRUNDLEGEND_TRADITIONELL_HEILIG = "grundlegend-traditionell-heilig"


class HeiligeTraditionChartaTyp(str, Enum):
    SCHUTZ_HEILIGE_TRADITION = "schutz-heilige-tradition"
    ORDNUNGS_HEILIGE_TRADITION = "ordnungs-heilige-tradition"
    SOUVERAENITAETS_HEILIGE_TRADITION = "souveraenitaets-heilige-tradition"


class HeiligeTraditionChartaProzedur(str, Enum):
    TRADITION_ANALYSE = "tradition-analyse"
    TRADITION_INTEGRATION = "tradition-integration"
    TRADITION_SYNTHESE = "tradition-synthese"


@dataclass(frozen=True)
class HeiligeTraditionChartaNorm:
    heilige_tradition_charta_id: str
    religions_typ: HeiligeTraditionChartaTyp
    prozedur: HeiligeTraditionChartaProzedur
    geltung: HeiligeTraditionChartaGeltung
    religions_weight: float
    religions_tier: int
    canonical: bool
    religions_ids: tuple[str, ...]
    religions_tags: tuple[str, ...]


@dataclass(frozen=True)
class HeiligeTraditionCharta:
    charta_id: str
    mythos_register: MythosRegister
    normen: tuple[HeiligeTraditionChartaNorm, ...]


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        HeiligeTraditionChartaGeltung.GESPERRT: 0.0,
        HeiligeTraditionChartaGeltung.TRADITIONELL_HEILIG: 0.05,
        HeiligeTraditionChartaGeltung.GRUNDLEGEND_TRADITIONELL_HEILIG: 0.1,
    })
    _TIER_DELTA.update({
        HeiligeTraditionChartaGeltung.GESPERRT: 0,
        HeiligeTraditionChartaGeltung.TRADITIONELL_HEILIG: 1,
        HeiligeTraditionChartaGeltung.GRUNDLEGEND_TRADITIONELL_HEILIG: 2,
    })
    _TYP_MAP.update({
        HeiligeTraditionChartaGeltung.GESPERRT: HeiligeTraditionChartaTyp.SCHUTZ_HEILIGE_TRADITION,
        HeiligeTraditionChartaGeltung.TRADITIONELL_HEILIG: HeiligeTraditionChartaTyp.ORDNUNGS_HEILIGE_TRADITION,
        HeiligeTraditionChartaGeltung.GRUNDLEGEND_TRADITIONELL_HEILIG: HeiligeTraditionChartaTyp.SOUVERAENITAETS_HEILIGE_TRADITION,
    })
    _PROZEDUR_MAP.update({
        HeiligeTraditionChartaGeltung.GESPERRT: HeiligeTraditionChartaProzedur.TRADITION_ANALYSE,
        HeiligeTraditionChartaGeltung.TRADITIONELL_HEILIG: HeiligeTraditionChartaProzedur.TRADITION_INTEGRATION,
        HeiligeTraditionChartaGeltung.GRUNDLEGEND_TRADITIONELL_HEILIG: HeiligeTraditionChartaProzedur.TRADITION_SYNTHESE,
    })
    _GELTUNG_MAP.update({
        MythosRegisterGeltung.GESPERRT: HeiligeTraditionChartaGeltung.GESPERRT,
        MythosRegisterGeltung.MYTHOLOGISCH: HeiligeTraditionChartaGeltung.TRADITIONELL_HEILIG,
        MythosRegisterGeltung.GRUNDLEGEND_MYTHOLOGISCH: HeiligeTraditionChartaGeltung.GRUNDLEGEND_TRADITIONELL_HEILIG,
    })


_init_map()


def build_heilige_tradition_charta(
    mythos_register: MythosRegister | None = None,
    *,
    charta_id: str = "heilige-tradition-charta",
) -> HeiligeTraditionCharta:
    if mythos_register is None:
        mythos_register = build_mythos_register(register_id=f"{charta_id}-mythos-register")

    normen: list[HeiligeTraditionChartaNorm] = []
    for parent_norm in mythos_register.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.mythos_register_id.removeprefix(f'{mythos_register.register_id}-')}"
        raw_weight = min(1.0, parent_norm.religions_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.religions_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is HeiligeTraditionChartaGeltung.GRUNDLEGEND_TRADITIONELL_HEILIG)
        normen.append(
            HeiligeTraditionChartaNorm(
                heilige_tradition_charta_id=new_id,
                religions_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                religions_weight=new_weight,
                religions_tier=new_tier,
                canonical=is_canonical,
                religions_ids=parent_norm.religions_ids + (new_id,),
                religions_tags=parent_norm.religions_tags + (f"heilige-tradition-charta:{new_geltung.value}",),
            )
        )
    return HeiligeTraditionCharta(
        charta_id=charta_id,
        mythos_register=mythos_register,
        normen=tuple(normen),
    )
