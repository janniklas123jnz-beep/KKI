from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .taphonomie_charta import TaphonomieCharta, build_taphonomie_charta


class PalaeontologieVerfassungGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_PALAEONTOLOGIE_SOUVERAEN = auto()
    PALAEONTOLOGIE_SOUVERAEN = auto()
    PALAEONTOLOGIE_SOUVERAEN_AKTIV = auto()
    PALAEONTOLOGIE_SOUVERAEN_ABSOLUT = auto()


class PalaeontologieVerfassungTyp(Enum):
    PALAEONTOLOGIEVERFASSUNG = auto()
    PALAEONTOLOGIESOUVERAENITAET = auto()
    PALAEONTOLOGIEKONSTITUTION = auto()


class PalaeontologieVerfassungProzedur(Enum):
    PALAEONTOLOGIEVERFASSUNGSANALYSE = auto()
    PALAEONTOLOGIEVERFASSUNGSSYNTHESE = auto()
    PALAEONTOLOGIEVERFASSUNGSBEWERTUNG = auto()


_WEIGHT_DELTA: dict[PalaeontologieVerfassungGeltung, float] = {
    PalaeontologieVerfassungGeltung.GESPERRT: 0.0,
    PalaeontologieVerfassungGeltung.GRUNDLEGEND_PALAEONTOLOGIE_SOUVERAEN: 2.1,
    PalaeontologieVerfassungGeltung.PALAEONTOLOGIE_SOUVERAEN: 4.2,
    PalaeontologieVerfassungGeltung.PALAEONTOLOGIE_SOUVERAEN_AKTIV: 6.3,
    PalaeontologieVerfassungGeltung.PALAEONTOLOGIE_SOUVERAEN_ABSOLUT: 8.4,
}

_TYP_MAP = {
    PalaeontologieVerfassungGeltung.GESPERRT: PalaeontologieVerfassungTyp.PALAEONTOLOGIEVERFASSUNG,
    PalaeontologieVerfassungGeltung.GRUNDLEGEND_PALAEONTOLOGIE_SOUVERAEN: PalaeontologieVerfassungTyp.PALAEONTOLOGIEKONSTITUTION,
    PalaeontologieVerfassungGeltung.PALAEONTOLOGIE_SOUVERAEN: PalaeontologieVerfassungTyp.PALAEONTOLOGIEKONSTITUTION,
    PalaeontologieVerfassungGeltung.PALAEONTOLOGIE_SOUVERAEN_AKTIV: PalaeontologieVerfassungTyp.PALAEONTOLOGIESOUVERAENITAET,
    PalaeontologieVerfassungGeltung.PALAEONTOLOGIE_SOUVERAEN_ABSOLUT: PalaeontologieVerfassungTyp.PALAEONTOLOGIESOUVERAENITAET,
}

_PROZEDUR_MAP = {
    PalaeontologieVerfassungGeltung.GESPERRT: PalaeontologieVerfassungProzedur.PALAEONTOLOGIEVERFASSUNGSANALYSE,
    PalaeontologieVerfassungGeltung.GRUNDLEGEND_PALAEONTOLOGIE_SOUVERAEN: PalaeontologieVerfassungProzedur.PALAEONTOLOGIEVERFASSUNGSANALYSE,
    PalaeontologieVerfassungGeltung.PALAEONTOLOGIE_SOUVERAEN: PalaeontologieVerfassungProzedur.PALAEONTOLOGIEVERFASSUNGSSYNTHESE,
    PalaeontologieVerfassungGeltung.PALAEONTOLOGIE_SOUVERAEN_AKTIV: PalaeontologieVerfassungProzedur.PALAEONTOLOGIEVERFASSUNGSSYNTHESE,
    PalaeontologieVerfassungGeltung.PALAEONTOLOGIE_SOUVERAEN_ABSOLUT: PalaeontologieVerfassungProzedur.PALAEONTOLOGIEVERFASSUNGSBEWERTUNG,
}


@dataclass(frozen=True)
class PalaeontologieVerfassungsNorm:
    geltung: PalaeontologieVerfassungGeltung
    palaeontologie_weight: float
    palaeontologie_tier: int
    palaeontologie_ids: tuple[str, ...]
    palaeontologie_tags: tuple[str, ...]
    typ: PalaeontologieVerfassungTyp
    prozedur: PalaeontologieVerfassungProzedur
    canonical: bool = True


@dataclass(frozen=True)
class PalaeontologieVerfassung:
    normen: tuple[PalaeontologieVerfassungsNorm, ...]
    parent: Optional[TaphonomieCharta] = None

    def aggregates_verfassung_signal(self) -> dict:
        return {
            "verfassung_id": "palaeontologie-verfassung-850",
            "total_weight": round(sum(n.palaeontologie_weight for n in self.normen), 4),
            "norm_count": len(self.normen),
        }


def build_palaeontologie_verfassung(parent: Optional[TaphonomieCharta] = None) -> PalaeontologieVerfassung:
    if parent is None:
        parent = build_taphonomie_charta()
    base = sum(n.palaeontologie_weight for n in parent.normen)
    tier_base = max(n.palaeontologie_tier for n in parent.normen)
    normen = tuple(
        PalaeontologieVerfassungsNorm(
            geltung=g,
            palaeontologie_weight=round(base + _WEIGHT_DELTA[g], 4),
            palaeontologie_tier=tier_base + i + 1,
            palaeontologie_ids=(f"palaeontologie-verfassung-{g.name.lower()}-001",),
            palaeontologie_tags=("palaeontologie", "verfassung", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(PalaeontologieVerfassungGeltung)
    )
    return PalaeontologieVerfassung(normen=normen, parent=parent)
