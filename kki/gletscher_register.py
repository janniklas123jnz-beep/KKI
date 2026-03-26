from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .glaziologie_feld import GlaziologieFeld, build_glaziologie_feld


class GletscherRegisterTyp(Enum):
    AKKUMULATIONSZONE = auto()
    ABLATIONSZONE = auto()
    GLEICHGEWICHTSLINIE = auto()
    GLETSCHERZUNGE = auto()
    GLETSCHERSPALTE = auto()


class GletscherRegisterProzedur(Enum):
    INVENTAR = auto()
    KLASSIFIKATION = auto()
    MONITORING = auto()
    DOKUMENTATION = auto()
    ANALYSE = auto()


_WEIGHT_DELTA = {
    GletscherRegisterTyp.AKKUMULATIONSZONE: 0.0,
    GletscherRegisterTyp.ABLATIONSZONE: 1.3,
    GletscherRegisterTyp.GLEICHGEWICHTSLINIE: 2.6,
    GletscherRegisterTyp.GLETSCHERZUNGE: 3.9,
    GletscherRegisterTyp.GLETSCHERSPALTE: 5.2,
}
_TYP_MAP = {
    GletscherRegisterTyp.AKKUMULATIONSZONE: "akkumulationszone",
    GletscherRegisterTyp.ABLATIONSZONE: "ablationszone",
    GletscherRegisterTyp.GLEICHGEWICHTSLINIE: "gleichgewichtslinie",
    GletscherRegisterTyp.GLETSCHERZUNGE: "gletscherzunge",
    GletscherRegisterTyp.GLETSCHERSPALTE: "gletscherspalte",
}
_PROZEDUR_MAP = {
    GletscherRegisterProzedur.INVENTAR: "inventar",
    GletscherRegisterProzedur.KLASSIFIKATION: "klassifikation",
    GletscherRegisterProzedur.MONITORING: "monitoring",
    GletscherRegisterProzedur.DOKUMENTATION: "dokumentation",
    GletscherRegisterProzedur.ANALYSE: "analyse",
}


@dataclass(frozen=True)
class GletscherRegisterEintrag:
    typ: GletscherRegisterTyp
    prozedur: GletscherRegisterProzedur
    glaziologie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class GletscherRegister:
    eintraege: tuple[GletscherRegisterEintrag, ...]
    canonical: bool = True

    def aggregates_register_signal(self) -> dict:
        return {
            "register_id": "gletscher-register-892",
            "eintraege_count": len(self.eintraege),
            "canonical": self.canonical,
        }


def build_gletscher_register(parent: Optional[GlaziologieFeld] = None) -> GletscherRegister:
    if parent is None:
        parent = build_glaziologie_feld()
    base = sum(n.glaziologie_weight for n in parent.normen)
    eintraege = tuple(
        GletscherRegisterEintrag(
            typ=t,
            prozedur=list(GletscherRegisterProzedur)[i],
            glaziologie_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(GletscherRegisterTyp)
    )
    return GletscherRegister(eintraege=eintraege)
