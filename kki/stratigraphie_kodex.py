from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .radiometrie_charta import RadiometrieCharta, build_radiometrie_charta


class StartigraphieKodexTyp(Enum):
    LITHOSTRATIGRAPHIE = auto()
    CHRONOSTRATIGRAPHIE = auto()
    SEQUENZSTRATIGRAPHIE = auto()
    ZYKLOSTRATIGRAPHIE = auto()
    CHEMOSTRATIGRAPHIE = auto()


class StartigraphieKodexProzedur(Enum):
    KORRELATION = auto()
    KARTIERUNG = auto()
    TYPISIERUNG = auto()
    STANDARDISIERUNG = auto()
    GLIEDERUNG = auto()


_WEIGHT_DELTA = {
    StartigraphieKodexTyp.LITHOSTRATIGRAPHIE: 0.0,
    StartigraphieKodexTyp.CHRONOSTRATIGRAPHIE: 1.5,
    StartigraphieKodexTyp.SEQUENZSTRATIGRAPHIE: 3.0,
    StartigraphieKodexTyp.ZYKLOSTRATIGRAPHIE: 4.5,
    StartigraphieKodexTyp.CHEMOSTRATIGRAPHIE: 6.0,
}
_TYP_MAP = {
    StartigraphieKodexTyp.LITHOSTRATIGRAPHIE: "lithostratigraphie",
    StartigraphieKodexTyp.CHRONOSTRATIGRAPHIE: "chronostratigraphie",
    StartigraphieKodexTyp.SEQUENZSTRATIGRAPHIE: "sequenzstratigraphie",
    StartigraphieKodexTyp.ZYKLOSTRATIGRAPHIE: "zyklostratigraphie",
    StartigraphieKodexTyp.CHEMOSTRATIGRAPHIE: "chemostratigraphie",
}
_PROZEDUR_MAP = {
    StartigraphieKodexProzedur.KORRELATION: "korrelation",
    StartigraphieKodexProzedur.KARTIERUNG: "kartierung",
    StartigraphieKodexProzedur.TYPISIERUNG: "typisierung",
    StartigraphieKodexProzedur.STANDARDISIERUNG: "standardisierung",
    StartigraphieKodexProzedur.GLIEDERUNG: "gliederung",
}


@dataclass(frozen=True)
class StartigraphieKodexEintrag:
    typ: StartigraphieKodexTyp
    prozedur: StartigraphieKodexProzedur
    geochronologie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class StartigraphieKodex:
    eintraege: tuple[StartigraphieKodexEintrag, ...]
    canonical: bool = True

    def aggregates_kodex_signal(self) -> dict:
        return {
            "kodex_id": "stratigraphie-kodex-874",
            "eintraege_count": len(self.eintraege),
            "canonical": self.canonical,
        }


def build_stratigraphie_kodex(parent: Optional[RadiometrieCharta] = None) -> StartigraphieKodex:
    if parent is None:
        parent = build_radiometrie_charta()
    base = sum(n.geochronologie_weight for n in parent.normen)
    eintraege = tuple(
        StartigraphieKodexEintrag(
            typ=t,
            prozedur=list(StartigraphieKodexProzedur)[i],
            geochronologie_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(StartigraphieKodexTyp)
    )
    return StartigraphieKodex(eintraege=eintraege)
