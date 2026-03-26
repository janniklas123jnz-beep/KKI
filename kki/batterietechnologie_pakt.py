"""
#956 BatterietechnologiePakt — Batterietechnologie: Li-Ion, Goodenough & Solid-State.
Goodenough, Whittingham & Yoshino (1970s–1980s): Lithium-Ion Battery — Nobelpreis
  Chemie 2019; LiCoO2-Kathode, Graphit-Anode; Revolutionierung portabler Elektronik
  und Elektromobilität; Grundlage aller modernen Energiespeicher.
Musk/Tesla (2012–2020s): Gigafactory & Battery Day — Skalierung der Li-Ion-
  Produktion; Kostensenkung von >1000 $/kWh auf <100 $/kWh; 4680-Zelle.
Toyota/QuantumScape (2020s): Solid-State Batteries — Festkörperelektrolyt statt
  flüssig; höhere Energiedichte, kein Brandrisiko; nächste Batteriegeneration.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .wasserstoff_manifest import WasserstoffManifest, build_wasserstoff_manifest


class BatterietechnologiePaktTyp(Enum):
    LITHIUM_ION = auto()
    LITHIUM_EISENPHOSPHAT = auto()
    FESTKOERPER_BATTERIE = auto()
    NATRIUM_ION = auto()
    REDOX_FLOW = auto()


class BatterietechnologiePaktProzedur(Enum):
    ZELLDESIGN = auto()
    ELEKTRODENHERSTELLUNG = auto()
    FORMATION = auto()
    SYSTEMINTEGRATION = auto()
    RECYCLING = auto()


_WEIGHT_DELTA = {
    BatterietechnologiePaktTyp.LITHIUM_ION: 0.0,
    BatterietechnologiePaktTyp.LITHIUM_EISENPHOSPHAT: 1.7,
    BatterietechnologiePaktTyp.FESTKOERPER_BATTERIE: 3.4,
    BatterietechnologiePaktTyp.NATRIUM_ION: 5.1,
    BatterietechnologiePaktTyp.REDOX_FLOW: 6.8,
}
_TYP_MAP = {
    BatterietechnologiePaktTyp.LITHIUM_ION: "lithium_ion",
    BatterietechnologiePaktTyp.LITHIUM_EISENPHOSPHAT: "lithium_eisenphosphat",
    BatterietechnologiePaktTyp.FESTKOERPER_BATTERIE: "festkoerper_batterie",
    BatterietechnologiePaktTyp.NATRIUM_ION: "natrium_ion",
    BatterietechnologiePaktTyp.REDOX_FLOW: "redox_flow",
}
_PROZEDUR_MAP = {
    BatterietechnologiePaktProzedur.ZELLDESIGN: "zelldesign",
    BatterietechnologiePaktProzedur.ELEKTRODENHERSTELLUNG: "elektrodenherstellung",
    BatterietechnologiePaktProzedur.FORMATION: "formation",
    BatterietechnologiePaktProzedur.SYSTEMINTEGRATION: "systemintegration",
    BatterietechnologiePaktProzedur.RECYCLING: "recycling",
}


@dataclass(frozen=True)
class BatterietechnologiePaktEintrag:
    typ: BatterietechnologiePaktTyp
    prozedur: BatterietechnologiePaktProzedur
    energie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class BatterietechnologiePakt:
    eintraege: tuple[BatterietechnologiePaktEintrag, ...]
    canonical: bool = True

    def aggregates_pakt_signal(self) -> dict:
        return {
            "pakt_id": "batterietechnologie-pakt-956",
            "eintraege_count": len(self.eintraege),
            "canonical": self.canonical,
        }


def build_batterietechnologie_pakt(parent: Optional[WasserstoffManifest] = None) -> BatterietechnologiePakt:
    if parent is None:
        parent = build_wasserstoff_manifest()
    base = sum(n.energie_weight for n in parent.normen)
    eintraege = tuple(
        BatterietechnologiePaktEintrag(
            typ=t,
            prozedur=list(BatterietechnologiePaktProzedur)[i],
            energie_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(BatterietechnologiePaktTyp)
    )
    return BatterietechnologiePakt(eintraege=eintraege)
