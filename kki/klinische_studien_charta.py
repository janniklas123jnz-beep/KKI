from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .pharma_norm import PharmaNormSatz, build_pharma_norm


class KlinischeStudienChartaGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_KLINISCH = auto()
    KLINISCH = auto()
    KLINISCH_AKTIV = auto()
    KLINISCH_SOUVERAEN = auto()


class KlinischeStudienChartaTyp(Enum):
    KLINISCHESTUDIENCHARTA = auto()
    STUDIENPROTOKOLL = auto()
    WIRKSAMKEITSNACHWEIS = auto()


class KlinischeStudienChartaProzedur(Enum):
    STUDIENPLANUNG = auto()
    DATENEVALUATION = auto()
    ZULASSUNGSBEWERTUNG = auto()


_WEIGHT_DELTA: dict[KlinischeStudienChartaGeltung, float] = {
    KlinischeStudienChartaGeltung.GESPERRT: 0.0,
    KlinischeStudienChartaGeltung.GRUNDLEGEND_KLINISCH: 2.1,
    KlinischeStudienChartaGeltung.KLINISCH: 4.2,
    KlinischeStudienChartaGeltung.KLINISCH_AKTIV: 6.3,
    KlinischeStudienChartaGeltung.KLINISCH_SOUVERAEN: 8.4,
}

_TYP_MAP = {
    KlinischeStudienChartaGeltung.GESPERRT: KlinischeStudienChartaTyp.KLINISCHESTUDIENCHARTA,
    KlinischeStudienChartaGeltung.GRUNDLEGEND_KLINISCH: KlinischeStudienChartaTyp.STUDIENPROTOKOLL,
    KlinischeStudienChartaGeltung.KLINISCH: KlinischeStudienChartaTyp.STUDIENPROTOKOLL,
    KlinischeStudienChartaGeltung.KLINISCH_AKTIV: KlinischeStudienChartaTyp.WIRKSAMKEITSNACHWEIS,
    KlinischeStudienChartaGeltung.KLINISCH_SOUVERAEN: KlinischeStudienChartaTyp.WIRKSAMKEITSNACHWEIS,
}

_PROZEDUR_MAP = {
    KlinischeStudienChartaGeltung.GESPERRT: KlinischeStudienChartaProzedur.STUDIENPLANUNG,
    KlinischeStudienChartaGeltung.GRUNDLEGEND_KLINISCH: KlinischeStudienChartaProzedur.STUDIENPLANUNG,
    KlinischeStudienChartaGeltung.KLINISCH: KlinischeStudienChartaProzedur.DATENEVALUATION,
    KlinischeStudienChartaGeltung.KLINISCH_AKTIV: KlinischeStudienChartaProzedur.DATENEVALUATION,
    KlinischeStudienChartaGeltung.KLINISCH_SOUVERAEN: KlinischeStudienChartaProzedur.ZULASSUNGSBEWERTUNG,
}


@dataclass(frozen=True)
class KlinischeStudienChartaNorm:
    geltung: KlinischeStudienChartaGeltung
    pharma_weight: float
    pharma_tier: int
    pharma_ids: tuple[str, ...]
    pharma_tags: tuple[str, ...]
    typ: KlinischeStudienChartaTyp
    prozedur: KlinischeStudienChartaProzedur
    canonical: bool = True


@dataclass(frozen=True)
class KlinischeStudienCharta:
    normen: tuple[KlinischeStudienChartaNorm, ...]
    parent: Optional[PharmaNormSatz] = None


def build_klinische_studien_charta(parent: Optional[PharmaNormSatz] = None) -> KlinischeStudienCharta:
    if parent is None:
        parent = build_pharma_norm()
    base = sum(e.pharma_norm_weight for e in parent.normen)
    tier_base = max(e.pharma_norm_tier for e in parent.normen)
    normen = tuple(
        KlinischeStudienChartaNorm(
            geltung=g,
            pharma_weight=round(base + _WEIGHT_DELTA[g], 4),
            pharma_tier=tier_base + i + 1,
            pharma_ids=(f"klinische-studien-{g.name.lower()}-001",),
            pharma_tags=("klinische-studien", "charta", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(KlinischeStudienChartaGeltung)
    )
    return KlinischeStudienCharta(normen=normen, parent=parent)
