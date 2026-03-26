from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .stratigraphie_charta import StratigraphieCharta, build_stratigraphie_charta


class PalaeoklimatologieKodexGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_PALAEONTOLOGISCH = auto()
    PALAEONTOLOGISCH = auto()
    PALAEONTOLOGISCH_AKTIV = auto()
    PALAEONTOLOGIE_SOUVERAEN = auto()


class PalaeoklimatologieKodexTyp(Enum):
    PALAEOKLIMATOLOGIEKODEX = auto()
    PALAEOKLIMATOLOGIESYSTEM = auto()
    PALAEOKLIMATOLOGIEKOMPONENTE = auto()


class PalaeoklimatologieKodexProzedur(Enum):
    PALAEOKLIMATOLOGIEANALYSE = auto()
    PALAEOKLIMATOLOGIESYNTHESE = auto()
    PALAEOKLIMATOLOGIEBEWERTUNG = auto()


_WEIGHT_DELTA: dict[PalaeoklimatologieKodexGeltung, float] = {
    PalaeoklimatologieKodexGeltung.GESPERRT: 0.0,
    PalaeoklimatologieKodexGeltung.GRUNDLEGEND_PALAEONTOLOGISCH: 1.5,
    PalaeoklimatologieKodexGeltung.PALAEONTOLOGISCH: 3.0,
    PalaeoklimatologieKodexGeltung.PALAEONTOLOGISCH_AKTIV: 4.5,
    PalaeoklimatologieKodexGeltung.PALAEONTOLOGIE_SOUVERAEN: 6.0,
}

_TYP_MAP = {
    PalaeoklimatologieKodexGeltung.GESPERRT: PalaeoklimatologieKodexTyp.PALAEOKLIMATOLOGIEKODEX,
    PalaeoklimatologieKodexGeltung.GRUNDLEGEND_PALAEONTOLOGISCH: PalaeoklimatologieKodexTyp.PALAEOKLIMATOLOGIEKOMPONENTE,
    PalaeoklimatologieKodexGeltung.PALAEONTOLOGISCH: PalaeoklimatologieKodexTyp.PALAEOKLIMATOLOGIEKOMPONENTE,
    PalaeoklimatologieKodexGeltung.PALAEONTOLOGISCH_AKTIV: PalaeoklimatologieKodexTyp.PALAEOKLIMATOLOGIESYSTEM,
    PalaeoklimatologieKodexGeltung.PALAEONTOLOGIE_SOUVERAEN: PalaeoklimatologieKodexTyp.PALAEOKLIMATOLOGIESYSTEM,
}

_PROZEDUR_MAP = {
    PalaeoklimatologieKodexGeltung.GESPERRT: PalaeoklimatologieKodexProzedur.PALAEOKLIMATOLOGIEANALYSE,
    PalaeoklimatologieKodexGeltung.GRUNDLEGEND_PALAEONTOLOGISCH: PalaeoklimatologieKodexProzedur.PALAEOKLIMATOLOGIEANALYSE,
    PalaeoklimatologieKodexGeltung.PALAEONTOLOGISCH: PalaeoklimatologieKodexProzedur.PALAEOKLIMATOLOGIESYNTHESE,
    PalaeoklimatologieKodexGeltung.PALAEONTOLOGISCH_AKTIV: PalaeoklimatologieKodexProzedur.PALAEOKLIMATOLOGIESYNTHESE,
    PalaeoklimatologieKodexGeltung.PALAEONTOLOGIE_SOUVERAEN: PalaeoklimatologieKodexProzedur.PALAEOKLIMATOLOGIEBEWERTUNG,
}


@dataclass(frozen=True)
class PalaeoklimatologieKodexEintrag:
    geltung: PalaeoklimatologieKodexGeltung
    palaeontologie_weight: float
    palaeontologie_tier: int
    palaeontologie_ids: tuple[str, ...]
    palaeontologie_tags: tuple[str, ...]
    typ: PalaeoklimatologieKodexTyp
    prozedur: PalaeoklimatologieKodexProzedur
    canonical: bool = True


@dataclass(frozen=True)
class PalaeoklimatologieKodex:
    eintraege: tuple[PalaeoklimatologieKodexEintrag, ...]
    parent: Optional[StratigraphieCharta] = None


def build_palaeoklimatologie_kodex(parent: Optional[StratigraphieCharta] = None) -> PalaeoklimatologieKodex:
    if parent is None:
        parent = build_stratigraphie_charta()
    base = sum(n.palaeontologie_weight for n in parent.normen)
    eintraege = tuple(
        PalaeoklimatologieKodexEintrag(
            geltung=g,
            palaeontologie_weight=round(base + _WEIGHT_DELTA[g], 4),
            palaeontologie_tier=i + 1,
            palaeontologie_ids=(f"palaeoklimatologie-kodex-{g.name.lower()}-001",),
            palaeontologie_tags=("palaeontologie", "palaeoklimatologie", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(PalaeoklimatologieKodexGeltung)
    )
    return PalaeoklimatologieKodex(eintraege=eintraege, parent=parent)
