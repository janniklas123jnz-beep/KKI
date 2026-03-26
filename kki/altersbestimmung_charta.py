from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .geochronologie_norm import GeochronologieNorm, build_geochronologie_norm


class AltersbestimmungChartaTyp(Enum):
    DENDROCHRONOLOGIE = auto()
    THERMOLUMINESZENZ = auto()
    OPTISCH_STIMULIERT = auto()
    ELEKTRONEN_SPIN = auto()
    AMINOSAEUREN = auto()


class AltersbestimmungChartaProzedur(Enum):
    PROBENAHME = auto()
    VORBEREITUNG = auto()
    MESSUNG = auto()
    AUSWERTUNG = auto()
    DATIERUNG = auto()


_WEIGHT_DELTA = {
    AltersbestimmungChartaTyp.DENDROCHRONOLOGIE: 0.0,
    AltersbestimmungChartaTyp.THERMOLUMINESZENZ: 2.0,
    AltersbestimmungChartaTyp.OPTISCH_STIMULIERT: 4.0,
    AltersbestimmungChartaTyp.ELEKTRONEN_SPIN: 6.0,
    AltersbestimmungChartaTyp.AMINOSAEUREN: 8.0,
}
_TYP_MAP = {
    AltersbestimmungChartaTyp.DENDROCHRONOLOGIE: "dendrochronologie",
    AltersbestimmungChartaTyp.THERMOLUMINESZENZ: "thermolumineszenz",
    AltersbestimmungChartaTyp.OPTISCH_STIMULIERT: "optisch_stimuliert",
    AltersbestimmungChartaTyp.ELEKTRONEN_SPIN: "elektronen_spin",
    AltersbestimmungChartaTyp.AMINOSAEUREN: "aminosaeuren",
}
_PROZEDUR_MAP = {
    AltersbestimmungChartaProzedur.PROBENAHME: "probenahme",
    AltersbestimmungChartaProzedur.VORBEREITUNG: "vorbereitung",
    AltersbestimmungChartaProzedur.MESSUNG: "messung",
    AltersbestimmungChartaProzedur.AUSWERTUNG: "auswertung",
    AltersbestimmungChartaProzedur.DATIERUNG: "datierung",
}


@dataclass(frozen=True)
class AltersbestimmungChartaNorm:
    typ: AltersbestimmungChartaTyp
    prozedur: AltersbestimmungChartaProzedur
    geochronologie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class AltersbestimmungCharta:
    normen: tuple[AltersbestimmungChartaNorm, ...]
    canonical: bool = True

    def aggregates_charta_signal(self) -> dict:
        return {
            "charta_id": "altersbestimmung-charta-879",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_altersbestimmung_charta(parent: Optional[GeochronologieNorm] = None) -> AltersbestimmungCharta:
    if parent is None:
        parent = build_geochronologie_norm()
    base = sum(e.geochronologie_norm_weight for e in parent.normen)
    tier_base = max(e.geochronologie_norm_tier for e in parent.normen)
    normen = tuple(
        AltersbestimmungChartaNorm(
            typ=t,
            prozedur=list(AltersbestimmungChartaProzedur)[i],
            geochronologie_weight=base + _WEIGHT_DELTA[t],
            tier=tier_base + i + 1,
        )
        for i, t in enumerate(AltersbestimmungChartaTyp)
    )
    return AltersbestimmungCharta(normen=normen)
