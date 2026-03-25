from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .klimawandel_pakt import KlimawandelPakt, build_klimawandel_pakt


class KlimaanpassungSenatGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_KLIMAANPASSEND = auto()
    KLIMAANPASSEND = auto()
    KLIMAANPASSEND_AKTIV = auto()
    KLIMAANPASSUNG_SOUVERAEN = auto()


class KlimaanpassungSenatTyp(Enum):
    KLIMAANPASSUNGSENAT = auto()
    ANPASSUNGSSTRATEGIE = auto()
    RESILIENZMASSZNAHME = auto()


class KlimaanpassungSenatProzedur(Enum):
    ANPASSUNGSANALYSE = auto()
    ANPASSUNGSSYNTHESE = auto()
    ANPASSUNGSBEWERTUNG = auto()


_WEIGHT_DELTA: dict[KlimaanpassungSenatGeltung, float] = {
    KlimaanpassungSenatGeltung.GESPERRT: 0.0,
    KlimaanpassungSenatGeltung.GRUNDLEGEND_KLIMAANPASSEND: 1.8,
    KlimaanpassungSenatGeltung.KLIMAANPASSEND: 3.6,
    KlimaanpassungSenatGeltung.KLIMAANPASSEND_AKTIV: 5.4,
    KlimaanpassungSenatGeltung.KLIMAANPASSUNG_SOUVERAEN: 7.2,
}

_TYP_MAP = {
    KlimaanpassungSenatGeltung.GESPERRT: KlimaanpassungSenatTyp.KLIMAANPASSUNGSENAT,
    KlimaanpassungSenatGeltung.GRUNDLEGEND_KLIMAANPASSEND: KlimaanpassungSenatTyp.RESILIENZMASSZNAHME,
    KlimaanpassungSenatGeltung.KLIMAANPASSEND: KlimaanpassungSenatTyp.RESILIENZMASSZNAHME,
    KlimaanpassungSenatGeltung.KLIMAANPASSEND_AKTIV: KlimaanpassungSenatTyp.ANPASSUNGSSTRATEGIE,
    KlimaanpassungSenatGeltung.KLIMAANPASSUNG_SOUVERAEN: KlimaanpassungSenatTyp.ANPASSUNGSSTRATEGIE,
}

_PROZEDUR_MAP = {
    KlimaanpassungSenatGeltung.GESPERRT: KlimaanpassungSenatProzedur.ANPASSUNGSANALYSE,
    KlimaanpassungSenatGeltung.GRUNDLEGEND_KLIMAANPASSEND: KlimaanpassungSenatProzedur.ANPASSUNGSANALYSE,
    KlimaanpassungSenatGeltung.KLIMAANPASSEND: KlimaanpassungSenatProzedur.ANPASSUNGSSYNTHESE,
    KlimaanpassungSenatGeltung.KLIMAANPASSEND_AKTIV: KlimaanpassungSenatProzedur.ANPASSUNGSSYNTHESE,
    KlimaanpassungSenatGeltung.KLIMAANPASSUNG_SOUVERAEN: KlimaanpassungSenatProzedur.ANPASSUNGSBEWERTUNG,
}


@dataclass(frozen=True)
class KlimaanpassungSenatNorm:
    geltung: KlimaanpassungSenatGeltung
    klima_weight: float
    klima_tier: int
    klima_ids: tuple[str, ...]
    klima_tags: tuple[str, ...]
    typ: KlimaanpassungSenatTyp
    prozedur: KlimaanpassungSenatProzedur
    canonical: bool = True


@dataclass(frozen=True)
class KlimaanpassungSenat:
    normen: tuple[KlimaanpassungSenatNorm, ...]
    parent: Optional[KlimawandelPakt] = None


def build_klimaanpassung_senat(parent: Optional[KlimawandelPakt] = None) -> KlimaanpassungSenat:
    if parent is None:
        parent = build_klimawandel_pakt()
    base = sum(e.klima_weight for e in parent.eintraege)
    normen = tuple(
        KlimaanpassungSenatNorm(
            geltung=g,
            klima_weight=round(base + _WEIGHT_DELTA[g], 4),
            klima_tier=i + 1,
            klima_ids=(f"klimaanpassung-senat-{g.name.lower()}-001",),
            klima_tags=("klimaanpassung", "senat", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(KlimaanpassungSenatGeltung)
    )
    return KlimaanpassungSenat(normen=normen, parent=parent)
