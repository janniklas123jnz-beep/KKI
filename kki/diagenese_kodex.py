from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .fazies_charta import FaziesCharta, build_fazies_charta


class DiageneseKodexTyp(Enum):
    KOMPAKION = auto()
    ZEMENTATION = auto()
    REKRISTALLISATION = auto()
    DOLOMITISIERUNG = auto()
    SILIFIZIERUNG = auto()


class DiageneseKodexProzedur(Enum):
    FRUEHDIAGENES = auto()
    MESSDIAGENES = auto()
    SPAETDIAGENES = auto()
    VERSENKUNG = auto()
    HEBUNG = auto()


_WEIGHT_DELTA = {
    DiageneseKodexTyp.KOMPAKION: 0.0,
    DiageneseKodexTyp.ZEMENTATION: 1.5,
    DiageneseKodexTyp.REKRISTALLISATION: 3.0,
    DiageneseKodexTyp.DOLOMITISIERUNG: 4.5,
    DiageneseKodexTyp.SILIFIZIERUNG: 6.0,
}
_TYP_MAP = {
    DiageneseKodexTyp.KOMPAKION: "kompakion",
    DiageneseKodexTyp.ZEMENTATION: "zementation",
    DiageneseKodexTyp.REKRISTALLISATION: "rekristallisation",
    DiageneseKodexTyp.DOLOMITISIERUNG: "dolomitisierung",
    DiageneseKodexTyp.SILIFIZIERUNG: "silifizierung",
}
_PROZEDUR_MAP = {
    DiageneseKodexProzedur.FRUEHDIAGENES: "fruehdiagenes",
    DiageneseKodexProzedur.MESSDIAGENES: "messdiagenes",
    DiageneseKodexProzedur.SPAETDIAGENES: "spaetdiagenes",
    DiageneseKodexProzedur.VERSENKUNG: "versenkung",
    DiageneseKodexProzedur.HEBUNG: "hebung",
}


@dataclass(frozen=True)
class DiageneseKodexEintrag:
    typ: DiageneseKodexTyp
    prozedur: DiageneseKodexProzedur
    sedimentologie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class DiageneseKodex:
    eintraege: tuple[DiageneseKodexEintrag, ...]
    canonical: bool = True

    def aggregates_kodex_signal(self) -> dict:
        return {
            "kodex_id": "diagenese-kodex-864",
            "eintraege_count": len(self.eintraege),
            "canonical": self.canonical,
        }


def build_diagenese_kodex(parent: Optional[FaziesCharta] = None) -> DiageneseKodex:
    if parent is None:
        parent = build_fazies_charta()
    base = sum(n.sedimentologie_weight for n in parent.normen)
    eintraege = tuple(
        DiageneseKodexEintrag(
            typ=t,
            prozedur=list(DiageneseKodexProzedur)[i],
            sedimentologie_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(DiageneseKodexTyp)
    )
    return DiageneseKodex(eintraege=eintraege)
