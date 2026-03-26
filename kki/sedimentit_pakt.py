from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .magmatit_manifest import MagmatitManifest, build_magmatit_manifest


class SedimentitPaktTyp(Enum):
    SANDSTEIN = auto()
    TONSTEIN = auto()
    KALKSTEIN = auto()
    KONGLOMERAT = auto()
    EVAPORIT = auto()


class SedimentitPaktProzedur(Enum):
    KLASSIFIKATION = auto()
    FAZIES = auto()
    DIAGENESE = auto()
    STRATIGRAPHIE = auto()
    RESSOURCEN = auto()


_WEIGHT_DELTA = {
    SedimentitPaktTyp.SANDSTEIN: 0.0,
    SedimentitPaktTyp.TONSTEIN: 1.7,
    SedimentitPaktTyp.KALKSTEIN: 3.4,
    SedimentitPaktTyp.KONGLOMERAT: 5.1,
    SedimentitPaktTyp.EVAPORIT: 6.8,
}
_TYP_MAP = {
    SedimentitPaktTyp.SANDSTEIN: "sandstein",
    SedimentitPaktTyp.TONSTEIN: "tonstein",
    SedimentitPaktTyp.KALKSTEIN: "kalkstein",
    SedimentitPaktTyp.KONGLOMERAT: "konglomerat",
    SedimentitPaktTyp.EVAPORIT: "evaporit",
}
_PROZEDUR_MAP = {
    SedimentitPaktProzedur.KLASSIFIKATION: "klassifikation",
    SedimentitPaktProzedur.FAZIES: "fazies",
    SedimentitPaktProzedur.DIAGENESE: "diagenese",
    SedimentitPaktProzedur.STRATIGRAPHIE: "stratigraphie",
    SedimentitPaktProzedur.RESSOURCEN: "ressourcen",
}


@dataclass(frozen=True)
class SedimentitPaktEintrag:
    typ: SedimentitPaktTyp
    prozedur: SedimentitPaktProzedur
    petrographie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class SedimentitPakt:
    eintraege: tuple[SedimentitPaktEintrag, ...]
    canonical: bool = True

    def aggregates_pakt_signal(self) -> dict:
        return {
            "pakt_id": "sedimentit-pakt-886",
            "eintraege_count": len(self.eintraege),
            "canonical": self.canonical,
        }


def build_sedimentit_pakt(parent: Optional[MagmatitManifest] = None) -> SedimentitPakt:
    if parent is None:
        parent = build_magmatit_manifest()
    base = sum(n.petrographie_weight for n in parent.normen)
    eintraege = tuple(
        SedimentitPaktEintrag(
            typ=t,
            prozedur=list(SedimentitPaktProzedur)[i],
            petrographie_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(SedimentitPaktTyp)
    )
    return SedimentitPakt(eintraege=eintraege)
