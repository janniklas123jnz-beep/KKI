from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .tektonik_charta import TektonikCharta, build_tektonik_charta


class GravitationsfeldKodexGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_GEOPHYSIKALISCH = auto()
    GEOPHYSIKALISCH = auto()
    GEOPHYSIKALISCH_AKTIV = auto()
    GEOPHYSIK_SOUVERAEN = auto()


class GravitationsfeldKodexTyp(Enum):
    GRAVITATIONSFELD = auto()
    SCHWEREFELDSSYSTEM = auto()
    GRAVITATIONSKOMPONENTE = auto()


class GravitationsfeldKodexProzedur(Enum):
    GRAVITATIONSANALYSE = auto()
    GRAVITATIONSSYNTHESE = auto()
    GRAVITATIONSBEWERTUNG = auto()


_WEIGHT_DELTA: dict[GravitationsfeldKodexGeltung, float] = {
    GravitationsfeldKodexGeltung.GESPERRT: 0.0,
    GravitationsfeldKodexGeltung.GRUNDLEGEND_GEOPHYSIKALISCH: 1.5,
    GravitationsfeldKodexGeltung.GEOPHYSIKALISCH: 3.0,
    GravitationsfeldKodexGeltung.GEOPHYSIKALISCH_AKTIV: 4.5,
    GravitationsfeldKodexGeltung.GEOPHYSIK_SOUVERAEN: 6.0,
}

_TYP_MAP = {
    GravitationsfeldKodexGeltung.GESPERRT: GravitationsfeldKodexTyp.GRAVITATIONSFELD,
    GravitationsfeldKodexGeltung.GRUNDLEGEND_GEOPHYSIKALISCH: GravitationsfeldKodexTyp.GRAVITATIONSKOMPONENTE,
    GravitationsfeldKodexGeltung.GEOPHYSIKALISCH: GravitationsfeldKodexTyp.GRAVITATIONSKOMPONENTE,
    GravitationsfeldKodexGeltung.GEOPHYSIKALISCH_AKTIV: GravitationsfeldKodexTyp.SCHWEREFELDSSYSTEM,
    GravitationsfeldKodexGeltung.GEOPHYSIK_SOUVERAEN: GravitationsfeldKodexTyp.SCHWEREFELDSSYSTEM,
}

_PROZEDUR_MAP = {
    GravitationsfeldKodexGeltung.GESPERRT: GravitationsfeldKodexProzedur.GRAVITATIONSANALYSE,
    GravitationsfeldKodexGeltung.GRUNDLEGEND_GEOPHYSIKALISCH: GravitationsfeldKodexProzedur.GRAVITATIONSANALYSE,
    GravitationsfeldKodexGeltung.GEOPHYSIKALISCH: GravitationsfeldKodexProzedur.GRAVITATIONSSYNTHESE,
    GravitationsfeldKodexGeltung.GEOPHYSIKALISCH_AKTIV: GravitationsfeldKodexProzedur.GRAVITATIONSSYNTHESE,
    GravitationsfeldKodexGeltung.GEOPHYSIK_SOUVERAEN: GravitationsfeldKodexProzedur.GRAVITATIONSBEWERTUNG,
}


@dataclass(frozen=True)
class GravitationsfeldKodexEintrag:
    geltung: GravitationsfeldKodexGeltung
    geophysik_weight: float
    geophysik_tier: int
    geophysik_ids: tuple[str, ...]
    geophysik_tags: tuple[str, ...]
    typ: GravitationsfeldKodexTyp
    prozedur: GravitationsfeldKodexProzedur
    canonical: bool = True


@dataclass(frozen=True)
class GravitationsfeldKodex:
    eintraege: tuple[GravitationsfeldKodexEintrag, ...]
    parent: Optional[TektonikCharta] = None


def build_gravitationsfeld_kodex(parent: Optional[TektonikCharta] = None) -> GravitationsfeldKodex:
    if parent is None:
        parent = build_tektonik_charta()
    base = sum(n.geophysik_weight for n in parent.normen)
    eintraege = tuple(
        GravitationsfeldKodexEintrag(
            geltung=g,
            geophysik_weight=round(base + _WEIGHT_DELTA[g], 4),
            geophysik_tier=i + 1,
            geophysik_ids=(f"gravitationsfeld-{g.name.lower()}-001",),
            geophysik_tags=("geophysik", "gravitationsfeld", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(GravitationsfeldKodexGeltung)
    )
    return GravitationsfeldKodex(eintraege=eintraege, parent=parent)
