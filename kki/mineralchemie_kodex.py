from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .gesteinskunde_charta import GesteinskundeCharta, build_gesteinskunde_charta


class MineralchemieKodexGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_MINERALOGISCH = auto()
    MINERALOGISCH = auto()
    MINERALOGISCH_AKTIV = auto()
    MINERALOGIE_SOUVERAEN = auto()


class MineralchemieKodexTyp(Enum):
    MINERALCHEMIEKODEX = auto()
    MINERALCHEMIESYSTEM = auto()
    MINERALCHEMIEKOMPONENTE = auto()


class MineralchemieKodexProzedur(Enum):
    MINERALCHEMIEANALYSE = auto()
    MINERALCHEMIESYNTHESE = auto()
    MINERALCHEMIEBEWERTUNG = auto()


_WEIGHT_DELTA: dict[MineralchemieKodexGeltung, float] = {
    MineralchemieKodexGeltung.GESPERRT: 0.0,
    MineralchemieKodexGeltung.GRUNDLEGEND_MINERALOGISCH: 1.5,
    MineralchemieKodexGeltung.MINERALOGISCH: 3.0,
    MineralchemieKodexGeltung.MINERALOGISCH_AKTIV: 4.5,
    MineralchemieKodexGeltung.MINERALOGIE_SOUVERAEN: 6.0,
}

_TYP_MAP = {
    MineralchemieKodexGeltung.GESPERRT: MineralchemieKodexTyp.MINERALCHEMIEKODEX,
    MineralchemieKodexGeltung.GRUNDLEGEND_MINERALOGISCH: MineralchemieKodexTyp.MINERALCHEMIEKOMPONENTE,
    MineralchemieKodexGeltung.MINERALOGISCH: MineralchemieKodexTyp.MINERALCHEMIEKOMPONENTE,
    MineralchemieKodexGeltung.MINERALOGISCH_AKTIV: MineralchemieKodexTyp.MINERALCHEMIESYSTEM,
    MineralchemieKodexGeltung.MINERALOGIE_SOUVERAEN: MineralchemieKodexTyp.MINERALCHEMIESYSTEM,
}

_PROZEDUR_MAP = {
    MineralchemieKodexGeltung.GESPERRT: MineralchemieKodexProzedur.MINERALCHEMIEANALYSE,
    MineralchemieKodexGeltung.GRUNDLEGEND_MINERALOGISCH: MineralchemieKodexProzedur.MINERALCHEMIEANALYSE,
    MineralchemieKodexGeltung.MINERALOGISCH: MineralchemieKodexProzedur.MINERALCHEMIESYNTHESE,
    MineralchemieKodexGeltung.MINERALOGISCH_AKTIV: MineralchemieKodexProzedur.MINERALCHEMIESYNTHESE,
    MineralchemieKodexGeltung.MINERALOGIE_SOUVERAEN: MineralchemieKodexProzedur.MINERALCHEMIEBEWERTUNG,
}


@dataclass(frozen=True)
class MineralchemieKodexEintrag:
    geltung: MineralchemieKodexGeltung
    mineralogie_weight: float
    mineralogie_tier: int
    mineralogie_ids: tuple[str, ...]
    mineralogie_tags: tuple[str, ...]
    typ: MineralchemieKodexTyp
    prozedur: MineralchemieKodexProzedur
    canonical: bool = True


@dataclass(frozen=True)
class MineralchemieKodex:
    eintraege: tuple[MineralchemieKodexEintrag, ...]
    parent: Optional[GesteinskundeCharta] = None


def build_mineralchemie_kodex(parent: Optional[GesteinskundeCharta] = None) -> MineralchemieKodex:
    if parent is None:
        parent = build_gesteinskunde_charta()
    base = sum(n.mineralogie_weight for n in parent.normen)
    eintraege = tuple(
        MineralchemieKodexEintrag(
            geltung=g,
            mineralogie_weight=round(base + _WEIGHT_DELTA[g], 4),
            mineralogie_tier=i + 1,
            mineralogie_ids=(f"mineralchemie-kodex-{g.name.lower()}-001",),
            mineralogie_tags=("mineralogie", "mineralchemie", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(MineralchemieKodexGeltung)
    )
    return MineralchemieKodex(eintraege=eintraege, parent=parent)
