"""#650 GesundheitswissenschaftVerfassung — Block-Krone Medizin & Gesundheitswissenschaften (parent: PublicHealthCharta)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .public_health_charta import PublicHealthCharta, build_public_health_charta

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class GesundheitswissenschaftVerfassungGeltung(str, Enum):
    GESPERRT = "gesperrt"
    GESUNDHEITSWISS_SOUVERAEN = "gesundheitswiss-souveraen"
    GRUNDLEGEND_GESUNDHEITSWISS_SOUVERAEN = "grundlegend-gesundheitswiss-souveraen"


class GesundheitswissenschaftVerfassungTyp(str, Enum):
    KLINISCH = "klinisch"
    THEORETISCH = "theoretisch"
    ANGEWANDT = "angewandt"
    PRAEVENTIV = "praeventiv"


class GesundheitswissenschaftVerfassungProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class GesundheitswissenschaftVerfassungsNorm:
    gesundheitswiss_verfassung_id: str
    geltung: GesundheitswissenschaftVerfassungGeltung
    typ: GesundheitswissenschaftVerfassungTyp
    prozedur: GesundheitswissenschaftVerfassungProzedur
    medizin_weight: float
    medizin_tier: int
    medizin_ids: List[str]
    medizin_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class GesundheitswissenschaftVerfassung:
    verfassung_id: str
    normen: List[GesundheitswissenschaftVerfassungsNorm]
    parent: PublicHealthCharta

    def aggregates_verfassung_signal(self) -> dict:
        return {
            "verfassung_id": self.verfassung_id,
            "total_weight": round(sum(n.medizin_weight for n in self.normen if n.canonical), 4),
            "norm_count": len(self.normen),
        }


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        GesundheitswissenschaftVerfassungGeltung.GESPERRT: 0.0,
        GesundheitswissenschaftVerfassungGeltung.GESUNDHEITSWISS_SOUVERAEN: 0.05,
        GesundheitswissenschaftVerfassungGeltung.GRUNDLEGEND_GESUNDHEITSWISS_SOUVERAEN: 0.1,
    })
    _TIER_DELTA.update({
        GesundheitswissenschaftVerfassungGeltung.GESPERRT: 0,
        GesundheitswissenschaftVerfassungGeltung.GESUNDHEITSWISS_SOUVERAEN: 1,
        GesundheitswissenschaftVerfassungGeltung.GRUNDLEGEND_GESUNDHEITSWISS_SOUVERAEN: 2,
    })
    _TYP_MAP.update({
        GesundheitswissenschaftVerfassungGeltung.GESPERRT: GesundheitswissenschaftVerfassungTyp.KLINISCH,
        GesundheitswissenschaftVerfassungGeltung.GESUNDHEITSWISS_SOUVERAEN: GesundheitswissenschaftVerfassungTyp.THEORETISCH,
        GesundheitswissenschaftVerfassungGeltung.GRUNDLEGEND_GESUNDHEITSWISS_SOUVERAEN: GesundheitswissenschaftVerfassungTyp.ANGEWANDT,
    })
    _PROZEDUR_MAP.update({
        GesundheitswissenschaftVerfassungGeltung.GESPERRT: GesundheitswissenschaftVerfassungProzedur.INITIALISIEREN,
        GesundheitswissenschaftVerfassungGeltung.GESUNDHEITSWISS_SOUVERAEN: GesundheitswissenschaftVerfassungProzedur.AKTIVIEREN,
        GesundheitswissenschaftVerfassungGeltung.GRUNDLEGEND_GESUNDHEITSWISS_SOUVERAEN: GesundheitswissenschaftVerfassungProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        GesundheitswissenschaftVerfassungGeltung.GESPERRT: [GesundheitswissenschaftVerfassungGeltung.GESPERRT],
        GesundheitswissenschaftVerfassungGeltung.GESUNDHEITSWISS_SOUVERAEN: [GesundheitswissenschaftVerfassungGeltung.GESUNDHEITSWISS_SOUVERAEN],
        GesundheitswissenschaftVerfassungGeltung.GRUNDLEGEND_GESUNDHEITSWISS_SOUVERAEN: [GesundheitswissenschaftVerfassungGeltung.GRUNDLEGEND_GESUNDHEITSWISS_SOUVERAEN],
    })


_init_map()


def build_gesundheitswissenschaft_verfassung(*, verfassung_id: str = "gesundheitswiss-verfassung") -> GesundheitswissenschaftVerfassung:
    parent = build_public_health_charta(charta_id=f"{verfassung_id}-parent")
    normen: List[GesundheitswissenschaftVerfassungsNorm] = []
    for g in GesundheitswissenschaftVerfassungGeltung:
        normen.append(GesundheitswissenschaftVerfassungsNorm(
            gesundheitswiss_verfassung_id=f"{verfassung_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            medizin_weight=round(sum(n.medizin_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            medizin_tier=max(n.medizin_tier for n in parent.normen) + _TIER_DELTA[g],
            medizin_ids=[f"gv-{verfassung_id}-{g.value}-001", f"gv-{verfassung_id}-{g.value}-002"],
            medizin_tags=["medizin", "gesundheitswissenschaft", "verfassung", g.value],
        ))
    return GesundheitswissenschaftVerfassung(verfassung_id=verfassung_id, normen=normen, parent=parent)
