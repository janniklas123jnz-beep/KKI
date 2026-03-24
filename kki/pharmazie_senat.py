"""#647 PharmazieSenat — Pharmazie & Arzneimittelkunde (parent: TherapiePakt)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .therapie_pakt import TherapiePakt, build_therapie_pakt

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class PharmazieSenatGeltung(str, Enum):
    GESPERRT = "gesperrt"
    PHARMAZEUTISCH = "pharmazeutisch"
    GRUNDLEGEND_PHARMAZEUTISCH = "grundlegend-pharmazeutisch"


class PharmazieSenatTyp(str, Enum):
    KLINISCH = "klinisch"
    THEORETISCH = "theoretisch"
    ANGEWANDT = "angewandt"
    PRAEVENTIV = "praeventiv"


class PharmazieSenatProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class PharmazieSenatNorm:
    senat_id: str
    geltung: PharmazieSenatGeltung
    typ: PharmazieSenatTyp
    prozedur: PharmazieSenatProzedur
    medizin_weight: float
    medizin_tier: int
    medizin_ids: List[str]
    medizin_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class PharmazieSenat:
    senat_id: str
    normen: List[PharmazieSenatNorm]
    parent: TherapiePakt


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        PharmazieSenatGeltung.GESPERRT: 0.0,
        PharmazieSenatGeltung.PHARMAZEUTISCH: 0.05,
        PharmazieSenatGeltung.GRUNDLEGEND_PHARMAZEUTISCH: 0.1,
    })
    _TIER_DELTA.update({
        PharmazieSenatGeltung.GESPERRT: 0,
        PharmazieSenatGeltung.PHARMAZEUTISCH: 1,
        PharmazieSenatGeltung.GRUNDLEGEND_PHARMAZEUTISCH: 2,
    })
    _TYP_MAP.update({
        PharmazieSenatGeltung.GESPERRT: PharmazieSenatTyp.KLINISCH,
        PharmazieSenatGeltung.PHARMAZEUTISCH: PharmazieSenatTyp.THEORETISCH,
        PharmazieSenatGeltung.GRUNDLEGEND_PHARMAZEUTISCH: PharmazieSenatTyp.ANGEWANDT,
    })
    _PROZEDUR_MAP.update({
        PharmazieSenatGeltung.GESPERRT: PharmazieSenatProzedur.INITIALISIEREN,
        PharmazieSenatGeltung.PHARMAZEUTISCH: PharmazieSenatProzedur.AKTIVIEREN,
        PharmazieSenatGeltung.GRUNDLEGEND_PHARMAZEUTISCH: PharmazieSenatProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        PharmazieSenatGeltung.GESPERRT: [PharmazieSenatGeltung.GESPERRT],
        PharmazieSenatGeltung.PHARMAZEUTISCH: [PharmazieSenatGeltung.PHARMAZEUTISCH],
        PharmazieSenatGeltung.GRUNDLEGEND_PHARMAZEUTISCH: [PharmazieSenatGeltung.GRUNDLEGEND_PHARMAZEUTISCH],
    })


_init_map()


def build_pharmazie_senat(*, senat_id: str = "pharmazie-senat") -> PharmazieSenat:
    parent = build_therapie_pakt(pakt_id=f"{senat_id}-parent")
    normen: List[PharmazieSenatNorm] = []
    for g in PharmazieSenatGeltung:
        normen.append(PharmazieSenatNorm(
            senat_id=f"{senat_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            medizin_weight=round(sum(e.medizin_weight for e in parent.eintraege) * (1.0 + _WEIGHT_DELTA[g]), 4),
            medizin_tier=max(e.medizin_tier for e in parent.eintraege) + _TIER_DELTA[g],
            medizin_ids=[f"ps-{senat_id}-{g.value}-001", f"ps-{senat_id}-{g.value}-002"],
            medizin_tags=["medizin", "pharmazie", g.value],
        ))
    return PharmazieSenat(senat_id=senat_id, normen=normen, parent=parent)
