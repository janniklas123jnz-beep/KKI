"""#660 InternetkapazitaetVerfassung — Block-Krone Internet & Wissensrecherche (parent: AutonomeRechercheCharta)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .autonome_recherche_charta import AutonomeRechercheCharta, build_autonome_recherche_charta

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class InternetkapazitaetVerfassungGeltung(str, Enum):
    GESPERRT = "gesperrt"
    INTERNETKAP_SOUVERAEN = "internetkap-souveraen"
    GRUNDLEGEND_INTERNETKAP_SOUVERAEN = "grundlegend-internetkap-souveraen"


class InternetkapazitaetVerfassungTyp(str, Enum):
    RECHERCHE = "recherche"
    VALIDIERUNG = "validierung"
    AGGREGATION = "aggregation"
    AUTONOME_ENTDECKUNG = "autonome-entdeckung"


class InternetkapazitaetVerfassungProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class InternetkapazitaetVerfassungsNorm:
    internetkap_verfassung_id: str
    geltung: InternetkapazitaetVerfassungGeltung
    typ: InternetkapazitaetVerfassungTyp
    prozedur: InternetkapazitaetVerfassungProzedur
    internet_weight: float
    internet_tier: int
    internet_ids: List[str]
    internet_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class InternetkapazitaetVerfassung:
    verfassung_id: str
    normen: List[InternetkapazitaetVerfassungsNorm]
    parent: AutonomeRechercheCharta

    def aggregates_verfassung_signal(self) -> dict:
        return {
            "verfassung_id": self.verfassung_id,
            "total_weight": round(sum(n.internet_weight for n in self.normen if n.canonical), 4),
            "norm_count": len(self.normen),
        }


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        InternetkapazitaetVerfassungGeltung.GESPERRT: 0.0,
        InternetkapazitaetVerfassungGeltung.INTERNETKAP_SOUVERAEN: 0.05,
        InternetkapazitaetVerfassungGeltung.GRUNDLEGEND_INTERNETKAP_SOUVERAEN: 0.1,
    })
    _TIER_DELTA.update({
        InternetkapazitaetVerfassungGeltung.GESPERRT: 0,
        InternetkapazitaetVerfassungGeltung.INTERNETKAP_SOUVERAEN: 1,
        InternetkapazitaetVerfassungGeltung.GRUNDLEGEND_INTERNETKAP_SOUVERAEN: 2,
    })
    _TYP_MAP.update({
        InternetkapazitaetVerfassungGeltung.GESPERRT: InternetkapazitaetVerfassungTyp.RECHERCHE,
        InternetkapazitaetVerfassungGeltung.INTERNETKAP_SOUVERAEN: InternetkapazitaetVerfassungTyp.VALIDIERUNG,
        InternetkapazitaetVerfassungGeltung.GRUNDLEGEND_INTERNETKAP_SOUVERAEN: InternetkapazitaetVerfassungTyp.AUTONOME_ENTDECKUNG,
    })
    _PROZEDUR_MAP.update({
        InternetkapazitaetVerfassungGeltung.GESPERRT: InternetkapazitaetVerfassungProzedur.INITIALISIEREN,
        InternetkapazitaetVerfassungGeltung.INTERNETKAP_SOUVERAEN: InternetkapazitaetVerfassungProzedur.AKTIVIEREN,
        InternetkapazitaetVerfassungGeltung.GRUNDLEGEND_INTERNETKAP_SOUVERAEN: InternetkapazitaetVerfassungProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        InternetkapazitaetVerfassungGeltung.GESPERRT: [InternetkapazitaetVerfassungGeltung.GESPERRT],
        InternetkapazitaetVerfassungGeltung.INTERNETKAP_SOUVERAEN: [InternetkapazitaetVerfassungGeltung.INTERNETKAP_SOUVERAEN],
        InternetkapazitaetVerfassungGeltung.GRUNDLEGEND_INTERNETKAP_SOUVERAEN: [InternetkapazitaetVerfassungGeltung.GRUNDLEGEND_INTERNETKAP_SOUVERAEN],
    })


_init_map()


def build_internetkapazitaet_verfassung(*, verfassung_id: str = "internetkap-verfassung") -> InternetkapazitaetVerfassung:
    parent = build_autonome_recherche_charta(charta_id=f"{verfassung_id}-parent")
    normen: List[InternetkapazitaetVerfassungsNorm] = []
    for g in InternetkapazitaetVerfassungGeltung:
        normen.append(InternetkapazitaetVerfassungsNorm(
            internetkap_verfassung_id=f"{verfassung_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            internet_weight=round(sum(n.internet_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            internet_tier=max(n.internet_tier for n in parent.normen) + _TIER_DELTA[g],
            internet_ids=[f"ikv-{verfassung_id}-{g.value}-001", f"ikv-{verfassung_id}-{g.value}-002"],
            internet_tags=["internet", "kapazitaet", "verfassung", g.value],
        ))
    return InternetkapazitaetVerfassung(verfassung_id=verfassung_id, normen=normen, parent=parent)
