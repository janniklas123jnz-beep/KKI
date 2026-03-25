"""#720 — InformatikVerfassung ⭐: Block-Krone Informatik & Algorithmik."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.kuenstliche_intelligenz_charta import KuenstlicheIntelligenzCharta, build_kuenstliche_intelligenz_charta


class InformatikVerfassungGeltung(str, Enum):
    GESPERRT = "gesperrt"
    INFO_SOUVERAEN = "info-souveraen"
    GRUNDLEGEND_INFO_SOUVERAEN = "grundlegend-info-souveraen"


class InformatikVerfassungTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class InformatikVerfassungProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class InformatikVerfassungsNorm:
    info_verfassung_id: str
    geltung: InformatikVerfassungGeltung
    typ: InformatikVerfassungTyp
    prozedur: InformatikVerfassungProzedur
    info_weight: float
    info_tier: int
    info_ids: List[str]
    info_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class InformatikVerfassung:
    verfassung_id: str
    normen: List[InformatikVerfassungsNorm]
    parent: KuenstlicheIntelligenzCharta

    def aggregates_verfassung_signal(self) -> dict:
        return {
            "verfassung_id": self.verfassung_id,
            "total_weight": round(sum(n.info_weight for n in self.normen), 4),
            "norm_count": len(self.normen),
        }


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        InformatikVerfassungGeltung.GESPERRT: 0.0,
        InformatikVerfassungGeltung.INFO_SOUVERAEN: 0.05,
        InformatikVerfassungGeltung.GRUNDLEGEND_INFO_SOUVERAEN: 0.1,
    })
    _TIER_DELTA.update({
        InformatikVerfassungGeltung.GESPERRT: 0,
        InformatikVerfassungGeltung.INFO_SOUVERAEN: 1,
        InformatikVerfassungGeltung.GRUNDLEGEND_INFO_SOUVERAEN: 2,
    })
    _TYP_MAP.update({
        InformatikVerfassungGeltung.GESPERRT: InformatikVerfassungTyp.BEOBACHTUNG,
        InformatikVerfassungGeltung.INFO_SOUVERAEN: InformatikVerfassungTyp.ANALYSE,
        InformatikVerfassungGeltung.GRUNDLEGEND_INFO_SOUVERAEN: InformatikVerfassungTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        InformatikVerfassungGeltung.GESPERRT: InformatikVerfassungProzedur.INITIALISIEREN,
        InformatikVerfassungGeltung.INFO_SOUVERAEN: InformatikVerfassungProzedur.AKTIVIEREN,
        InformatikVerfassungGeltung.GRUNDLEGEND_INFO_SOUVERAEN: InformatikVerfassungProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        InformatikVerfassungGeltung.GESPERRT: [InformatikVerfassungGeltung.GESPERRT],
        InformatikVerfassungGeltung.INFO_SOUVERAEN: [InformatikVerfassungGeltung.INFO_SOUVERAEN],
        InformatikVerfassungGeltung.GRUNDLEGEND_INFO_SOUVERAEN: [InformatikVerfassungGeltung.GRUNDLEGEND_INFO_SOUVERAEN],
    })


_init_map()


def build_informatik_verfassung(*, verfassung_id: str = "informatik-verfassung") -> InformatikVerfassung:
    parent = build_kuenstliche_intelligenz_charta(charta_id=f"{verfassung_id}-parent")
    normen: List[InformatikVerfassungsNorm] = []
    for g in InformatikVerfassungGeltung:
        normen.append(InformatikVerfassungsNorm(
            info_verfassung_id=f"{verfassung_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            info_weight=round(sum(n.info_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            info_tier=max(n.info_tier for n in parent.normen) + _TIER_DELTA[g],
            info_ids=[f"iv-{verfassung_id}-{g.value}-001", f"iv-{verfassung_id}-{g.value}-002"],
            info_tags=["info", "informatik", "verfassung", g.value],
        ))
    return InformatikVerfassung(verfassung_id=verfassung_id, normen=normen, parent=parent)
