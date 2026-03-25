"""#670 UmweltwissenschaftVerfassung — Block-Krone Ökologie & Umweltwissenschaft ⭐ (parent: KlimawandelCharta)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .klimawandel_charta import KlimawandelCharta, build_klimawandel_charta

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class UmweltwissenschaftVerfassungGeltung(str, Enum):
    GESPERRT = "gesperrt"
    UMWELTWISS_SOUVERAEN = "umweltwiss-souveraen"
    GRUNDLEGEND_UMWELTWISS_SOUVERAEN = "grundlegend-umweltwiss-souveraen"


class UmweltwissenschaftVerfassungTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"
    SCHUTZ = "schutz"


class UmweltwissenschaftVerfassungProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class UmweltwissenschaftVerfassungsNorm:
    umweltwiss_verfassung_id: str
    geltung: UmweltwissenschaftVerfassungGeltung
    typ: UmweltwissenschaftVerfassungTyp
    prozedur: UmweltwissenschaftVerfassungProzedur
    oekologie_weight: float
    oekologie_tier: int
    oekologie_ids: List[str]
    oekologie_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class UmweltwissenschaftVerfassung:
    verfassung_id: str
    normen: List[UmweltwissenschaftVerfassungsNorm]
    parent: KlimawandelCharta

    def aggregates_verfassung_signal(self) -> dict:
        return {
            "verfassung_id": self.verfassung_id,
            "total_weight": round(sum(n.oekologie_weight for n in self.normen), 4),
            "norm_count": len(self.normen),
        }


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        UmweltwissenschaftVerfassungGeltung.GESPERRT: 0.0,
        UmweltwissenschaftVerfassungGeltung.UMWELTWISS_SOUVERAEN: 0.05,
        UmweltwissenschaftVerfassungGeltung.GRUNDLEGEND_UMWELTWISS_SOUVERAEN: 0.1,
    })
    _TIER_DELTA.update({
        UmweltwissenschaftVerfassungGeltung.GESPERRT: 0,
        UmweltwissenschaftVerfassungGeltung.UMWELTWISS_SOUVERAEN: 1,
        UmweltwissenschaftVerfassungGeltung.GRUNDLEGEND_UMWELTWISS_SOUVERAEN: 2,
    })
    _TYP_MAP.update({
        UmweltwissenschaftVerfassungGeltung.GESPERRT: UmweltwissenschaftVerfassungTyp.BEOBACHTUNG,
        UmweltwissenschaftVerfassungGeltung.UMWELTWISS_SOUVERAEN: UmweltwissenschaftVerfassungTyp.ANALYSE,
        UmweltwissenschaftVerfassungGeltung.GRUNDLEGEND_UMWELTWISS_SOUVERAEN: UmweltwissenschaftVerfassungTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        UmweltwissenschaftVerfassungGeltung.GESPERRT: UmweltwissenschaftVerfassungProzedur.INITIALISIEREN,
        UmweltwissenschaftVerfassungGeltung.UMWELTWISS_SOUVERAEN: UmweltwissenschaftVerfassungProzedur.AKTIVIEREN,
        UmweltwissenschaftVerfassungGeltung.GRUNDLEGEND_UMWELTWISS_SOUVERAEN: UmweltwissenschaftVerfassungProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        UmweltwissenschaftVerfassungGeltung.GESPERRT: [UmweltwissenschaftVerfassungGeltung.GESPERRT],
        UmweltwissenschaftVerfassungGeltung.UMWELTWISS_SOUVERAEN: [UmweltwissenschaftVerfassungGeltung.UMWELTWISS_SOUVERAEN],
        UmweltwissenschaftVerfassungGeltung.GRUNDLEGEND_UMWELTWISS_SOUVERAEN: [UmweltwissenschaftVerfassungGeltung.GRUNDLEGEND_UMWELTWISS_SOUVERAEN],
    })


_init_map()


def build_umweltwissenschaft_verfassung(*, verfassung_id: str = "umweltwissenschaft-verfassung") -> UmweltwissenschaftVerfassung:
    parent = build_klimawandel_charta(charta_id=f"{verfassung_id}-parent")
    normen: List[UmweltwissenschaftVerfassungsNorm] = []
    for g in UmweltwissenschaftVerfassungGeltung:
        normen.append(UmweltwissenschaftVerfassungsNorm(
            umweltwiss_verfassung_id=f"{verfassung_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            oekologie_weight=round(sum(n.oekologie_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            oekologie_tier=max(n.oekologie_tier for n in parent.normen) + _TIER_DELTA[g],
            oekologie_ids=[f"uv-{verfassung_id}-{g.value}-001", f"uv-{verfassung_id}-{g.value}-002"],
            oekologie_tags=["oekologie", "umweltwissenschaft", "verfassung", g.value],
        ))
    return UmweltwissenschaftVerfassung(verfassung_id=verfassung_id, normen=normen, parent=parent)
