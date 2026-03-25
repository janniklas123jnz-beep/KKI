from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .klinische_studien_charta import KlinischeStudienCharta, build_klinische_studien_charta


class PharmaVerfassungGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_PHARMA_SOUVERAEN = auto()
    PHARMA_SOUVERAEN = auto()
    PHARMA_SOUVERAEN_AKTIV = auto()
    PHARMA_SOUVERAEN_ABSOLUT = auto()


class PharmaVerfassungTyp(Enum):
    PHARMAVERFASSUNG = auto()
    PHARMASOUVERAENITAET = auto()
    PHARMAKONSTITUTION = auto()


class PharmaVerfassungProzedur(Enum):
    PHARMAVERFASSUNGSANALYSE = auto()
    PHARMAVERFASSUNGSSYNTHESE = auto()
    PHARMAVERFASSUNGSBEWERTUNG = auto()


_WEIGHT_DELTA: dict[PharmaVerfassungGeltung, float] = {
    PharmaVerfassungGeltung.GESPERRT: 0.0,
    PharmaVerfassungGeltung.GRUNDLEGEND_PHARMA_SOUVERAEN: 2.2,
    PharmaVerfassungGeltung.PHARMA_SOUVERAEN: 4.4,
    PharmaVerfassungGeltung.PHARMA_SOUVERAEN_AKTIV: 6.6,
    PharmaVerfassungGeltung.PHARMA_SOUVERAEN_ABSOLUT: 8.8,
}

_TYP_MAP = {
    PharmaVerfassungGeltung.GESPERRT: PharmaVerfassungTyp.PHARMAVERFASSUNG,
    PharmaVerfassungGeltung.GRUNDLEGEND_PHARMA_SOUVERAEN: PharmaVerfassungTyp.PHARMAKONSTITUTION,
    PharmaVerfassungGeltung.PHARMA_SOUVERAEN: PharmaVerfassungTyp.PHARMAKONSTITUTION,
    PharmaVerfassungGeltung.PHARMA_SOUVERAEN_AKTIV: PharmaVerfassungTyp.PHARMASOUVERAENITAET,
    PharmaVerfassungGeltung.PHARMA_SOUVERAEN_ABSOLUT: PharmaVerfassungTyp.PHARMASOUVERAENITAET,
}

_PROZEDUR_MAP = {
    PharmaVerfassungGeltung.GESPERRT: PharmaVerfassungProzedur.PHARMAVERFASSUNGSANALYSE,
    PharmaVerfassungGeltung.GRUNDLEGEND_PHARMA_SOUVERAEN: PharmaVerfassungProzedur.PHARMAVERFASSUNGSANALYSE,
    PharmaVerfassungGeltung.PHARMA_SOUVERAEN: PharmaVerfassungProzedur.PHARMAVERFASSUNGSSYNTHESE,
    PharmaVerfassungGeltung.PHARMA_SOUVERAEN_AKTIV: PharmaVerfassungProzedur.PHARMAVERFASSUNGSSYNTHESE,
    PharmaVerfassungGeltung.PHARMA_SOUVERAEN_ABSOLUT: PharmaVerfassungProzedur.PHARMAVERFASSUNGSBEWERTUNG,
}


@dataclass(frozen=True)
class PharmaVerfassungsNorm:
    geltung: PharmaVerfassungGeltung
    pharma_weight: float
    pharma_tier: int
    pharma_ids: tuple[str, ...]
    pharma_tags: tuple[str, ...]
    typ: PharmaVerfassungTyp
    prozedur: PharmaVerfassungProzedur
    canonical: bool = True


@dataclass(frozen=True)
class PharmaVerfassung:
    normen: tuple[PharmaVerfassungsNorm, ...]
    parent: Optional[KlinischeStudienCharta] = None

    def aggregates_verfassung_signal(self) -> dict:
        return {
            "verfassung_id": "pharma-verfassung-770",
            "total_weight": round(sum(n.pharma_weight for n in self.normen), 4),
            "norm_count": len(self.normen),
        }


def build_pharma_verfassung(parent: Optional[KlinischeStudienCharta] = None) -> PharmaVerfassung:
    if parent is None:
        parent = build_klinische_studien_charta()
    base = sum(n.pharma_weight for n in parent.normen)
    tier_base = max(n.pharma_tier for n in parent.normen)
    normen = tuple(
        PharmaVerfassungsNorm(
            geltung=g,
            pharma_weight=round(base + _WEIGHT_DELTA[g], 4),
            pharma_tier=tier_base + i + 1,
            pharma_ids=(f"pharma-verfassung-{g.name.lower()}-001",),
            pharma_tags=("pharma", "verfassung", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(PharmaVerfassungGeltung)
    )
    return PharmaVerfassung(normen=normen, parent=parent)
