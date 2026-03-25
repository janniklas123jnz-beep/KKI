"""#740 — IngenieurVerfassung ⭐: Block-Krone Ingenieurwissenschaften & Technikwissenschaften."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.raumfahrttechnik_charta import RaumfahrttechnikCharta, build_raumfahrttechnik_charta


class IngenieurVerfassungGeltung(str, Enum):
    GESPERRT = "gesperrt"
    ING_SOUVERAEN = "ing-souveraen"
    GRUNDLEGEND_ING_SOUVERAEN = "grundlegend-ing-souveraen"


class IngenieurVerfassungTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class IngenieurVerfassungProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class IngenieurVerfassungsNorm:
    ing_verfassung_id: str
    geltung: IngenieurVerfassungGeltung
    typ: IngenieurVerfassungTyp
    prozedur: IngenieurVerfassungProzedur
    ing_weight: float
    ing_tier: int
    ing_ids: List[str]
    ing_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class IngenieurVerfassung:
    verfassung_id: str
    normen: List[IngenieurVerfassungsNorm]
    parent: RaumfahrttechnikCharta

    def aggregates_verfassung_signal(self) -> dict:
        return {
            "verfassung_id": self.verfassung_id,
            "total_weight": round(sum(n.ing_weight for n in self.normen), 4),
            "norm_count": len(self.normen),
        }


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        IngenieurVerfassungGeltung.GESPERRT: 0.0,
        IngenieurVerfassungGeltung.ING_SOUVERAEN: 0.05,
        IngenieurVerfassungGeltung.GRUNDLEGEND_ING_SOUVERAEN: 0.1,
    })
    _TIER_DELTA.update({
        IngenieurVerfassungGeltung.GESPERRT: 0,
        IngenieurVerfassungGeltung.ING_SOUVERAEN: 1,
        IngenieurVerfassungGeltung.GRUNDLEGEND_ING_SOUVERAEN: 2,
    })
    _TYP_MAP.update({
        IngenieurVerfassungGeltung.GESPERRT: IngenieurVerfassungTyp.BEOBACHTUNG,
        IngenieurVerfassungGeltung.ING_SOUVERAEN: IngenieurVerfassungTyp.ANALYSE,
        IngenieurVerfassungGeltung.GRUNDLEGEND_ING_SOUVERAEN: IngenieurVerfassungTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        IngenieurVerfassungGeltung.GESPERRT: IngenieurVerfassungProzedur.INITIALISIEREN,
        IngenieurVerfassungGeltung.ING_SOUVERAEN: IngenieurVerfassungProzedur.AKTIVIEREN,
        IngenieurVerfassungGeltung.GRUNDLEGEND_ING_SOUVERAEN: IngenieurVerfassungProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        IngenieurVerfassungGeltung.GESPERRT: [IngenieurVerfassungGeltung.GESPERRT],
        IngenieurVerfassungGeltung.ING_SOUVERAEN: [IngenieurVerfassungGeltung.ING_SOUVERAEN],
        IngenieurVerfassungGeltung.GRUNDLEGEND_ING_SOUVERAEN: [IngenieurVerfassungGeltung.GRUNDLEGEND_ING_SOUVERAEN],
    })


_init_map()


def build_ingenieur_verfassung(*, verfassung_id: str = "ingenieur-verfassung") -> IngenieurVerfassung:
    parent = build_raumfahrttechnik_charta(charta_id=f"{verfassung_id}-parent")
    normen: List[IngenieurVerfassungsNorm] = []
    for g in IngenieurVerfassungGeltung:
        normen.append(IngenieurVerfassungsNorm(
            ing_verfassung_id=f"{verfassung_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            ing_weight=round(sum(n.ing_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            ing_tier=max(n.ing_tier for n in parent.normen) + _TIER_DELTA[g],
            ing_ids=[f"iv-{verfassung_id}-{g.value}-001", f"iv-{verfassung_id}-{g.value}-002"],
            ing_tags=["ing", "ingenieur", "verfassung", g.value],
        ))
    return IngenieurVerfassung(verfassung_id=verfassung_id, normen=normen, parent=parent)
