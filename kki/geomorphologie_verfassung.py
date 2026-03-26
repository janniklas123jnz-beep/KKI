from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .karstsystem_charta import KarstsystemCharta, build_karstsystem_charta


class GeomorphologieVerfassungGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_GEOMORPHOLOGIE_SOUVERAEN = auto()
    GEOMORPHOLOGIE_SOUVERAEN = auto()
    GEOMORPHOLOGIE_SOUVERAEN_AKTIV = auto()
    GEOMORPHOLOGIE_SOUVERAEN_ABSOLUT = auto()


class GeomorphologieVerfassungTyp(Enum):
    GEOMORPHOLOGIEVERFASSUNG = auto()
    GEOMORPHOLOGIESOUVERAENITAET = auto()
    GEOMORPHOLOGIEKONSTITUTION = auto()


class GeomorphologieVerfassungProzedur(Enum):
    GEOMORPHOLOGIEVERFASSUNGSANALYSE = auto()
    GEOMORPHOLOGIEVERFASSUNGSSYNTHESE = auto()
    GEOMORPHOLOGIEVERFASSUNGSBEWERTUNG = auto()


_WEIGHT_DELTA: dict[GeomorphologieVerfassungGeltung, float] = {
    GeomorphologieVerfassungGeltung.GESPERRT: 0.0,
    GeomorphologieVerfassungGeltung.GRUNDLEGEND_GEOMORPHOLOGIE_SOUVERAEN: 2.1,
    GeomorphologieVerfassungGeltung.GEOMORPHOLOGIE_SOUVERAEN: 4.2,
    GeomorphologieVerfassungGeltung.GEOMORPHOLOGIE_SOUVERAEN_AKTIV: 6.3,
    GeomorphologieVerfassungGeltung.GEOMORPHOLOGIE_SOUVERAEN_ABSOLUT: 8.4,
}

_TYP_MAP = {
    GeomorphologieVerfassungGeltung.GESPERRT: GeomorphologieVerfassungTyp.GEOMORPHOLOGIEVERFASSUNG,
    GeomorphologieVerfassungGeltung.GRUNDLEGEND_GEOMORPHOLOGIE_SOUVERAEN: GeomorphologieVerfassungTyp.GEOMORPHOLOGIEKONSTITUTION,
    GeomorphologieVerfassungGeltung.GEOMORPHOLOGIE_SOUVERAEN: GeomorphologieVerfassungTyp.GEOMORPHOLOGIEKONSTITUTION,
    GeomorphologieVerfassungGeltung.GEOMORPHOLOGIE_SOUVERAEN_AKTIV: GeomorphologieVerfassungTyp.GEOMORPHOLOGIESOUVERAENITAET,
    GeomorphologieVerfassungGeltung.GEOMORPHOLOGIE_SOUVERAEN_ABSOLUT: GeomorphologieVerfassungTyp.GEOMORPHOLOGIESOUVERAENITAET,
}

_PROZEDUR_MAP = {
    GeomorphologieVerfassungGeltung.GESPERRT: GeomorphologieVerfassungProzedur.GEOMORPHOLOGIEVERFASSUNGSANALYSE,
    GeomorphologieVerfassungGeltung.GRUNDLEGEND_GEOMORPHOLOGIE_SOUVERAEN: GeomorphologieVerfassungProzedur.GEOMORPHOLOGIEVERFASSUNGSANALYSE,
    GeomorphologieVerfassungGeltung.GEOMORPHOLOGIE_SOUVERAEN: GeomorphologieVerfassungProzedur.GEOMORPHOLOGIEVERFASSUNGSSYNTHESE,
    GeomorphologieVerfassungGeltung.GEOMORPHOLOGIE_SOUVERAEN_AKTIV: GeomorphologieVerfassungProzedur.GEOMORPHOLOGIEVERFASSUNGSSYNTHESE,
    GeomorphologieVerfassungGeltung.GEOMORPHOLOGIE_SOUVERAEN_ABSOLUT: GeomorphologieVerfassungProzedur.GEOMORPHOLOGIEVERFASSUNGSBEWERTUNG,
}


@dataclass(frozen=True)
class GeomorphologieVerfassungsNorm:
    geltung: GeomorphologieVerfassungGeltung
    geomorphologie_weight: float
    geomorphologie_tier: int
    geomorphologie_ids: tuple[str, ...]
    geomorphologie_tags: tuple[str, ...]
    typ: GeomorphologieVerfassungTyp
    prozedur: GeomorphologieVerfassungProzedur
    canonical: bool = True


@dataclass(frozen=True)
class GeomorphologieVerfassung:
    normen: tuple[GeomorphologieVerfassungsNorm, ...]
    parent: Optional[KarstsystemCharta] = None

    def aggregates_verfassung_signal(self) -> dict:
        return {
            "verfassung_id": "geomorphologie-verfassung-860",
            "total_weight": round(sum(n.geomorphologie_weight for n in self.normen), 4),
            "norm_count": len(self.normen),
        }


def build_geomorphologie_verfassung(parent: Optional[KarstsystemCharta] = None) -> GeomorphologieVerfassung:
    if parent is None:
        parent = build_karstsystem_charta()
    base = sum(n.geomorphologie_weight for n in parent.normen)
    tier_base = max(n.geomorphologie_tier for n in parent.normen)
    normen = tuple(
        GeomorphologieVerfassungsNorm(
            geltung=g,
            geomorphologie_weight=round(base + _WEIGHT_DELTA[g], 4),
            geomorphologie_tier=tier_base + i + 1,
            geomorphologie_ids=(f"geomorphologie-verfassung-{g.name.lower()}-001",),
            geomorphologie_tags=("geomorphologie", "verfassung", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(GeomorphologieVerfassungGeltung)
    )
    return GeomorphologieVerfassung(normen=normen, parent=parent)
