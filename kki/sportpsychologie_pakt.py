from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .leistungsdiagnostik_manifest import LeistungsdiagnostikManifest, build_leistungsdiagnostik_manifest


class SportpsychologiePaktGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_SPORTPSYCHOLOGISCH = auto()
    SPORTPSYCHOLOGISCH = auto()
    SPORTPSYCHOLOGISCH_AKTIV = auto()
    SPORTPSYCHOLOGIE_SOUVERAEN = auto()


class SportpsychologiePaktTyp(Enum):
    SPORTPSYCHOLOGIEPAKT = auto()
    MOTIVATIONSMODELL = auto()
    MENTALTRAINING = auto()


class SportpsychologiePaktProzedur(Enum):
    MOTIVATIONSANALYSE = auto()
    STRESSBEWAELTIGUNG = auto()
    FLOWZUSTANDSFOERDERUNG = auto()


_WEIGHT_DELTA: dict[SportpsychologiePaktGeltung, float] = {
    SportpsychologiePaktGeltung.GESPERRT: 0.0,
    SportpsychologiePaktGeltung.GRUNDLEGEND_SPORTPSYCHOLOGISCH: 1.7,
    SportpsychologiePaktGeltung.SPORTPSYCHOLOGISCH: 3.4,
    SportpsychologiePaktGeltung.SPORTPSYCHOLOGISCH_AKTIV: 5.1,
    SportpsychologiePaktGeltung.SPORTPSYCHOLOGIE_SOUVERAEN: 6.8,
}

_TYP_MAP = {
    SportpsychologiePaktGeltung.GESPERRT: SportpsychologiePaktTyp.SPORTPSYCHOLOGIEPAKT,
    SportpsychologiePaktGeltung.GRUNDLEGEND_SPORTPSYCHOLOGISCH: SportpsychologiePaktTyp.MOTIVATIONSMODELL,
    SportpsychologiePaktGeltung.SPORTPSYCHOLOGISCH: SportpsychologiePaktTyp.MOTIVATIONSMODELL,
    SportpsychologiePaktGeltung.SPORTPSYCHOLOGISCH_AKTIV: SportpsychologiePaktTyp.MENTALTRAINING,
    SportpsychologiePaktGeltung.SPORTPSYCHOLOGIE_SOUVERAEN: SportpsychologiePaktTyp.MENTALTRAINING,
}

_PROZEDUR_MAP = {
    SportpsychologiePaktGeltung.GESPERRT: SportpsychologiePaktProzedur.MOTIVATIONSANALYSE,
    SportpsychologiePaktGeltung.GRUNDLEGEND_SPORTPSYCHOLOGISCH: SportpsychologiePaktProzedur.MOTIVATIONSANALYSE,
    SportpsychologiePaktGeltung.SPORTPSYCHOLOGISCH: SportpsychologiePaktProzedur.STRESSBEWAELTIGUNG,
    SportpsychologiePaktGeltung.SPORTPSYCHOLOGISCH_AKTIV: SportpsychologiePaktProzedur.STRESSBEWAELTIGUNG,
    SportpsychologiePaktGeltung.SPORTPSYCHOLOGIE_SOUVERAEN: SportpsychologiePaktProzedur.FLOWZUSTANDSFOERDERUNG,
}


@dataclass(frozen=True)
class SportpsychologiePaktEintrag:
    geltung: SportpsychologiePaktGeltung
    sport_weight: float
    sport_tier: int
    sport_ids: tuple[str, ...]
    sport_tags: tuple[str, ...]
    typ: SportpsychologiePaktTyp
    prozedur: SportpsychologiePaktProzedur
    canonical: bool = True


@dataclass(frozen=True)
class SportpsychologiePakt:
    eintraege: tuple[SportpsychologiePaktEintrag, ...]
    parent: Optional[LeistungsdiagnostikManifest] = None


def build_sportpsychologie_pakt(parent: Optional[LeistungsdiagnostikManifest] = None) -> SportpsychologiePakt:
    if parent is None:
        parent = build_leistungsdiagnostik_manifest()
    base = sum(n.sport_weight for n in parent.normen)
    eintraege = tuple(
        SportpsychologiePaktEintrag(
            geltung=g,
            sport_weight=round(base + _WEIGHT_DELTA[g], 4),
            sport_tier=i + 1,
            sport_ids=(f"sportpsychologie-{g.name.lower()}-001",),
            sport_tags=("sportpsychologie", "pakt", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(SportpsychologiePaktGeltung)
    )
    return SportpsychologiePakt(eintraege=eintraege, parent=parent)
