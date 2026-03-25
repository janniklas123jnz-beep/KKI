from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .regressions_manifest import RegressionsManifest, build_regressions_manifest


class ZeitreihenPaktGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_ZEITREIHENHAFT = auto()
    ZEITREIHENHAFT = auto()
    ZEITREIHENHAFT_AKTIV = auto()
    ZEITREIHEN_SOUVERAEN = auto()


class ZeitreihenPaktTyp(Enum):
    ZEITREIHENPAKT = auto()
    ZEITREIHENMODELL = auto()
    SAISONALITAET = auto()


class ZeitreihenPaktProzedur(Enum):
    ZEITREIHENANALYSE = auto()
    PROGNOSEBERECHNUNG = auto()
    ZEITREIHENBEWERTUNG = auto()


_WEIGHT_DELTA: dict[ZeitreihenPaktGeltung, float] = {
    ZeitreihenPaktGeltung.GESPERRT: 0.0,
    ZeitreihenPaktGeltung.GRUNDLEGEND_ZEITREIHENHAFT: 1.7,
    ZeitreihenPaktGeltung.ZEITREIHENHAFT: 3.4,
    ZeitreihenPaktGeltung.ZEITREIHENHAFT_AKTIV: 5.1,
    ZeitreihenPaktGeltung.ZEITREIHEN_SOUVERAEN: 6.8,
}

_TYP_MAP = {
    ZeitreihenPaktGeltung.GESPERRT: ZeitreihenPaktTyp.ZEITREIHENPAKT,
    ZeitreihenPaktGeltung.GRUNDLEGEND_ZEITREIHENHAFT: ZeitreihenPaktTyp.SAISONALITAET,
    ZeitreihenPaktGeltung.ZEITREIHENHAFT: ZeitreihenPaktTyp.SAISONALITAET,
    ZeitreihenPaktGeltung.ZEITREIHENHAFT_AKTIV: ZeitreihenPaktTyp.ZEITREIHENMODELL,
    ZeitreihenPaktGeltung.ZEITREIHEN_SOUVERAEN: ZeitreihenPaktTyp.ZEITREIHENMODELL,
}

_PROZEDUR_MAP = {
    ZeitreihenPaktGeltung.GESPERRT: ZeitreihenPaktProzedur.ZEITREIHENANALYSE,
    ZeitreihenPaktGeltung.GRUNDLEGEND_ZEITREIHENHAFT: ZeitreihenPaktProzedur.ZEITREIHENANALYSE,
    ZeitreihenPaktGeltung.ZEITREIHENHAFT: ZeitreihenPaktProzedur.PROGNOSEBERECHNUNG,
    ZeitreihenPaktGeltung.ZEITREIHENHAFT_AKTIV: ZeitreihenPaktProzedur.PROGNOSEBERECHNUNG,
    ZeitreihenPaktGeltung.ZEITREIHEN_SOUVERAEN: ZeitreihenPaktProzedur.ZEITREIHENBEWERTUNG,
}


@dataclass(frozen=True)
class ZeitreihenPaktEintrag:
    geltung: ZeitreihenPaktGeltung
    stat_weight: float
    stat_tier: int
    stat_ids: tuple[str, ...]
    stat_tags: tuple[str, ...]
    typ: ZeitreihenPaktTyp
    prozedur: ZeitreihenPaktProzedur
    canonical: bool = True


@dataclass(frozen=True)
class ZeitreihenPakt:
    eintraege: tuple[ZeitreihenPaktEintrag, ...]
    parent: Optional[RegressionsManifest] = None


def build_zeitreihen_pakt(parent: Optional[RegressionsManifest] = None) -> ZeitreihenPakt:
    if parent is None:
        parent = build_regressions_manifest()
    base = sum(n.stat_weight for n in parent.normen)
    eintraege = tuple(
        ZeitreihenPaktEintrag(
            geltung=g,
            stat_weight=round(base + _WEIGHT_DELTA[g], 4),
            stat_tier=i + 1,
            stat_ids=(f"zeitreihen-pakt-{g.name.lower()}-001",),
            stat_tags=("zeitreihen", "pakt", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(ZeitreihenPaktGeltung)
    )
    return ZeitreihenPakt(eintraege=eintraege, parent=parent)
