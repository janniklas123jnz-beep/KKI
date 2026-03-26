from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .flusshydrologie_charta import FlusshydrologieCharta, build_flusshydrologie_charta


class GletscherKodexGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_HYDROLOGISCH = auto()
    HYDROLOGISCH = auto()
    HYDROLOGISCH_AKTIV = auto()
    HYDROLOGIE_SOUVERAEN = auto()


class GletscherKodexTyp(Enum):
    GLETSCHERKODEX = auto()
    GLETSCHERSYSTEM = auto()
    GLETSCHERKOMPONENTE = auto()


class GletscherKodexProzedur(Enum):
    GLETSCHERANALYSE = auto()
    GLETSCHERSYNTHESE = auto()
    GLETSCHERBEWERTUNG = auto()


_WEIGHT_DELTA: dict[GletscherKodexGeltung, float] = {
    GletscherKodexGeltung.GESPERRT: 0.0,
    GletscherKodexGeltung.GRUNDLEGEND_HYDROLOGISCH: 1.5,
    GletscherKodexGeltung.HYDROLOGISCH: 3.0,
    GletscherKodexGeltung.HYDROLOGISCH_AKTIV: 4.5,
    GletscherKodexGeltung.HYDROLOGIE_SOUVERAEN: 6.0,
}

_TYP_MAP = {
    GletscherKodexGeltung.GESPERRT: GletscherKodexTyp.GLETSCHERKODEX,
    GletscherKodexGeltung.GRUNDLEGEND_HYDROLOGISCH: GletscherKodexTyp.GLETSCHERKOMPONENTE,
    GletscherKodexGeltung.HYDROLOGISCH: GletscherKodexTyp.GLETSCHERKOMPONENTE,
    GletscherKodexGeltung.HYDROLOGISCH_AKTIV: GletscherKodexTyp.GLETSCHERSYSTEM,
    GletscherKodexGeltung.HYDROLOGIE_SOUVERAEN: GletscherKodexTyp.GLETSCHERSYSTEM,
}

_PROZEDUR_MAP = {
    GletscherKodexGeltung.GESPERRT: GletscherKodexProzedur.GLETSCHERANALYSE,
    GletscherKodexGeltung.GRUNDLEGEND_HYDROLOGISCH: GletscherKodexProzedur.GLETSCHERANALYSE,
    GletscherKodexGeltung.HYDROLOGISCH: GletscherKodexProzedur.GLETSCHERSYNTHESE,
    GletscherKodexGeltung.HYDROLOGISCH_AKTIV: GletscherKodexProzedur.GLETSCHERSYNTHESE,
    GletscherKodexGeltung.HYDROLOGIE_SOUVERAEN: GletscherKodexProzedur.GLETSCHERBEWERTUNG,
}


@dataclass(frozen=True)
class GletscherKodexEintrag:
    geltung: GletscherKodexGeltung
    hydrologie_weight: float
    hydrologie_tier: int
    hydrologie_ids: tuple[str, ...]
    hydrologie_tags: tuple[str, ...]
    typ: GletscherKodexTyp
    prozedur: GletscherKodexProzedur
    canonical: bool = True


@dataclass(frozen=True)
class GletscherKodex:
    eintraege: tuple[GletscherKodexEintrag, ...]
    parent: Optional[FlusshydrologieCharta] = None


def build_gletscher_kodex(parent: Optional[FlusshydrologieCharta] = None) -> GletscherKodex:
    if parent is None:
        parent = build_flusshydrologie_charta()
    base = sum(n.hydrologie_weight for n in parent.normen)
    eintraege = tuple(
        GletscherKodexEintrag(
            geltung=g,
            hydrologie_weight=round(base + _WEIGHT_DELTA[g], 4),
            hydrologie_tier=i + 1,
            hydrologie_ids=(f"gletscher-kodex-{g.name.lower()}-001",),
            hydrologie_tags=("hydrologie", "gletscher", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(GletscherKodexGeltung)
    )
    return GletscherKodex(eintraege=eintraege, parent=parent)
