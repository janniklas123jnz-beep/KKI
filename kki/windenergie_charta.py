"""
#953 WindenergieCharta — Windenergie: Betz-Limit, Offshore & Floating Wind.
Betz (1919): Das Maximum der theoretisch möglichen Ausnutzung des Windes —
  Betz-Limit von 59,3% als theoretische Maximalausbeute einer Windturbine;
  aerodynamisches Fundament aller Rotorblattoptimierung.
Vestas & Siemens Gamesa (1990s–2020s): Onshore & Offshore Scaling — systematische
  Größenskalierung von Windturbinen; 15+ MW Offshore-Anlagen; Lernkurven.
Equinor (2017): Hywind Scotland — erste kommerzielle Floating-Offshore-Windanlage;
  erschließt Tiefseepotenzial; nächste Generation der Windkraft.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .solarenergie_register import SolarenergieRegister, build_solarenergie_register


class WindenergieChartaTyp(Enum):
    ONSHORE_WIND = auto()
    OFFSHORE_WIND = auto()
    FLOATING_WIND = auto()
    KLEINWINDANLAGE = auto()
    AIRBORNE_WIND = auto()


class WindenergieChartaProzedur(Enum):
    STANDORTBEWERTUNG = auto()
    ROTORAUSLEGUNG = auto()
    TURMKONSTRUKTION = auto()
    NETZANSCHLUSS = auto()
    WARTUNG = auto()


_WEIGHT_DELTA = {
    WindenergieChartaTyp.ONSHORE_WIND: 0.0,
    WindenergieChartaTyp.OFFSHORE_WIND: 1.7,
    WindenergieChartaTyp.FLOATING_WIND: 3.4,
    WindenergieChartaTyp.KLEINWINDANLAGE: 5.1,
    WindenergieChartaTyp.AIRBORNE_WIND: 6.8,
}
_TYP_MAP = {
    WindenergieChartaTyp.ONSHORE_WIND: "onshore_wind",
    WindenergieChartaTyp.OFFSHORE_WIND: "offshore_wind",
    WindenergieChartaTyp.FLOATING_WIND: "floating_wind",
    WindenergieChartaTyp.KLEINWINDANLAGE: "kleinwindanlage",
    WindenergieChartaTyp.AIRBORNE_WIND: "airborne_wind",
}
_PROZEDUR_MAP = {
    WindenergieChartaProzedur.STANDORTBEWERTUNG: "standortbewertung",
    WindenergieChartaProzedur.ROTORAUSLEGUNG: "rotorauslegung",
    WindenergieChartaProzedur.TURMKONSTRUKTION: "turmkonstruktion",
    WindenergieChartaProzedur.NETZANSCHLUSS: "netzanschluss",
    WindenergieChartaProzedur.WARTUNG: "wartung",
}


@dataclass(frozen=True)
class WindenergieChartaNorm:
    typ: WindenergieChartaTyp
    prozedur: WindenergieChartaProzedur
    energie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class WindenergieCharta:
    normen: tuple[WindenergieChartaNorm, ...]
    canonical: bool = True

    def aggregates_charta_signal(self) -> dict:
        return {
            "charta_id": "windenergie-charta-953",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_windenergie_charta(parent: Optional[SolarenergieRegister] = None) -> WindenergieCharta:
    if parent is None:
        parent = build_solarenergie_register()
    base = sum(e.energie_weight for e in parent.eintraege)
    normen = tuple(
        WindenergieChartaNorm(
            typ=t,
            prozedur=list(WindenergieChartaProzedur)[i],
            energie_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(WindenergieChartaTyp)
    )
    return WindenergieCharta(normen=normen)
