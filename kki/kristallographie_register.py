from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .mineralogie_feld import MineralogieFeld, build_mineralogie_feld


class KristallographieRegisterGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_MINERALOGISCH = auto()
    MINERALOGISCH = auto()
    MINERALOGISCH_AKTIV = auto()
    MINERALOGIE_SOUVERAEN = auto()


class KristallographieRegisterTyp(Enum):
    KRISTALLOGRAPHIEREGISTER = auto()
    KRISTALLOGRAPHIESYSTEM = auto()
    KRISTALLOGRAPHIEKOMPONENTE = auto()


class KristallographieRegisterProzedur(Enum):
    KRISTALLOGRAPHIEANALYSE = auto()
    KRISTALLOGRAPHIESYNTHESE = auto()
    KRISTALLOGRAPHIEBEWERTUNG = auto()


_WEIGHT_DELTA: dict[KristallographieRegisterGeltung, float] = {
    KristallographieRegisterGeltung.GESPERRT: 0.0,
    KristallographieRegisterGeltung.GRUNDLEGEND_MINERALOGISCH: 1.3,
    KristallographieRegisterGeltung.MINERALOGISCH: 2.6,
    KristallographieRegisterGeltung.MINERALOGISCH_AKTIV: 3.9,
    KristallographieRegisterGeltung.MINERALOGIE_SOUVERAEN: 5.2,
}

_TYP_MAP = {
    KristallographieRegisterGeltung.GESPERRT: KristallographieRegisterTyp.KRISTALLOGRAPHIEREGISTER,
    KristallographieRegisterGeltung.GRUNDLEGEND_MINERALOGISCH: KristallographieRegisterTyp.KRISTALLOGRAPHIEKOMPONENTE,
    KristallographieRegisterGeltung.MINERALOGISCH: KristallographieRegisterTyp.KRISTALLOGRAPHIEKOMPONENTE,
    KristallographieRegisterGeltung.MINERALOGISCH_AKTIV: KristallographieRegisterTyp.KRISTALLOGRAPHIESYSTEM,
    KristallographieRegisterGeltung.MINERALOGIE_SOUVERAEN: KristallographieRegisterTyp.KRISTALLOGRAPHIESYSTEM,
}

_PROZEDUR_MAP = {
    KristallographieRegisterGeltung.GESPERRT: KristallographieRegisterProzedur.KRISTALLOGRAPHIEANALYSE,
    KristallographieRegisterGeltung.GRUNDLEGEND_MINERALOGISCH: KristallographieRegisterProzedur.KRISTALLOGRAPHIEANALYSE,
    KristallographieRegisterGeltung.MINERALOGISCH: KristallographieRegisterProzedur.KRISTALLOGRAPHIESYNTHESE,
    KristallographieRegisterGeltung.MINERALOGISCH_AKTIV: KristallographieRegisterProzedur.KRISTALLOGRAPHIESYNTHESE,
    KristallographieRegisterGeltung.MINERALOGIE_SOUVERAEN: KristallographieRegisterProzedur.KRISTALLOGRAPHIEBEWERTUNG,
}


@dataclass(frozen=True)
class KristallographieRegisterEintrag:
    geltung: KristallographieRegisterGeltung
    mineralogie_weight: float
    mineralogie_tier: int
    mineralogie_ids: tuple[str, ...]
    mineralogie_tags: tuple[str, ...]
    typ: KristallographieRegisterTyp
    prozedur: KristallographieRegisterProzedur
    canonical: bool = True


@dataclass(frozen=True)
class KristallographieRegister:
    eintraege: tuple[KristallographieRegisterEintrag, ...]
    parent: Optional[MineralogieFeld] = None


def build_kristallographie_register(parent: Optional[MineralogieFeld] = None) -> KristallographieRegister:
    if parent is None:
        parent = build_mineralogie_feld()
    base = sum(n.mineralogie_weight for n in parent.normen)
    eintraege = tuple(
        KristallographieRegisterEintrag(
            geltung=g,
            mineralogie_weight=round(base + _WEIGHT_DELTA[g], 4),
            mineralogie_tier=i + 1,
            mineralogie_ids=(f"kristallographie-register-{g.name.lower()}-001",),
            mineralogie_tags=("mineralogie", "kristallographie", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(KristallographieRegisterGeltung)
    )
    return KristallographieRegister(eintraege=eintraege, parent=parent)
