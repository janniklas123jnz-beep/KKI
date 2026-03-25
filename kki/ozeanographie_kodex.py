from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .meteorologie_charta import MeteorologieCharta, build_meteorologie_charta


class OzeanographieKodexGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_OZEANOGRAPHISCH = auto()
    OZEANOGRAPHISCH = auto()
    OZEANOGRAPHISCH_AKTIV = auto()
    OZEANOGRAPHIE_SOUVERAEN = auto()


class OzeanographieKodexTyp(Enum):
    OZEANOGRAPHIEKODEX = auto()
    MEERESSTROEMUNG = auto()
    OZEANKOMPONENTE = auto()


class OzeanographieKodexProzedur(Enum):
    OZEANANALYSE = auto()
    OZEANSYNTHESE = auto()
    OZEANBEWERTUNG = auto()


_WEIGHT_DELTA: dict[OzeanographieKodexGeltung, float] = {
    OzeanographieKodexGeltung.GESPERRT: 0.0,
    OzeanographieKodexGeltung.GRUNDLEGEND_OZEANOGRAPHISCH: 1.5,
    OzeanographieKodexGeltung.OZEANOGRAPHISCH: 3.0,
    OzeanographieKodexGeltung.OZEANOGRAPHISCH_AKTIV: 4.5,
    OzeanographieKodexGeltung.OZEANOGRAPHIE_SOUVERAEN: 6.0,
}

_TYP_MAP = {
    OzeanographieKodexGeltung.GESPERRT: OzeanographieKodexTyp.OZEANOGRAPHIEKODEX,
    OzeanographieKodexGeltung.GRUNDLEGEND_OZEANOGRAPHISCH: OzeanographieKodexTyp.OZEANKOMPONENTE,
    OzeanographieKodexGeltung.OZEANOGRAPHISCH: OzeanographieKodexTyp.OZEANKOMPONENTE,
    OzeanographieKodexGeltung.OZEANOGRAPHISCH_AKTIV: OzeanographieKodexTyp.MEERESSTROEMUNG,
    OzeanographieKodexGeltung.OZEANOGRAPHIE_SOUVERAEN: OzeanographieKodexTyp.MEERESSTROEMUNG,
}

_PROZEDUR_MAP = {
    OzeanographieKodexGeltung.GESPERRT: OzeanographieKodexProzedur.OZEANANALYSE,
    OzeanographieKodexGeltung.GRUNDLEGEND_OZEANOGRAPHISCH: OzeanographieKodexProzedur.OZEANANALYSE,
    OzeanographieKodexGeltung.OZEANOGRAPHISCH: OzeanographieKodexProzedur.OZEANSYNTHESE,
    OzeanographieKodexGeltung.OZEANOGRAPHISCH_AKTIV: OzeanographieKodexProzedur.OZEANSYNTHESE,
    OzeanographieKodexGeltung.OZEANOGRAPHIE_SOUVERAEN: OzeanographieKodexProzedur.OZEANBEWERTUNG,
}


@dataclass(frozen=True)
class OzeanographieKodexEintrag:
    geltung: OzeanographieKodexGeltung
    klima_weight: float
    klima_tier: int
    klima_ids: tuple[str, ...]
    klima_tags: tuple[str, ...]
    typ: OzeanographieKodexTyp
    prozedur: OzeanographieKodexProzedur
    canonical: bool = True


@dataclass(frozen=True)
class OzeanographieKodex:
    eintraege: tuple[OzeanographieKodexEintrag, ...]
    parent: Optional[MeteorologieCharta] = None


def build_ozeanographie_kodex(parent: Optional[MeteorologieCharta] = None) -> OzeanographieKodex:
    if parent is None:
        parent = build_meteorologie_charta()
    base = sum(n.klima_weight for n in parent.normen)
    eintraege = tuple(
        OzeanographieKodexEintrag(
            geltung=g,
            klima_weight=round(base + _WEIGHT_DELTA[g], 4),
            klima_tier=i + 1,
            klima_ids=(f"ozeanographie-kodex-{g.name.lower()}-001",),
            klima_tags=("ozeanographie", "kodex", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(OzeanographieKodexGeltung)
    )
    return OzeanographieKodex(eintraege=eintraege, parent=parent)
