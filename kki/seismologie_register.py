from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .geophysik_feld import GeophysikFeld, build_geophysik_feld


class SeismologieRegisterGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_GEOPHYSIKALISCH = auto()
    GEOPHYSIKALISCH = auto()
    GEOPHYSIKALISCH_AKTIV = auto()
    GEOPHYSIK_SOUVERAEN = auto()


class SeismologieRegisterTyp(Enum):
    SEISMOLOGIE = auto()
    BEBENSYSTEM = auto()
    SEISMOLOGIEKOMPONENTE = auto()


class SeismologieRegisterProzedur(Enum):
    SEISMOLOGIEANALYSE = auto()
    SEISMOLOGIESYNTHESE = auto()
    SEISMOLOGIEBEWERTUNG = auto()


_WEIGHT_DELTA: dict[SeismologieRegisterGeltung, float] = {
    SeismologieRegisterGeltung.GESPERRT: 0.0,
    SeismologieRegisterGeltung.GRUNDLEGEND_GEOPHYSIKALISCH: 1.3,
    SeismologieRegisterGeltung.GEOPHYSIKALISCH: 2.6,
    SeismologieRegisterGeltung.GEOPHYSIKALISCH_AKTIV: 3.9,
    SeismologieRegisterGeltung.GEOPHYSIK_SOUVERAEN: 5.2,
}

_TYP_MAP = {
    SeismologieRegisterGeltung.GESPERRT: SeismologieRegisterTyp.SEISMOLOGIE,
    SeismologieRegisterGeltung.GRUNDLEGEND_GEOPHYSIKALISCH: SeismologieRegisterTyp.SEISMOLOGIEKOMPONENTE,
    SeismologieRegisterGeltung.GEOPHYSIKALISCH: SeismologieRegisterTyp.SEISMOLOGIEKOMPONENTE,
    SeismologieRegisterGeltung.GEOPHYSIKALISCH_AKTIV: SeismologieRegisterTyp.BEBENSYSTEM,
    SeismologieRegisterGeltung.GEOPHYSIK_SOUVERAEN: SeismologieRegisterTyp.BEBENSYSTEM,
}

_PROZEDUR_MAP = {
    SeismologieRegisterGeltung.GESPERRT: SeismologieRegisterProzedur.SEISMOLOGIEANALYSE,
    SeismologieRegisterGeltung.GRUNDLEGEND_GEOPHYSIKALISCH: SeismologieRegisterProzedur.SEISMOLOGIEANALYSE,
    SeismologieRegisterGeltung.GEOPHYSIKALISCH: SeismologieRegisterProzedur.SEISMOLOGIESYNTHESE,
    SeismologieRegisterGeltung.GEOPHYSIKALISCH_AKTIV: SeismologieRegisterProzedur.SEISMOLOGIESYNTHESE,
    SeismologieRegisterGeltung.GEOPHYSIK_SOUVERAEN: SeismologieRegisterProzedur.SEISMOLOGIEBEWERTUNG,
}


@dataclass(frozen=True)
class SeismologieRegisterEintrag:
    geltung: SeismologieRegisterGeltung
    geophysik_weight: float
    geophysik_tier: int
    geophysik_ids: tuple[str, ...]
    geophysik_tags: tuple[str, ...]
    typ: SeismologieRegisterTyp
    prozedur: SeismologieRegisterProzedur
    canonical: bool = True


@dataclass(frozen=True)
class SeismologieRegister:
    eintraege: tuple[SeismologieRegisterEintrag, ...]
    parent: Optional[GeophysikFeld] = None


def build_seismologie_register(parent: Optional[GeophysikFeld] = None) -> SeismologieRegister:
    if parent is None:
        parent = build_geophysik_feld()
    base = sum(n.geophysik_weight for n in parent.normen)
    eintraege = tuple(
        SeismologieRegisterEintrag(
            geltung=g,
            geophysik_weight=round(base + _WEIGHT_DELTA[g], 4),
            geophysik_tier=i + 1,
            geophysik_ids=(f"seismologie-{g.name.lower()}-001",),
            geophysik_tags=("geophysik", "seismologie", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(SeismologieRegisterGeltung)
    )
    return SeismologieRegister(eintraege=eintraege, parent=parent)
