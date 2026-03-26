"""
#957 SmartGridSenat — Intelligente Energienetze: Smart Grid, Speicher & Digitalisierung.
Edison vs. Tesla (1880s): War of Currents — Gleichstrom vs. Wechselstrom;
  Tesla/Westinghouse gewinnen; Wechselstromnetz als globaler Standard.
EPRI (2003): IntelliGrid Architecture — Smart Grid als digitalisiertes Stromnetz;
  bidirektionale Kommunikation zwischen Erzeugern, Speichern und Verbrauchern.
Pickerel et al. (2010s): Virtual Power Plants — dezentrale Energieressourcen
  als aggregierter virtueller Kraftwerksverbund; Flexibilitätsmärkte.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .batterietechnologie_pakt import BatterietechnologiePakt, build_batterietechnologie_pakt


class SmartGridSenatTyp(Enum):
    SMART_METER = auto()
    DEMAND_RESPONSE = auto()
    VIRTUAL_POWER_PLANT = auto()
    MICROGRIDS = auto()
    HOCHSPANNUNGS_GLEICHSTROM = auto()


class SmartGridSenatProzedur(Enum):
    NETZUEBERWACHUNG = auto()
    LASTSTEUERUNG = auto()
    FREQUENZREGELUNG = auto()
    FEHLERMANAGEMENT = auto()
    MARKTINTEGRATION = auto()


_WEIGHT_DELTA = {
    SmartGridSenatTyp.SMART_METER: 0.0,
    SmartGridSenatTyp.DEMAND_RESPONSE: 1.9,
    SmartGridSenatTyp.VIRTUAL_POWER_PLANT: 3.8,
    SmartGridSenatTyp.MICROGRIDS: 5.7,
    SmartGridSenatTyp.HOCHSPANNUNGS_GLEICHSTROM: 7.6,
}
_TYP_MAP = {
    SmartGridSenatTyp.SMART_METER: "smart_meter",
    SmartGridSenatTyp.DEMAND_RESPONSE: "demand_response",
    SmartGridSenatTyp.VIRTUAL_POWER_PLANT: "virtual_power_plant",
    SmartGridSenatTyp.MICROGRIDS: "microgrids",
    SmartGridSenatTyp.HOCHSPANNUNGS_GLEICHSTROM: "hochspannungs_gleichstrom",
}
_PROZEDUR_MAP = {
    SmartGridSenatProzedur.NETZUEBERWACHUNG: "netzueberwachung",
    SmartGridSenatProzedur.LASTSTEUERUNG: "laststeuerung",
    SmartGridSenatProzedur.FREQUENZREGELUNG: "frequenzregelung",
    SmartGridSenatProzedur.FEHLERMANAGEMENT: "fehlermanagement",
    SmartGridSenatProzedur.MARKTINTEGRATION: "marktintegration",
}


@dataclass(frozen=True)
class SmartGridSenatNorm:
    typ: SmartGridSenatTyp
    prozedur: SmartGridSenatProzedur
    energie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class SmartGridSenat:
    normen: tuple[SmartGridSenatNorm, ...]
    canonical: bool = True

    def aggregates_senat_signal(self) -> dict:
        return {
            "senat_id": "smart-grid-senat-957",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_smart_grid_senat(parent: Optional[BatterietechnologiePakt] = None) -> SmartGridSenat:
    if parent is None:
        parent = build_batterietechnologie_pakt()
    base = sum(e.energie_weight for e in parent.eintraege)
    normen = tuple(
        SmartGridSenatNorm(
            typ=t,
            prozedur=list(SmartGridSenatProzedur)[i],
            energie_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(SmartGridSenatTyp)
    )
    return SmartGridSenat(normen=normen)
