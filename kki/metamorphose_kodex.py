from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .gefuege_charta import GefuegeCharta, build_gefuege_charta


class MetamorphoseKodexTyp(Enum):
    KONTAKTMETAMORPH = auto()
    REGIONALMETAMORPH = auto()
    DYNAMOMETAMORPH = auto()
    DRUCKMETAMORPH = auto()
    THERMALMETAMORPH = auto()


class MetamorphoseKodexProzedur(Enum):
    KLASSIFIKATION = auto()
    ZONIERUNG = auto()
    INDEXMINERALE = auto()
    FAZIES = auto()
    PFAD = auto()


_WEIGHT_DELTA = {
    MetamorphoseKodexTyp.KONTAKTMETAMORPH: 0.0,
    MetamorphoseKodexTyp.REGIONALMETAMORPH: 1.5,
    MetamorphoseKodexTyp.DYNAMOMETAMORPH: 3.0,
    MetamorphoseKodexTyp.DRUCKMETAMORPH: 4.5,
    MetamorphoseKodexTyp.THERMALMETAMORPH: 6.0,
}
_TYP_MAP = {
    MetamorphoseKodexTyp.KONTAKTMETAMORPH: "kontaktmetamorph",
    MetamorphoseKodexTyp.REGIONALMETAMORPH: "regionalmetamorph",
    MetamorphoseKodexTyp.DYNAMOMETAMORPH: "dynamometamorph",
    MetamorphoseKodexTyp.DRUCKMETAMORPH: "druckmetamorph",
    MetamorphoseKodexTyp.THERMALMETAMORPH: "thermalmetamorph",
}
_PROZEDUR_MAP = {
    MetamorphoseKodexProzedur.KLASSIFIKATION: "klassifikation",
    MetamorphoseKodexProzedur.ZONIERUNG: "zonierung",
    MetamorphoseKodexProzedur.INDEXMINERALE: "indexminerale",
    MetamorphoseKodexProzedur.FAZIES: "fazies",
    MetamorphoseKodexProzedur.PFAD: "pfad",
}


@dataclass(frozen=True)
class MetamorphoseKodexEintrag:
    typ: MetamorphoseKodexTyp
    prozedur: MetamorphoseKodexProzedur
    petrographie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class MetamorphoseKodex:
    eintraege: tuple[MetamorphoseKodexEintrag, ...]
    canonical: bool = True

    def aggregates_kodex_signal(self) -> dict:
        return {
            "kodex_id": "metamorphose-kodex-884",
            "eintraege_count": len(self.eintraege),
            "canonical": self.canonical,
        }


def build_metamorphose_kodex(parent: Optional[GefuegeCharta] = None) -> MetamorphoseKodex:
    if parent is None:
        parent = build_gefuege_charta()
    base = sum(n.petrographie_weight for n in parent.normen)
    eintraege = tuple(
        MetamorphoseKodexEintrag(
            typ=t,
            prozedur=list(MetamorphoseKodexProzedur)[i],
            petrographie_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(MetamorphoseKodexTyp)
    )
    return MetamorphoseKodex(eintraege=eintraege)
