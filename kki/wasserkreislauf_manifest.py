from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .gletscher_kodex import GletscherKodex, build_gletscher_kodex


class WasserkreislaufManifestGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_HYDROLOGISCH = auto()
    HYDROLOGISCH = auto()
    HYDROLOGISCH_AKTIV = auto()
    HYDROLOGIE_SOUVERAEN = auto()


class WasserkreislaufManifestTyp(Enum):
    WASSERKREISLAUFMANIFEST = auto()
    WASSERKREISLAUFSYSTEM = auto()
    WASSERKREISLAUFKOMPONENTE = auto()


class WasserkreislaufManifestProzedur(Enum):
    WASSERKREISLAUFANALYSE = auto()
    WASSERKREISLAUFSYNTHESE = auto()
    WASSERKREISLAUFBEWERTUNG = auto()


_WEIGHT_DELTA: dict[WasserkreislaufManifestGeltung, float] = {
    WasserkreislaufManifestGeltung.GESPERRT: 0.0,
    WasserkreislaufManifestGeltung.GRUNDLEGEND_HYDROLOGISCH: 1.6,
    WasserkreislaufManifestGeltung.HYDROLOGISCH: 3.2,
    WasserkreislaufManifestGeltung.HYDROLOGISCH_AKTIV: 4.8,
    WasserkreislaufManifestGeltung.HYDROLOGIE_SOUVERAEN: 6.4,
}

_TYP_MAP = {
    WasserkreislaufManifestGeltung.GESPERRT: WasserkreislaufManifestTyp.WASSERKREISLAUFMANIFEST,
    WasserkreislaufManifestGeltung.GRUNDLEGEND_HYDROLOGISCH: WasserkreislaufManifestTyp.WASSERKREISLAUFKOMPONENTE,
    WasserkreislaufManifestGeltung.HYDROLOGISCH: WasserkreislaufManifestTyp.WASSERKREISLAUFKOMPONENTE,
    WasserkreislaufManifestGeltung.HYDROLOGISCH_AKTIV: WasserkreislaufManifestTyp.WASSERKREISLAUFSYSTEM,
    WasserkreislaufManifestGeltung.HYDROLOGIE_SOUVERAEN: WasserkreislaufManifestTyp.WASSERKREISLAUFSYSTEM,
}

_PROZEDUR_MAP = {
    WasserkreislaufManifestGeltung.GESPERRT: WasserkreislaufManifestProzedur.WASSERKREISLAUFANALYSE,
    WasserkreislaufManifestGeltung.GRUNDLEGEND_HYDROLOGISCH: WasserkreislaufManifestProzedur.WASSERKREISLAUFANALYSE,
    WasserkreislaufManifestGeltung.HYDROLOGISCH: WasserkreislaufManifestProzedur.WASSERKREISLAUFSYNTHESE,
    WasserkreislaufManifestGeltung.HYDROLOGISCH_AKTIV: WasserkreislaufManifestProzedur.WASSERKREISLAUFSYNTHESE,
    WasserkreislaufManifestGeltung.HYDROLOGIE_SOUVERAEN: WasserkreislaufManifestProzedur.WASSERKREISLAUFBEWERTUNG,
}


@dataclass(frozen=True)
class WasserkreislaufManifestNorm:
    geltung: WasserkreislaufManifestGeltung
    hydrologie_weight: float
    hydrologie_tier: int
    hydrologie_ids: tuple[str, ...]
    hydrologie_tags: tuple[str, ...]
    typ: WasserkreislaufManifestTyp
    prozedur: WasserkreislaufManifestProzedur
    canonical: bool = True


@dataclass(frozen=True)
class WasserkreislaufManifest:
    normen: tuple[WasserkreislaufManifestNorm, ...]
    parent: Optional[GletscherKodex] = None


def build_wasserkreislauf_manifest(parent: Optional[GletscherKodex] = None) -> WasserkreislaufManifest:
    if parent is None:
        parent = build_gletscher_kodex()
    base = sum(e.hydrologie_weight for e in parent.eintraege)
    normen = tuple(
        WasserkreislaufManifestNorm(
            geltung=g,
            hydrologie_weight=round(base + _WEIGHT_DELTA[g], 4),
            hydrologie_tier=i + 1,
            hydrologie_ids=(f"wasserkreislauf-manifest-{g.name.lower()}-001",),
            hydrologie_tags=("hydrologie", "wasserkreislauf", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(WasserkreislaufManifestGeltung)
    )
    return WasserkreislaufManifest(normen=normen, parent=parent)
