from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .periglazialmorphologie_manifest import PeriglazialmorphologieManifest, build_periglazialmorphologie_manifest


class FlussmorphologiePaktGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_GEOMORPHOLOGISCH = auto()
    GEOMORPHOLOGISCH = auto()
    GEOMORPHOLOGISCH_AKTIV = auto()
    GEOMORPHOLOGIE_SOUVERAEN = auto()


class FlussmorphologiePaktTyp(Enum):
    FLUSSMORPHOLOGIEPAKT = auto()
    FLUSSMORPHOLOGIESYSTEM = auto()
    FLUSSMORPHOLOGIEKOMPONENTE = auto()


class FlussmorphologiePaktProzedur(Enum):
    FLUSSMORPHOLOGIEANALYSE = auto()
    FLUSSMORPHOLOGIESYNTHESE = auto()
    FLUSSMORPHOLOGIEBEWERTUNG = auto()


_WEIGHT_DELTA: dict[FlussmorphologiePaktGeltung, float] = {
    FlussmorphologiePaktGeltung.GESPERRT: 0.0,
    FlussmorphologiePaktGeltung.GRUNDLEGEND_GEOMORPHOLOGISCH: 1.7,
    FlussmorphologiePaktGeltung.GEOMORPHOLOGISCH: 3.4,
    FlussmorphologiePaktGeltung.GEOMORPHOLOGISCH_AKTIV: 5.1,
    FlussmorphologiePaktGeltung.GEOMORPHOLOGIE_SOUVERAEN: 6.8,
}

_TYP_MAP = {
    FlussmorphologiePaktGeltung.GESPERRT: FlussmorphologiePaktTyp.FLUSSMORPHOLOGIEPAKT,
    FlussmorphologiePaktGeltung.GRUNDLEGEND_GEOMORPHOLOGISCH: FlussmorphologiePaktTyp.FLUSSMORPHOLOGIEKOMPONENTE,
    FlussmorphologiePaktGeltung.GEOMORPHOLOGISCH: FlussmorphologiePaktTyp.FLUSSMORPHOLOGIEKOMPONENTE,
    FlussmorphologiePaktGeltung.GEOMORPHOLOGISCH_AKTIV: FlussmorphologiePaktTyp.FLUSSMORPHOLOGIESYSTEM,
    FlussmorphologiePaktGeltung.GEOMORPHOLOGIE_SOUVERAEN: FlussmorphologiePaktTyp.FLUSSMORPHOLOGIESYSTEM,
}

_PROZEDUR_MAP = {
    FlussmorphologiePaktGeltung.GESPERRT: FlussmorphologiePaktProzedur.FLUSSMORPHOLOGIEANALYSE,
    FlussmorphologiePaktGeltung.GRUNDLEGEND_GEOMORPHOLOGISCH: FlussmorphologiePaktProzedur.FLUSSMORPHOLOGIEANALYSE,
    FlussmorphologiePaktGeltung.GEOMORPHOLOGISCH: FlussmorphologiePaktProzedur.FLUSSMORPHOLOGIESYNTHESE,
    FlussmorphologiePaktGeltung.GEOMORPHOLOGISCH_AKTIV: FlussmorphologiePaktProzedur.FLUSSMORPHOLOGIESYNTHESE,
    FlussmorphologiePaktGeltung.GEOMORPHOLOGIE_SOUVERAEN: FlussmorphologiePaktProzedur.FLUSSMORPHOLOGIEBEWERTUNG,
}


@dataclass(frozen=True)
class FlussmorphologiePaktEintrag:
    geltung: FlussmorphologiePaktGeltung
    geomorphologie_weight: float
    geomorphologie_tier: int
    geomorphologie_ids: tuple[str, ...]
    geomorphologie_tags: tuple[str, ...]
    typ: FlussmorphologiePaktTyp
    prozedur: FlussmorphologiePaktProzedur
    canonical: bool = True


@dataclass(frozen=True)
class FlussmorphologiePakt:
    eintraege: tuple[FlussmorphologiePaktEintrag, ...]
    parent: Optional[PeriglazialmorphologieManifest] = None


def build_flussmorphologie_pakt(parent: Optional[PeriglazialmorphologieManifest] = None) -> FlussmorphologiePakt:
    if parent is None:
        parent = build_periglazialmorphologie_manifest()
    base = sum(n.geomorphologie_weight for n in parent.normen)
    eintraege = tuple(
        FlussmorphologiePaktEintrag(
            geltung=g,
            geomorphologie_weight=round(base + _WEIGHT_DELTA[g], 4),
            geomorphologie_tier=i + 1,
            geomorphologie_ids=(f"flussmorphologie-pakt-{g.name.lower()}-001",),
            geomorphologie_tags=("geomorphologie", "flussmorphologie", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(FlussmorphologiePaktGeltung)
    )
    return FlussmorphologiePakt(eintraege=eintraege, parent=parent)
