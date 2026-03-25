from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .ozeanchemie_manifest import OzeanchemieManifest, build_ozeanchemie_manifest


class KuestenoekologiePaktGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_OZEANOGRAPHISCH = auto()
    OZEANOGRAPHISCH = auto()
    OZEANOGRAPHISCH_AKTIV = auto()
    OZEAN_SOUVERAEN = auto()


class KuestenoekologiePaktTyp(Enum):
    KUESTENOEKOLOGIE = auto()
    KUESTENSYSTEM = auto()
    KUESTENKOMPONENTE = auto()


class KuestenoekologiePaktProzedur(Enum):
    KUESTENANALYSE = auto()
    KUESTENSYNTHESE = auto()
    KUESTENBEWERTUNG = auto()


_WEIGHT_DELTA: dict[KuestenoekologiePaktGeltung, float] = {
    KuestenoekologiePaktGeltung.GESPERRT: 0.0,
    KuestenoekologiePaktGeltung.GRUNDLEGEND_OZEANOGRAPHISCH: 1.7,
    KuestenoekologiePaktGeltung.OZEANOGRAPHISCH: 3.4,
    KuestenoekologiePaktGeltung.OZEANOGRAPHISCH_AKTIV: 5.1,
    KuestenoekologiePaktGeltung.OZEAN_SOUVERAEN: 6.8,
}

_TYP_MAP = {
    KuestenoekologiePaktGeltung.GESPERRT: KuestenoekologiePaktTyp.KUESTENOEKOLOGIE,
    KuestenoekologiePaktGeltung.GRUNDLEGEND_OZEANOGRAPHISCH: KuestenoekologiePaktTyp.KUESTENKOMPONENTE,
    KuestenoekologiePaktGeltung.OZEANOGRAPHISCH: KuestenoekologiePaktTyp.KUESTENKOMPONENTE,
    KuestenoekologiePaktGeltung.OZEANOGRAPHISCH_AKTIV: KuestenoekologiePaktTyp.KUESTENSYSTEM,
    KuestenoekologiePaktGeltung.OZEAN_SOUVERAEN: KuestenoekologiePaktTyp.KUESTENSYSTEM,
}

_PROZEDUR_MAP = {
    KuestenoekologiePaktGeltung.GESPERRT: KuestenoekologiePaktProzedur.KUESTENANALYSE,
    KuestenoekologiePaktGeltung.GRUNDLEGEND_OZEANOGRAPHISCH: KuestenoekologiePaktProzedur.KUESTENANALYSE,
    KuestenoekologiePaktGeltung.OZEANOGRAPHISCH: KuestenoekologiePaktProzedur.KUESTENSYNTHESE,
    KuestenoekologiePaktGeltung.OZEANOGRAPHISCH_AKTIV: KuestenoekologiePaktProzedur.KUESTENSYNTHESE,
    KuestenoekologiePaktGeltung.OZEAN_SOUVERAEN: KuestenoekologiePaktProzedur.KUESTENBEWERTUNG,
}


@dataclass(frozen=True)
class KuestenoekologiePaktEintrag:
    geltung: KuestenoekologiePaktGeltung
    ozean_weight: float
    ozean_tier: int
    ozean_ids: tuple[str, ...]
    ozean_tags: tuple[str, ...]
    typ: KuestenoekologiePaktTyp
    prozedur: KuestenoekologiePaktProzedur
    canonical: bool = True


@dataclass(frozen=True)
class KuestenoekologiePakt:
    eintraege: tuple[KuestenoekologiePaktEintrag, ...]
    parent: Optional[OzeanchemieManifest] = None


def build_kuestenoekologie_pakt(parent: Optional[OzeanchemieManifest] = None) -> KuestenoekologiePakt:
    if parent is None:
        parent = build_ozeanchemie_manifest()
    base = sum(n.ozean_weight for n in parent.normen)
    eintraege = tuple(
        KuestenoekologiePaktEintrag(
            geltung=g,
            ozean_weight=round(base + _WEIGHT_DELTA[g], 4),
            ozean_tier=i + 1,
            ozean_ids=(f"kuestenoekologie-{g.name.lower()}-001",),
            ozean_tags=("ozean", "kuestenoekologie", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(KuestenoekologiePaktGeltung)
    )
    return KuestenoekologiePakt(eintraege=eintraege, parent=parent)
