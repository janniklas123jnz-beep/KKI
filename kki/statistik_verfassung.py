from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .inferenzstatistik_charta import InferenzstatistikCharta, build_inferenzstatistik_charta


class StatistikVerfassungGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_STAT_SOUVERAEN = auto()
    STAT_SOUVERAEN = auto()
    STAT_SOUVERAEN_AKTIV = auto()
    STAT_SOUVERAEN_ABSOLUT = auto()


class StatistikVerfassungTyp(Enum):
    STATISTIKVERFASSUNG = auto()
    STATISTIKSOUVERAENITAET = auto()
    STATISTIKKONSTITUTION = auto()


class StatistikVerfassungProzedur(Enum):
    STATISTIKVERFASSUNGSANALYSE = auto()
    STATISTIKVERFASSUNGSSYNTHESE = auto()
    STATISTIKVERFASSUNGSBEWERTUNG = auto()


_WEIGHT_DELTA: dict[StatistikVerfassungGeltung, float] = {
    StatistikVerfassungGeltung.GESPERRT: 0.0,
    StatistikVerfassungGeltung.GRUNDLEGEND_STAT_SOUVERAEN: 2.1,
    StatistikVerfassungGeltung.STAT_SOUVERAEN: 4.2,
    StatistikVerfassungGeltung.STAT_SOUVERAEN_AKTIV: 6.3,
    StatistikVerfassungGeltung.STAT_SOUVERAEN_ABSOLUT: 8.4,
}

_TYP_MAP = {
    StatistikVerfassungGeltung.GESPERRT: StatistikVerfassungTyp.STATISTIKVERFASSUNG,
    StatistikVerfassungGeltung.GRUNDLEGEND_STAT_SOUVERAEN: StatistikVerfassungTyp.STATISTIKKONSTITUTION,
    StatistikVerfassungGeltung.STAT_SOUVERAEN: StatistikVerfassungTyp.STATISTIKKONSTITUTION,
    StatistikVerfassungGeltung.STAT_SOUVERAEN_AKTIV: StatistikVerfassungTyp.STATISTIKSOUVERAENITAET,
    StatistikVerfassungGeltung.STAT_SOUVERAEN_ABSOLUT: StatistikVerfassungTyp.STATISTIKSOUVERAENITAET,
}

_PROZEDUR_MAP = {
    StatistikVerfassungGeltung.GESPERRT: StatistikVerfassungProzedur.STATISTIKVERFASSUNGSANALYSE,
    StatistikVerfassungGeltung.GRUNDLEGEND_STAT_SOUVERAEN: StatistikVerfassungProzedur.STATISTIKVERFASSUNGSANALYSE,
    StatistikVerfassungGeltung.STAT_SOUVERAEN: StatistikVerfassungProzedur.STATISTIKVERFASSUNGSSYNTHESE,
    StatistikVerfassungGeltung.STAT_SOUVERAEN_AKTIV: StatistikVerfassungProzedur.STATISTIKVERFASSUNGSSYNTHESE,
    StatistikVerfassungGeltung.STAT_SOUVERAEN_ABSOLUT: StatistikVerfassungProzedur.STATISTIKVERFASSUNGSBEWERTUNG,
}


@dataclass(frozen=True)
class StatistikVerfassungsNorm:
    geltung: StatistikVerfassungGeltung
    stat_weight: float
    stat_tier: int
    stat_ids: tuple[str, ...]
    stat_tags: tuple[str, ...]
    typ: StatistikVerfassungTyp
    prozedur: StatistikVerfassungProzedur
    canonical: bool = True


@dataclass(frozen=True)
class StatistikVerfassung:
    normen: tuple[StatistikVerfassungsNorm, ...]
    parent: Optional[InferenzstatistikCharta] = None

    def aggregates_verfassung_signal(self) -> dict:
        return {
            "verfassung_id": "statistik-verfassung-760",
            "total_weight": round(sum(n.stat_weight for n in self.normen), 4),
            "norm_count": len(self.normen),
        }


def build_statistik_verfassung(parent: Optional[InferenzstatistikCharta] = None) -> StatistikVerfassung:
    if parent is None:
        parent = build_inferenzstatistik_charta()
    base = sum(n.stat_weight for n in parent.normen)
    tier_base = max(n.stat_tier for n in parent.normen)
    normen = tuple(
        StatistikVerfassungsNorm(
            geltung=g,
            stat_weight=round(base + _WEIGHT_DELTA[g], 4),
            stat_tier=tier_base + i + 1,
            stat_ids=(f"statistik-verfassung-{g.name.lower()}-001",),
            stat_tags=("statistik", "verfassung", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(StatistikVerfassungGeltung)
    )
    return StatistikVerfassung(normen=normen, parent=parent)
