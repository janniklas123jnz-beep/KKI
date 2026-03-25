"""#669 KlimawandelCharta — Klimawandel & Erderwärmung (parent: OekologieNormSatz)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .oekologie_norm import OekologieNormSatz, build_oekologie_norm

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class KlimawandelChartaGeltung(str, Enum):
    GESPERRT = "gesperrt"
    KLIMAWANDEL_BEWERTET = "klimawandel-bewertet"
    GRUNDLEGEND_KLIMAWANDEL_BEWERTET = "grundlegend-klimawandel-bewertet"


class KlimawandelChartaTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"
    SCHUTZ = "schutz"


class KlimawandelChartaProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class KlimawandelChartaNorm:
    klimawandel_charta_id: str
    geltung: KlimawandelChartaGeltung
    typ: KlimawandelChartaTyp
    prozedur: KlimawandelChartaProzedur
    oekologie_weight: float
    oekologie_tier: int
    oekologie_ids: List[str]
    oekologie_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class KlimawandelCharta:
    charta_id: str
    normen: List[KlimawandelChartaNorm]
    parent: OekologieNormSatz


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        KlimawandelChartaGeltung.GESPERRT: 0.0,
        KlimawandelChartaGeltung.KLIMAWANDEL_BEWERTET: 0.05,
        KlimawandelChartaGeltung.GRUNDLEGEND_KLIMAWANDEL_BEWERTET: 0.1,
    })
    _TIER_DELTA.update({
        KlimawandelChartaGeltung.GESPERRT: 0,
        KlimawandelChartaGeltung.KLIMAWANDEL_BEWERTET: 1,
        KlimawandelChartaGeltung.GRUNDLEGEND_KLIMAWANDEL_BEWERTET: 2,
    })
    _TYP_MAP.update({
        KlimawandelChartaGeltung.GESPERRT: KlimawandelChartaTyp.BEOBACHTUNG,
        KlimawandelChartaGeltung.KLIMAWANDEL_BEWERTET: KlimawandelChartaTyp.ANALYSE,
        KlimawandelChartaGeltung.GRUNDLEGEND_KLIMAWANDEL_BEWERTET: KlimawandelChartaTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        KlimawandelChartaGeltung.GESPERRT: KlimawandelChartaProzedur.INITIALISIEREN,
        KlimawandelChartaGeltung.KLIMAWANDEL_BEWERTET: KlimawandelChartaProzedur.AKTIVIEREN,
        KlimawandelChartaGeltung.GRUNDLEGEND_KLIMAWANDEL_BEWERTET: KlimawandelChartaProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        KlimawandelChartaGeltung.GESPERRT: [KlimawandelChartaGeltung.GESPERRT],
        KlimawandelChartaGeltung.KLIMAWANDEL_BEWERTET: [KlimawandelChartaGeltung.KLIMAWANDEL_BEWERTET],
        KlimawandelChartaGeltung.GRUNDLEGEND_KLIMAWANDEL_BEWERTET: [KlimawandelChartaGeltung.GRUNDLEGEND_KLIMAWANDEL_BEWERTET],
    })


_init_map()


def build_klimawandel_charta(*, charta_id: str = "klimawandel-charta") -> KlimawandelCharta:
    parent = build_oekologie_norm(norm_id=f"{charta_id}-parent")
    normen: List[KlimawandelChartaNorm] = []
    for g in KlimawandelChartaGeltung:
        normen.append(KlimawandelChartaNorm(
            klimawandel_charta_id=f"{charta_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            oekologie_weight=round(sum(e.oekologie_norm_weight for e in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            oekologie_tier=max(e.oekologie_norm_tier for e in parent.normen) + _TIER_DELTA[g],
            oekologie_ids=[f"kc-{charta_id}-{g.value}-001", f"kc-{charta_id}-{g.value}-002"],
            oekologie_tags=["oekologie", "klimawandel", "charta", g.value],
        ))
    return KlimawandelCharta(charta_id=charta_id, normen=normen, parent=parent)
