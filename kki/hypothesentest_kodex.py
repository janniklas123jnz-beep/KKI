from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .bayes_charta import BayesCharta, build_bayes_charta


class HypothesentestKodexGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_HYPOTHETISCH = auto()
    HYPOTHETISCH = auto()
    HYPOTHETISCH_AKTIV = auto()
    HYPOTHESENTEST_SOUVERAEN = auto()


class HypothesentestKodexTyp(Enum):
    HYPOTHESENTESTKODEX = auto()
    SIGNIFIKANZTEST = auto()
    NULLHYPOTHESE = auto()


class HypothesentestKodexProzedur(Enum):
    HYPOTHESENANALYSE = auto()
    SIGNIFIKANZBERECHNUNG = auto()
    HYPOTHESENBEWERTUNG = auto()


_WEIGHT_DELTA: dict[HypothesentestKodexGeltung, float] = {
    HypothesentestKodexGeltung.GESPERRT: 0.0,
    HypothesentestKodexGeltung.GRUNDLEGEND_HYPOTHETISCH: 1.5,
    HypothesentestKodexGeltung.HYPOTHETISCH: 3.0,
    HypothesentestKodexGeltung.HYPOTHETISCH_AKTIV: 4.5,
    HypothesentestKodexGeltung.HYPOTHESENTEST_SOUVERAEN: 6.0,
}

_TYP_MAP = {
    HypothesentestKodexGeltung.GESPERRT: HypothesentestKodexTyp.HYPOTHESENTESTKODEX,
    HypothesentestKodexGeltung.GRUNDLEGEND_HYPOTHETISCH: HypothesentestKodexTyp.NULLHYPOTHESE,
    HypothesentestKodexGeltung.HYPOTHETISCH: HypothesentestKodexTyp.NULLHYPOTHESE,
    HypothesentestKodexGeltung.HYPOTHETISCH_AKTIV: HypothesentestKodexTyp.SIGNIFIKANZTEST,
    HypothesentestKodexGeltung.HYPOTHESENTEST_SOUVERAEN: HypothesentestKodexTyp.SIGNIFIKANZTEST,
}

_PROZEDUR_MAP = {
    HypothesentestKodexGeltung.GESPERRT: HypothesentestKodexProzedur.HYPOTHESENANALYSE,
    HypothesentestKodexGeltung.GRUNDLEGEND_HYPOTHETISCH: HypothesentestKodexProzedur.HYPOTHESENANALYSE,
    HypothesentestKodexGeltung.HYPOTHETISCH: HypothesentestKodexProzedur.SIGNIFIKANZBERECHNUNG,
    HypothesentestKodexGeltung.HYPOTHETISCH_AKTIV: HypothesentestKodexProzedur.SIGNIFIKANZBERECHNUNG,
    HypothesentestKodexGeltung.HYPOTHESENTEST_SOUVERAEN: HypothesentestKodexProzedur.HYPOTHESENBEWERTUNG,
}


@dataclass(frozen=True)
class HypothesentestKodexEintrag:
    geltung: HypothesentestKodexGeltung
    stat_weight: float
    stat_tier: int
    stat_ids: tuple[str, ...]
    stat_tags: tuple[str, ...]
    typ: HypothesentestKodexTyp
    prozedur: HypothesentestKodexProzedur
    canonical: bool = True


@dataclass(frozen=True)
class HypothesentestKodex:
    eintraege: tuple[HypothesentestKodexEintrag, ...]
    parent: Optional[BayesCharta] = None


def build_hypothesentest_kodex(parent: Optional[BayesCharta] = None) -> HypothesentestKodex:
    if parent is None:
        parent = build_bayes_charta()
    base = sum(n.stat_weight for n in parent.normen)
    eintraege = tuple(
        HypothesentestKodexEintrag(
            geltung=g,
            stat_weight=round(base + _WEIGHT_DELTA[g], 4),
            stat_tier=i + 1,
            stat_ids=(f"hypothesentest-kodex-{g.name.lower()}-001",),
            stat_tags=("hypothesentest", "kodex", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(HypothesentestKodexGeltung)
    )
    return HypothesentestKodex(eintraege=eintraege, parent=parent)
