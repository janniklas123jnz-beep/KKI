"""
#954 FusionsenergieKodex — Fusionsenergie: ITER, Tokamak & Trägheitsfusion.
Lawson (1957): Some Criteria for a Power Producing Thermonuclear Reactor —
  Lawson-Kriterium: Produkt aus Plasmadichte, Temperatur und Einschlusszeit
  als Bedingung für Netto-Fusionsenergie; fundamentale Grenze der Fusionsforschung.
ITER Organization (2020s): International Thermonuclear Experimental Reactor —
  35-Nationen-Projekt; 500 MW Fusionsleistung bei 50 MW Eingangsleistung (Q=10);
  größtes Wissenschaftsprojekt der Menschheit in Cadarache/Frankreich.
NIF/LLNL (2022): Ignition Achieved — erstes Mal mehr Fusionsenergie als
  Laserenergie; Trägheitsfusion als Meilenstein; privater Fusionsboom folgt.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .windenergie_charta import WindenergieCharta, build_windenergie_charta


class FusionsenergieKodexTyp(Enum):
    TOKAMAK = auto()
    STELLARATOR = auto()
    TRAEGHEITSFUSION = auto()
    KOMPAKTER_TOKAMAK = auto()
    ANEUTRONEN_FUSION = auto()


class FusionsenergieKodexProzedur(Enum):
    PLASMAHEIZUNG = auto()
    MAGNETEINSCHLUSS = auto()
    ZUENDUNG = auto()
    TRITIUMBRUETUNG = auto()
    ENERGIEAUSKOPPLUNG = auto()


_WEIGHT_DELTA = {
    FusionsenergieKodexTyp.TOKAMAK: 0.0,
    FusionsenergieKodexTyp.STELLARATOR: 1.8,
    FusionsenergieKodexTyp.TRAEGHEITSFUSION: 3.6,
    FusionsenergieKodexTyp.KOMPAKTER_TOKAMAK: 5.4,
    FusionsenergieKodexTyp.ANEUTRONEN_FUSION: 7.2,
}
_TYP_MAP = {
    FusionsenergieKodexTyp.TOKAMAK: "tokamak",
    FusionsenergieKodexTyp.STELLARATOR: "stellarator",
    FusionsenergieKodexTyp.TRAEGHEITSFUSION: "traegheitsfusion",
    FusionsenergieKodexTyp.KOMPAKTER_TOKAMAK: "kompakter_tokamak",
    FusionsenergieKodexTyp.ANEUTRONEN_FUSION: "aneutronen_fusion",
}
_PROZEDUR_MAP = {
    FusionsenergieKodexProzedur.PLASMAHEIZUNG: "plasmaheizung",
    FusionsenergieKodexProzedur.MAGNETEINSCHLUSS: "magneteinschluss",
    FusionsenergieKodexProzedur.ZUENDUNG: "zuendung",
    FusionsenergieKodexProzedur.TRITIUMBRUETUNG: "tritiumbruetung",
    FusionsenergieKodexProzedur.ENERGIEAUSKOPPLUNG: "energieauskopplung",
}


@dataclass(frozen=True)
class FusionsenergieKodexEintrag:
    typ: FusionsenergieKodexTyp
    prozedur: FusionsenergieKodexProzedur
    energie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class FusionsenergieKodex:
    eintraege: tuple[FusionsenergieKodexEintrag, ...]
    canonical: bool = True

    def aggregates_kodex_signal(self) -> dict:
        return {
            "kodex_id": "fusionsenergie-kodex-954",
            "eintraege_count": len(self.eintraege),
            "canonical": self.canonical,
        }


def build_fusionsenergie_kodex(parent: Optional[WindenergieCharta] = None) -> FusionsenergieKodex:
    if parent is None:
        parent = build_windenergie_charta()
    base = sum(n.energie_weight for n in parent.normen)
    eintraege = tuple(
        FusionsenergieKodexEintrag(
            typ=t,
            prozedur=list(FusionsenergieKodexProzedur)[i],
            energie_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(FusionsenergieKodexTyp)
    )
    return FusionsenergieKodex(eintraege=eintraege)
