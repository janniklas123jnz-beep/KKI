from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .geophysik_verfassung import GeophysikVerfassung, build_geophysik_verfassung


class HydrologieFeldGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_HYDROLOGISCH = auto()
    HYDROLOGISCH = auto()
    HYDROLOGISCH_AKTIV = auto()
    HYDROLOGIE_SOUVERAEN = auto()


class HydrologieFeldTyp(Enum):
    HYDROLOGIEFELD = auto()
    HYDROLOGIESYSTEM = auto()
    HYDROLOGIEKOMPONENTE = auto()


class HydrologieFeldProzedur(Enum):
    HYDROLOGIEANALYSE = auto()
    HYDROLOGIESYNTHESE = auto()
    HYDROLOGIEBEWERTUNG = auto()


_WEIGHT_DELTA: dict[HydrologieFeldGeltung, float] = {
    HydrologieFeldGeltung.GESPERRT: 0.0,
    HydrologieFeldGeltung.GRUNDLEGEND_HYDROLOGISCH: 1.2,
    HydrologieFeldGeltung.HYDROLOGISCH: 2.4,
    HydrologieFeldGeltung.HYDROLOGISCH_AKTIV: 3.6,
    HydrologieFeldGeltung.HYDROLOGIE_SOUVERAEN: 5.0,
}

_TYP_MAP = {
    HydrologieFeldGeltung.GESPERRT: HydrologieFeldTyp.HYDROLOGIEFELD,
    HydrologieFeldGeltung.GRUNDLEGEND_HYDROLOGISCH: HydrologieFeldTyp.HYDROLOGIEKOMPONENTE,
    HydrologieFeldGeltung.HYDROLOGISCH: HydrologieFeldTyp.HYDROLOGIEKOMPONENTE,
    HydrologieFeldGeltung.HYDROLOGISCH_AKTIV: HydrologieFeldTyp.HYDROLOGIESYSTEM,
    HydrologieFeldGeltung.HYDROLOGIE_SOUVERAEN: HydrologieFeldTyp.HYDROLOGIESYSTEM,
}

_PROZEDUR_MAP = {
    HydrologieFeldGeltung.GESPERRT: HydrologieFeldProzedur.HYDROLOGIEANALYSE,
    HydrologieFeldGeltung.GRUNDLEGEND_HYDROLOGISCH: HydrologieFeldProzedur.HYDROLOGIEANALYSE,
    HydrologieFeldGeltung.HYDROLOGISCH: HydrologieFeldProzedur.HYDROLOGIESYNTHESE,
    HydrologieFeldGeltung.HYDROLOGISCH_AKTIV: HydrologieFeldProzedur.HYDROLOGIESYNTHESE,
    HydrologieFeldGeltung.HYDROLOGIE_SOUVERAEN: HydrologieFeldProzedur.HYDROLOGIEBEWERTUNG,
}


@dataclass(frozen=True)
class HydrologieFeldNorm:
    geltung: HydrologieFeldGeltung
    hydrologie_weight: float
    hydrologie_tier: int
    hydrologie_ids: tuple[str, ...]
    hydrologie_tags: tuple[str, ...]
    typ: HydrologieFeldTyp
    prozedur: HydrologieFeldProzedur
    canonical: bool = True


@dataclass(frozen=True)
class HydrologieFeld:
    normen: tuple[HydrologieFeldNorm, ...]
    parent: Optional[GeophysikVerfassung] = None


def build_hydrologie_feld(parent: Optional[GeophysikVerfassung] = None) -> HydrologieFeld:
    if parent is None:
        parent = build_geophysik_verfassung()
    base = sum(n.geophysik_weight for n in parent.normen)
    normen = tuple(
        HydrologieFeldNorm(
            geltung=g,
            hydrologie_weight=round(base + _WEIGHT_DELTA[g], 4),
            hydrologie_tier=i + 1,
            hydrologie_ids=(f"hydrologie-feld-{g.name.lower()}-001",),
            hydrologie_tags=("hydrologie", "feld", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(HydrologieFeldGeltung)
    )
    return HydrologieFeld(normen=normen, parent=parent)
