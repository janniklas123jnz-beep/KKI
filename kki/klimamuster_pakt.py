from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .sturm_manifest import SturmManifest, build_sturm_manifest


class KlimamusterPaktGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_METEOROLOGISCH = auto()
    METEOROLOGISCH = auto()
    METEOROLOGISCH_AKTIV = auto()
    METEOROLOGIE_SOUVERAEN = auto()


class KlimamusterPaktTyp(Enum):
    KLIMAMUSTERPAKT = auto()
    KLIMAMUSTERSYSTEM = auto()
    KLIMAMUSTERKOMPONENTE = auto()


class KlimamusterPaktProzedur(Enum):
    KLIMAMUSTERANALYSE = auto()
    KLIMAMUSTERSYNTHESE = auto()
    KLIMAMUSTERBEWERTUNG = auto()


_WEIGHT_DELTA: dict[KlimamusterPaktGeltung, float] = {
    KlimamusterPaktGeltung.GESPERRT: 0.0,
    KlimamusterPaktGeltung.GRUNDLEGEND_METEOROLOGISCH: 1.7,
    KlimamusterPaktGeltung.METEOROLOGISCH: 3.4,
    KlimamusterPaktGeltung.METEOROLOGISCH_AKTIV: 5.1,
    KlimamusterPaktGeltung.METEOROLOGIE_SOUVERAEN: 6.8,
}

_TYP_MAP = {
    KlimamusterPaktGeltung.GESPERRT: KlimamusterPaktTyp.KLIMAMUSTERPAKT,
    KlimamusterPaktGeltung.GRUNDLEGEND_METEOROLOGISCH: KlimamusterPaktTyp.KLIMAMUSTERKOMPONENTE,
    KlimamusterPaktGeltung.METEOROLOGISCH: KlimamusterPaktTyp.KLIMAMUSTERKOMPONENTE,
    KlimamusterPaktGeltung.METEOROLOGISCH_AKTIV: KlimamusterPaktTyp.KLIMAMUSTERSYSTEM,
    KlimamusterPaktGeltung.METEOROLOGIE_SOUVERAEN: KlimamusterPaktTyp.KLIMAMUSTERSYSTEM,
}

_PROZEDUR_MAP = {
    KlimamusterPaktGeltung.GESPERRT: KlimamusterPaktProzedur.KLIMAMUSTERANALYSE,
    KlimamusterPaktGeltung.GRUNDLEGEND_METEOROLOGISCH: KlimamusterPaktProzedur.KLIMAMUSTERANALYSE,
    KlimamusterPaktGeltung.METEOROLOGISCH: KlimamusterPaktProzedur.KLIMAMUSTERSYNTHESE,
    KlimamusterPaktGeltung.METEOROLOGISCH_AKTIV: KlimamusterPaktProzedur.KLIMAMUSTERSYNTHESE,
    KlimamusterPaktGeltung.METEOROLOGIE_SOUVERAEN: KlimamusterPaktProzedur.KLIMAMUSTERBEWERTUNG,
}


@dataclass(frozen=True)
class KlimamusterPaktEintrag:
    geltung: KlimamusterPaktGeltung
    meteorologie_weight: float
    meteorologie_tier: int
    meteorologie_ids: tuple[str, ...]
    meteorologie_tags: tuple[str, ...]
    typ: KlimamusterPaktTyp
    prozedur: KlimamusterPaktProzedur
    canonical: bool = True


@dataclass(frozen=True)
class KlimamusterPakt:
    eintraege: tuple[KlimamusterPaktEintrag, ...]
    parent: Optional[SturmManifest] = None


def build_klimamuster_pakt(parent: Optional[SturmManifest] = None) -> KlimamusterPakt:
    if parent is None:
        parent = build_sturm_manifest()
    base = sum(n.meteorologie_weight for n in parent.normen)
    eintraege = tuple(
        KlimamusterPaktEintrag(
            geltung=g,
            meteorologie_weight=round(base + _WEIGHT_DELTA[g], 4),
            meteorologie_tier=i + 1,
            meteorologie_ids=(f"klimamuster-pakt-{g.name.lower()}-001",),
            meteorologie_tags=("meteorologie", "klimamuster", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(KlimamusterPaktGeltung)
    )
    return KlimamusterPakt(eintraege=eintraege, parent=parent)
