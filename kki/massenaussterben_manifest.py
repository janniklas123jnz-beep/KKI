from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .palaeoklimatologie_kodex import PalaeoklimatologieKodex, build_palaeoklimatologie_kodex


class MassenaussterbenManifestGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_PALAEONTOLOGISCH = auto()
    PALAEONTOLOGISCH = auto()
    PALAEONTOLOGISCH_AKTIV = auto()
    PALAEONTOLOGIE_SOUVERAEN = auto()


class MassenaussterbenManifestTyp(Enum):
    MASSENAUSSTERBENMANIFEST = auto()
    MASSENAUSSTERBESYSTEM = auto()
    MASSENAUSSTERBEKOMPONENTE = auto()


class MassenaussterbenManifestProzedur(Enum):
    MASSENAUSSTERBEANALYSE = auto()
    MASSENAUSSTERBSYNTHESE = auto()
    MASSENAUSSTERBEBEWERTUNG = auto()


_WEIGHT_DELTA: dict[MassenaussterbenManifestGeltung, float] = {
    MassenaussterbenManifestGeltung.GESPERRT: 0.0,
    MassenaussterbenManifestGeltung.GRUNDLEGEND_PALAEONTOLOGISCH: 1.6,
    MassenaussterbenManifestGeltung.PALAEONTOLOGISCH: 3.2,
    MassenaussterbenManifestGeltung.PALAEONTOLOGISCH_AKTIV: 4.8,
    MassenaussterbenManifestGeltung.PALAEONTOLOGIE_SOUVERAEN: 6.4,
}

_TYP_MAP = {
    MassenaussterbenManifestGeltung.GESPERRT: MassenaussterbenManifestTyp.MASSENAUSSTERBENMANIFEST,
    MassenaussterbenManifestGeltung.GRUNDLEGEND_PALAEONTOLOGISCH: MassenaussterbenManifestTyp.MASSENAUSSTERBEKOMPONENTE,
    MassenaussterbenManifestGeltung.PALAEONTOLOGISCH: MassenaussterbenManifestTyp.MASSENAUSSTERBEKOMPONENTE,
    MassenaussterbenManifestGeltung.PALAEONTOLOGISCH_AKTIV: MassenaussterbenManifestTyp.MASSENAUSSTERBESYSTEM,
    MassenaussterbenManifestGeltung.PALAEONTOLOGIE_SOUVERAEN: MassenaussterbenManifestTyp.MASSENAUSSTERBESYSTEM,
}

_PROZEDUR_MAP = {
    MassenaussterbenManifestGeltung.GESPERRT: MassenaussterbenManifestProzedur.MASSENAUSSTERBEANALYSE,
    MassenaussterbenManifestGeltung.GRUNDLEGEND_PALAEONTOLOGISCH: MassenaussterbenManifestProzedur.MASSENAUSSTERBEANALYSE,
    MassenaussterbenManifestGeltung.PALAEONTOLOGISCH: MassenaussterbenManifestProzedur.MASSENAUSSTERBSYNTHESE,
    MassenaussterbenManifestGeltung.PALAEONTOLOGISCH_AKTIV: MassenaussterbenManifestProzedur.MASSENAUSSTERBSYNTHESE,
    MassenaussterbenManifestGeltung.PALAEONTOLOGIE_SOUVERAEN: MassenaussterbenManifestProzedur.MASSENAUSSTERBEBEWERTUNG,
}


@dataclass(frozen=True)
class MassenaussterbenManifestNorm:
    geltung: MassenaussterbenManifestGeltung
    palaeontologie_weight: float
    palaeontologie_tier: int
    palaeontologie_ids: tuple[str, ...]
    palaeontologie_tags: tuple[str, ...]
    typ: MassenaussterbenManifestTyp
    prozedur: MassenaussterbenManifestProzedur
    canonical: bool = True


@dataclass(frozen=True)
class MassenaussterbenManifest:
    normen: tuple[MassenaussterbenManifestNorm, ...]
    parent: Optional[PalaeoklimatologieKodex] = None


def build_massenaussterben_manifest(parent: Optional[PalaeoklimatologieKodex] = None) -> MassenaussterbenManifest:
    if parent is None:
        parent = build_palaeoklimatologie_kodex()
    base = sum(e.palaeontologie_weight for e in parent.eintraege)
    normen = tuple(
        MassenaussterbenManifestNorm(
            geltung=g,
            palaeontologie_weight=round(base + _WEIGHT_DELTA[g], 4),
            palaeontologie_tier=i + 1,
            palaeontologie_ids=(f"massenaussterben-manifest-{g.name.lower()}-001",),
            palaeontologie_tags=("palaeontologie", "massenaussterben", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(MassenaussterbenManifestGeltung)
    )
    return MassenaussterbenManifest(normen=normen, parent=parent)
