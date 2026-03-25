from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional
from .ingenieur_verfassung import IngenieurVerfassung, build_ingenieur_verfassung


class KlimaFeldGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_KLIMATISCH = auto()
    KLIMATISCH = auto()
    KLIMATISCH_AKTIV = auto()
    KLIMA_SOUVERAEN = auto()


class KlimaFeldTyp(Enum):
    KLIMAFELD = auto()
    KLIMASYSTEM = auto()
    KLIMAKOMPONENTE = auto()


class KlimaFeldProzedur(Enum):
    KLIMAANALYSE = auto()
    KLIMASYNTHESE = auto()
    KLIMABEWERTUNG = auto()


_WEIGHT_DELTA: dict[KlimaFeldGeltung, float] = {
    KlimaFeldGeltung.GESPERRT: 0.0,
    KlimaFeldGeltung.GRUNDLEGEND_KLIMATISCH: 1.2,
    KlimaFeldGeltung.KLIMATISCH: 2.4,
    KlimaFeldGeltung.KLIMATISCH_AKTIV: 3.6,
    KlimaFeldGeltung.KLIMA_SOUVERAEN: 5.0,
}

_TYP_MAP: dict[KlimaFeldGeltung, KlimaFeldTyp] = {
    KlimaFeldGeltung.GESPERRT: KlimaFeldTyp.KLIMAFELD,
    KlimaFeldGeltung.GRUNDLEGEND_KLIMATISCH: KlimaFeldTyp.KLIMAKOMPONENTE,
    KlimaFeldGeltung.KLIMATISCH: KlimaFeldTyp.KLIMAKOMPONENTE,
    KlimaFeldGeltung.KLIMATISCH_AKTIV: KlimaFeldTyp.KLIMASYSTEM,
    KlimaFeldGeltung.KLIMA_SOUVERAEN: KlimaFeldTyp.KLIMASYSTEM,
}

_PROZEDUR_MAP: dict[KlimaFeldGeltung, KlimaFeldProzedur] = {
    KlimaFeldGeltung.GESPERRT: KlimaFeldProzedur.KLIMAANALYSE,
    KlimaFeldGeltung.GRUNDLEGEND_KLIMATISCH: KlimaFeldProzedur.KLIMAANALYSE,
    KlimaFeldGeltung.KLIMATISCH: KlimaFeldProzedur.KLIMASYNTHESE,
    KlimaFeldGeltung.KLIMATISCH_AKTIV: KlimaFeldProzedur.KLIMASYNTHESE,
    KlimaFeldGeltung.KLIMA_SOUVERAEN: KlimaFeldProzedur.KLIMABEWERTUNG,
}


@dataclass(frozen=True)
class KlimaFeldNorm:
    geltung: KlimaFeldGeltung
    klima_weight: float
    klima_tier: int
    klima_ids: tuple[str, ...]
    klima_tags: tuple[str, ...]
    typ: KlimaFeldTyp
    prozedur: KlimaFeldProzedur
    canonical: bool = True


@dataclass(frozen=True)
class KlimaFeld:
    normen: tuple[KlimaFeldNorm, ...]
    parent: Optional[IngenieurVerfassung] = None


def build_klima_feld(parent: Optional[IngenieurVerfassung] = None) -> KlimaFeld:
    if parent is None:
        parent = build_ingenieur_verfassung()
    parent_weights = [n.ing_weight for n in parent.normen]
    base = sum(parent_weights)
    normen = tuple(
        KlimaFeldNorm(
            geltung=g,
            klima_weight=round(base + _WEIGHT_DELTA[g], 4),
            klima_tier=i + 1,
            klima_ids=(f"klima-feld-{g.name.lower()}-001",),
            klima_tags=("klima", "feld", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(KlimaFeldGeltung)
    )
    return KlimaFeld(normen=normen, parent=parent)
