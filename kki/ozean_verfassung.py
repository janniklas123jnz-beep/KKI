from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .meeresforschung_charta import MeeresforschungCharta, build_meeresforschung_charta


class OzeanVerfassungGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_OZEAN_SOUVERAEN = auto()
    OZEAN_SOUVERAEN = auto()
    OZEAN_SOUVERAEN_AKTIV = auto()
    OZEAN_SOUVERAEN_ABSOLUT = auto()


class OzeanVerfassungTyp(Enum):
    OZEANVERFASSUNG = auto()
    OZEANSOUVERAENITAET = auto()
    OZEANKONSTITUTION = auto()


class OzeanVerfassungProzedur(Enum):
    OZEANVERFASSUNGSANALYSE = auto()
    OZEANVERFASSUNGSSYNTHESE = auto()
    OZEANVERFASSUNGSBEWERTUNG = auto()


_WEIGHT_DELTA: dict[OzeanVerfassungGeltung, float] = {
    OzeanVerfassungGeltung.GESPERRT: 0.0,
    OzeanVerfassungGeltung.GRUNDLEGEND_OZEAN_SOUVERAEN: 2.1,
    OzeanVerfassungGeltung.OZEAN_SOUVERAEN: 4.2,
    OzeanVerfassungGeltung.OZEAN_SOUVERAEN_AKTIV: 6.3,
    OzeanVerfassungGeltung.OZEAN_SOUVERAEN_ABSOLUT: 8.4,
}

_TYP_MAP = {
    OzeanVerfassungGeltung.GESPERRT: OzeanVerfassungTyp.OZEANVERFASSUNG,
    OzeanVerfassungGeltung.GRUNDLEGEND_OZEAN_SOUVERAEN: OzeanVerfassungTyp.OZEANKONSTITUTION,
    OzeanVerfassungGeltung.OZEAN_SOUVERAEN: OzeanVerfassungTyp.OZEANKONSTITUTION,
    OzeanVerfassungGeltung.OZEAN_SOUVERAEN_AKTIV: OzeanVerfassungTyp.OZEANSOUVERAENITAET,
    OzeanVerfassungGeltung.OZEAN_SOUVERAEN_ABSOLUT: OzeanVerfassungTyp.OZEANSOUVERAENITAET,
}

_PROZEDUR_MAP = {
    OzeanVerfassungGeltung.GESPERRT: OzeanVerfassungProzedur.OZEANVERFASSUNGSANALYSE,
    OzeanVerfassungGeltung.GRUNDLEGEND_OZEAN_SOUVERAEN: OzeanVerfassungProzedur.OZEANVERFASSUNGSANALYSE,
    OzeanVerfassungGeltung.OZEAN_SOUVERAEN: OzeanVerfassungProzedur.OZEANVERFASSUNGSSYNTHESE,
    OzeanVerfassungGeltung.OZEAN_SOUVERAEN_AKTIV: OzeanVerfassungProzedur.OZEANVERFASSUNGSSYNTHESE,
    OzeanVerfassungGeltung.OZEAN_SOUVERAEN_ABSOLUT: OzeanVerfassungProzedur.OZEANVERFASSUNGSBEWERTUNG,
}


@dataclass(frozen=True)
class OzeanVerfassungsNorm:
    geltung: OzeanVerfassungGeltung
    ozean_weight: float
    ozean_tier: int
    ozean_ids: tuple[str, ...]
    ozean_tags: tuple[str, ...]
    typ: OzeanVerfassungTyp
    prozedur: OzeanVerfassungProzedur
    canonical: bool = True


@dataclass(frozen=True)
class OzeanVerfassung:
    normen: tuple[OzeanVerfassungsNorm, ...]
    parent: Optional[MeeresforschungCharta] = None

    def aggregates_verfassung_signal(self) -> dict:
        return {
            "verfassung_id": "ozean-verfassung-800",
            "total_weight": round(sum(n.ozean_weight for n in self.normen), 4),
            "norm_count": len(self.normen),
        }


def build_ozean_verfassung(parent: Optional[MeeresforschungCharta] = None) -> OzeanVerfassung:
    if parent is None:
        parent = build_meeresforschung_charta()
    base = sum(n.ozean_weight for n in parent.normen)
    tier_base = max(n.ozean_tier for n in parent.normen)
    normen = tuple(
        OzeanVerfassungsNorm(
            geltung=g,
            ozean_weight=round(base + _WEIGHT_DELTA[g], 4),
            ozean_tier=tier_base + i + 1,
            ozean_ids=(f"ozean-verfassung-{g.name.lower()}-001",),
            ozean_tags=("ozean", "verfassung", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(OzeanVerfassungGeltung)
    )
    return OzeanVerfassung(normen=normen, parent=parent)
