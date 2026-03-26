from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .wolkenphysik_charta import WolkenphysikCharta, build_wolkenphysik_charta


class NiederschlagsKodexGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_METEOROLOGISCH = auto()
    METEOROLOGISCH = auto()
    METEOROLOGISCH_AKTIV = auto()
    METEOROLOGIE_SOUVERAEN = auto()


class NiederschlagsKodexTyp(Enum):
    NIEDERSCHLAGSKODEX = auto()
    NIEDERSCHLAGSSYSTEM = auto()
    NIEDERSCHLAGSKOMPONENTE = auto()


class NiederschlagsKodexProzedur(Enum):
    NIEDERSCHLAGSANALYSE = auto()
    NIEDERSCHLAGSSYNTHESE = auto()
    NIEDERSCHLAGSBEWERTUNG = auto()


_WEIGHT_DELTA: dict[NiederschlagsKodexGeltung, float] = {
    NiederschlagsKodexGeltung.GESPERRT: 0.0,
    NiederschlagsKodexGeltung.GRUNDLEGEND_METEOROLOGISCH: 1.5,
    NiederschlagsKodexGeltung.METEOROLOGISCH: 3.0,
    NiederschlagsKodexGeltung.METEOROLOGISCH_AKTIV: 4.5,
    NiederschlagsKodexGeltung.METEOROLOGIE_SOUVERAEN: 6.0,
}

_TYP_MAP = {
    NiederschlagsKodexGeltung.GESPERRT: NiederschlagsKodexTyp.NIEDERSCHLAGSKODEX,
    NiederschlagsKodexGeltung.GRUNDLEGEND_METEOROLOGISCH: NiederschlagsKodexTyp.NIEDERSCHLAGSKOMPONENTE,
    NiederschlagsKodexGeltung.METEOROLOGISCH: NiederschlagsKodexTyp.NIEDERSCHLAGSKOMPONENTE,
    NiederschlagsKodexGeltung.METEOROLOGISCH_AKTIV: NiederschlagsKodexTyp.NIEDERSCHLAGSSYSTEM,
    NiederschlagsKodexGeltung.METEOROLOGIE_SOUVERAEN: NiederschlagsKodexTyp.NIEDERSCHLAGSSYSTEM,
}

_PROZEDUR_MAP = {
    NiederschlagsKodexGeltung.GESPERRT: NiederschlagsKodexProzedur.NIEDERSCHLAGSANALYSE,
    NiederschlagsKodexGeltung.GRUNDLEGEND_METEOROLOGISCH: NiederschlagsKodexProzedur.NIEDERSCHLAGSANALYSE,
    NiederschlagsKodexGeltung.METEOROLOGISCH: NiederschlagsKodexProzedur.NIEDERSCHLAGSSYNTHESE,
    NiederschlagsKodexGeltung.METEOROLOGISCH_AKTIV: NiederschlagsKodexProzedur.NIEDERSCHLAGSSYNTHESE,
    NiederschlagsKodexGeltung.METEOROLOGIE_SOUVERAEN: NiederschlagsKodexProzedur.NIEDERSCHLAGSBEWERTUNG,
}


@dataclass(frozen=True)
class NiederschlagsKodexEintrag:
    geltung: NiederschlagsKodexGeltung
    meteorologie_weight: float
    meteorologie_tier: int
    meteorologie_ids: tuple[str, ...]
    meteorologie_tags: tuple[str, ...]
    typ: NiederschlagsKodexTyp
    prozedur: NiederschlagsKodexProzedur
    canonical: bool = True


@dataclass(frozen=True)
class NiederschlagsKodex:
    eintraege: tuple[NiederschlagsKodexEintrag, ...]
    parent: Optional[WolkenphysikCharta] = None


def build_niederschlags_kodex(parent: Optional[WolkenphysikCharta] = None) -> NiederschlagsKodex:
    if parent is None:
        parent = build_wolkenphysik_charta()
    base = sum(n.meteorologie_weight for n in parent.normen)
    eintraege = tuple(
        NiederschlagsKodexEintrag(
            geltung=g,
            meteorologie_weight=round(base + _WEIGHT_DELTA[g], 4),
            meteorologie_tier=i + 1,
            meteorologie_ids=(f"niederschlags-kodex-{g.name.lower()}-001",),
            meteorologie_tags=("meteorologie", "niederschlag", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(NiederschlagsKodexGeltung)
    )
    return NiederschlagsKodex(eintraege=eintraege, parent=parent)
