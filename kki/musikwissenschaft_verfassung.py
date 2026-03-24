"""#630 MusikwissenschaftVerfassung — Block-Krone Musikwissenschaft (parent: AkustikCharta)."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List
from .akustik_charta import AkustikCharta, build_akustik_charta

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class MusikwissenschaftVerfassungGeltung(str, Enum):
    GESPERRT = "gesperrt"
    MUSIKWISS_SOUVERAEN = "musikwiss-souveraen"
    GRUNDLEGEND_MUSIKWISS_SOUVERAEN = "grundlegend-musikwiss-souveraen"


class MusikwissenschaftVerfassungTyp(str, Enum):
    ANALYTISCH = "analytisch"
    SYNTHETISCH = "synthetisch"
    HISTORISCH = "historisch"
    KOMPARATIV = "komparativ"


class MusikwissenschaftVerfassungProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class MusikwissenschaftVerfassungsNorm:
    musikwiss_verfassung_id: str
    geltung: MusikwissenschaftVerfassungGeltung
    typ: MusikwissenschaftVerfassungTyp
    prozedur: MusikwissenschaftVerfassungProzedur
    musik_weight: float
    musik_tier: int
    musik_ids: List[str]
    musik_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class MusikwissenschaftVerfassung:
    verfassung_id: str
    normen: List[MusikwissenschaftVerfassungsNorm]
    parent: AkustikCharta

    def aggregates_verfassung_signal(self) -> dict:
        return {
            "verfassung_id": self.verfassung_id,
            "total_weight": round(sum(n.musik_weight for n in self.normen if n.canonical), 4),
            "norm_count": len(self.normen),
        }


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        MusikwissenschaftVerfassungGeltung.GESPERRT: 0.0,
        MusikwissenschaftVerfassungGeltung.MUSIKWISS_SOUVERAEN: 0.05,
        MusikwissenschaftVerfassungGeltung.GRUNDLEGEND_MUSIKWISS_SOUVERAEN: 0.1,
    })
    _TIER_DELTA.update({
        MusikwissenschaftVerfassungGeltung.GESPERRT: 0,
        MusikwissenschaftVerfassungGeltung.MUSIKWISS_SOUVERAEN: 1,
        MusikwissenschaftVerfassungGeltung.GRUNDLEGEND_MUSIKWISS_SOUVERAEN: 2,
    })
    _TYP_MAP.update({
        MusikwissenschaftVerfassungGeltung.GESPERRT: MusikwissenschaftVerfassungTyp.ANALYTISCH,
        MusikwissenschaftVerfassungGeltung.MUSIKWISS_SOUVERAEN: MusikwissenschaftVerfassungTyp.SYNTHETISCH,
        MusikwissenschaftVerfassungGeltung.GRUNDLEGEND_MUSIKWISS_SOUVERAEN: MusikwissenschaftVerfassungTyp.HISTORISCH,
    })
    _PROZEDUR_MAP.update({
        MusikwissenschaftVerfassungGeltung.GESPERRT: MusikwissenschaftVerfassungProzedur.INITIALISIEREN,
        MusikwissenschaftVerfassungGeltung.MUSIKWISS_SOUVERAEN: MusikwissenschaftVerfassungProzedur.AKTIVIEREN,
        MusikwissenschaftVerfassungGeltung.GRUNDLEGEND_MUSIKWISS_SOUVERAEN: MusikwissenschaftVerfassungProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        MusikwissenschaftVerfassungGeltung.GESPERRT: [MusikwissenschaftVerfassungGeltung.GESPERRT],
        MusikwissenschaftVerfassungGeltung.MUSIKWISS_SOUVERAEN: [MusikwissenschaftVerfassungGeltung.MUSIKWISS_SOUVERAEN],
        MusikwissenschaftVerfassungGeltung.GRUNDLEGEND_MUSIKWISS_SOUVERAEN: [MusikwissenschaftVerfassungGeltung.GRUNDLEGEND_MUSIKWISS_SOUVERAEN],
    })


_init_map()


def build_musikwissenschaft_verfassung(*, verfassung_id: str = "musikwiss-verfassung") -> MusikwissenschaftVerfassung:
    parent = build_akustik_charta(charta_id=f"{verfassung_id}-parent")
    normen: List[MusikwissenschaftVerfassungsNorm] = []
    for g in MusikwissenschaftVerfassungGeltung:
        normen.append(MusikwissenschaftVerfassungsNorm(
            musikwiss_verfassung_id=f"{verfassung_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            musik_weight=round(sum(n.musik_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            musik_tier=max(n.musik_tier for n in parent.normen) + _TIER_DELTA[g],
            musik_ids=[f"mv-{verfassung_id}-{g.value}-001", f"mv-{verfassung_id}-{g.value}-002"],
            musik_tags=["musikwissenschaft", "verfassung", g.value],
        ))
    return MusikwissenschaftVerfassung(verfassung_id=verfassung_id, normen=normen, parent=parent)
