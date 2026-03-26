from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .meteorologie_verfassung import MeteorologieVerfassung, build_meteorologie_verfassung


class PalaeontologieFeldGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_PALAEONTOLOGISCH = auto()
    PALAEONTOLOGISCH = auto()
    PALAEONTOLOGISCH_AKTIV = auto()
    PALAEONTOLOGIE_SOUVERAEN = auto()


class PalaeontologieFeldTyp(Enum):
    PALAEONTOLOGIEFELD = auto()
    PALAEONTOLOGIESYSTEM = auto()
    PALAEONTOLOGIEKOMPONENTE = auto()


class PalaeontologieFeldProzedur(Enum):
    PALAEONTOLOGIEANALYSE = auto()
    PALAEONTOLOGIESYNTHESE = auto()
    PALAEONTOLOGIEBEWERTUNG = auto()


_WEIGHT_DELTA: dict[PalaeontologieFeldGeltung, float] = {
    PalaeontologieFeldGeltung.GESPERRT: 0.0,
    PalaeontologieFeldGeltung.GRUNDLEGEND_PALAEONTOLOGISCH: 1.2,
    PalaeontologieFeldGeltung.PALAEONTOLOGISCH: 2.4,
    PalaeontologieFeldGeltung.PALAEONTOLOGISCH_AKTIV: 3.6,
    PalaeontologieFeldGeltung.PALAEONTOLOGIE_SOUVERAEN: 5.0,
}

_TYP_MAP = {
    PalaeontologieFeldGeltung.GESPERRT: PalaeontologieFeldTyp.PALAEONTOLOGIEFELD,
    PalaeontologieFeldGeltung.GRUNDLEGEND_PALAEONTOLOGISCH: PalaeontologieFeldTyp.PALAEONTOLOGIEKOMPONENTE,
    PalaeontologieFeldGeltung.PALAEONTOLOGISCH: PalaeontologieFeldTyp.PALAEONTOLOGIEKOMPONENTE,
    PalaeontologieFeldGeltung.PALAEONTOLOGISCH_AKTIV: PalaeontologieFeldTyp.PALAEONTOLOGIESYSTEM,
    PalaeontologieFeldGeltung.PALAEONTOLOGIE_SOUVERAEN: PalaeontologieFeldTyp.PALAEONTOLOGIESYSTEM,
}

_PROZEDUR_MAP = {
    PalaeontologieFeldGeltung.GESPERRT: PalaeontologieFeldProzedur.PALAEONTOLOGIEANALYSE,
    PalaeontologieFeldGeltung.GRUNDLEGEND_PALAEONTOLOGISCH: PalaeontologieFeldProzedur.PALAEONTOLOGIEANALYSE,
    PalaeontologieFeldGeltung.PALAEONTOLOGISCH: PalaeontologieFeldProzedur.PALAEONTOLOGIESYNTHESE,
    PalaeontologieFeldGeltung.PALAEONTOLOGISCH_AKTIV: PalaeontologieFeldProzedur.PALAEONTOLOGIESYNTHESE,
    PalaeontologieFeldGeltung.PALAEONTOLOGIE_SOUVERAEN: PalaeontologieFeldProzedur.PALAEONTOLOGIEBEWERTUNG,
}


@dataclass(frozen=True)
class PalaeontologieFeldNorm:
    geltung: PalaeontologieFeldGeltung
    palaeontologie_weight: float
    palaeontologie_tier: int
    palaeontologie_ids: tuple[str, ...]
    palaeontologie_tags: tuple[str, ...]
    typ: PalaeontologieFeldTyp
    prozedur: PalaeontologieFeldProzedur
    canonical: bool = True


@dataclass(frozen=True)
class PalaeontologieFeld:
    normen: tuple[PalaeontologieFeldNorm, ...]
    parent: Optional[MeteorologieVerfassung] = None


def build_palaeontologie_feld(parent: Optional[MeteorologieVerfassung] = None) -> PalaeontologieFeld:
    if parent is None:
        parent = build_meteorologie_verfassung()
    base = sum(n.meteorologie_weight for n in parent.normen)
    normen = tuple(
        PalaeontologieFeldNorm(
            geltung=g,
            palaeontologie_weight=round(base + _WEIGHT_DELTA[g], 4),
            palaeontologie_tier=i + 1,
            palaeontologie_ids=(f"palaeontologie-feld-{g.name.lower()}-001",),
            palaeontologie_tags=("palaeontologie", "feld", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(PalaeontologieFeldGeltung)
    )
    return PalaeontologieFeld(normen=normen, parent=parent)
