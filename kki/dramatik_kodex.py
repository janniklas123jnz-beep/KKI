"""#634 DramatikKodex — Dramatik & Theatertext (parent: LyrikCharta)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .lyrik_charta import LyrikCharta, build_lyrik_charta

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class DramatikKodexGeltung(str, Enum):
    GESPERRT = "gesperrt"
    DRAMATISCH = "dramatisch"
    GRUNDLEGEND_DRAMATISCH = "grundlegend-dramatisch"


class DramatikKodexTyp(str, Enum):
    ANALYTISCH = "analytisch"
    SYNTHETISCH = "synthetisch"
    HISTORISCH = "historisch"
    KOMPARATIV = "komparativ"


class DramatikKodexProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class DramatikKodexNorm:
    dramatik_kodex_id: str
    geltung: DramatikKodexGeltung
    typ: DramatikKodexTyp
    literatur_weight: float
    literatur_tier: int
    literatur_ids: List[str]
    literatur_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class DramatikKodex:
    kodex_id: str
    normen: List[DramatikKodexNorm]
    parent: LyrikCharta


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        DramatikKodexGeltung.GESPERRT: 0.0,
        DramatikKodexGeltung.DRAMATISCH: 0.05,
        DramatikKodexGeltung.GRUNDLEGEND_DRAMATISCH: 0.1,
    })
    _TIER_DELTA.update({
        DramatikKodexGeltung.GESPERRT: 0,
        DramatikKodexGeltung.DRAMATISCH: 1,
        DramatikKodexGeltung.GRUNDLEGEND_DRAMATISCH: 2,
    })
    _TYP_MAP.update({
        DramatikKodexGeltung.GESPERRT: DramatikKodexTyp.ANALYTISCH,
        DramatikKodexGeltung.DRAMATISCH: DramatikKodexTyp.SYNTHETISCH,
        DramatikKodexGeltung.GRUNDLEGEND_DRAMATISCH: DramatikKodexTyp.HISTORISCH,
    })
    _PROZEDUR_MAP.update({
        DramatikKodexGeltung.GESPERRT: DramatikKodexProzedur.INITIALISIEREN,
        DramatikKodexGeltung.DRAMATISCH: DramatikKodexProzedur.AKTIVIEREN,
        DramatikKodexGeltung.GRUNDLEGEND_DRAMATISCH: DramatikKodexProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        DramatikKodexGeltung.GESPERRT: [DramatikKodexGeltung.GESPERRT],
        DramatikKodexGeltung.DRAMATISCH: [DramatikKodexGeltung.DRAMATISCH],
        DramatikKodexGeltung.GRUNDLEGEND_DRAMATISCH: [DramatikKodexGeltung.GRUNDLEGEND_DRAMATISCH],
    })


_init_map()


def build_dramatik_kodex(*, kodex_id: str = "dramatik-kodex") -> DramatikKodex:
    parent = build_lyrik_charta(charta_id=f"{kodex_id}-parent")
    normen: List[DramatikKodexNorm] = []
    for g in DramatikKodexGeltung:
        normen.append(DramatikKodexNorm(
            dramatik_kodex_id=f"dk-{kodex_id}-{g.value}-001",
            geltung=g,
            typ=_TYP_MAP[g],
            literatur_weight=round(sum(n.literatur_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            literatur_tier=max(n.literatur_tier for n in parent.normen) + _TIER_DELTA[g],
            literatur_ids=[f"dk-{kodex_id}-{g.value}-001", f"dk-{kodex_id}-{g.value}-002"],
            literatur_tags=["literaturwissenschaft", "dramatik", g.value],
        ))
    return DramatikKodex(kodex_id=kodex_id, normen=normen, parent=parent)
