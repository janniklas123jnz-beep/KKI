from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .sportmedizin_charta import SportmedizinCharta, build_sportmedizin_charta


class SportVerfassungGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_SPORT_SOUVERAEN = auto()
    SPORT_SOUVERAEN = auto()
    SPORT_SOUVERAEN_AKTIV = auto()
    SPORT_SOUVERAEN_ABSOLUT = auto()


class SportVerfassungTyp(Enum):
    SPORTVERFASSUNG = auto()
    SPORTSOUVERAENITAET = auto()
    SPORTKONSTITUTION = auto()


class SportVerfassungProzedur(Enum):
    SPORTVERFASSUNGSANALYSE = auto()
    SPORTVERFASSUNGSSYNTHESE = auto()
    SPORTVERFASSUNGSBEWERTUNG = auto()


_WEIGHT_DELTA: dict[SportVerfassungGeltung, float] = {
    SportVerfassungGeltung.GESPERRT: 0.0,
    SportVerfassungGeltung.GRUNDLEGEND_SPORT_SOUVERAEN: 2.1,
    SportVerfassungGeltung.SPORT_SOUVERAEN: 4.2,
    SportVerfassungGeltung.SPORT_SOUVERAEN_AKTIV: 6.3,
    SportVerfassungGeltung.SPORT_SOUVERAEN_ABSOLUT: 8.4,
}

_TYP_MAP = {
    SportVerfassungGeltung.GESPERRT: SportVerfassungTyp.SPORTVERFASSUNG,
    SportVerfassungGeltung.GRUNDLEGEND_SPORT_SOUVERAEN: SportVerfassungTyp.SPORTKONSTITUTION,
    SportVerfassungGeltung.SPORT_SOUVERAEN: SportVerfassungTyp.SPORTKONSTITUTION,
    SportVerfassungGeltung.SPORT_SOUVERAEN_AKTIV: SportVerfassungTyp.SPORTSOUVERAENITAET,
    SportVerfassungGeltung.SPORT_SOUVERAEN_ABSOLUT: SportVerfassungTyp.SPORTSOUVERAENITAET,
}

_PROZEDUR_MAP = {
    SportVerfassungGeltung.GESPERRT: SportVerfassungProzedur.SPORTVERFASSUNGSANALYSE,
    SportVerfassungGeltung.GRUNDLEGEND_SPORT_SOUVERAEN: SportVerfassungProzedur.SPORTVERFASSUNGSANALYSE,
    SportVerfassungGeltung.SPORT_SOUVERAEN: SportVerfassungProzedur.SPORTVERFASSUNGSSYNTHESE,
    SportVerfassungGeltung.SPORT_SOUVERAEN_AKTIV: SportVerfassungProzedur.SPORTVERFASSUNGSSYNTHESE,
    SportVerfassungGeltung.SPORT_SOUVERAEN_ABSOLUT: SportVerfassungProzedur.SPORTVERFASSUNGSBEWERTUNG,
}


@dataclass(frozen=True)
class SportVerfassungsNorm:
    geltung: SportVerfassungGeltung
    sport_weight: float
    sport_tier: int
    sport_ids: tuple[str, ...]
    sport_tags: tuple[str, ...]
    typ: SportVerfassungTyp
    prozedur: SportVerfassungProzedur
    canonical: bool = True


@dataclass(frozen=True)
class SportVerfassung:
    normen: tuple[SportVerfassungsNorm, ...]
    parent: Optional[SportmedizinCharta] = None

    def aggregates_verfassung_signal(self) -> dict:
        return {
            "verfassung_id": "sport-verfassung-780",
            "total_weight": round(sum(n.sport_weight for n in self.normen), 4),
            "norm_count": len(self.normen),
        }


def build_sport_verfassung(parent: Optional[SportmedizinCharta] = None) -> SportVerfassung:
    if parent is None:
        parent = build_sportmedizin_charta()
    base = sum(n.sport_weight for n in parent.normen)
    tier_base = max(n.sport_tier for n in parent.normen)
    normen = tuple(
        SportVerfassungsNorm(
            geltung=g,
            sport_weight=round(base + _WEIGHT_DELTA[g], 4),
            sport_tier=tier_base + i + 1,
            sport_ids=(f"sport-verfassung-{g.name.lower()}-001",),
            sport_tags=("sport", "verfassung", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(SportVerfassungGeltung)
    )
    return SportVerfassung(normen=normen, parent=parent)
