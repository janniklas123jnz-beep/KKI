from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .eisdecken_charta import EisdeckenCharta, build_eisdecken_charta


class PermafrostKodexTyp(Enum):
    DAUERFROSTBODEN = auto()
    AKTIVE_SCHICHT = auto()
    TALIK = auto()
    PINGOS = auto()
    EISKEILE = auto()


class PermafrostKodexProzedur(Enum):
    KARTIERUNG = auto()
    MONITORING = auto()
    MODELLIERUNG = auto()
    ANALYSE = auto()
    SCHUTZ = auto()


_WEIGHT_DELTA = {
    PermafrostKodexTyp.DAUERFROSTBODEN: 0.0,
    PermafrostKodexTyp.AKTIVE_SCHICHT: 1.5,
    PermafrostKodexTyp.TALIK: 3.0,
    PermafrostKodexTyp.PINGOS: 4.5,
    PermafrostKodexTyp.EISKEILE: 6.0,
}
_TYP_MAP = {
    PermafrostKodexTyp.DAUERFROSTBODEN: "dauerfrostboden",
    PermafrostKodexTyp.AKTIVE_SCHICHT: "aktive_schicht",
    PermafrostKodexTyp.TALIK: "talik",
    PermafrostKodexTyp.PINGOS: "pingos",
    PermafrostKodexTyp.EISKEILE: "eiskeile",
}
_PROZEDUR_MAP = {
    PermafrostKodexProzedur.KARTIERUNG: "kartierung",
    PermafrostKodexProzedur.MONITORING: "monitoring",
    PermafrostKodexProzedur.MODELLIERUNG: "modellierung",
    PermafrostKodexProzedur.ANALYSE: "analyse",
    PermafrostKodexProzedur.SCHUTZ: "schutz",
}


@dataclass(frozen=True)
class PermafrostKodexEintrag:
    typ: PermafrostKodexTyp
    prozedur: PermafrostKodexProzedur
    glaziologie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class PermafrostKodex:
    eintraege: tuple[PermafrostKodexEintrag, ...]
    canonical: bool = True

    def aggregates_kodex_signal(self) -> dict:
        return {
            "kodex_id": "permafrost-kodex-894",
            "eintraege_count": len(self.eintraege),
            "canonical": self.canonical,
        }


def build_permafrost_kodex(parent: Optional[EisdeckenCharta] = None) -> PermafrostKodex:
    if parent is None:
        parent = build_eisdecken_charta()
    base = sum(n.glaziologie_weight for n in parent.normen)
    eintraege = tuple(
        PermafrostKodexEintrag(
            typ=t,
            prozedur=list(PermafrostKodexProzedur)[i],
            glaziologie_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(PermafrostKodexTyp)
    )
    return PermafrostKodex(eintraege=eintraege)
