from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .wasserressourcen_charta import WasserressourcenCharta, build_wasserressourcen_charta


class HydrologieVerfassungGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_HYDROLOGIE_SOUVERAEN = auto()
    HYDROLOGIE_SOUVERAEN = auto()
    HYDROLOGIE_SOUVERAEN_AKTIV = auto()
    HYDROLOGIE_SOUVERAEN_ABSOLUT = auto()


class HydrologieVerfassungTyp(Enum):
    HYDROLOGIEVERFASSUNG = auto()
    HYDROLOGIESOUVERAENITAET = auto()
    HYDROLOGIEKONSTITUTION = auto()


class HydrologieVerfassungProzedur(Enum):
    HYDROLOGIEVERFASSUNGSANALYSE = auto()
    HYDROLOGIEVERFASSUNGSSYNTHESE = auto()
    HYDROLOGIEVERFASSUNGSBEWERTUNG = auto()


_WEIGHT_DELTA: dict[HydrologieVerfassungGeltung, float] = {
    HydrologieVerfassungGeltung.GESPERRT: 0.0,
    HydrologieVerfassungGeltung.GRUNDLEGEND_HYDROLOGIE_SOUVERAEN: 2.1,
    HydrologieVerfassungGeltung.HYDROLOGIE_SOUVERAEN: 4.2,
    HydrologieVerfassungGeltung.HYDROLOGIE_SOUVERAEN_AKTIV: 6.3,
    HydrologieVerfassungGeltung.HYDROLOGIE_SOUVERAEN_ABSOLUT: 8.4,
}

_TYP_MAP = {
    HydrologieVerfassungGeltung.GESPERRT: HydrologieVerfassungTyp.HYDROLOGIEVERFASSUNG,
    HydrologieVerfassungGeltung.GRUNDLEGEND_HYDROLOGIE_SOUVERAEN: HydrologieVerfassungTyp.HYDROLOGIEKONSTITUTION,
    HydrologieVerfassungGeltung.HYDROLOGIE_SOUVERAEN: HydrologieVerfassungTyp.HYDROLOGIEKONSTITUTION,
    HydrologieVerfassungGeltung.HYDROLOGIE_SOUVERAEN_AKTIV: HydrologieVerfassungTyp.HYDROLOGIESOUVERAENITAET,
    HydrologieVerfassungGeltung.HYDROLOGIE_SOUVERAEN_ABSOLUT: HydrologieVerfassungTyp.HYDROLOGIESOUVERAENITAET,
}

_PROZEDUR_MAP = {
    HydrologieVerfassungGeltung.GESPERRT: HydrologieVerfassungProzedur.HYDROLOGIEVERFASSUNGSANALYSE,
    HydrologieVerfassungGeltung.GRUNDLEGEND_HYDROLOGIE_SOUVERAEN: HydrologieVerfassungProzedur.HYDROLOGIEVERFASSUNGSANALYSE,
    HydrologieVerfassungGeltung.HYDROLOGIE_SOUVERAEN: HydrologieVerfassungProzedur.HYDROLOGIEVERFASSUNGSSYNTHESE,
    HydrologieVerfassungGeltung.HYDROLOGIE_SOUVERAEN_AKTIV: HydrologieVerfassungProzedur.HYDROLOGIEVERFASSUNGSSYNTHESE,
    HydrologieVerfassungGeltung.HYDROLOGIE_SOUVERAEN_ABSOLUT: HydrologieVerfassungProzedur.HYDROLOGIEVERFASSUNGSBEWERTUNG,
}


@dataclass(frozen=True)
class HydrologieVerfassungsNorm:
    geltung: HydrologieVerfassungGeltung
    hydrologie_weight: float
    hydrologie_tier: int
    hydrologie_ids: tuple[str, ...]
    hydrologie_tags: tuple[str, ...]
    typ: HydrologieVerfassungTyp
    prozedur: HydrologieVerfassungProzedur
    canonical: bool = True


@dataclass(frozen=True)
class HydrologieVerfassung:
    normen: tuple[HydrologieVerfassungsNorm, ...]
    parent: Optional[WasserressourcenCharta] = None

    def aggregates_verfassung_signal(self) -> dict:
        return {
            "verfassung_id": "hydrologie-verfassung-820",
            "total_weight": round(sum(n.hydrologie_weight for n in self.normen), 4),
            "norm_count": len(self.normen),
        }


def build_hydrologie_verfassung(parent: Optional[WasserressourcenCharta] = None) -> HydrologieVerfassung:
    if parent is None:
        parent = build_wasserressourcen_charta()
    base = sum(n.hydrologie_weight for n in parent.normen)
    tier_base = max(n.hydrologie_tier for n in parent.normen)
    normen = tuple(
        HydrologieVerfassungsNorm(
            geltung=g,
            hydrologie_weight=round(base + _WEIGHT_DELTA[g], 4),
            hydrologie_tier=tier_base + i + 1,
            hydrologie_ids=(f"hydrologie-verfassung-{g.name.lower()}-001",),
            hydrologie_tags=("hydrologie", "verfassung", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(HydrologieVerfassungGeltung)
    )
    return HydrologieVerfassung(normen=normen, parent=parent)
