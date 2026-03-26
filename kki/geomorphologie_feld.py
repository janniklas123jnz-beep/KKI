from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .palaeontologie_verfassung import PalaeontologieVerfassung, build_palaeontologie_verfassung


class GeomorphologieFeldGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_GEOMORPHOLOGISCH = auto()
    GEOMORPHOLOGISCH = auto()
    GEOMORPHOLOGISCH_AKTIV = auto()
    GEOMORPHOLOGIE_SOUVERAEN = auto()


class GeomorphologieFeldTyp(Enum):
    GEOMORPHOLOGIEFELD = auto()
    GEOMORPHOLOGIESYSTEM = auto()
    GEOMORPHOLOGIEKOMPONENTE = auto()


class GeomorphologieFeldProzedur(Enum):
    GEOMORPHOLOGIEANALYSE = auto()
    GEOMORPHOLOGIESYNTHESE = auto()
    GEOMORPHOLOGIEBEWERTUNG = auto()


_WEIGHT_DELTA: dict[GeomorphologieFeldGeltung, float] = {
    GeomorphologieFeldGeltung.GESPERRT: 0.0,
    GeomorphologieFeldGeltung.GRUNDLEGEND_GEOMORPHOLOGISCH: 1.2,
    GeomorphologieFeldGeltung.GEOMORPHOLOGISCH: 2.4,
    GeomorphologieFeldGeltung.GEOMORPHOLOGISCH_AKTIV: 3.6,
    GeomorphologieFeldGeltung.GEOMORPHOLOGIE_SOUVERAEN: 5.0,
}

_TYP_MAP = {
    GeomorphologieFeldGeltung.GESPERRT: GeomorphologieFeldTyp.GEOMORPHOLOGIEFELD,
    GeomorphologieFeldGeltung.GRUNDLEGEND_GEOMORPHOLOGISCH: GeomorphologieFeldTyp.GEOMORPHOLOGIEKOMPONENTE,
    GeomorphologieFeldGeltung.GEOMORPHOLOGISCH: GeomorphologieFeldTyp.GEOMORPHOLOGIEKOMPONENTE,
    GeomorphologieFeldGeltung.GEOMORPHOLOGISCH_AKTIV: GeomorphologieFeldTyp.GEOMORPHOLOGIESYSTEM,
    GeomorphologieFeldGeltung.GEOMORPHOLOGIE_SOUVERAEN: GeomorphologieFeldTyp.GEOMORPHOLOGIESYSTEM,
}

_PROZEDUR_MAP = {
    GeomorphologieFeldGeltung.GESPERRT: GeomorphologieFeldProzedur.GEOMORPHOLOGIEANALYSE,
    GeomorphologieFeldGeltung.GRUNDLEGEND_GEOMORPHOLOGISCH: GeomorphologieFeldProzedur.GEOMORPHOLOGIEANALYSE,
    GeomorphologieFeldGeltung.GEOMORPHOLOGISCH: GeomorphologieFeldProzedur.GEOMORPHOLOGIESYNTHESE,
    GeomorphologieFeldGeltung.GEOMORPHOLOGISCH_AKTIV: GeomorphologieFeldProzedur.GEOMORPHOLOGIESYNTHESE,
    GeomorphologieFeldGeltung.GEOMORPHOLOGIE_SOUVERAEN: GeomorphologieFeldProzedur.GEOMORPHOLOGIEBEWERTUNG,
}


@dataclass(frozen=True)
class GeomorphologieFeldNorm:
    geltung: GeomorphologieFeldGeltung
    geomorphologie_weight: float
    geomorphologie_tier: int
    geomorphologie_ids: tuple[str, ...]
    geomorphologie_tags: tuple[str, ...]
    typ: GeomorphologieFeldTyp
    prozedur: GeomorphologieFeldProzedur
    canonical: bool = True


@dataclass(frozen=True)
class GeomorphologieFeld:
    normen: tuple[GeomorphologieFeldNorm, ...]
    parent: Optional[PalaeontologieVerfassung] = None


def build_geomorphologie_feld(parent: Optional[PalaeontologieVerfassung] = None) -> GeomorphologieFeld:
    if parent is None:
        parent = build_palaeontologie_verfassung()
    base = sum(n.palaeontologie_weight for n in parent.normen)
    normen = tuple(
        GeomorphologieFeldNorm(
            geltung=g,
            geomorphologie_weight=round(base + _WEIGHT_DELTA[g], 4),
            geomorphologie_tier=i + 1,
            geomorphologie_ids=(f"geomorphologie-feld-{g.name.lower()}-001",),
            geomorphologie_tags=("geomorphologie", "feld", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(GeomorphologieFeldGeltung)
    )
    return GeomorphologieFeld(normen=normen, parent=parent)
