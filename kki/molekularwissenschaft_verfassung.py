"""#680 MolekularwissenschaftVerfassung — Block-Krone Chemie & Molekularwissenschaft ⭐ (parent: GreenChemistryCharta)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .green_chemistry_charta import GreenChemistryCharta, build_green_chemistry_charta

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class MolekularwissenschaftVerfassungGeltung(str, Enum):
    GESPERRT = "gesperrt"
    MOLEKULARWISS_SOUVERAEN = "molekularwiss-souveraen"
    GRUNDLEGEND_MOLEKULARWISS_SOUVERAEN = "grundlegend-molekularwiss-souveraen"


class MolekularwissenschaftVerfassungTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"
    KATALYSE = "katalyse"


class MolekularwissenschaftVerfassungProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class MolekularwissenschaftVerfassungsNorm:
    molekularwiss_verfassung_id: str
    geltung: MolekularwissenschaftVerfassungGeltung
    typ: MolekularwissenschaftVerfassungTyp
    prozedur: MolekularwissenschaftVerfassungProzedur
    chemie_weight: float
    chemie_tier: int
    chemie_ids: List[str]
    chemie_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class MolekularwissenschaftVerfassung:
    verfassung_id: str
    normen: List[MolekularwissenschaftVerfassungsNorm]
    parent: GreenChemistryCharta

    def aggregates_verfassung_signal(self) -> dict:
        return {
            "verfassung_id": self.verfassung_id,
            "total_weight": round(sum(n.chemie_weight for n in self.normen), 4),
            "norm_count": len(self.normen),
        }


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        MolekularwissenschaftVerfassungGeltung.GESPERRT: 0.0,
        MolekularwissenschaftVerfassungGeltung.MOLEKULARWISS_SOUVERAEN: 0.05,
        MolekularwissenschaftVerfassungGeltung.GRUNDLEGEND_MOLEKULARWISS_SOUVERAEN: 0.1,
    })
    _TIER_DELTA.update({
        MolekularwissenschaftVerfassungGeltung.GESPERRT: 0,
        MolekularwissenschaftVerfassungGeltung.MOLEKULARWISS_SOUVERAEN: 1,
        MolekularwissenschaftVerfassungGeltung.GRUNDLEGEND_MOLEKULARWISS_SOUVERAEN: 2,
    })
    _TYP_MAP.update({
        MolekularwissenschaftVerfassungGeltung.GESPERRT: MolekularwissenschaftVerfassungTyp.BEOBACHTUNG,
        MolekularwissenschaftVerfassungGeltung.MOLEKULARWISS_SOUVERAEN: MolekularwissenschaftVerfassungTyp.ANALYSE,
        MolekularwissenschaftVerfassungGeltung.GRUNDLEGEND_MOLEKULARWISS_SOUVERAEN: MolekularwissenschaftVerfassungTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        MolekularwissenschaftVerfassungGeltung.GESPERRT: MolekularwissenschaftVerfassungProzedur.INITIALISIEREN,
        MolekularwissenschaftVerfassungGeltung.MOLEKULARWISS_SOUVERAEN: MolekularwissenschaftVerfassungProzedur.AKTIVIEREN,
        MolekularwissenschaftVerfassungGeltung.GRUNDLEGEND_MOLEKULARWISS_SOUVERAEN: MolekularwissenschaftVerfassungProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        MolekularwissenschaftVerfassungGeltung.GESPERRT: [MolekularwissenschaftVerfassungGeltung.GESPERRT],
        MolekularwissenschaftVerfassungGeltung.MOLEKULARWISS_SOUVERAEN: [MolekularwissenschaftVerfassungGeltung.MOLEKULARWISS_SOUVERAEN],
        MolekularwissenschaftVerfassungGeltung.GRUNDLEGEND_MOLEKULARWISS_SOUVERAEN: [MolekularwissenschaftVerfassungGeltung.GRUNDLEGEND_MOLEKULARWISS_SOUVERAEN],
    })


_init_map()


def build_molekularwissenschaft_verfassung(*, verfassung_id: str = "molekularwissenschaft-verfassung") -> MolekularwissenschaftVerfassung:
    parent = build_green_chemistry_charta(charta_id=f"{verfassung_id}-parent")
    normen: List[MolekularwissenschaftVerfassungsNorm] = []
    for g in MolekularwissenschaftVerfassungGeltung:
        normen.append(MolekularwissenschaftVerfassungsNorm(
            molekularwiss_verfassung_id=f"{verfassung_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            chemie_weight=round(sum(n.chemie_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            chemie_tier=max(n.chemie_tier for n in parent.normen) + _TIER_DELTA[g],
            chemie_ids=[f"mv-{verfassung_id}-{g.value}-001", f"mv-{verfassung_id}-{g.value}-002"],
            chemie_tags=["chemie", "molekularwissenschaft", "verfassung", g.value],
        ))
    return MolekularwissenschaftVerfassung(verfassung_id=verfassung_id, normen=normen, parent=parent)
