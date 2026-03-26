from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .klimamuster_pakt import KlimamusterPakt, build_klimamuster_pakt


class MeteorologieSenatGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_METEOROLOGISCH = auto()
    METEOROLOGISCH = auto()
    METEOROLOGISCH_AKTIV = auto()
    METEOROLOGIE_SOUVERAEN = auto()


class MeteorologieSenatTyp(Enum):
    METEOROLOGIESENAT = auto()
    METEOROLOGIESENATSSYSTEM = auto()
    METEOROLOGIESENAATSKOMPONENTE = auto()


class MeteorologieSenatProzedur(Enum):
    METEOROLOGIESENATANALYSE = auto()
    METEOROLOGIESENATSYNTHESE = auto()
    METEOROLOGIESENATBEWERTUNG = auto()


_WEIGHT_DELTA: dict[MeteorologieSenatGeltung, float] = {
    MeteorologieSenatGeltung.GESPERRT: 0.0,
    MeteorologieSenatGeltung.GRUNDLEGEND_METEOROLOGISCH: 1.8,
    MeteorologieSenatGeltung.METEOROLOGISCH: 3.6,
    MeteorologieSenatGeltung.METEOROLOGISCH_AKTIV: 5.4,
    MeteorologieSenatGeltung.METEOROLOGIE_SOUVERAEN: 7.2,
}

_TYP_MAP = {
    MeteorologieSenatGeltung.GESPERRT: MeteorologieSenatTyp.METEOROLOGIESENAT,
    MeteorologieSenatGeltung.GRUNDLEGEND_METEOROLOGISCH: MeteorologieSenatTyp.METEOROLOGIESENAATSKOMPONENTE,
    MeteorologieSenatGeltung.METEOROLOGISCH: MeteorologieSenatTyp.METEOROLOGIESENAATSKOMPONENTE,
    MeteorologieSenatGeltung.METEOROLOGISCH_AKTIV: MeteorologieSenatTyp.METEOROLOGIESENATSSYSTEM,
    MeteorologieSenatGeltung.METEOROLOGIE_SOUVERAEN: MeteorologieSenatTyp.METEOROLOGIESENATSSYSTEM,
}

_PROZEDUR_MAP = {
    MeteorologieSenatGeltung.GESPERRT: MeteorologieSenatProzedur.METEOROLOGIESENATANALYSE,
    MeteorologieSenatGeltung.GRUNDLEGEND_METEOROLOGISCH: MeteorologieSenatProzedur.METEOROLOGIESENATANALYSE,
    MeteorologieSenatGeltung.METEOROLOGISCH: MeteorologieSenatProzedur.METEOROLOGIESENATSYNTHESE,
    MeteorologieSenatGeltung.METEOROLOGISCH_AKTIV: MeteorologieSenatProzedur.METEOROLOGIESENATSYNTHESE,
    MeteorologieSenatGeltung.METEOROLOGIE_SOUVERAEN: MeteorologieSenatProzedur.METEOROLOGIESENATBEWERTUNG,
}


@dataclass(frozen=True)
class MeteorologieSenatNorm:
    geltung: MeteorologieSenatGeltung
    meteorologie_weight: float
    meteorologie_tier: int
    meteorologie_ids: tuple[str, ...]
    meteorologie_tags: tuple[str, ...]
    typ: MeteorologieSenatTyp
    prozedur: MeteorologieSenatProzedur
    canonical: bool = True


@dataclass(frozen=True)
class MeteorologieSenat:
    normen: tuple[MeteorologieSenatNorm, ...]
    parent: Optional[KlimamusterPakt] = None


def build_meteorologie_senat(parent: Optional[KlimamusterPakt] = None) -> MeteorologieSenat:
    if parent is None:
        parent = build_klimamuster_pakt()
    base = sum(e.meteorologie_weight for e in parent.eintraege)
    normen = tuple(
        MeteorologieSenatNorm(
            geltung=g,
            meteorologie_weight=round(base + _WEIGHT_DELTA[g], 4),
            meteorologie_tier=i + 1,
            meteorologie_ids=(f"meteorologie-senat-{g.name.lower()}-001",),
            meteorologie_tags=("meteorologie", "senat", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(MeteorologieSenatGeltung)
    )
    return MeteorologieSenat(normen=normen, parent=parent)
