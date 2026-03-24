"""#643 PhysiologieCharta — Physiologie & Körperfunktionen (parent: AnatomieRegister)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .anatomie_register import AnatomieRegister, build_anatomie_register

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class PhysiologieChartaGeltung(str, Enum):
    GESPERRT = "gesperrt"
    PHYSIOLOGISCH = "physiologisch"
    GRUNDLEGEND_PHYSIOLOGISCH = "grundlegend-physiologisch"


class PhysiologieChartaTyp(str, Enum):
    KLINISCH = "klinisch"
    THEORETISCH = "theoretisch"
    ANGEWANDT = "angewandt"
    PRAEVENTIV = "praeventiv"


class PhysiologieChartaProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class PhysiologieChartaNorm:
    charta_id: str
    geltung: PhysiologieChartaGeltung
    typ: PhysiologieChartaTyp
    prozedur: PhysiologieChartaProzedur
    medizin_weight: float
    medizin_tier: int
    medizin_ids: List[str]
    medizin_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class PhysiologieCharta:
    charta_id: str
    normen: List[PhysiologieChartaNorm]
    parent: AnatomieRegister


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        PhysiologieChartaGeltung.GESPERRT: 0.0,
        PhysiologieChartaGeltung.PHYSIOLOGISCH: 0.05,
        PhysiologieChartaGeltung.GRUNDLEGEND_PHYSIOLOGISCH: 0.1,
    })
    _TIER_DELTA.update({
        PhysiologieChartaGeltung.GESPERRT: 0,
        PhysiologieChartaGeltung.PHYSIOLOGISCH: 1,
        PhysiologieChartaGeltung.GRUNDLEGEND_PHYSIOLOGISCH: 2,
    })
    _TYP_MAP.update({
        PhysiologieChartaGeltung.GESPERRT: PhysiologieChartaTyp.KLINISCH,
        PhysiologieChartaGeltung.PHYSIOLOGISCH: PhysiologieChartaTyp.THEORETISCH,
        PhysiologieChartaGeltung.GRUNDLEGEND_PHYSIOLOGISCH: PhysiologieChartaTyp.ANGEWANDT,
    })
    _PROZEDUR_MAP.update({
        PhysiologieChartaGeltung.GESPERRT: PhysiologieChartaProzedur.INITIALISIEREN,
        PhysiologieChartaGeltung.PHYSIOLOGISCH: PhysiologieChartaProzedur.AKTIVIEREN,
        PhysiologieChartaGeltung.GRUNDLEGEND_PHYSIOLOGISCH: PhysiologieChartaProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        PhysiologieChartaGeltung.GESPERRT: [PhysiologieChartaGeltung.GESPERRT],
        PhysiologieChartaGeltung.PHYSIOLOGISCH: [PhysiologieChartaGeltung.PHYSIOLOGISCH],
        PhysiologieChartaGeltung.GRUNDLEGEND_PHYSIOLOGISCH: [PhysiologieChartaGeltung.GRUNDLEGEND_PHYSIOLOGISCH],
    })


_init_map()


def build_physiologie_charta(*, charta_id: str = "physiologie-charta") -> PhysiologieCharta:
    parent = build_anatomie_register(register_id=f"{charta_id}-parent")
    normen: List[PhysiologieChartaNorm] = []
    for g in PhysiologieChartaGeltung:
        normen.append(PhysiologieChartaNorm(
            charta_id=f"{charta_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            medizin_weight=round(sum(e.medizin_weight for e in parent.eintraege) * (1.0 + _WEIGHT_DELTA[g]), 4),
            medizin_tier=max(e.medizin_tier for e in parent.eintraege) + _TIER_DELTA[g],
            medizin_ids=[f"pc-{charta_id}-{g.value}-001", f"pc-{charta_id}-{g.value}-002"],
            medizin_tags=["medizin", "physiologie", g.value],
        ))
    return PhysiologieCharta(charta_id=charta_id, normen=normen, parent=parent)
