from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .isotopen_register import IsotopenRegister, build_isotopen_register


class RadiometrieChartaTyp(Enum):
    HALBWERTSZEIT = auto()
    ZERFALLSKONSTANTE = auto()
    ANFANGSVERHAELTNIS = auto()
    ZERFALLSREIHE = auto()
    ISOTOPENVERHAELTNIS = auto()


class RadiometrieChartaProzedur(Enum):
    MESSUNG = auto()
    KALIBRIERUNG = auto()
    FEHLERKORREKTUR = auto()
    NORMIERUNG = auto()
    INTERPRETATION = auto()


_WEIGHT_DELTA = {
    RadiometrieChartaTyp.HALBWERTSZEIT: 0.0,
    RadiometrieChartaTyp.ZERFALLSKONSTANTE: 1.4,
    RadiometrieChartaTyp.ANFANGSVERHAELTNIS: 2.8,
    RadiometrieChartaTyp.ZERFALLSREIHE: 4.2,
    RadiometrieChartaTyp.ISOTOPENVERHAELTNIS: 5.6,
}
_TYP_MAP = {
    RadiometrieChartaTyp.HALBWERTSZEIT: "halbwertszeit",
    RadiometrieChartaTyp.ZERFALLSKONSTANTE: "zerfallskonstante",
    RadiometrieChartaTyp.ANFANGSVERHAELTNIS: "anfangsverhaeltnis",
    RadiometrieChartaTyp.ZERFALLSREIHE: "zerfallsreihe",
    RadiometrieChartaTyp.ISOTOPENVERHAELTNIS: "isotopenverhaeltnis",
}
_PROZEDUR_MAP = {
    RadiometrieChartaProzedur.MESSUNG: "messung",
    RadiometrieChartaProzedur.KALIBRIERUNG: "kalibrierung",
    RadiometrieChartaProzedur.FEHLERKORREKTUR: "fehlerkorrektur",
    RadiometrieChartaProzedur.NORMIERUNG: "normierung",
    RadiometrieChartaProzedur.INTERPRETATION: "interpretation",
}


@dataclass(frozen=True)
class RadiometrieChartaNorm:
    typ: RadiometrieChartaTyp
    prozedur: RadiometrieChartaProzedur
    geochronologie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class RadiometrieCharta:
    normen: tuple[RadiometrieChartaNorm, ...]
    canonical: bool = True

    def aggregates_charta_signal(self) -> dict:
        return {
            "charta_id": "radiometrie-charta-873",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_radiometrie_charta(parent: Optional[IsotopenRegister] = None) -> RadiometrieCharta:
    if parent is None:
        parent = build_isotopen_register()
    base = sum(e.geochronologie_weight for e in parent.eintraege)
    normen = tuple(
        RadiometrieChartaNorm(
            typ=t,
            prozedur=list(RadiometrieChartaProzedur)[i],
            geochronologie_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(RadiometrieChartaTyp)
    )
    return RadiometrieCharta(normen=normen)
