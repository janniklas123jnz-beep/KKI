from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .ozean_norm import OzeanNormSatz, build_ozean_norm


class MeeresforschungChartaGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_OZEANOGRAPHISCH = auto()
    OZEANOGRAPHISCH = auto()
    OZEANOGRAPHISCH_AKTIV = auto()
    OZEAN_SOUVERAEN = auto()


class MeeresforschungChartaTyp(Enum):
    MEERESFORSCHUNG = auto()
    FORSCHUNGSSYSTEM = auto()
    FORSCHUNGSKOMPONENTE = auto()


class MeeresforschungChartaProzedur(Enum):
    FORSCHUNGSANALYSE = auto()
    FORSCHUNGSSYNTHESE = auto()
    FORSCHUNGSBEWERTUNG = auto()


_WEIGHT_DELTA: dict[MeeresforschungChartaGeltung, float] = {
    MeeresforschungChartaGeltung.GESPERRT: 0.0,
    MeeresforschungChartaGeltung.GRUNDLEGEND_OZEANOGRAPHISCH: 2.0,
    MeeresforschungChartaGeltung.OZEANOGRAPHISCH: 4.0,
    MeeresforschungChartaGeltung.OZEANOGRAPHISCH_AKTIV: 6.0,
    MeeresforschungChartaGeltung.OZEAN_SOUVERAEN: 8.0,
}

_TYP_MAP = {
    MeeresforschungChartaGeltung.GESPERRT: MeeresforschungChartaTyp.MEERESFORSCHUNG,
    MeeresforschungChartaGeltung.GRUNDLEGEND_OZEANOGRAPHISCH: MeeresforschungChartaTyp.FORSCHUNGSKOMPONENTE,
    MeeresforschungChartaGeltung.OZEANOGRAPHISCH: MeeresforschungChartaTyp.FORSCHUNGSKOMPONENTE,
    MeeresforschungChartaGeltung.OZEANOGRAPHISCH_AKTIV: MeeresforschungChartaTyp.FORSCHUNGSSYSTEM,
    MeeresforschungChartaGeltung.OZEAN_SOUVERAEN: MeeresforschungChartaTyp.FORSCHUNGSSYSTEM,
}

_PROZEDUR_MAP = {
    MeeresforschungChartaGeltung.GESPERRT: MeeresforschungChartaProzedur.FORSCHUNGSANALYSE,
    MeeresforschungChartaGeltung.GRUNDLEGEND_OZEANOGRAPHISCH: MeeresforschungChartaProzedur.FORSCHUNGSANALYSE,
    MeeresforschungChartaGeltung.OZEANOGRAPHISCH: MeeresforschungChartaProzedur.FORSCHUNGSSYNTHESE,
    MeeresforschungChartaGeltung.OZEANOGRAPHISCH_AKTIV: MeeresforschungChartaProzedur.FORSCHUNGSSYNTHESE,
    MeeresforschungChartaGeltung.OZEAN_SOUVERAEN: MeeresforschungChartaProzedur.FORSCHUNGSBEWERTUNG,
}


@dataclass(frozen=True)
class MeeresforschungChartaNorm:
    geltung: MeeresforschungChartaGeltung
    ozean_weight: float
    ozean_tier: int
    ozean_ids: tuple[str, ...]
    ozean_tags: tuple[str, ...]
    typ: MeeresforschungChartaTyp
    prozedur: MeeresforschungChartaProzedur
    canonical: bool = True


@dataclass(frozen=True)
class MeeresforschungCharta:
    normen: tuple[MeeresforschungChartaNorm, ...]
    parent: Optional[OzeanNormSatz] = None


def build_meeresforschung_charta(parent: Optional[OzeanNormSatz] = None) -> MeeresforschungCharta:
    if parent is None:
        parent = build_ozean_norm()
    base = sum(e.ozean_norm_weight for e in parent.normen)
    tier_base = max(e.ozean_norm_tier for e in parent.normen)
    normen = tuple(
        MeeresforschungChartaNorm(
            geltung=g,
            ozean_weight=round(base + _WEIGHT_DELTA[g], 4),
            ozean_tier=tier_base + i + 1,
            ozean_ids=(f"meeresforschung-{g.name.lower()}-001",),
            ozean_tags=("ozean", "meeresforschung", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(MeeresforschungChartaGeltung)
    )
    return MeeresforschungCharta(normen=normen, parent=parent)
