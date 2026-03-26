from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .hydrologie_verfassung import HydrologieVerfassung, build_hydrologie_verfassung


class MineralogieFeldGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_MINERALOGISCH = auto()
    MINERALOGISCH = auto()
    MINERALOGISCH_AKTIV = auto()
    MINERALOGIE_SOUVERAEN = auto()


class MineralogieFeldTyp(Enum):
    MINERALOGIEFELD = auto()
    MINERALOGIESYSTEM = auto()
    MINERALOGIEKOMPONENTE = auto()


class MineralogieFeldProzedur(Enum):
    MINERALOGIEANALYSE = auto()
    MINERALOGIESYNTHESE = auto()
    MINERALOGIEBEWERTUNG = auto()


_WEIGHT_DELTA: dict[MineralogieFeldGeltung, float] = {
    MineralogieFeldGeltung.GESPERRT: 0.0,
    MineralogieFeldGeltung.GRUNDLEGEND_MINERALOGISCH: 1.2,
    MineralogieFeldGeltung.MINERALOGISCH: 2.4,
    MineralogieFeldGeltung.MINERALOGISCH_AKTIV: 3.6,
    MineralogieFeldGeltung.MINERALOGIE_SOUVERAEN: 5.0,
}

_TYP_MAP = {
    MineralogieFeldGeltung.GESPERRT: MineralogieFeldTyp.MINERALOGIEFELD,
    MineralogieFeldGeltung.GRUNDLEGEND_MINERALOGISCH: MineralogieFeldTyp.MINERALOGIEKOMPONENTE,
    MineralogieFeldGeltung.MINERALOGISCH: MineralogieFeldTyp.MINERALOGIEKOMPONENTE,
    MineralogieFeldGeltung.MINERALOGISCH_AKTIV: MineralogieFeldTyp.MINERALOGIESYSTEM,
    MineralogieFeldGeltung.MINERALOGIE_SOUVERAEN: MineralogieFeldTyp.MINERALOGIESYSTEM,
}

_PROZEDUR_MAP = {
    MineralogieFeldGeltung.GESPERRT: MineralogieFeldProzedur.MINERALOGIEANALYSE,
    MineralogieFeldGeltung.GRUNDLEGEND_MINERALOGISCH: MineralogieFeldProzedur.MINERALOGIEANALYSE,
    MineralogieFeldGeltung.MINERALOGISCH: MineralogieFeldProzedur.MINERALOGIESYNTHESE,
    MineralogieFeldGeltung.MINERALOGISCH_AKTIV: MineralogieFeldProzedur.MINERALOGIESYNTHESE,
    MineralogieFeldGeltung.MINERALOGIE_SOUVERAEN: MineralogieFeldProzedur.MINERALOGIEBEWERTUNG,
}


@dataclass(frozen=True)
class MineralogieFeldNorm:
    geltung: MineralogieFeldGeltung
    mineralogie_weight: float
    mineralogie_tier: int
    mineralogie_ids: tuple[str, ...]
    mineralogie_tags: tuple[str, ...]
    typ: MineralogieFeldTyp
    prozedur: MineralogieFeldProzedur
    canonical: bool = True


@dataclass(frozen=True)
class MineralogieFeld:
    normen: tuple[MineralogieFeldNorm, ...]
    parent: Optional[HydrologieVerfassung] = None


def build_mineralogie_feld(parent: Optional[HydrologieVerfassung] = None) -> MineralogieFeld:
    if parent is None:
        parent = build_hydrologie_verfassung()
    base = sum(n.hydrologie_weight for n in parent.normen)
    normen = tuple(
        MineralogieFeldNorm(
            geltung=g,
            mineralogie_weight=round(base + _WEIGHT_DELTA[g], 4),
            mineralogie_tier=i + 1,
            mineralogie_ids=(f"mineralogie-feld-{g.name.lower()}-001",),
            mineralogie_tags=("mineralogie", "feld", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(MineralogieFeldGeltung)
    )
    return MineralogieFeld(normen=normen, parent=parent)
