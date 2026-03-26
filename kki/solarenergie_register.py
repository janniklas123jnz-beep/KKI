"""
#952 SolarenergieRegister — Solarenergie: Shockley-Queisser, Perowskit & Agri-PV.
Shockley & Queisser (1961): Detailed Balance Limit of Efficiency of p-n Junction
  Solar Cells — theoretische Effizienzgrenze von ~33% für Einfach-Solarzellen;
  Grundlage aller Wirkungsgradoptimierung.
Green et al. (1990s–2020s): PERC, Tandem & TOPCon-Solarzellen — systematische
  Steigerung von Silizium-Solarzelleneffizienz; Weltrekorde durch passivierte Kontakte.
Kojima et al. (2009): Organometal Halide Perovskites — Perowskit-Solarzellen
  als Durchbruch; >25% Effizienz; günstige Herstellung; nächste Generation.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .energie_feld import EnergieFeld, build_energie_feld


class SolarenergieRegisterTyp(Enum):
    SILIZIUM_PV = auto()
    DUENNSCHICHT_PV = auto()
    PEROWSKIT_PV = auto()
    KONZENTRIERENDE_SOLAR = auto()
    AGRI_PV = auto()


class SolarenergieRegisterProzedur(Enum):
    ZELLHERSTELLUNG = auto()
    MODULINTEGRATION = auto()
    SYSTEMAUSLEGUNG = auto()
    NETZINTEGRATION = auto()
    RECYCLING = auto()


_WEIGHT_DELTA = {
    SolarenergieRegisterTyp.SILIZIUM_PV: 0.0,
    SolarenergieRegisterTyp.DUENNSCHICHT_PV: 1.5,
    SolarenergieRegisterTyp.PEROWSKIT_PV: 3.0,
    SolarenergieRegisterTyp.KONZENTRIERENDE_SOLAR: 4.5,
    SolarenergieRegisterTyp.AGRI_PV: 6.0,
}
_TYP_MAP = {
    SolarenergieRegisterTyp.SILIZIUM_PV: "silizium_pv",
    SolarenergieRegisterTyp.DUENNSCHICHT_PV: "duennschicht_pv",
    SolarenergieRegisterTyp.PEROWSKIT_PV: "perowskit_pv",
    SolarenergieRegisterTyp.KONZENTRIERENDE_SOLAR: "konzentrierende_solar",
    SolarenergieRegisterTyp.AGRI_PV: "agri_pv",
}
_PROZEDUR_MAP = {
    SolarenergieRegisterProzedur.ZELLHERSTELLUNG: "zellherstellung",
    SolarenergieRegisterProzedur.MODULINTEGRATION: "modulintegration",
    SolarenergieRegisterProzedur.SYSTEMAUSLEGUNG: "systemauslegung",
    SolarenergieRegisterProzedur.NETZINTEGRATION: "netzintegration",
    SolarenergieRegisterProzedur.RECYCLING: "recycling",
}


@dataclass(frozen=True)
class SolarenergieRegisterEintrag:
    typ: SolarenergieRegisterTyp
    prozedur: SolarenergieRegisterProzedur
    energie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class SolarenergieRegister:
    eintraege: tuple[SolarenergieRegisterEintrag, ...]
    canonical: bool = True

    def aggregates_register_signal(self) -> dict:
        return {
            "register_id": "solarenergie-register-952",
            "eintraege_count": len(self.eintraege),
            "canonical": self.canonical,
        }


def build_solarenergie_register(parent: Optional[EnergieFeld] = None) -> SolarenergieRegister:
    if parent is None:
        parent = build_energie_feld()
    base = sum(n.energie_weight for n in parent.normen)
    eintraege = tuple(
        SolarenergieRegisterEintrag(
            typ=t,
            prozedur=list(SolarenergieRegisterProzedur)[i],
            energie_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(SolarenergieRegisterTyp)
    )
    return SolarenergieRegister(eintraege=eintraege)
