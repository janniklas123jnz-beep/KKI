from __future__ import annotations

# Leitsterns TheologieKodex: GESPERRT schützt theologische Grundprinzipien,
# THEOLOGISCH aktiviert theologische Souveränität,
# GRUNDLEGEND_THEOLOGISCH verankert universelles Theologiefundament.
# Geltungsstufen: GESPERRT / THEOLOGISCH / GRUNDLEGEND_THEOLOGISCH

from dataclasses import dataclass
from enum import Enum

from kki.heilige_tradition_charta import (
    HeiligeTraditionCharta,
    HeiligeTraditionChartaGeltung,
    build_heilige_tradition_charta,
)

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class TheologieKodexGeltung(str, Enum):
    GESPERRT = "gesperrt"
    THEOLOGISCH = "theologisch"
    GRUNDLEGEND_THEOLOGISCH = "grundlegend-theologisch"


class TheologieKodexTyp(str, Enum):
    SCHUTZ_THEOLOGIEKODEX = "schutz-theologiekodex"
    ORDNUNGS_THEOLOGIEKODEX = "ordnungs-theologiekodex"
    SOUVERAENITAETS_THEOLOGIEKODEX = "souveraenitaets-theologiekodex"


class TheologieKodexProzedur(str, Enum):
    THEOLOGIE_SITZUNG = "theologie-sitzung"
    THEOLOGIE_REGELPROTOKOLL = "theologie-regelprotokoll"
    THEOLOGIE_PLENARPROTOKOLL = "theologie-plenarprotokoll"


@dataclass(frozen=True)
class TheologieKodexNorm:
    theologie_kodex_id: str
    religions_typ: TheologieKodexTyp
    prozedur: TheologieKodexProzedur
    geltung: TheologieKodexGeltung
    religions_weight: float
    religions_tier: int
    canonical: bool
    religions_ids: tuple[str, ...]
    religions_tags: tuple[str, ...]


@dataclass(frozen=True)
class TheologieKodex:
    kodex_id: str
    heilige_tradition_charta: HeiligeTraditionCharta
    normen: tuple[TheologieKodexNorm, ...]


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        TheologieKodexGeltung.GESPERRT: 0.0,
        TheologieKodexGeltung.THEOLOGISCH: 0.05,
        TheologieKodexGeltung.GRUNDLEGEND_THEOLOGISCH: 0.1,
    })
    _TIER_DELTA.update({
        TheologieKodexGeltung.GESPERRT: 0,
        TheologieKodexGeltung.THEOLOGISCH: 1,
        TheologieKodexGeltung.GRUNDLEGEND_THEOLOGISCH: 2,
    })
    _TYP_MAP.update({
        TheologieKodexGeltung.GESPERRT: TheologieKodexTyp.SCHUTZ_THEOLOGIEKODEX,
        TheologieKodexGeltung.THEOLOGISCH: TheologieKodexTyp.ORDNUNGS_THEOLOGIEKODEX,
        TheologieKodexGeltung.GRUNDLEGEND_THEOLOGISCH: TheologieKodexTyp.SOUVERAENITAETS_THEOLOGIEKODEX,
    })
    _PROZEDUR_MAP.update({
        TheologieKodexGeltung.GESPERRT: TheologieKodexProzedur.THEOLOGIE_SITZUNG,
        TheologieKodexGeltung.THEOLOGISCH: TheologieKodexProzedur.THEOLOGIE_REGELPROTOKOLL,
        TheologieKodexGeltung.GRUNDLEGEND_THEOLOGISCH: TheologieKodexProzedur.THEOLOGIE_PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        HeiligeTraditionChartaGeltung.GESPERRT: TheologieKodexGeltung.GESPERRT,
        HeiligeTraditionChartaGeltung.TRADITIONELL_HEILIG: TheologieKodexGeltung.THEOLOGISCH,
        HeiligeTraditionChartaGeltung.GRUNDLEGEND_TRADITIONELL_HEILIG: TheologieKodexGeltung.GRUNDLEGEND_THEOLOGISCH,
    })


_init_map()


def build_theologie_kodex(
    heilige_tradition_charta: HeiligeTraditionCharta | None = None,
    *,
    kodex_id: str = "theologie-kodex",
) -> TheologieKodex:
    if heilige_tradition_charta is None:
        heilige_tradition_charta = build_heilige_tradition_charta(charta_id=f"{kodex_id}-heilige-tradition-charta")

    normen: list[TheologieKodexNorm] = []
    for parent_norm in heilige_tradition_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{kodex_id}-{parent_norm.heilige_tradition_charta_id.removeprefix(f'{heilige_tradition_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.religions_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.religions_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is TheologieKodexGeltung.GRUNDLEGEND_THEOLOGISCH)
        normen.append(
            TheologieKodexNorm(
                theologie_kodex_id=new_id,
                religions_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                religions_weight=new_weight,
                religions_tier=new_tier,
                canonical=is_canonical,
                religions_ids=parent_norm.religions_ids + (new_id,),
                religions_tags=parent_norm.religions_tags + (f"theologie-kodex:{new_geltung.value}",),
            )
        )
    return TheologieKodex(
        kodex_id=kodex_id,
        heilige_tradition_charta=heilige_tradition_charta,
        normen=tuple(normen),
    )
