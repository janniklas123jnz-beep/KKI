from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .ernaehrungswissenschaft_manifest import ErnaehrungswissenschaftManifest, build_ernaehrungswissenschaft_manifest


class LandwirtschaftPaktGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_LANDWIRTSCHAFTLICH = auto()
    LANDWIRTSCHAFTLICH = auto()
    LANDWIRTSCHAFTLICH_AKTIV = auto()
    LANDWIRTSCHAFT_SOUVERAEN = auto()


class LandwirtschaftPaktTyp(Enum):
    LANDWIRTSCHAFTSPAKT = auto()
    BETRIEBSKONZEPT = auto()
    NACHHALTIGKEITSSTRATEGIE = auto()


class LandwirtschaftPaktProzedur(Enum):
    BETRIEBSANALYSE = auto()
    RESSOURCENPLANUNG = auto()
    NACHHALTIGKEITSBEWERTUNG = auto()


_WEIGHT_DELTA: dict[LandwirtschaftPaktGeltung, float] = {
    LandwirtschaftPaktGeltung.GESPERRT: 0.0,
    LandwirtschaftPaktGeltung.GRUNDLEGEND_LANDWIRTSCHAFTLICH: 1.7,
    LandwirtschaftPaktGeltung.LANDWIRTSCHAFTLICH: 3.4,
    LandwirtschaftPaktGeltung.LANDWIRTSCHAFTLICH_AKTIV: 5.1,
    LandwirtschaftPaktGeltung.LANDWIRTSCHAFT_SOUVERAEN: 6.8,
}

_TYP_MAP = {
    LandwirtschaftPaktGeltung.GESPERRT: LandwirtschaftPaktTyp.LANDWIRTSCHAFTSPAKT,
    LandwirtschaftPaktGeltung.GRUNDLEGEND_LANDWIRTSCHAFTLICH: LandwirtschaftPaktTyp.BETRIEBSKONZEPT,
    LandwirtschaftPaktGeltung.LANDWIRTSCHAFTLICH: LandwirtschaftPaktTyp.BETRIEBSKONZEPT,
    LandwirtschaftPaktGeltung.LANDWIRTSCHAFTLICH_AKTIV: LandwirtschaftPaktTyp.NACHHALTIGKEITSSTRATEGIE,
    LandwirtschaftPaktGeltung.LANDWIRTSCHAFT_SOUVERAEN: LandwirtschaftPaktTyp.NACHHALTIGKEITSSTRATEGIE,
}

_PROZEDUR_MAP = {
    LandwirtschaftPaktGeltung.GESPERRT: LandwirtschaftPaktProzedur.BETRIEBSANALYSE,
    LandwirtschaftPaktGeltung.GRUNDLEGEND_LANDWIRTSCHAFTLICH: LandwirtschaftPaktProzedur.BETRIEBSANALYSE,
    LandwirtschaftPaktGeltung.LANDWIRTSCHAFTLICH: LandwirtschaftPaktProzedur.RESSOURCENPLANUNG,
    LandwirtschaftPaktGeltung.LANDWIRTSCHAFTLICH_AKTIV: LandwirtschaftPaktProzedur.RESSOURCENPLANUNG,
    LandwirtschaftPaktGeltung.LANDWIRTSCHAFT_SOUVERAEN: LandwirtschaftPaktProzedur.NACHHALTIGKEITSBEWERTUNG,
}


@dataclass(frozen=True)
class LandwirtschaftPaktEintrag:
    geltung: LandwirtschaftPaktGeltung
    agrar_weight: float
    agrar_tier: int
    agrar_ids: tuple[str, ...]
    agrar_tags: tuple[str, ...]
    typ: LandwirtschaftPaktTyp
    prozedur: LandwirtschaftPaktProzedur
    canonical: bool = True


@dataclass(frozen=True)
class LandwirtschaftPakt:
    eintraege: tuple[LandwirtschaftPaktEintrag, ...]
    parent: Optional[ErnaehrungswissenschaftManifest] = None


def build_landwirtschaft_pakt(parent: Optional[ErnaehrungswissenschaftManifest] = None) -> LandwirtschaftPakt:
    if parent is None:
        parent = build_ernaehrungswissenschaft_manifest()
    base = sum(n.agrar_weight for n in parent.normen)
    eintraege = tuple(
        LandwirtschaftPaktEintrag(
            geltung=g,
            agrar_weight=round(base + _WEIGHT_DELTA[g], 4),
            agrar_tier=i + 1,
            agrar_ids=(f"landwirtschaft-{g.name.lower()}-001",),
            agrar_tags=("landwirtschaft", "pakt", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(LandwirtschaftPaktGeltung)
    )
    return LandwirtschaftPakt(eintraege=eintraege, parent=parent)
