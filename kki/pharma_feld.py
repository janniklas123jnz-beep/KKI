from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .statistik_verfassung import StatistikVerfassung, build_statistik_verfassung


class PharmaFeldGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_PHARMAZEUTISCH = auto()
    PHARMAZEUTISCH = auto()
    PHARMAZEUTISCH_AKTIV = auto()
    PHARMA_SOUVERAEN = auto()


class PharmaFeldTyp(Enum):
    PHARMAFELD = auto()
    PHARMASYSTEM = auto()
    PHARMAKOMPONENTE = auto()


class PharmaFeldProzedur(Enum):
    PHARMAANALYSE = auto()
    PHARMASYNTHESE = auto()
    PHARMABEWERTUNG = auto()


_WEIGHT_DELTA: dict[PharmaFeldGeltung, float] = {
    PharmaFeldGeltung.GESPERRT: 0.0,
    PharmaFeldGeltung.GRUNDLEGEND_PHARMAZEUTISCH: 1.3,
    PharmaFeldGeltung.PHARMAZEUTISCH: 2.6,
    PharmaFeldGeltung.PHARMAZEUTISCH_AKTIV: 3.9,
    PharmaFeldGeltung.PHARMA_SOUVERAEN: 5.2,
}

_TYP_MAP = {
    PharmaFeldGeltung.GESPERRT: PharmaFeldTyp.PHARMAFELD,
    PharmaFeldGeltung.GRUNDLEGEND_PHARMAZEUTISCH: PharmaFeldTyp.PHARMAKOMPONENTE,
    PharmaFeldGeltung.PHARMAZEUTISCH: PharmaFeldTyp.PHARMAKOMPONENTE,
    PharmaFeldGeltung.PHARMAZEUTISCH_AKTIV: PharmaFeldTyp.PHARMASYSTEM,
    PharmaFeldGeltung.PHARMA_SOUVERAEN: PharmaFeldTyp.PHARMASYSTEM,
}

_PROZEDUR_MAP = {
    PharmaFeldGeltung.GESPERRT: PharmaFeldProzedur.PHARMAANALYSE,
    PharmaFeldGeltung.GRUNDLEGEND_PHARMAZEUTISCH: PharmaFeldProzedur.PHARMAANALYSE,
    PharmaFeldGeltung.PHARMAZEUTISCH: PharmaFeldProzedur.PHARMASYNTHESE,
    PharmaFeldGeltung.PHARMAZEUTISCH_AKTIV: PharmaFeldProzedur.PHARMASYNTHESE,
    PharmaFeldGeltung.PHARMA_SOUVERAEN: PharmaFeldProzedur.PHARMABEWERTUNG,
}


@dataclass(frozen=True)
class PharmaFeldNorm:
    geltung: PharmaFeldGeltung
    pharma_weight: float
    pharma_tier: int
    pharma_ids: tuple[str, ...]
    pharma_tags: tuple[str, ...]
    typ: PharmaFeldTyp
    prozedur: PharmaFeldProzedur
    canonical: bool = True


@dataclass(frozen=True)
class PharmaFeld:
    normen: tuple[PharmaFeldNorm, ...]
    parent: Optional[StatistikVerfassung] = None


def build_pharma_feld(parent: Optional[StatistikVerfassung] = None) -> PharmaFeld:
    if parent is None:
        parent = build_statistik_verfassung()
    base = sum(n.stat_weight for n in parent.normen)
    normen = tuple(
        PharmaFeldNorm(
            geltung=g,
            pharma_weight=round(base + _WEIGHT_DELTA[g], 4),
            pharma_tier=i + 1,
            pharma_ids=(f"pharma-feld-{g.name.lower()}-001",),
            pharma_tags=("pharma", "feld", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(PharmaFeldGeltung)
    )
    return PharmaFeld(normen=normen, parent=parent)
