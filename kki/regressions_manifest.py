from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .hypothesentest_kodex import HypothesentestKodex, build_hypothesentest_kodex


class RegressionsManifestGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_REGRESSIV = auto()
    REGRESSIV = auto()
    REGRESSIV_AKTIV = auto()
    REGRESSION_SOUVERAEN = auto()


class RegressionsManifestTyp(Enum):
    REGRESSIONSMANIFEST = auto()
    REGRESSIONSMODELL = auto()
    KOVARIANZSTRUKTUR = auto()


class RegressionsManifestProzedur(Enum):
    REGRESSIONSANALYSE = auto()
    MODELLSELEKTION = auto()
    REGRESSIONSBEWERTUNG = auto()


_WEIGHT_DELTA: dict[RegressionsManifestGeltung, float] = {
    RegressionsManifestGeltung.GESPERRT: 0.0,
    RegressionsManifestGeltung.GRUNDLEGEND_REGRESSIV: 1.6,
    RegressionsManifestGeltung.REGRESSIV: 3.2,
    RegressionsManifestGeltung.REGRESSIV_AKTIV: 4.8,
    RegressionsManifestGeltung.REGRESSION_SOUVERAEN: 6.4,
}

_TYP_MAP = {
    RegressionsManifestGeltung.GESPERRT: RegressionsManifestTyp.REGRESSIONSMANIFEST,
    RegressionsManifestGeltung.GRUNDLEGEND_REGRESSIV: RegressionsManifestTyp.KOVARIANZSTRUKTUR,
    RegressionsManifestGeltung.REGRESSIV: RegressionsManifestTyp.KOVARIANZSTRUKTUR,
    RegressionsManifestGeltung.REGRESSIV_AKTIV: RegressionsManifestTyp.REGRESSIONSMODELL,
    RegressionsManifestGeltung.REGRESSION_SOUVERAEN: RegressionsManifestTyp.REGRESSIONSMODELL,
}

_PROZEDUR_MAP = {
    RegressionsManifestGeltung.GESPERRT: RegressionsManifestProzedur.REGRESSIONSANALYSE,
    RegressionsManifestGeltung.GRUNDLEGEND_REGRESSIV: RegressionsManifestProzedur.REGRESSIONSANALYSE,
    RegressionsManifestGeltung.REGRESSIV: RegressionsManifestProzedur.MODELLSELEKTION,
    RegressionsManifestGeltung.REGRESSIV_AKTIV: RegressionsManifestProzedur.MODELLSELEKTION,
    RegressionsManifestGeltung.REGRESSION_SOUVERAEN: RegressionsManifestProzedur.REGRESSIONSBEWERTUNG,
}


@dataclass(frozen=True)
class RegressionsManifestNorm:
    geltung: RegressionsManifestGeltung
    stat_weight: float
    stat_tier: int
    stat_ids: tuple[str, ...]
    stat_tags: tuple[str, ...]
    typ: RegressionsManifestTyp
    prozedur: RegressionsManifestProzedur
    canonical: bool = True


@dataclass(frozen=True)
class RegressionsManifest:
    normen: tuple[RegressionsManifestNorm, ...]
    parent: Optional[HypothesentestKodex] = None


def build_regressions_manifest(parent: Optional[HypothesentestKodex] = None) -> RegressionsManifest:
    if parent is None:
        parent = build_hypothesentest_kodex()
    base = sum(e.stat_weight for e in parent.eintraege)
    normen = tuple(
        RegressionsManifestNorm(
            geltung=g,
            stat_weight=round(base + _WEIGHT_DELTA[g], 4),
            stat_tier=i + 1,
            stat_ids=(f"regressions-manifest-{g.name.lower()}-001",),
            stat_tags=("regression", "manifest", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(RegressionsManifestGeltung)
    )
    return RegressionsManifest(normen=normen, parent=parent)
