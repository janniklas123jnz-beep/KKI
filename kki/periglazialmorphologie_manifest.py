from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .denudations_kodex import DenudationsKodex, build_denudations_kodex


class PeriglazialmorphologieManifestGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_GEOMORPHOLOGISCH = auto()
    GEOMORPHOLOGISCH = auto()
    GEOMORPHOLOGISCH_AKTIV = auto()
    GEOMORPHOLOGIE_SOUVERAEN = auto()


class PeriglazialmorphologieManifestTyp(Enum):
    PERIGLAZIALMORPHOLOGIEMANIFEST = auto()
    PERIGLAZIALMORPHOLOGIESYSTEM = auto()
    PERIGLAZIALMORPHOLOGIEKOMPONENTE = auto()


class PeriglazialmorphologieManifestProzedur(Enum):
    PERIGLAZIALMORPHOLOGIEANALYSE = auto()
    PERIGLAZIALMORPHOLOGIESYNTHESE = auto()
    PERIGLAZIALMORPHOLOGIEBEWERTUNG = auto()


_WEIGHT_DELTA: dict[PeriglazialmorphologieManifestGeltung, float] = {
    PeriglazialmorphologieManifestGeltung.GESPERRT: 0.0,
    PeriglazialmorphologieManifestGeltung.GRUNDLEGEND_GEOMORPHOLOGISCH: 1.6,
    PeriglazialmorphologieManifestGeltung.GEOMORPHOLOGISCH: 3.2,
    PeriglazialmorphologieManifestGeltung.GEOMORPHOLOGISCH_AKTIV: 4.8,
    PeriglazialmorphologieManifestGeltung.GEOMORPHOLOGIE_SOUVERAEN: 6.4,
}

_TYP_MAP = {
    PeriglazialmorphologieManifestGeltung.GESPERRT: PeriglazialmorphologieManifestTyp.PERIGLAZIALMORPHOLOGIEMANIFEST,
    PeriglazialmorphologieManifestGeltung.GRUNDLEGEND_GEOMORPHOLOGISCH: PeriglazialmorphologieManifestTyp.PERIGLAZIALMORPHOLOGIEKOMPONENTE,
    PeriglazialmorphologieManifestGeltung.GEOMORPHOLOGISCH: PeriglazialmorphologieManifestTyp.PERIGLAZIALMORPHOLOGIEKOMPONENTE,
    PeriglazialmorphologieManifestGeltung.GEOMORPHOLOGISCH_AKTIV: PeriglazialmorphologieManifestTyp.PERIGLAZIALMORPHOLOGIESYSTEM,
    PeriglazialmorphologieManifestGeltung.GEOMORPHOLOGIE_SOUVERAEN: PeriglazialmorphologieManifestTyp.PERIGLAZIALMORPHOLOGIESYSTEM,
}

_PROZEDUR_MAP = {
    PeriglazialmorphologieManifestGeltung.GESPERRT: PeriglazialmorphologieManifestProzedur.PERIGLAZIALMORPHOLOGIEANALYSE,
    PeriglazialmorphologieManifestGeltung.GRUNDLEGEND_GEOMORPHOLOGISCH: PeriglazialmorphologieManifestProzedur.PERIGLAZIALMORPHOLOGIEANALYSE,
    PeriglazialmorphologieManifestGeltung.GEOMORPHOLOGISCH: PeriglazialmorphologieManifestProzedur.PERIGLAZIALMORPHOLOGIESYNTHESE,
    PeriglazialmorphologieManifestGeltung.GEOMORPHOLOGISCH_AKTIV: PeriglazialmorphologieManifestProzedur.PERIGLAZIALMORPHOLOGIESYNTHESE,
    PeriglazialmorphologieManifestGeltung.GEOMORPHOLOGIE_SOUVERAEN: PeriglazialmorphologieManifestProzedur.PERIGLAZIALMORPHOLOGIEBEWERTUNG,
}


@dataclass(frozen=True)
class PeriglazialmorphologieManifestNorm:
    geltung: PeriglazialmorphologieManifestGeltung
    geomorphologie_weight: float
    geomorphologie_tier: int
    geomorphologie_ids: tuple[str, ...]
    geomorphologie_tags: tuple[str, ...]
    typ: PeriglazialmorphologieManifestTyp
    prozedur: PeriglazialmorphologieManifestProzedur
    canonical: bool = True


@dataclass(frozen=True)
class PeriglazialmorphologieManifest:
    normen: tuple[PeriglazialmorphologieManifestNorm, ...]
    parent: Optional[DenudationsKodex] = None


def build_periglazialmorphologie_manifest(parent: Optional[DenudationsKodex] = None) -> PeriglazialmorphologieManifest:
    if parent is None:
        parent = build_denudations_kodex()
    base = sum(e.geomorphologie_weight for e in parent.eintraege)
    normen = tuple(
        PeriglazialmorphologieManifestNorm(
            geltung=g,
            geomorphologie_weight=round(base + _WEIGHT_DELTA[g], 4),
            geomorphologie_tier=i + 1,
            geomorphologie_ids=(f"periglazialmorphologie-manifest-{g.name.lower()}-001",),
            geomorphologie_tags=("geomorphologie", "periglazialmorphologie", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(PeriglazialmorphologieManifestGeltung)
    )
    return PeriglazialmorphologieManifest(normen=normen, parent=parent)
