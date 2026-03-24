from __future__ import annotations

# Leitsterns ReligionsphilosophieSenat: GESPERRT schützt religionsphilosophische Grundprinzipien,
# RELIGIONSPHILOSOPHISCH aktiviert religionsphilosophische Souveränität,
# GRUNDLEGEND_RELIGIONSPHILOSOPHISCH verankert universelles Religionsphilosophiefundament.
# Geltungsstufen: GESPERRT / RELIGIONSPHILOSOPHISCH / GRUNDLEGEND_RELIGIONSPHILOSOPHISCH

from dataclasses import dataclass
from enum import Enum

from kki.spiritualitaets_pakt import (
    SpiritualitaetsPakt,
    SpiritualitaetsPaktGeltung,
    build_spiritualitaets_pakt,
)

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class ReligionsphilosophieSenatGeltung(str, Enum):
    GESPERRT = "gesperrt"
    RELIGIONSPHILOSOPHISCH = "religionsphilosophisch"
    GRUNDLEGEND_RELIGIONSPHILOSOPHISCH = "grundlegend-religionsphilosophisch"


class ReligionsphilosophieSenatTyp(str, Enum):
    SCHUTZ_RELIGIONSPHILOSOPHIE = "schutz-religionsphilosophie"
    ORDNUNGS_RELIGIONSPHILOSOPHIE = "ordnungs-religionsphilosophie"
    SOUVERAENITAETS_RELIGIONSPHILOSOPHIE = "souveraenitaets-religionsphilosophie"


class ReligionsphilosophieSenatProzedur(str, Enum):
    RELIGIONSPHILOSOPHIE_SITZUNG = "religionsphilosophie-sitzung"
    RELIGIONSPHILOSOPHIE_REGELPROTOKOLL = "religionsphilosophie-regelprotokoll"
    RELIGIONSPHILOSOPHIE_PLENARPROTOKOLL = "religionsphilosophie-plenarprotokoll"


@dataclass(frozen=True)
class ReligionsphilosophieSenatNorm:
    religionsphilosophie_senat_id: str
    religions_typ: ReligionsphilosophieSenatTyp
    prozedur: ReligionsphilosophieSenatProzedur
    geltung: ReligionsphilosophieSenatGeltung
    religions_weight: float
    religions_tier: int
    canonical: bool
    religions_ids: tuple[str, ...]
    religions_tags: tuple[str, ...]


@dataclass(frozen=True)
class ReligionsphilosophieSenat:
    senat_id: str
    spiritualitaets_pakt: SpiritualitaetsPakt
    normen: tuple[ReligionsphilosophieSenatNorm, ...]


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        ReligionsphilosophieSenatGeltung.GESPERRT: 0.0,
        ReligionsphilosophieSenatGeltung.RELIGIONSPHILOSOPHISCH: 0.05,
        ReligionsphilosophieSenatGeltung.GRUNDLEGEND_RELIGIONSPHILOSOPHISCH: 0.1,
    })
    _TIER_DELTA.update({
        ReligionsphilosophieSenatGeltung.GESPERRT: 0,
        ReligionsphilosophieSenatGeltung.RELIGIONSPHILOSOPHISCH: 1,
        ReligionsphilosophieSenatGeltung.GRUNDLEGEND_RELIGIONSPHILOSOPHISCH: 2,
    })
    _TYP_MAP.update({
        ReligionsphilosophieSenatGeltung.GESPERRT: ReligionsphilosophieSenatTyp.SCHUTZ_RELIGIONSPHILOSOPHIE,
        ReligionsphilosophieSenatGeltung.RELIGIONSPHILOSOPHISCH: ReligionsphilosophieSenatTyp.ORDNUNGS_RELIGIONSPHILOSOPHIE,
        ReligionsphilosophieSenatGeltung.GRUNDLEGEND_RELIGIONSPHILOSOPHISCH: ReligionsphilosophieSenatTyp.SOUVERAENITAETS_RELIGIONSPHILOSOPHIE,
    })
    _PROZEDUR_MAP.update({
        ReligionsphilosophieSenatGeltung.GESPERRT: ReligionsphilosophieSenatProzedur.RELIGIONSPHILOSOPHIE_SITZUNG,
        ReligionsphilosophieSenatGeltung.RELIGIONSPHILOSOPHISCH: ReligionsphilosophieSenatProzedur.RELIGIONSPHILOSOPHIE_REGELPROTOKOLL,
        ReligionsphilosophieSenatGeltung.GRUNDLEGEND_RELIGIONSPHILOSOPHISCH: ReligionsphilosophieSenatProzedur.RELIGIONSPHILOSOPHIE_PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        SpiritualitaetsPaktGeltung.GESPERRT: ReligionsphilosophieSenatGeltung.GESPERRT,
        SpiritualitaetsPaktGeltung.SPIRITUELL: ReligionsphilosophieSenatGeltung.RELIGIONSPHILOSOPHISCH,
        SpiritualitaetsPaktGeltung.GRUNDLEGEND_SPIRITUELL: ReligionsphilosophieSenatGeltung.GRUNDLEGEND_RELIGIONSPHILOSOPHISCH,
    })


_init_map()


def build_religionsphilosophie_senat(
    spiritualitaets_pakt: SpiritualitaetsPakt | None = None,
    *,
    senat_id: str = "religionsphilosophie-senat",
) -> ReligionsphilosophieSenat:
    if spiritualitaets_pakt is None:
        spiritualitaets_pakt = build_spiritualitaets_pakt(pakt_id=f"{senat_id}-spiritualitaets-pakt")

    normen: list[ReligionsphilosophieSenatNorm] = []
    for parent_norm in spiritualitaets_pakt.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{senat_id}-{parent_norm.spiritualitaets_pakt_id.removeprefix(f'{spiritualitaets_pakt.pakt_id}-')}"
        raw_weight = min(1.0, parent_norm.religions_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.religions_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is ReligionsphilosophieSenatGeltung.GRUNDLEGEND_RELIGIONSPHILOSOPHISCH)
        normen.append(
            ReligionsphilosophieSenatNorm(
                religionsphilosophie_senat_id=new_id,
                religions_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                religions_weight=new_weight,
                religions_tier=new_tier,
                canonical=is_canonical,
                religions_ids=parent_norm.religions_ids + (new_id,),
                religions_tags=parent_norm.religions_tags + (f"religionsphilosophie-senat:{new_geltung.value}",),
            )
        )
    return ReligionsphilosophieSenat(
        senat_id=senat_id,
        spiritualitaets_pakt=spiritualitaets_pakt,
        normen=tuple(normen),
    )
