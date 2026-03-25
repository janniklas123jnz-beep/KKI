from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .sportphysiologie_kodex import SportphysiologieKodex, build_sportphysiologie_kodex


class LeistungsdiagnostikManifestGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_LEISTUNGSDIAGNOSTISCH = auto()
    LEISTUNGSDIAGNOSTISCH = auto()
    LEISTUNGSDIAGNOSTISCH_AKTIV = auto()
    LEISTUNGSDIAGNOSTIK_SOUVERAEN = auto()


class LeistungsdiagnostikManifestTyp(Enum):
    LEISTUNGSDIAGNOSTIKMANIFEST = auto()
    LEISTUNGSTEST = auto()
    WETTKAMPFANALYSE = auto()


class LeistungsdiagnostikManifestProzedur(Enum):
    LEISTUNGSTESTUNG = auto()
    LEISTUNGSPROFILIERUNG = auto()
    TALENTSICHTUNG = auto()


_WEIGHT_DELTA: dict[LeistungsdiagnostikManifestGeltung, float] = {
    LeistungsdiagnostikManifestGeltung.GESPERRT: 0.0,
    LeistungsdiagnostikManifestGeltung.GRUNDLEGEND_LEISTUNGSDIAGNOSTISCH: 1.6,
    LeistungsdiagnostikManifestGeltung.LEISTUNGSDIAGNOSTISCH: 3.2,
    LeistungsdiagnostikManifestGeltung.LEISTUNGSDIAGNOSTISCH_AKTIV: 4.8,
    LeistungsdiagnostikManifestGeltung.LEISTUNGSDIAGNOSTIK_SOUVERAEN: 6.4,
}

_TYP_MAP = {
    LeistungsdiagnostikManifestGeltung.GESPERRT: LeistungsdiagnostikManifestTyp.LEISTUNGSDIAGNOSTIKMANIFEST,
    LeistungsdiagnostikManifestGeltung.GRUNDLEGEND_LEISTUNGSDIAGNOSTISCH: LeistungsdiagnostikManifestTyp.LEISTUNGSTEST,
    LeistungsdiagnostikManifestGeltung.LEISTUNGSDIAGNOSTISCH: LeistungsdiagnostikManifestTyp.LEISTUNGSTEST,
    LeistungsdiagnostikManifestGeltung.LEISTUNGSDIAGNOSTISCH_AKTIV: LeistungsdiagnostikManifestTyp.WETTKAMPFANALYSE,
    LeistungsdiagnostikManifestGeltung.LEISTUNGSDIAGNOSTIK_SOUVERAEN: LeistungsdiagnostikManifestTyp.WETTKAMPFANALYSE,
}

_PROZEDUR_MAP = {
    LeistungsdiagnostikManifestGeltung.GESPERRT: LeistungsdiagnostikManifestProzedur.LEISTUNGSTESTUNG,
    LeistungsdiagnostikManifestGeltung.GRUNDLEGEND_LEISTUNGSDIAGNOSTISCH: LeistungsdiagnostikManifestProzedur.LEISTUNGSTESTUNG,
    LeistungsdiagnostikManifestGeltung.LEISTUNGSDIAGNOSTISCH: LeistungsdiagnostikManifestProzedur.LEISTUNGSPROFILIERUNG,
    LeistungsdiagnostikManifestGeltung.LEISTUNGSDIAGNOSTISCH_AKTIV: LeistungsdiagnostikManifestProzedur.LEISTUNGSPROFILIERUNG,
    LeistungsdiagnostikManifestGeltung.LEISTUNGSDIAGNOSTIK_SOUVERAEN: LeistungsdiagnostikManifestProzedur.TALENTSICHTUNG,
}


@dataclass(frozen=True)
class LeistungsdiagnostikManifestNorm:
    geltung: LeistungsdiagnostikManifestGeltung
    sport_weight: float
    sport_tier: int
    sport_ids: tuple[str, ...]
    sport_tags: tuple[str, ...]
    typ: LeistungsdiagnostikManifestTyp
    prozedur: LeistungsdiagnostikManifestProzedur
    canonical: bool = True


@dataclass(frozen=True)
class LeistungsdiagnostikManifest:
    normen: tuple[LeistungsdiagnostikManifestNorm, ...]
    parent: Optional[SportphysiologieKodex] = None


def build_leistungsdiagnostik_manifest(parent: Optional[SportphysiologieKodex] = None) -> LeistungsdiagnostikManifest:
    if parent is None:
        parent = build_sportphysiologie_kodex()
    base = sum(e.sport_weight for e in parent.eintraege)
    normen = tuple(
        LeistungsdiagnostikManifestNorm(
            geltung=g,
            sport_weight=round(base + _WEIGHT_DELTA[g], 4),
            sport_tier=i + 1,
            sport_ids=(f"leistungsdiagnostik-{g.name.lower()}-001",),
            sport_tags=("leistungsdiagnostik", "manifest", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(LeistungsdiagnostikManifestGeltung)
    )
    return LeistungsdiagnostikManifest(normen=normen, parent=parent)
