from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .wettervorhersage_charta import WettervorhersageCharta, build_wettervorhersage_charta


class MeteorologieVerfassungGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_METEOROLOGIE_SOUVERAEN = auto()
    METEOROLOGIE_SOUVERAEN = auto()
    METEOROLOGIE_SOUVERAEN_AKTIV = auto()
    METEOROLOGIE_SOUVERAEN_ABSOLUT = auto()


class MeteorologieVerfassungTyp(Enum):
    METEOROLOGIEVERFASSUNG = auto()
    METEOROLOGIESOUVERAENITAET = auto()
    METEOROLOGIEKONSTITUTION = auto()


class MeteorologieVerfassungProzedur(Enum):
    METEOROLOGIEVERFASSUNGSANALYSE = auto()
    METEOROLOGIEVERFASSUNGSSYNTHESE = auto()
    METEOROLOGIEVERFASSUNGSBEWERTUNG = auto()


_WEIGHT_DELTA: dict[MeteorologieVerfassungGeltung, float] = {
    MeteorologieVerfassungGeltung.GESPERRT: 0.0,
    MeteorologieVerfassungGeltung.GRUNDLEGEND_METEOROLOGIE_SOUVERAEN: 2.1,
    MeteorologieVerfassungGeltung.METEOROLOGIE_SOUVERAEN: 4.2,
    MeteorologieVerfassungGeltung.METEOROLOGIE_SOUVERAEN_AKTIV: 6.3,
    MeteorologieVerfassungGeltung.METEOROLOGIE_SOUVERAEN_ABSOLUT: 8.4,
}

_TYP_MAP = {
    MeteorologieVerfassungGeltung.GESPERRT: MeteorologieVerfassungTyp.METEOROLOGIEVERFASSUNG,
    MeteorologieVerfassungGeltung.GRUNDLEGEND_METEOROLOGIE_SOUVERAEN: MeteorologieVerfassungTyp.METEOROLOGIEKONSTITUTION,
    MeteorologieVerfassungGeltung.METEOROLOGIE_SOUVERAEN: MeteorologieVerfassungTyp.METEOROLOGIEKONSTITUTION,
    MeteorologieVerfassungGeltung.METEOROLOGIE_SOUVERAEN_AKTIV: MeteorologieVerfassungTyp.METEOROLOGIESOUVERAENITAET,
    MeteorologieVerfassungGeltung.METEOROLOGIE_SOUVERAEN_ABSOLUT: MeteorologieVerfassungTyp.METEOROLOGIESOUVERAENITAET,
}

_PROZEDUR_MAP = {
    MeteorologieVerfassungGeltung.GESPERRT: MeteorologieVerfassungProzedur.METEOROLOGIEVERFASSUNGSANALYSE,
    MeteorologieVerfassungGeltung.GRUNDLEGEND_METEOROLOGIE_SOUVERAEN: MeteorologieVerfassungProzedur.METEOROLOGIEVERFASSUNGSANALYSE,
    MeteorologieVerfassungGeltung.METEOROLOGIE_SOUVERAEN: MeteorologieVerfassungProzedur.METEOROLOGIEVERFASSUNGSSYNTHESE,
    MeteorologieVerfassungGeltung.METEOROLOGIE_SOUVERAEN_AKTIV: MeteorologieVerfassungProzedur.METEOROLOGIEVERFASSUNGSSYNTHESE,
    MeteorologieVerfassungGeltung.METEOROLOGIE_SOUVERAEN_ABSOLUT: MeteorologieVerfassungProzedur.METEOROLOGIEVERFASSUNGSBEWERTUNG,
}


@dataclass(frozen=True)
class MeteorologieVerfassungsNorm:
    geltung: MeteorologieVerfassungGeltung
    meteorologie_weight: float
    meteorologie_tier: int
    meteorologie_ids: tuple[str, ...]
    meteorologie_tags: tuple[str, ...]
    typ: MeteorologieVerfassungTyp
    prozedur: MeteorologieVerfassungProzedur
    canonical: bool = True


@dataclass(frozen=True)
class MeteorologieVerfassung:
    normen: tuple[MeteorologieVerfassungsNorm, ...]
    parent: Optional[WettervorhersageCharta] = None

    def aggregates_verfassung_signal(self) -> dict:
        return {
            "verfassung_id": "meteorologie-verfassung-840",
            "total_weight": round(sum(n.meteorologie_weight for n in self.normen), 4),
            "norm_count": len(self.normen),
        }


def build_meteorologie_verfassung(parent: Optional[WettervorhersageCharta] = None) -> MeteorologieVerfassung:
    if parent is None:
        parent = build_wettervorhersage_charta()
    base = sum(n.meteorologie_weight for n in parent.normen)
    tier_base = max(n.meteorologie_tier for n in parent.normen)
    normen = tuple(
        MeteorologieVerfassungsNorm(
            geltung=g,
            meteorologie_weight=round(base + _WEIGHT_DELTA[g], 4),
            meteorologie_tier=tier_base + i + 1,
            meteorologie_ids=(f"meteorologie-verfassung-{g.name.lower()}-001",),
            meteorologie_tags=("meteorologie", "verfassung", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(MeteorologieVerfassungGeltung)
    )
    return MeteorologieVerfassung(normen=normen, parent=parent)
