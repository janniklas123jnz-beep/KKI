from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .arzneimittel_register import ArzneimittelRegister, build_arzneimittel_register


class PharmakokinetikaChartaGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_PHARMAKOKINETISCH = auto()
    PHARMAKOKINETISCH = auto()
    PHARMAKOKINETISCH_AKTIV = auto()
    PHARMAKOKINETIK_SOUVERAEN = auto()


class PharmakokinetikaChartaTyp(Enum):
    PHARMAKOKINETIKCHARTA = auto()
    ABSORPTIONSMODELL = auto()
    VERTEILUNGSMODELL = auto()


class PharmakokinetikaChartaProzedur(Enum):
    ABSORPTIONSANALYSE = auto()
    VERTEILUNGSBERECHNUNG = auto()
    ELIMINATIONSBEWERTUNG = auto()


_WEIGHT_DELTA: dict[PharmakokinetikaChartaGeltung, float] = {
    PharmakokinetikaChartaGeltung.GESPERRT: 0.0,
    PharmakokinetikaChartaGeltung.GRUNDLEGEND_PHARMAKOKINETISCH: 1.5,
    PharmakokinetikaChartaGeltung.PHARMAKOKINETISCH: 3.0,
    PharmakokinetikaChartaGeltung.PHARMAKOKINETISCH_AKTIV: 4.5,
    PharmakokinetikaChartaGeltung.PHARMAKOKINETIK_SOUVERAEN: 6.0,
}

_TYP_MAP = {
    PharmakokinetikaChartaGeltung.GESPERRT: PharmakokinetikaChartaTyp.PHARMAKOKINETIKCHARTA,
    PharmakokinetikaChartaGeltung.GRUNDLEGEND_PHARMAKOKINETISCH: PharmakokinetikaChartaTyp.ABSORPTIONSMODELL,
    PharmakokinetikaChartaGeltung.PHARMAKOKINETISCH: PharmakokinetikaChartaTyp.ABSORPTIONSMODELL,
    PharmakokinetikaChartaGeltung.PHARMAKOKINETISCH_AKTIV: PharmakokinetikaChartaTyp.VERTEILUNGSMODELL,
    PharmakokinetikaChartaGeltung.PHARMAKOKINETIK_SOUVERAEN: PharmakokinetikaChartaTyp.VERTEILUNGSMODELL,
}

_PROZEDUR_MAP = {
    PharmakokinetikaChartaGeltung.GESPERRT: PharmakokinetikaChartaProzedur.ABSORPTIONSANALYSE,
    PharmakokinetikaChartaGeltung.GRUNDLEGEND_PHARMAKOKINETISCH: PharmakokinetikaChartaProzedur.ABSORPTIONSANALYSE,
    PharmakokinetikaChartaGeltung.PHARMAKOKINETISCH: PharmakokinetikaChartaProzedur.VERTEILUNGSBERECHNUNG,
    PharmakokinetikaChartaGeltung.PHARMAKOKINETISCH_AKTIV: PharmakokinetikaChartaProzedur.VERTEILUNGSBERECHNUNG,
    PharmakokinetikaChartaGeltung.PHARMAKOKINETIK_SOUVERAEN: PharmakokinetikaChartaProzedur.ELIMINATIONSBEWERTUNG,
}


@dataclass(frozen=True)
class PharmakokinetikaChartaNorm:
    geltung: PharmakokinetikaChartaGeltung
    pharma_weight: float
    pharma_tier: int
    pharma_ids: tuple[str, ...]
    pharma_tags: tuple[str, ...]
    typ: PharmakokinetikaChartaTyp
    prozedur: PharmakokinetikaChartaProzedur
    canonical: bool = True


@dataclass(frozen=True)
class PharmakokinetikaCharta:
    normen: tuple[PharmakokinetikaChartaNorm, ...]
    parent: Optional[ArzneimittelRegister] = None


def build_pharmakokinetika_charta(parent: Optional[ArzneimittelRegister] = None) -> PharmakokinetikaCharta:
    if parent is None:
        parent = build_arzneimittel_register()
    base = sum(e.pharma_weight for e in parent.eintraege)
    normen = tuple(
        PharmakokinetikaChartaNorm(
            geltung=g,
            pharma_weight=round(base + _WEIGHT_DELTA[g], 4),
            pharma_tier=i + 1,
            pharma_ids=(f"pharmakokinetika-{g.name.lower()}-001",),
            pharma_tags=("pharmakokinetika", "charta", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(PharmakokinetikaChartaGeltung)
    )
    return PharmakokinetikaCharta(normen=normen, parent=parent)
