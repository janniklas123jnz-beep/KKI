from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .mineralogie_verfassung import MineralogieVerfassung, build_mineralogie_verfassung


class MeteorologieFeldGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_METEOROLOGISCH = auto()
    METEOROLOGISCH = auto()
    METEOROLOGISCH_AKTIV = auto()
    METEOROLOGIE_SOUVERAEN = auto()


class MeteorologieFeldTyp(Enum):
    METEOROLOGIEFELD = auto()
    METEOROLOGIESYSTEM = auto()
    METEOROLOGIEKOMPONENTE = auto()


class MeteorologieFeldProzedur(Enum):
    METEOROLOGIEANALYSE = auto()
    METEOROLOGIESYNTHESE = auto()
    METEOROLOGIEBEWERTUNG = auto()


_WEIGHT_DELTA: dict[MeteorologieFeldGeltung, float] = {
    MeteorologieFeldGeltung.GESPERRT: 0.0,
    MeteorologieFeldGeltung.GRUNDLEGEND_METEOROLOGISCH: 1.2,
    MeteorologieFeldGeltung.METEOROLOGISCH: 2.4,
    MeteorologieFeldGeltung.METEOROLOGISCH_AKTIV: 3.6,
    MeteorologieFeldGeltung.METEOROLOGIE_SOUVERAEN: 5.0,
}

_TYP_MAP = {
    MeteorologieFeldGeltung.GESPERRT: MeteorologieFeldTyp.METEOROLOGIEFELD,
    MeteorologieFeldGeltung.GRUNDLEGEND_METEOROLOGISCH: MeteorologieFeldTyp.METEOROLOGIEKOMPONENTE,
    MeteorologieFeldGeltung.METEOROLOGISCH: MeteorologieFeldTyp.METEOROLOGIEKOMPONENTE,
    MeteorologieFeldGeltung.METEOROLOGISCH_AKTIV: MeteorologieFeldTyp.METEOROLOGIESYSTEM,
    MeteorologieFeldGeltung.METEOROLOGIE_SOUVERAEN: MeteorologieFeldTyp.METEOROLOGIESYSTEM,
}

_PROZEDUR_MAP = {
    MeteorologieFeldGeltung.GESPERRT: MeteorologieFeldProzedur.METEOROLOGIEANALYSE,
    MeteorologieFeldGeltung.GRUNDLEGEND_METEOROLOGISCH: MeteorologieFeldProzedur.METEOROLOGIEANALYSE,
    MeteorologieFeldGeltung.METEOROLOGISCH: MeteorologieFeldProzedur.METEOROLOGIESYNTHESE,
    MeteorologieFeldGeltung.METEOROLOGISCH_AKTIV: MeteorologieFeldProzedur.METEOROLOGIESYNTHESE,
    MeteorologieFeldGeltung.METEOROLOGIE_SOUVERAEN: MeteorologieFeldProzedur.METEOROLOGIEBEWERTUNG,
}


@dataclass(frozen=True)
class MeteorologieFeldNorm:
    geltung: MeteorologieFeldGeltung
    meteorologie_weight: float
    meteorologie_tier: int
    meteorologie_ids: tuple[str, ...]
    meteorologie_tags: tuple[str, ...]
    typ: MeteorologieFeldTyp
    prozedur: MeteorologieFeldProzedur
    canonical: bool = True


@dataclass(frozen=True)
class MeteorologieFeld:
    normen: tuple[MeteorologieFeldNorm, ...]
    parent: Optional[MineralogieVerfassung] = None


def build_meteorologie_feld(parent: Optional[MineralogieVerfassung] = None) -> MeteorologieFeld:
    if parent is None:
        parent = build_mineralogie_verfassung()
    base = sum(n.mineralogie_weight for n in parent.normen)
    normen = tuple(
        MeteorologieFeldNorm(
            geltung=g,
            meteorologie_weight=round(base + _WEIGHT_DELTA[g], 4),
            meteorologie_tier=i + 1,
            meteorologie_ids=(f"meteorologie-feld-{g.name.lower()}-001",),
            meteorologie_tags=("meteorologie", "feld", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(MeteorologieFeldGeltung)
    )
    return MeteorologieFeld(normen=normen, parent=parent)
