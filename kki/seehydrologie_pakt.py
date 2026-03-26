from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .wasserkreislauf_manifest import WasserkreislaufManifest, build_wasserkreislauf_manifest


class SeehydrologiePaktGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_HYDROLOGISCH = auto()
    HYDROLOGISCH = auto()
    HYDROLOGISCH_AKTIV = auto()
    HYDROLOGIE_SOUVERAEN = auto()


class SeehydrologiePaktTyp(Enum):
    SEEHYDROLOGIEPAKT = auto()
    SEEHYDROLOGIESYSTEM = auto()
    SEEHYDROLOGIEKOMPONENTE = auto()


class SeehydrologiePaktProzedur(Enum):
    SEEHYDROLOGIEANALYSE = auto()
    SEEHYDROLOGIESYNTHESE = auto()
    SEEHYDROLOGIEBEWERTUNG = auto()


_WEIGHT_DELTA: dict[SeehydrologiePaktGeltung, float] = {
    SeehydrologiePaktGeltung.GESPERRT: 0.0,
    SeehydrologiePaktGeltung.GRUNDLEGEND_HYDROLOGISCH: 1.7,
    SeehydrologiePaktGeltung.HYDROLOGISCH: 3.4,
    SeehydrologiePaktGeltung.HYDROLOGISCH_AKTIV: 5.1,
    SeehydrologiePaktGeltung.HYDROLOGIE_SOUVERAEN: 6.8,
}

_TYP_MAP = {
    SeehydrologiePaktGeltung.GESPERRT: SeehydrologiePaktTyp.SEEHYDROLOGIEPAKT,
    SeehydrologiePaktGeltung.GRUNDLEGEND_HYDROLOGISCH: SeehydrologiePaktTyp.SEEHYDROLOGIEKOMPONENTE,
    SeehydrologiePaktGeltung.HYDROLOGISCH: SeehydrologiePaktTyp.SEEHYDROLOGIEKOMPONENTE,
    SeehydrologiePaktGeltung.HYDROLOGISCH_AKTIV: SeehydrologiePaktTyp.SEEHYDROLOGIESYSTEM,
    SeehydrologiePaktGeltung.HYDROLOGIE_SOUVERAEN: SeehydrologiePaktTyp.SEEHYDROLOGIESYSTEM,
}

_PROZEDUR_MAP = {
    SeehydrologiePaktGeltung.GESPERRT: SeehydrologiePaktProzedur.SEEHYDROLOGIEANALYSE,
    SeehydrologiePaktGeltung.GRUNDLEGEND_HYDROLOGISCH: SeehydrologiePaktProzedur.SEEHYDROLOGIEANALYSE,
    SeehydrologiePaktGeltung.HYDROLOGISCH: SeehydrologiePaktProzedur.SEEHYDROLOGIESYNTHESE,
    SeehydrologiePaktGeltung.HYDROLOGISCH_AKTIV: SeehydrologiePaktProzedur.SEEHYDROLOGIESYNTHESE,
    SeehydrologiePaktGeltung.HYDROLOGIE_SOUVERAEN: SeehydrologiePaktProzedur.SEEHYDROLOGIEBEWERTUNG,
}


@dataclass(frozen=True)
class SeehydrologiePaktEintrag:
    geltung: SeehydrologiePaktGeltung
    hydrologie_weight: float
    hydrologie_tier: int
    hydrologie_ids: tuple[str, ...]
    hydrologie_tags: tuple[str, ...]
    typ: SeehydrologiePaktTyp
    prozedur: SeehydrologiePaktProzedur
    canonical: bool = True


@dataclass(frozen=True)
class SeehydrologiePakt:
    eintraege: tuple[SeehydrologiePaktEintrag, ...]
    parent: Optional[WasserkreislaufManifest] = None


def build_seehydrologie_pakt(parent: Optional[WasserkreislaufManifest] = None) -> SeehydrologiePakt:
    if parent is None:
        parent = build_wasserkreislauf_manifest()
    base = sum(n.hydrologie_weight for n in parent.normen)
    eintraege = tuple(
        SeehydrologiePaktEintrag(
            geltung=g,
            hydrologie_weight=round(base + _WEIGHT_DELTA[g], 4),
            hydrologie_tier=i + 1,
            hydrologie_ids=(f"seehydrologie-pakt-{g.name.lower()}-001",),
            hydrologie_tags=("hydrologie", "seehydrologie", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(SeehydrologiePaktGeltung)
    )
    return SeehydrologiePakt(eintraege=eintraege, parent=parent)
