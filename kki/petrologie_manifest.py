from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .mineralchemie_kodex import MineralchemieKodex, build_mineralchemie_kodex


class PetrologieManifestGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_MINERALOGISCH = auto()
    MINERALOGISCH = auto()
    MINERALOGISCH_AKTIV = auto()
    MINERALOGIE_SOUVERAEN = auto()


class PetrologieManifestTyp(Enum):
    PETROLOGIEMANIFEST = auto()
    PETROLOGIESYSTEM = auto()
    PETROLOGIEKOMPONENTE = auto()


class PetrologieManifestProzedur(Enum):
    PETROLOGIEANALYSE = auto()
    PETROLOGIESYNTHESE = auto()
    PETROLOGIEBEWERTUNG = auto()


_WEIGHT_DELTA: dict[PetrologieManifestGeltung, float] = {
    PetrologieManifestGeltung.GESPERRT: 0.0,
    PetrologieManifestGeltung.GRUNDLEGEND_MINERALOGISCH: 1.6,
    PetrologieManifestGeltung.MINERALOGISCH: 3.2,
    PetrologieManifestGeltung.MINERALOGISCH_AKTIV: 4.8,
    PetrologieManifestGeltung.MINERALOGIE_SOUVERAEN: 6.4,
}

_TYP_MAP = {
    PetrologieManifestGeltung.GESPERRT: PetrologieManifestTyp.PETROLOGIEMANIFEST,
    PetrologieManifestGeltung.GRUNDLEGEND_MINERALOGISCH: PetrologieManifestTyp.PETROLOGIEKOMPONENTE,
    PetrologieManifestGeltung.MINERALOGISCH: PetrologieManifestTyp.PETROLOGIEKOMPONENTE,
    PetrologieManifestGeltung.MINERALOGISCH_AKTIV: PetrologieManifestTyp.PETROLOGIESYSTEM,
    PetrologieManifestGeltung.MINERALOGIE_SOUVERAEN: PetrologieManifestTyp.PETROLOGIESYSTEM,
}

_PROZEDUR_MAP = {
    PetrologieManifestGeltung.GESPERRT: PetrologieManifestProzedur.PETROLOGIEANALYSE,
    PetrologieManifestGeltung.GRUNDLEGEND_MINERALOGISCH: PetrologieManifestProzedur.PETROLOGIEANALYSE,
    PetrologieManifestGeltung.MINERALOGISCH: PetrologieManifestProzedur.PETROLOGIESYNTHESE,
    PetrologieManifestGeltung.MINERALOGISCH_AKTIV: PetrologieManifestProzedur.PETROLOGIESYNTHESE,
    PetrologieManifestGeltung.MINERALOGIE_SOUVERAEN: PetrologieManifestProzedur.PETROLOGIEBEWERTUNG,
}


@dataclass(frozen=True)
class PetrologieManifestNorm:
    geltung: PetrologieManifestGeltung
    mineralogie_weight: float
    mineralogie_tier: int
    mineralogie_ids: tuple[str, ...]
    mineralogie_tags: tuple[str, ...]
    typ: PetrologieManifestTyp
    prozedur: PetrologieManifestProzedur
    canonical: bool = True


@dataclass(frozen=True)
class PetrologieManifest:
    normen: tuple[PetrologieManifestNorm, ...]
    parent: Optional[MineralchemieKodex] = None


def build_petrologie_manifest(parent: Optional[MineralchemieKodex] = None) -> PetrologieManifest:
    if parent is None:
        parent = build_mineralchemie_kodex()
    base = sum(e.mineralogie_weight for e in parent.eintraege)
    normen = tuple(
        PetrologieManifestNorm(
            geltung=g,
            mineralogie_weight=round(base + _WEIGHT_DELTA[g], 4),
            mineralogie_tier=i + 1,
            mineralogie_ids=(f"petrologie-manifest-{g.name.lower()}-001",),
            mineralogie_tags=("mineralogie", "petrologie", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(PetrologieManifestGeltung)
    )
    return PetrologieManifest(normen=normen, parent=parent)
