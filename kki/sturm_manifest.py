from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .niederschlags_kodex import NiederschlagsKodex, build_niederschlags_kodex


class SturmManifestGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_METEOROLOGISCH = auto()
    METEOROLOGISCH = auto()
    METEOROLOGISCH_AKTIV = auto()
    METEOROLOGIE_SOUVERAEN = auto()


class SturmManifestTyp(Enum):
    STURMMANIFEST = auto()
    STURMSYSTEM = auto()
    STURMKOMPONENTE = auto()


class SturmManifestProzedur(Enum):
    STURMANALYSE = auto()
    STURMSYNTHESE = auto()
    STURMBEWERTUNG = auto()


_WEIGHT_DELTA: dict[SturmManifestGeltung, float] = {
    SturmManifestGeltung.GESPERRT: 0.0,
    SturmManifestGeltung.GRUNDLEGEND_METEOROLOGISCH: 1.6,
    SturmManifestGeltung.METEOROLOGISCH: 3.2,
    SturmManifestGeltung.METEOROLOGISCH_AKTIV: 4.8,
    SturmManifestGeltung.METEOROLOGIE_SOUVERAEN: 6.4,
}

_TYP_MAP = {
    SturmManifestGeltung.GESPERRT: SturmManifestTyp.STURMMANIFEST,
    SturmManifestGeltung.GRUNDLEGEND_METEOROLOGISCH: SturmManifestTyp.STURMKOMPONENTE,
    SturmManifestGeltung.METEOROLOGISCH: SturmManifestTyp.STURMKOMPONENTE,
    SturmManifestGeltung.METEOROLOGISCH_AKTIV: SturmManifestTyp.STURMSYSTEM,
    SturmManifestGeltung.METEOROLOGIE_SOUVERAEN: SturmManifestTyp.STURMSYSTEM,
}

_PROZEDUR_MAP = {
    SturmManifestGeltung.GESPERRT: SturmManifestProzedur.STURMANALYSE,
    SturmManifestGeltung.GRUNDLEGEND_METEOROLOGISCH: SturmManifestProzedur.STURMANALYSE,
    SturmManifestGeltung.METEOROLOGISCH: SturmManifestProzedur.STURMSYNTHESE,
    SturmManifestGeltung.METEOROLOGISCH_AKTIV: SturmManifestProzedur.STURMSYNTHESE,
    SturmManifestGeltung.METEOROLOGIE_SOUVERAEN: SturmManifestProzedur.STURMBEWERTUNG,
}


@dataclass(frozen=True)
class SturmManifestNorm:
    geltung: SturmManifestGeltung
    meteorologie_weight: float
    meteorologie_tier: int
    meteorologie_ids: tuple[str, ...]
    meteorologie_tags: tuple[str, ...]
    typ: SturmManifestTyp
    prozedur: SturmManifestProzedur
    canonical: bool = True


@dataclass(frozen=True)
class SturmManifest:
    normen: tuple[SturmManifestNorm, ...]
    parent: Optional[NiederschlagsKodex] = None


def build_sturm_manifest(parent: Optional[NiederschlagsKodex] = None) -> SturmManifest:
    if parent is None:
        parent = build_niederschlags_kodex()
    base = sum(e.meteorologie_weight for e in parent.eintraege)
    normen = tuple(
        SturmManifestNorm(
            geltung=g,
            meteorologie_weight=round(base + _WEIGHT_DELTA[g], 4),
            meteorologie_tier=i + 1,
            meteorologie_ids=(f"sturm-manifest-{g.name.lower()}-001",),
            meteorologie_tags=("meteorologie", "sturm", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(SturmManifestGeltung)
    )
    return SturmManifest(normen=normen, parent=parent)
