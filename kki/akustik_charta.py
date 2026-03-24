"""#629 AkustikCharta — Akustik & Klangforschung (parent: MusikNormSatz)."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List
from .musik_norm import MusikNormSatz, build_musik_norm

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class AkustikChartaGeltung(str, Enum):
    GESPERRT = "gesperrt"
    AKUSTISCH_SOUVERAEN = "akustisch-souveraen"
    GRUNDLEGEND_AKUSTISCH_SOUVERAEN = "grundlegend-akustisch-souveraen"


class AkustikChartaTyp(str, Enum):
    ANALYTISCH = "analytisch"
    SYNTHETISCH = "synthetisch"
    HISTORISCH = "historisch"
    KOMPARATIV = "komparativ"


class AkustikChartaProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class AkustikChartaNorm:
    akustik_charta_id: str
    geltung: AkustikChartaGeltung
    typ: AkustikChartaTyp
    prozedur: AkustikChartaProzedur
    musik_weight: float
    musik_tier: int
    musik_ids: List[str]
    musik_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class AkustikCharta:
    charta_id: str
    normen: List[AkustikChartaNorm]
    parent: MusikNormSatz


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        AkustikChartaGeltung.GESPERRT: 0.0,
        AkustikChartaGeltung.AKUSTISCH_SOUVERAEN: 0.05,
        AkustikChartaGeltung.GRUNDLEGEND_AKUSTISCH_SOUVERAEN: 0.1,
    })
    _TIER_DELTA.update({
        AkustikChartaGeltung.GESPERRT: 0,
        AkustikChartaGeltung.AKUSTISCH_SOUVERAEN: 1,
        AkustikChartaGeltung.GRUNDLEGEND_AKUSTISCH_SOUVERAEN: 2,
    })
    _TYP_MAP.update({
        AkustikChartaGeltung.GESPERRT: AkustikChartaTyp.ANALYTISCH,
        AkustikChartaGeltung.AKUSTISCH_SOUVERAEN: AkustikChartaTyp.SYNTHETISCH,
        AkustikChartaGeltung.GRUNDLEGEND_AKUSTISCH_SOUVERAEN: AkustikChartaTyp.HISTORISCH,
    })
    _PROZEDUR_MAP.update({
        AkustikChartaGeltung.GESPERRT: AkustikChartaProzedur.INITIALISIEREN,
        AkustikChartaGeltung.AKUSTISCH_SOUVERAEN: AkustikChartaProzedur.AKTIVIEREN,
        AkustikChartaGeltung.GRUNDLEGEND_AKUSTISCH_SOUVERAEN: AkustikChartaProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        AkustikChartaGeltung.GESPERRT: [AkustikChartaGeltung.GESPERRT],
        AkustikChartaGeltung.AKUSTISCH_SOUVERAEN: [AkustikChartaGeltung.AKUSTISCH_SOUVERAEN],
        AkustikChartaGeltung.GRUNDLEGEND_AKUSTISCH_SOUVERAEN: [AkustikChartaGeltung.GRUNDLEGEND_AKUSTISCH_SOUVERAEN],
    })


_init_map()


def build_akustik_charta(*, charta_id: str = "akustik-charta") -> AkustikCharta:
    parent = build_musik_norm(norm_id=f"{charta_id}-parent")
    normen: List[AkustikChartaNorm] = []
    for g in AkustikChartaGeltung:
        normen.append(AkustikChartaNorm(
            akustik_charta_id=f"{charta_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            musik_weight=round(sum(e.musik_norm_weight for e in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            musik_tier=max(e.musik_norm_tier for e in parent.normen) + _TIER_DELTA[g],
            musik_ids=[f"ac-{charta_id}-{g.value}-001", f"ac-{charta_id}-{g.value}-002"],
            musik_tags=["musikwissenschaft", "akustik", g.value],
        ))
    return AkustikCharta(charta_id=charta_id, normen=normen, parent=parent)
