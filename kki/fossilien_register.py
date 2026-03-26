from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .palaeontologie_feld import PalaeontologieFeld, build_palaeontologie_feld


class FossilienRegisterGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_PALAEONTOLOGISCH = auto()
    PALAEONTOLOGISCH = auto()
    PALAEONTOLOGISCH_AKTIV = auto()
    PALAEONTOLOGIE_SOUVERAEN = auto()


class FossilienRegisterTyp(Enum):
    FOSSILIENREGISTER = auto()
    FOSSILIENSAMMLUNG = auto()
    FOSSILIENEINTRAG = auto()


class FossilienRegisterProzedur(Enum):
    FOSSILIENANALYSE = auto()
    FOSSILIENSYNTHESE = auto()
    FOSSILIENBEWERTUNG = auto()


_WEIGHT_DELTA: dict[FossilienRegisterGeltung, float] = {
    FossilienRegisterGeltung.GESPERRT: 0.0,
    FossilienRegisterGeltung.GRUNDLEGEND_PALAEONTOLOGISCH: 1.3,
    FossilienRegisterGeltung.PALAEONTOLOGISCH: 2.6,
    FossilienRegisterGeltung.PALAEONTOLOGISCH_AKTIV: 3.9,
    FossilienRegisterGeltung.PALAEONTOLOGIE_SOUVERAEN: 5.2,
}

_TYP_MAP = {
    FossilienRegisterGeltung.GESPERRT: FossilienRegisterTyp.FOSSILIENREGISTER,
    FossilienRegisterGeltung.GRUNDLEGEND_PALAEONTOLOGISCH: FossilienRegisterTyp.FOSSILIENEINTRAG,
    FossilienRegisterGeltung.PALAEONTOLOGISCH: FossilienRegisterTyp.FOSSILIENEINTRAG,
    FossilienRegisterGeltung.PALAEONTOLOGISCH_AKTIV: FossilienRegisterTyp.FOSSILIENSAMMLUNG,
    FossilienRegisterGeltung.PALAEONTOLOGIE_SOUVERAEN: FossilienRegisterTyp.FOSSILIENSAMMLUNG,
}

_PROZEDUR_MAP = {
    FossilienRegisterGeltung.GESPERRT: FossilienRegisterProzedur.FOSSILIENANALYSE,
    FossilienRegisterGeltung.GRUNDLEGEND_PALAEONTOLOGISCH: FossilienRegisterProzedur.FOSSILIENANALYSE,
    FossilienRegisterGeltung.PALAEONTOLOGISCH: FossilienRegisterProzedur.FOSSILIENSYNTHESE,
    FossilienRegisterGeltung.PALAEONTOLOGISCH_AKTIV: FossilienRegisterProzedur.FOSSILIENSYNTHESE,
    FossilienRegisterGeltung.PALAEONTOLOGIE_SOUVERAEN: FossilienRegisterProzedur.FOSSILIENBEWERTUNG,
}


@dataclass(frozen=True)
class FossilienRegisterEintrag:
    geltung: FossilienRegisterGeltung
    palaeontologie_weight: float
    palaeontologie_tier: int
    palaeontologie_ids: tuple[str, ...]
    palaeontologie_tags: tuple[str, ...]
    typ: FossilienRegisterTyp
    prozedur: FossilienRegisterProzedur
    canonical: bool = True


@dataclass(frozen=True)
class FossilienRegister:
    eintraege: tuple[FossilienRegisterEintrag, ...]
    parent: Optional[PalaeontologieFeld] = None


def build_fossilien_register(parent: Optional[PalaeontologieFeld] = None) -> FossilienRegister:
    if parent is None:
        parent = build_palaeontologie_feld()
    base = sum(n.palaeontologie_weight for n in parent.normen)
    eintraege = tuple(
        FossilienRegisterEintrag(
            geltung=g,
            palaeontologie_weight=round(base + _WEIGHT_DELTA[g], 4),
            palaeontologie_tier=i + 1,
            palaeontologie_ids=(f"fossilien-register-{g.name.lower()}-001",),
            palaeontologie_tags=("palaeontologie", "fossilien", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(FossilienRegisterGeltung)
    )
    return FossilienRegister(eintraege=eintraege, parent=parent)
