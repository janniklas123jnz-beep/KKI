"""#719 — KuenstlicheIntelligenzCharta: ML, Deep Learning & KI-Architekturen."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.informatik_norm import InformatikNormSatz, build_informatik_norm


class KuenstlicheIntelligenzChartaGeltung(str, Enum):
    GESPERRT = "gesperrt"
    KI_AKTIV = "ki-aktiv"
    GRUNDLEGEND_KI_AKTIV = "grundlegend-ki-aktiv"


class KuenstlicheIntelligenzChartaTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class KuenstlicheIntelligenzChartaProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class KuenstlicheIntelligenzChartaNorm:
    charta_id: str
    geltung: KuenstlicheIntelligenzChartaGeltung
    typ: KuenstlicheIntelligenzChartaTyp
    prozedur: KuenstlicheIntelligenzChartaProzedur
    info_weight: float
    info_tier: int
    info_ids: List[str]
    info_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class KuenstlicheIntelligenzCharta:
    charta_id: str
    normen: List[KuenstlicheIntelligenzChartaNorm]
    parent: InformatikNormSatz


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        KuenstlicheIntelligenzChartaGeltung.GESPERRT: 0.0,
        KuenstlicheIntelligenzChartaGeltung.KI_AKTIV: 0.05,
        KuenstlicheIntelligenzChartaGeltung.GRUNDLEGEND_KI_AKTIV: 0.1,
    })
    _TIER_DELTA.update({
        KuenstlicheIntelligenzChartaGeltung.GESPERRT: 0,
        KuenstlicheIntelligenzChartaGeltung.KI_AKTIV: 1,
        KuenstlicheIntelligenzChartaGeltung.GRUNDLEGEND_KI_AKTIV: 2,
    })
    _TYP_MAP.update({
        KuenstlicheIntelligenzChartaGeltung.GESPERRT: KuenstlicheIntelligenzChartaTyp.BEOBACHTUNG,
        KuenstlicheIntelligenzChartaGeltung.KI_AKTIV: KuenstlicheIntelligenzChartaTyp.ANALYSE,
        KuenstlicheIntelligenzChartaGeltung.GRUNDLEGEND_KI_AKTIV: KuenstlicheIntelligenzChartaTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        KuenstlicheIntelligenzChartaGeltung.GESPERRT: KuenstlicheIntelligenzChartaProzedur.INITIALISIEREN,
        KuenstlicheIntelligenzChartaGeltung.KI_AKTIV: KuenstlicheIntelligenzChartaProzedur.AKTIVIEREN,
        KuenstlicheIntelligenzChartaGeltung.GRUNDLEGEND_KI_AKTIV: KuenstlicheIntelligenzChartaProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        KuenstlicheIntelligenzChartaGeltung.GESPERRT: [KuenstlicheIntelligenzChartaGeltung.GESPERRT],
        KuenstlicheIntelligenzChartaGeltung.KI_AKTIV: [KuenstlicheIntelligenzChartaGeltung.KI_AKTIV],
        KuenstlicheIntelligenzChartaGeltung.GRUNDLEGEND_KI_AKTIV: [KuenstlicheIntelligenzChartaGeltung.GRUNDLEGEND_KI_AKTIV],
    })


_init_map()


def build_kuenstliche_intelligenz_charta(*, charta_id: str = "kuenstliche-intelligenz-charta") -> KuenstlicheIntelligenzCharta:
    parent = build_informatik_norm(norm_id=f"{charta_id}-parent")
    normen: List[KuenstlicheIntelligenzChartaNorm] = []
    for g in KuenstlicheIntelligenzChartaGeltung:
        normen.append(KuenstlicheIntelligenzChartaNorm(
            charta_id=f"{charta_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            info_weight=round(sum(e.info_norm_weight for e in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            info_tier=max(e.info_norm_tier for e in parent.normen) + _TIER_DELTA[g],
            info_ids=[f"ki-{charta_id}-{g.value}-001", f"ki-{charta_id}-{g.value}-002"],
            info_tags=["info", "kuenstliche-intelligenz", g.value],
        ))
    return KuenstlicheIntelligenzCharta(charta_id=charta_id, normen=normen, parent=parent)
