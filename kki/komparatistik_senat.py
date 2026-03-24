"""#637 KomparatistikSenat — Komparatistik & Weltliteratur (parent: LiteraturgeschichtePakt)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .literaturgeschichte_pakt import LiteraturgeschichtePakt, build_literaturgeschichte_pakt

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class KomparatistikSenatGeltung(str, Enum):
    GESPERRT = "gesperrt"
    KOMPARATISTISCH = "komparatistisch"
    GRUNDLEGEND_KOMPARATISTISCH = "grundlegend-komparatistisch"


class KomparatistikSenatTyp(str, Enum):
    ANALYTISCH = "analytisch"
    SYNTHETISCH = "synthetisch"
    HISTORISCH = "historisch"
    KOMPARATIV = "komparativ"


class KomparatistikSenatProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class KomparatistikSenatNorm:
    komparatistik_senat_id: str
    geltung: KomparatistikSenatGeltung
    typ: KomparatistikSenatTyp
    literatur_weight: float
    literatur_tier: int
    literatur_ids: List[str]
    literatur_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class KomparatistikSenat:
    senat_id: str
    normen: List[KomparatistikSenatNorm]
    parent: LiteraturgeschichtePakt


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        KomparatistikSenatGeltung.GESPERRT: 0.0,
        KomparatistikSenatGeltung.KOMPARATISTISCH: 0.05,
        KomparatistikSenatGeltung.GRUNDLEGEND_KOMPARATISTISCH: 0.1,
    })
    _TIER_DELTA.update({
        KomparatistikSenatGeltung.GESPERRT: 0,
        KomparatistikSenatGeltung.KOMPARATISTISCH: 1,
        KomparatistikSenatGeltung.GRUNDLEGEND_KOMPARATISTISCH: 2,
    })
    _TYP_MAP.update({
        KomparatistikSenatGeltung.GESPERRT: KomparatistikSenatTyp.ANALYTISCH,
        KomparatistikSenatGeltung.KOMPARATISTISCH: KomparatistikSenatTyp.SYNTHETISCH,
        KomparatistikSenatGeltung.GRUNDLEGEND_KOMPARATISTISCH: KomparatistikSenatTyp.HISTORISCH,
    })
    _PROZEDUR_MAP.update({
        KomparatistikSenatGeltung.GESPERRT: KomparatistikSenatProzedur.INITIALISIEREN,
        KomparatistikSenatGeltung.KOMPARATISTISCH: KomparatistikSenatProzedur.AKTIVIEREN,
        KomparatistikSenatGeltung.GRUNDLEGEND_KOMPARATISTISCH: KomparatistikSenatProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        KomparatistikSenatGeltung.GESPERRT: [KomparatistikSenatGeltung.GESPERRT],
        KomparatistikSenatGeltung.KOMPARATISTISCH: [KomparatistikSenatGeltung.KOMPARATISTISCH],
        KomparatistikSenatGeltung.GRUNDLEGEND_KOMPARATISTISCH: [KomparatistikSenatGeltung.GRUNDLEGEND_KOMPARATISTISCH],
    })


_init_map()


def build_komparatistik_senat(*, senat_id: str = "komparatistik-senat") -> KomparatistikSenat:
    parent = build_literaturgeschichte_pakt(pakt_id=f"{senat_id}-parent")
    normen: List[KomparatistikSenatNorm] = []
    for g in KomparatistikSenatGeltung:
        normen.append(KomparatistikSenatNorm(
            komparatistik_senat_id=f"ks-{senat_id}-{g.value}-001",
            geltung=g,
            typ=_TYP_MAP[g],
            literatur_weight=round(sum(n.literatur_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            literatur_tier=max(n.literatur_tier for n in parent.normen) + _TIER_DELTA[g],
            literatur_ids=[f"ks-{senat_id}-{g.value}-001", f"ks-{senat_id}-{g.value}-002"],
            literatur_tags=["literaturwissenschaft", "komparatistik", g.value],
        ))
    return KomparatistikSenat(senat_id=senat_id, normen=normen, parent=parent)
