from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .sedimentologie_feld import SedimentologieFeld, build_sedimentologie_feld


class AblagerungsRegisterTyp(Enum):
    FLUVIAL = auto()
    MARIN = auto()
    AEOLISCH = auto()
    GLAZIAL = auto()
    LAKUSTRIN = auto()


class AblagerungsRegisterProzedur(Enum):
    AUFBAU = auto()
    VERDICHTUNG = auto()
    SORTIERUNG = auto()
    ZEMENTIERUNG = auto()
    VERFESTIGUNG = auto()


_WEIGHT_DELTA = {
    AblagerungsRegisterTyp.FLUVIAL: 0.0,
    AblagerungsRegisterTyp.MARIN: 1.3,
    AblagerungsRegisterTyp.AEOLISCH: 2.6,
    AblagerungsRegisterTyp.GLAZIAL: 3.9,
    AblagerungsRegisterTyp.LAKUSTRIN: 5.2,
}
_TYP_MAP = {
    AblagerungsRegisterTyp.FLUVIAL: "fluvial",
    AblagerungsRegisterTyp.MARIN: "marin",
    AblagerungsRegisterTyp.AEOLISCH: "aeolisch",
    AblagerungsRegisterTyp.GLAZIAL: "glazial",
    AblagerungsRegisterTyp.LAKUSTRIN: "lakustrin",
}
_PROZEDUR_MAP = {
    AblagerungsRegisterProzedur.AUFBAU: "aufbau",
    AblagerungsRegisterProzedur.VERDICHTUNG: "verdichtung",
    AblagerungsRegisterProzedur.SORTIERUNG: "sortierung",
    AblagerungsRegisterProzedur.ZEMENTIERUNG: "zementierung",
    AblagerungsRegisterProzedur.VERFESTIGUNG: "verfestigung",
}


@dataclass(frozen=True)
class AblagerungsRegisterEintrag:
    typ: AblagerungsRegisterTyp
    prozedur: AblagerungsRegisterProzedur
    sedimentologie_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class AblagerungsRegister:
    eintraege: tuple[AblagerungsRegisterEintrag, ...]
    canonical: bool = True

    def aggregates_register_signal(self) -> dict:
        return {
            "register_id": "ablagerungs-register-862",
            "eintraege_count": len(self.eintraege),
            "canonical": self.canonical,
        }


def build_ablagerungs_register(parent: Optional[SedimentologieFeld] = None) -> AblagerungsRegister:
    if parent is None:
        parent = build_sedimentologie_feld()
    base = sum(n.sedimentologie_weight for n in parent.normen)
    eintraege = tuple(
        AblagerungsRegisterEintrag(
            typ=t,
            prozedur=list(AblagerungsRegisterProzedur)[i],
            sedimentologie_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(AblagerungsRegisterTyp)
    )
    return AblagerungsRegister(eintraege=eintraege)
