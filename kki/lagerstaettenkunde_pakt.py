from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .petrologie_manifest import PetrologieManifest, build_petrologie_manifest


class LagerstättenkundePaktGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_MINERALOGISCH = auto()
    MINERALOGISCH = auto()
    MINERALOGISCH_AKTIV = auto()
    MINERALOGIE_SOUVERAEN = auto()


class LagerstättenkundePaktTyp(Enum):
    LAGERSTAETTENPAKT = auto()
    LAGERSTAETTENSYSTEM = auto()
    LAGERSTAETTENKOMPONENTE = auto()


class LagerstättenkundePaktProzedur(Enum):
    LAGERSTAETTENANALYSE = auto()
    LAGERSTAETTENSYNTHESE = auto()
    LAGERSTAETTENBEWERTUNG = auto()


_WEIGHT_DELTA: dict[LagerstättenkundePaktGeltung, float] = {
    LagerstättenkundePaktGeltung.GESPERRT: 0.0,
    LagerstättenkundePaktGeltung.GRUNDLEGEND_MINERALOGISCH: 1.7,
    LagerstättenkundePaktGeltung.MINERALOGISCH: 3.4,
    LagerstättenkundePaktGeltung.MINERALOGISCH_AKTIV: 5.1,
    LagerstättenkundePaktGeltung.MINERALOGIE_SOUVERAEN: 6.8,
}

_TYP_MAP = {
    LagerstättenkundePaktGeltung.GESPERRT: LagerstättenkundePaktTyp.LAGERSTAETTENPAKT,
    LagerstättenkundePaktGeltung.GRUNDLEGEND_MINERALOGISCH: LagerstättenkundePaktTyp.LAGERSTAETTENKOMPONENTE,
    LagerstättenkundePaktGeltung.MINERALOGISCH: LagerstättenkundePaktTyp.LAGERSTAETTENKOMPONENTE,
    LagerstättenkundePaktGeltung.MINERALOGISCH_AKTIV: LagerstättenkundePaktTyp.LAGERSTAETTENSYSTEM,
    LagerstättenkundePaktGeltung.MINERALOGIE_SOUVERAEN: LagerstättenkundePaktTyp.LAGERSTAETTENSYSTEM,
}

_PROZEDUR_MAP = {
    LagerstättenkundePaktGeltung.GESPERRT: LagerstättenkundePaktProzedur.LAGERSTAETTENANALYSE,
    LagerstättenkundePaktGeltung.GRUNDLEGEND_MINERALOGISCH: LagerstättenkundePaktProzedur.LAGERSTAETTENANALYSE,
    LagerstättenkundePaktGeltung.MINERALOGISCH: LagerstättenkundePaktProzedur.LAGERSTAETTENSYNTHESE,
    LagerstättenkundePaktGeltung.MINERALOGISCH_AKTIV: LagerstättenkundePaktProzedur.LAGERSTAETTENSYNTHESE,
    LagerstättenkundePaktGeltung.MINERALOGIE_SOUVERAEN: LagerstättenkundePaktProzedur.LAGERSTAETTENBEWERTUNG,
}


@dataclass(frozen=True)
class LagerstättenkundePaktEintrag:
    geltung: LagerstättenkundePaktGeltung
    mineralogie_weight: float
    mineralogie_tier: int
    mineralogie_ids: tuple[str, ...]
    mineralogie_tags: tuple[str, ...]
    typ: LagerstättenkundePaktTyp
    prozedur: LagerstättenkundePaktProzedur
    canonical: bool = True


@dataclass(frozen=True)
class LagerstättenkundePakt:
    eintraege: tuple[LagerstättenkundePaktEintrag, ...]
    parent: Optional[PetrologieManifest] = None


def build_lagerstaettenkunde_pakt(parent: Optional[PetrologieManifest] = None) -> LagerstättenkundePakt:
    if parent is None:
        parent = build_petrologie_manifest()
    base = sum(n.mineralogie_weight for n in parent.normen)
    eintraege = tuple(
        LagerstättenkundePaktEintrag(
            geltung=g,
            mineralogie_weight=round(base + _WEIGHT_DELTA[g], 4),
            mineralogie_tier=i + 1,
            mineralogie_ids=(f"lagerstaettenkunde-pakt-{g.name.lower()}-001",),
            mineralogie_tags=("mineralogie", "lagerstaettenkunde", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(LagerstättenkundePaktGeltung)
    )
    return LagerstättenkundePakt(eintraege=eintraege, parent=parent)
