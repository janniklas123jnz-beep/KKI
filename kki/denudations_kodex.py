from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .reliefentwicklung_charta import ReliefentwicklungCharta, build_reliefentwicklung_charta


class DenudationsKodexGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_GEOMORPHOLOGISCH = auto()
    GEOMORPHOLOGISCH = auto()
    GEOMORPHOLOGISCH_AKTIV = auto()
    GEOMORPHOLOGIE_SOUVERAEN = auto()


class DenudationsKodexTyp(Enum):
    DENUDATIONSKODEX = auto()
    DENUDATIONSSYSTEM = auto()
    DENUDATIONSKOMPONENTE = auto()


class DenudationsKodexProzedur(Enum):
    DENUDATIONSANALYSE = auto()
    DENUDATIONSSYNTHESE = auto()
    DENUDATIONSBEWERTUNG = auto()


_WEIGHT_DELTA: dict[DenudationsKodexGeltung, float] = {
    DenudationsKodexGeltung.GESPERRT: 0.0,
    DenudationsKodexGeltung.GRUNDLEGEND_GEOMORPHOLOGISCH: 1.5,
    DenudationsKodexGeltung.GEOMORPHOLOGISCH: 3.0,
    DenudationsKodexGeltung.GEOMORPHOLOGISCH_AKTIV: 4.5,
    DenudationsKodexGeltung.GEOMORPHOLOGIE_SOUVERAEN: 6.0,
}

_TYP_MAP = {
    DenudationsKodexGeltung.GESPERRT: DenudationsKodexTyp.DENUDATIONSKODEX,
    DenudationsKodexGeltung.GRUNDLEGEND_GEOMORPHOLOGISCH: DenudationsKodexTyp.DENUDATIONSKOMPONENTE,
    DenudationsKodexGeltung.GEOMORPHOLOGISCH: DenudationsKodexTyp.DENUDATIONSKOMPONENTE,
    DenudationsKodexGeltung.GEOMORPHOLOGISCH_AKTIV: DenudationsKodexTyp.DENUDATIONSSYSTEM,
    DenudationsKodexGeltung.GEOMORPHOLOGIE_SOUVERAEN: DenudationsKodexTyp.DENUDATIONSSYSTEM,
}

_PROZEDUR_MAP = {
    DenudationsKodexGeltung.GESPERRT: DenudationsKodexProzedur.DENUDATIONSANALYSE,
    DenudationsKodexGeltung.GRUNDLEGEND_GEOMORPHOLOGISCH: DenudationsKodexProzedur.DENUDATIONSANALYSE,
    DenudationsKodexGeltung.GEOMORPHOLOGISCH: DenudationsKodexProzedur.DENUDATIONSSYNTHESE,
    DenudationsKodexGeltung.GEOMORPHOLOGISCH_AKTIV: DenudationsKodexProzedur.DENUDATIONSSYNTHESE,
    DenudationsKodexGeltung.GEOMORPHOLOGIE_SOUVERAEN: DenudationsKodexProzedur.DENUDATIONSBEWERTUNG,
}


@dataclass(frozen=True)
class DenudationsKodexEintrag:
    geltung: DenudationsKodexGeltung
    geomorphologie_weight: float
    geomorphologie_tier: int
    geomorphologie_ids: tuple[str, ...]
    geomorphologie_tags: tuple[str, ...]
    typ: DenudationsKodexTyp
    prozedur: DenudationsKodexProzedur
    canonical: bool = True


@dataclass(frozen=True)
class DenudationsKodex:
    eintraege: tuple[DenudationsKodexEintrag, ...]
    parent: Optional[ReliefentwicklungCharta] = None


def build_denudations_kodex(parent: Optional[ReliefentwicklungCharta] = None) -> DenudationsKodex:
    if parent is None:
        parent = build_reliefentwicklung_charta()
    base = sum(n.geomorphologie_weight for n in parent.normen)
    eintraege = tuple(
        DenudationsKodexEintrag(
            geltung=g,
            geomorphologie_weight=round(base + _WEIGHT_DELTA[g], 4),
            geomorphologie_tier=i + 1,
            geomorphologie_ids=(f"denudations-kodex-{g.name.lower()}-001",),
            geomorphologie_tags=("geomorphologie", "denudation", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(DenudationsKodexGeltung)
    )
    return DenudationsKodex(eintraege=eintraege, parent=parent)
