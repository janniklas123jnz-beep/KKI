"""#649 PublicHealthCharta — Public Health & Gesundheitsversorgung (parent: MedizinNormSatz)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .medizin_norm import MedizinNormSatz, build_medizin_norm

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class PublicHealthChartaGeltung(str, Enum):
    GESPERRT = "gesperrt"
    OEFFENTLICH_GESUNDHEITLICH = "oeffentlich-gesundheitlich"
    GRUNDLEGEND_OEFFENTLICH_GESUNDHEITLICH = "grundlegend-oeffentlich-gesundheitlich"


class PublicHealthChartaTyp(str, Enum):
    KLINISCH = "klinisch"
    THEORETISCH = "theoretisch"
    ANGEWANDT = "angewandt"
    PRAEVENTIV = "praeventiv"


class PublicHealthChartaProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class PublicHealthChartaNorm:
    charta_id: str
    geltung: PublicHealthChartaGeltung
    typ: PublicHealthChartaTyp
    prozedur: PublicHealthChartaProzedur
    medizin_weight: float
    medizin_tier: int
    medizin_ids: List[str]
    medizin_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class PublicHealthCharta:
    charta_id: str
    normen: List[PublicHealthChartaNorm]
    parent: MedizinNormSatz


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        PublicHealthChartaGeltung.GESPERRT: 0.0,
        PublicHealthChartaGeltung.OEFFENTLICH_GESUNDHEITLICH: 0.05,
        PublicHealthChartaGeltung.GRUNDLEGEND_OEFFENTLICH_GESUNDHEITLICH: 0.1,
    })
    _TIER_DELTA.update({
        PublicHealthChartaGeltung.GESPERRT: 0,
        PublicHealthChartaGeltung.OEFFENTLICH_GESUNDHEITLICH: 1,
        PublicHealthChartaGeltung.GRUNDLEGEND_OEFFENTLICH_GESUNDHEITLICH: 2,
    })
    _TYP_MAP.update({
        PublicHealthChartaGeltung.GESPERRT: PublicHealthChartaTyp.KLINISCH,
        PublicHealthChartaGeltung.OEFFENTLICH_GESUNDHEITLICH: PublicHealthChartaTyp.THEORETISCH,
        PublicHealthChartaGeltung.GRUNDLEGEND_OEFFENTLICH_GESUNDHEITLICH: PublicHealthChartaTyp.ANGEWANDT,
    })
    _PROZEDUR_MAP.update({
        PublicHealthChartaGeltung.GESPERRT: PublicHealthChartaProzedur.INITIALISIEREN,
        PublicHealthChartaGeltung.OEFFENTLICH_GESUNDHEITLICH: PublicHealthChartaProzedur.AKTIVIEREN,
        PublicHealthChartaGeltung.GRUNDLEGEND_OEFFENTLICH_GESUNDHEITLICH: PublicHealthChartaProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        PublicHealthChartaGeltung.GESPERRT: [PublicHealthChartaGeltung.GESPERRT],
        PublicHealthChartaGeltung.OEFFENTLICH_GESUNDHEITLICH: [PublicHealthChartaGeltung.OEFFENTLICH_GESUNDHEITLICH],
        PublicHealthChartaGeltung.GRUNDLEGEND_OEFFENTLICH_GESUNDHEITLICH: [PublicHealthChartaGeltung.GRUNDLEGEND_OEFFENTLICH_GESUNDHEITLICH],
    })


_init_map()


def build_public_health_charta(*, charta_id: str = "public-health-charta") -> PublicHealthCharta:
    parent = build_medizin_norm(norm_id=f"{charta_id}-parent")
    normen: List[PublicHealthChartaNorm] = []
    for g in PublicHealthChartaGeltung:
        normen.append(PublicHealthChartaNorm(
            charta_id=f"{charta_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            medizin_weight=round(sum(e.medizin_norm_weight for e in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            medizin_tier=max(e.medizin_norm_tier for e in parent.normen) + _TIER_DELTA[g],
            medizin_ids=[f"ph-{charta_id}-{g.value}-001", f"ph-{charta_id}-{g.value}-002"],
            medizin_tags=["medizin", "public-health", g.value],
        ))
    return PublicHealthCharta(charta_id=charta_id, normen=normen, parent=parent)
