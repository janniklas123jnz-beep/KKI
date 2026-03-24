"""#659 AutonomeRechercheCharta — Autonome Recherche & Selbstorganisation (parent: InternetNormSatz)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .internet_norm import InternetNormSatz, build_internet_norm

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class AutonomeRechercheChartaGeltung(str, Enum):
    GESPERRT = "gesperrt"
    AUTONOM_RECHERCHIERT = "autonom-recherchiert"
    GRUNDLEGEND_AUTONOM_RECHERCHIERT = "grundlegend-autonom-recherchiert"


class AutonomeRechercheChartaTyp(str, Enum):
    RECHERCHE = "recherche"
    VALIDIERUNG = "validierung"
    AGGREGATION = "aggregation"
    AUTONOME_ENTDECKUNG = "autonome-entdeckung"


class AutonomeRechercheChartaProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class AutonomeRechercheChartaNorm:
    charta_id: str
    geltung: AutonomeRechercheChartaGeltung
    typ: AutonomeRechercheChartaTyp
    prozedur: AutonomeRechercheChartaProzedur
    internet_weight: float
    internet_tier: int
    internet_ids: List[str]
    internet_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class AutonomeRechercheCharta:
    charta_id: str
    normen: List[AutonomeRechercheChartaNorm]
    parent: InternetNormSatz


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        AutonomeRechercheChartaGeltung.GESPERRT: 0.0,
        AutonomeRechercheChartaGeltung.AUTONOM_RECHERCHIERT: 0.05,
        AutonomeRechercheChartaGeltung.GRUNDLEGEND_AUTONOM_RECHERCHIERT: 0.1,
    })
    _TIER_DELTA.update({
        AutonomeRechercheChartaGeltung.GESPERRT: 0,
        AutonomeRechercheChartaGeltung.AUTONOM_RECHERCHIERT: 1,
        AutonomeRechercheChartaGeltung.GRUNDLEGEND_AUTONOM_RECHERCHIERT: 2,
    })
    _TYP_MAP.update({
        AutonomeRechercheChartaGeltung.GESPERRT: AutonomeRechercheChartaTyp.RECHERCHE,
        AutonomeRechercheChartaGeltung.AUTONOM_RECHERCHIERT: AutonomeRechercheChartaTyp.VALIDIERUNG,
        AutonomeRechercheChartaGeltung.GRUNDLEGEND_AUTONOM_RECHERCHIERT: AutonomeRechercheChartaTyp.AUTONOME_ENTDECKUNG,
    })
    _PROZEDUR_MAP.update({
        AutonomeRechercheChartaGeltung.GESPERRT: AutonomeRechercheChartaProzedur.INITIALISIEREN,
        AutonomeRechercheChartaGeltung.AUTONOM_RECHERCHIERT: AutonomeRechercheChartaProzedur.AKTIVIEREN,
        AutonomeRechercheChartaGeltung.GRUNDLEGEND_AUTONOM_RECHERCHIERT: AutonomeRechercheChartaProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        AutonomeRechercheChartaGeltung.GESPERRT: [AutonomeRechercheChartaGeltung.GESPERRT],
        AutonomeRechercheChartaGeltung.AUTONOM_RECHERCHIERT: [AutonomeRechercheChartaGeltung.AUTONOM_RECHERCHIERT],
        AutonomeRechercheChartaGeltung.GRUNDLEGEND_AUTONOM_RECHERCHIERT: [AutonomeRechercheChartaGeltung.GRUNDLEGEND_AUTONOM_RECHERCHIERT],
    })


_init_map()


def build_autonome_recherche_charta(*, charta_id: str = "autonome-recherche-charta") -> AutonomeRechercheCharta:
    parent = build_internet_norm(norm_id=f"{charta_id}-parent")
    normen: List[AutonomeRechercheChartaNorm] = []
    for g in AutonomeRechercheChartaGeltung:
        normen.append(AutonomeRechercheChartaNorm(
            charta_id=f"{charta_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            internet_weight=round(sum(e.internet_norm_weight for e in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            internet_tier=max(e.internet_norm_tier for e in parent.normen) + _TIER_DELTA[g],
            internet_ids=[f"arc-{charta_id}-{g.value}-001", f"arc-{charta_id}-{g.value}-002"],
            internet_tags=["internet", "autonome-recherche", g.value],
        ))
    return AutonomeRechercheCharta(charta_id=charta_id, normen=normen, parent=parent)
