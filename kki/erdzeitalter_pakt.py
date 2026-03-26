from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .massenaussterben_manifest import MassenaussterbenManifest, build_massenaussterben_manifest


class ErdzeitalterPaktGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_PALAEONTOLOGISCH = auto()
    PALAEONTOLOGISCH = auto()
    PALAEONTOLOGISCH_AKTIV = auto()
    PALAEONTOLOGIE_SOUVERAEN = auto()


class ErdzeitalterPaktTyp(Enum):
    ERDZEITALTERPAKT = auto()
    ERDZEITALTERSYSTEM = auto()
    ERDZEITALTERKOMPONENTE = auto()


class ErdzeitalterPaktProzedur(Enum):
    ERDZEITALTERANALYSE = auto()
    ERDZEITALTERBEWERTUNG = auto()
    ERDZEITALTERVERPFLICHTUNG = auto()


_WEIGHT_DELTA: dict[ErdzeitalterPaktGeltung, float] = {
    ErdzeitalterPaktGeltung.GESPERRT: 0.0,
    ErdzeitalterPaktGeltung.GRUNDLEGEND_PALAEONTOLOGISCH: 1.7,
    ErdzeitalterPaktGeltung.PALAEONTOLOGISCH: 3.4,
    ErdzeitalterPaktGeltung.PALAEONTOLOGISCH_AKTIV: 5.1,
    ErdzeitalterPaktGeltung.PALAEONTOLOGIE_SOUVERAEN: 6.8,
}

_TYP_MAP = {
    ErdzeitalterPaktGeltung.GESPERRT: ErdzeitalterPaktTyp.ERDZEITALTERPAKT,
    ErdzeitalterPaktGeltung.GRUNDLEGEND_PALAEONTOLOGISCH: ErdzeitalterPaktTyp.ERDZEITALTERKOMPONENTE,
    ErdzeitalterPaktGeltung.PALAEONTOLOGISCH: ErdzeitalterPaktTyp.ERDZEITALTERKOMPONENTE,
    ErdzeitalterPaktGeltung.PALAEONTOLOGISCH_AKTIV: ErdzeitalterPaktTyp.ERDZEITALTERSYSTEM,
    ErdzeitalterPaktGeltung.PALAEONTOLOGIE_SOUVERAEN: ErdzeitalterPaktTyp.ERDZEITALTERSYSTEM,
}

_PROZEDUR_MAP = {
    ErdzeitalterPaktGeltung.GESPERRT: ErdzeitalterPaktProzedur.ERDZEITALTERANALYSE,
    ErdzeitalterPaktGeltung.GRUNDLEGEND_PALAEONTOLOGISCH: ErdzeitalterPaktProzedur.ERDZEITALTERANALYSE,
    ErdzeitalterPaktGeltung.PALAEONTOLOGISCH: ErdzeitalterPaktProzedur.ERDZEITALTERBEWERTUNG,
    ErdzeitalterPaktGeltung.PALAEONTOLOGISCH_AKTIV: ErdzeitalterPaktProzedur.ERDZEITALTERBEWERTUNG,
    ErdzeitalterPaktGeltung.PALAEONTOLOGIE_SOUVERAEN: ErdzeitalterPaktProzedur.ERDZEITALTERVERPFLICHTUNG,
}


@dataclass(frozen=True)
class ErdzeitalterPaktEintrag:
    geltung: ErdzeitalterPaktGeltung
    palaeontologie_weight: float
    palaeontologie_tier: int
    palaeontologie_ids: tuple[str, ...]
    palaeontologie_tags: tuple[str, ...]
    typ: ErdzeitalterPaktTyp
    prozedur: ErdzeitalterPaktProzedur
    canonical: bool = True


@dataclass(frozen=True)
class ErdzeitalterPakt:
    eintraege: tuple[ErdzeitalterPaktEintrag, ...]
    parent: Optional[MassenaussterbenManifest] = None


def build_erdzeitalter_pakt(parent: Optional[MassenaussterbenManifest] = None) -> ErdzeitalterPakt:
    if parent is None:
        parent = build_massenaussterben_manifest()
    base = sum(n.palaeontologie_weight for n in parent.normen)
    eintraege = tuple(
        ErdzeitalterPaktEintrag(
            geltung=g,
            palaeontologie_weight=round(base + _WEIGHT_DELTA[g], 4),
            palaeontologie_tier=i + 1,
            palaeontologie_ids=(f"erdzeitalter-pakt-{g.name.lower()}-001",),
            palaeontologie_tags=("palaeontologie", "erdzeitalter", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(ErdzeitalterPaktGeltung)
    )
    return ErdzeitalterPakt(eintraege=eintraege, parent=parent)
