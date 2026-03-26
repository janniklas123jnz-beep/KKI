from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .petrographie_feld import PetrographieFeld, build_petrographie_feld


class MineralRegisterTyp(Enum):
    SILIKAT = auto()
    OXID = auto()
    KARBONAT = auto()
    SULFID = auto()
    PHOSPHAT = auto()


class MineralRegisterProzedur(Enum):
    IDENTIFIKATION = auto()
    BESTIMMUNG = auto()
    ANALYSE = auto()
    KLASSIFIKATION = auto()
    DOKUMENTATION = auto()


_WEIGHT_DELTA = {
    MineralRegisterTyp.SILIKAT: 0.0,
    MineralRegisterTyp.OXID: 1.3,
    MineralRegisterTyp.KARBONAT: 2.6,
    MineralRegisterTyp.SULFID: 3.9,
    MineralRegisterTyp.PHOSPHAT: 5.2,
}
_TYP_MAP = {
    MineralRegisterTyp.SILIKAT: "silikat",
    MineralRegisterTyp.OXID: "oxid",
    MineralRegisterTyp.KARBONAT: "karbonat",
    MineralRegisterTyp.SULFID: "sulfid",
    MineralRegisterTyp.PHOSPHAT: "phosphat",
}
_PROZEDUR_MAP = {
    MineralRegisterProzedur.IDENTIFIKATION: "identifikation",
    MineralRegisterProzedur.BESTIMMUNG: "bestimmung",
    MineralRegisterProzedur.ANALYSE: "analyse",
    MineralRegisterProzedur.KLASSIFIKATION: "klassifikation",
    MineralRegisterProzedur.DOKUMENTATION: "dokumentation",
}


@dataclass(frozen=True)
class MineralRegisterEintrag:
    typ: MineralRegisterTyp
    prozedur: MineralRegisterProzedur
    petrographie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class MineralRegister:
    eintraege: tuple[MineralRegisterEintrag, ...]
    canonical: bool = True

    def aggregates_register_signal(self) -> dict:
        return {
            "register_id": "mineral-register-882",
            "eintraege_count": len(self.eintraege),
            "canonical": self.canonical,
        }


def build_mineral_register(parent: Optional[PetrographieFeld] = None) -> MineralRegister:
    if parent is None:
        parent = build_petrographie_feld()
    base = sum(n.petrographie_weight for n in parent.normen)
    eintraege = tuple(
        MineralRegisterEintrag(
            typ=t,
            prozedur=list(MineralRegisterProzedur)[i],
            petrographie_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(MineralRegisterTyp)
    )
    return MineralRegister(eintraege=eintraege)
