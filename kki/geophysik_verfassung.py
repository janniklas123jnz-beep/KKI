from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .erdkern_charta import ErdkernCharta, build_erdkern_charta


class GeophysikVerfassungGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_GEOPHYSIK_SOUVERAEN = auto()
    GEOPHYSIK_SOUVERAEN = auto()
    GEOPHYSIK_SOUVERAEN_AKTIV = auto()
    GEOPHYSIK_SOUVERAEN_ABSOLUT = auto()


class GeophysikVerfassungTyp(Enum):
    GEOPHYSIKVERFASSUNG = auto()
    GEOPHYSIKSOUVERAENITAET = auto()
    GEOPHYSIKKONSTITUTION = auto()


class GeophysikVerfassungProzedur(Enum):
    GEOPHYSIKVERFASSUNGSANALYSE = auto()
    GEOPHYSIKVERFASSUNGSSYNTHESE = auto()
    GEOPHYSIKVERFASSUNGSBEWERTUNG = auto()


_WEIGHT_DELTA: dict[GeophysikVerfassungGeltung, float] = {
    GeophysikVerfassungGeltung.GESPERRT: 0.0,
    GeophysikVerfassungGeltung.GRUNDLEGEND_GEOPHYSIK_SOUVERAEN: 2.1,
    GeophysikVerfassungGeltung.GEOPHYSIK_SOUVERAEN: 4.2,
    GeophysikVerfassungGeltung.GEOPHYSIK_SOUVERAEN_AKTIV: 6.3,
    GeophysikVerfassungGeltung.GEOPHYSIK_SOUVERAEN_ABSOLUT: 8.4,
}

_TYP_MAP = {
    GeophysikVerfassungGeltung.GESPERRT: GeophysikVerfassungTyp.GEOPHYSIKVERFASSUNG,
    GeophysikVerfassungGeltung.GRUNDLEGEND_GEOPHYSIK_SOUVERAEN: GeophysikVerfassungTyp.GEOPHYSIKKONSTITUTION,
    GeophysikVerfassungGeltung.GEOPHYSIK_SOUVERAEN: GeophysikVerfassungTyp.GEOPHYSIKKONSTITUTION,
    GeophysikVerfassungGeltung.GEOPHYSIK_SOUVERAEN_AKTIV: GeophysikVerfassungTyp.GEOPHYSIKSOUVERAENITAET,
    GeophysikVerfassungGeltung.GEOPHYSIK_SOUVERAEN_ABSOLUT: GeophysikVerfassungTyp.GEOPHYSIKSOUVERAENITAET,
}

_PROZEDUR_MAP = {
    GeophysikVerfassungGeltung.GESPERRT: GeophysikVerfassungProzedur.GEOPHYSIKVERFASSUNGSANALYSE,
    GeophysikVerfassungGeltung.GRUNDLEGEND_GEOPHYSIK_SOUVERAEN: GeophysikVerfassungProzedur.GEOPHYSIKVERFASSUNGSANALYSE,
    GeophysikVerfassungGeltung.GEOPHYSIK_SOUVERAEN: GeophysikVerfassungProzedur.GEOPHYSIKVERFASSUNGSSYNTHESE,
    GeophysikVerfassungGeltung.GEOPHYSIK_SOUVERAEN_AKTIV: GeophysikVerfassungProzedur.GEOPHYSIKVERFASSUNGSSYNTHESE,
    GeophysikVerfassungGeltung.GEOPHYSIK_SOUVERAEN_ABSOLUT: GeophysikVerfassungProzedur.GEOPHYSIKVERFASSUNGSBEWERTUNG,
}


@dataclass(frozen=True)
class GeophysikVerfassungsNorm:
    geltung: GeophysikVerfassungGeltung
    geophysik_weight: float
    geophysik_tier: int
    geophysik_ids: tuple[str, ...]
    geophysik_tags: tuple[str, ...]
    typ: GeophysikVerfassungTyp
    prozedur: GeophysikVerfassungProzedur
    canonical: bool = True


@dataclass(frozen=True)
class GeophysikVerfassung:
    normen: tuple[GeophysikVerfassungsNorm, ...]
    parent: Optional[ErdkernCharta] = None

    def aggregates_verfassung_signal(self) -> dict:
        return {
            "verfassung_id": "geophysik-verfassung-810",
            "total_weight": round(sum(n.geophysik_weight for n in self.normen), 4),
            "norm_count": len(self.normen),
        }


def build_geophysik_verfassung(parent: Optional[ErdkernCharta] = None) -> GeophysikVerfassung:
    if parent is None:
        parent = build_erdkern_charta()
    base = sum(n.geophysik_weight for n in parent.normen)
    tier_base = max(n.geophysik_tier for n in parent.normen)
    normen = tuple(
        GeophysikVerfassungsNorm(
            geltung=g,
            geophysik_weight=round(base + _WEIGHT_DELTA[g], 4),
            geophysik_tier=tier_base + i + 1,
            geophysik_ids=(f"geophysik-verfassung-{g.name.lower()}-001",),
            geophysik_tags=("geophysik", "verfassung", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(GeophysikVerfassungGeltung)
    )
    return GeophysikVerfassung(normen=normen, parent=parent)
