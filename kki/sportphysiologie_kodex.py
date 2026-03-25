from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .trainingslehre_charta import TrainingslehreCharta, build_trainingslehre_charta


class SportphysiologieKodexGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_SPORTPHYSIOLOGISCH = auto()
    SPORTPHYSIOLOGISCH = auto()
    SPORTPHYSIOLOGISCH_AKTIV = auto()
    SPORTPHYSIOLOGIE_SOUVERAEN = auto()


class SportphysiologieKodexTyp(Enum):
    SPORTPHYSIOLOGIEKODEX = auto()
    ENERGIESTOFFWECHSEL = auto()
    AUSDAUERPHYSIOLOGIE = auto()


class SportphysiologieKodexProzedur(Enum):
    STOFFWECHSELANALYSE = auto()
    LAKTATDIAGNOSTIK = auto()
    HERZKREISLAUFBEWERTUNG = auto()


_WEIGHT_DELTA: dict[SportphysiologieKodexGeltung, float] = {
    SportphysiologieKodexGeltung.GESPERRT: 0.0,
    SportphysiologieKodexGeltung.GRUNDLEGEND_SPORTPHYSIOLOGISCH: 1.5,
    SportphysiologieKodexGeltung.SPORTPHYSIOLOGISCH: 3.0,
    SportphysiologieKodexGeltung.SPORTPHYSIOLOGISCH_AKTIV: 4.5,
    SportphysiologieKodexGeltung.SPORTPHYSIOLOGIE_SOUVERAEN: 6.0,
}

_TYP_MAP = {
    SportphysiologieKodexGeltung.GESPERRT: SportphysiologieKodexTyp.SPORTPHYSIOLOGIEKODEX,
    SportphysiologieKodexGeltung.GRUNDLEGEND_SPORTPHYSIOLOGISCH: SportphysiologieKodexTyp.ENERGIESTOFFWECHSEL,
    SportphysiologieKodexGeltung.SPORTPHYSIOLOGISCH: SportphysiologieKodexTyp.ENERGIESTOFFWECHSEL,
    SportphysiologieKodexGeltung.SPORTPHYSIOLOGISCH_AKTIV: SportphysiologieKodexTyp.AUSDAUERPHYSIOLOGIE,
    SportphysiologieKodexGeltung.SPORTPHYSIOLOGIE_SOUVERAEN: SportphysiologieKodexTyp.AUSDAUERPHYSIOLOGIE,
}

_PROZEDUR_MAP = {
    SportphysiologieKodexGeltung.GESPERRT: SportphysiologieKodexProzedur.STOFFWECHSELANALYSE,
    SportphysiologieKodexGeltung.GRUNDLEGEND_SPORTPHYSIOLOGISCH: SportphysiologieKodexProzedur.STOFFWECHSELANALYSE,
    SportphysiologieKodexGeltung.SPORTPHYSIOLOGISCH: SportphysiologieKodexProzedur.LAKTATDIAGNOSTIK,
    SportphysiologieKodexGeltung.SPORTPHYSIOLOGISCH_AKTIV: SportphysiologieKodexProzedur.LAKTATDIAGNOSTIK,
    SportphysiologieKodexGeltung.SPORTPHYSIOLOGIE_SOUVERAEN: SportphysiologieKodexProzedur.HERZKREISLAUFBEWERTUNG,
}


@dataclass(frozen=True)
class SportphysiologieKodexEintrag:
    geltung: SportphysiologieKodexGeltung
    sport_weight: float
    sport_tier: int
    sport_ids: tuple[str, ...]
    sport_tags: tuple[str, ...]
    typ: SportphysiologieKodexTyp
    prozedur: SportphysiologieKodexProzedur
    canonical: bool = True


@dataclass(frozen=True)
class SportphysiologieKodex:
    eintraege: tuple[SportphysiologieKodexEintrag, ...]
    parent: Optional[TrainingslehreCharta] = None


def build_sportphysiologie_kodex(parent: Optional[TrainingslehreCharta] = None) -> SportphysiologieKodex:
    if parent is None:
        parent = build_trainingslehre_charta()
    base = sum(n.sport_weight for n in parent.normen)
    eintraege = tuple(
        SportphysiologieKodexEintrag(
            geltung=g,
            sport_weight=round(base + _WEIGHT_DELTA[g], 4),
            sport_tier=i + 1,
            sport_ids=(f"sportphysiologie-{g.name.lower()}-001",),
            sport_tags=("sportphysiologie", "kodex", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(SportphysiologieKodexGeltung)
    )
    return SportphysiologieKodex(eintraege=eintraege, parent=parent)
