from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .eisdynamik_manifest import EisdynamikManifest, build_eisdynamik_manifest


class MeereisPaktTyp(Enum):
    ARKTISCHES_EIS = auto()
    ANTARKTISCHES_EIS = auto()
    ERSTES_JAHR = auto()
    MEHRJAEHRIG = auto()
    TREIBEIS = auto()


class MeereisPaktProzedur(Enum):
    MONITORING = auto()
    KARTIERUNG = auto()
    MODELLIERUNG = auto()
    PROGNOSE = auto()
    ANALYSE = auto()


_WEIGHT_DELTA = {
    MeereisPaktTyp.ARKTISCHES_EIS: 0.0,
    MeereisPaktTyp.ANTARKTISCHES_EIS: 1.7,
    MeereisPaktTyp.ERSTES_JAHR: 3.4,
    MeereisPaktTyp.MEHRJAEHRIG: 5.1,
    MeereisPaktTyp.TREIBEIS: 6.8,
}
_TYP_MAP = {
    MeereisPaktTyp.ARKTISCHES_EIS: "arktisches_eis",
    MeereisPaktTyp.ANTARKTISCHES_EIS: "antarktisches_eis",
    MeereisPaktTyp.ERSTES_JAHR: "erstes_jahr",
    MeereisPaktTyp.MEHRJAEHRIG: "mehrjaehrig",
    MeereisPaktTyp.TREIBEIS: "treibeis",
}
_PROZEDUR_MAP = {
    MeereisPaktProzedur.MONITORING: "monitoring",
    MeereisPaktProzedur.KARTIERUNG: "kartierung",
    MeereisPaktProzedur.MODELLIERUNG: "modellierung",
    MeereisPaktProzedur.PROGNOSE: "prognose",
    MeereisPaktProzedur.ANALYSE: "analyse",
}


@dataclass(frozen=True)
class MeereisPaktEintrag:
    typ: MeereisPaktTyp
    prozedur: MeereisPaktProzedur
    glaziologie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class MeereisPakt:
    eintraege: tuple[MeereisPaktEintrag, ...]
    canonical: bool = True

    def aggregates_pakt_signal(self) -> dict:
        return {
            "pakt_id": "meereis-pakt-896",
            "eintraege_count": len(self.eintraege),
            "canonical": self.canonical,
        }


def build_meereis_pakt(parent: Optional[EisdynamikManifest] = None) -> MeereisPakt:
    if parent is None:
        parent = build_eisdynamik_manifest()
    base = sum(n.glaziologie_weight for n in parent.normen)
    eintraege = tuple(
        MeereisPaktEintrag(
            typ=t,
            prozedur=list(MeereisPaktProzedur)[i],
            glaziologie_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(MeereisPaktTyp)
    )
    return MeereisPakt(eintraege=eintraege)
