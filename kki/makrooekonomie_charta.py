"""#723 — MakrooekonomieCharta: BIP, Inflation & Konjunktur."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.mikrooekonomie_register import MikrooekonomieRegister, build_mikrooekonomie_register


class MakrooekonomieChartaGeltung(str, Enum):
    GESPERRT = "gesperrt"
    MAKROOEKONOMISCH = "makrooekonomisch"
    GRUNDLEGEND_MAKROOEKONOMISCH = "grundlegend-makrooekonomisch"


class MakrooekonomieChartaTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class MakrooekonomieChartaProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class MakrooekonomieChartaNorm:
    charta_id: str
    geltung: MakrooekonomieChartaGeltung
    typ: MakrooekonomieChartaTyp
    prozedur: MakrooekonomieChartaProzedur
    wirt_weight: float
    wirt_tier: int
    wirt_ids: List[str]
    wirt_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class MakrooekonomieCharta:
    charta_id: str
    normen: List[MakrooekonomieChartaNorm]
    parent: MikrooekonomieRegister


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        MakrooekonomieChartaGeltung.GESPERRT: 0.0,
        MakrooekonomieChartaGeltung.MAKROOEKONOMISCH: 0.05,
        MakrooekonomieChartaGeltung.GRUNDLEGEND_MAKROOEKONOMISCH: 0.1,
    })
    _TIER_DELTA.update({
        MakrooekonomieChartaGeltung.GESPERRT: 0,
        MakrooekonomieChartaGeltung.MAKROOEKONOMISCH: 1,
        MakrooekonomieChartaGeltung.GRUNDLEGEND_MAKROOEKONOMISCH: 2,
    })
    _TYP_MAP.update({
        MakrooekonomieChartaGeltung.GESPERRT: MakrooekonomieChartaTyp.BEOBACHTUNG,
        MakrooekonomieChartaGeltung.MAKROOEKONOMISCH: MakrooekonomieChartaTyp.ANALYSE,
        MakrooekonomieChartaGeltung.GRUNDLEGEND_MAKROOEKONOMISCH: MakrooekonomieChartaTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        MakrooekonomieChartaGeltung.GESPERRT: MakrooekonomieChartaProzedur.INITIALISIEREN,
        MakrooekonomieChartaGeltung.MAKROOEKONOMISCH: MakrooekonomieChartaProzedur.AKTIVIEREN,
        MakrooekonomieChartaGeltung.GRUNDLEGEND_MAKROOEKONOMISCH: MakrooekonomieChartaProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        MakrooekonomieChartaGeltung.GESPERRT: [MakrooekonomieChartaGeltung.GESPERRT],
        MakrooekonomieChartaGeltung.MAKROOEKONOMISCH: [MakrooekonomieChartaGeltung.MAKROOEKONOMISCH],
        MakrooekonomieChartaGeltung.GRUNDLEGEND_MAKROOEKONOMISCH: [MakrooekonomieChartaGeltung.GRUNDLEGEND_MAKROOEKONOMISCH],
    })


_init_map()


def build_makrooekonomie_charta(*, charta_id: str = "makrooekonomie-charta") -> MakrooekonomieCharta:
    parent = build_mikrooekonomie_register(register_id=f"{charta_id}-parent")
    normen: List[MakrooekonomieChartaNorm] = []
    for g in MakrooekonomieChartaGeltung:
        normen.append(MakrooekonomieChartaNorm(
            charta_id=f"{charta_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            wirt_weight=round(sum(e.wirt_weight for e in parent.eintraege) * (1.0 + _WEIGHT_DELTA[g]), 4),
            wirt_tier=max(e.wirt_tier for e in parent.eintraege) + _TIER_DELTA[g],
            wirt_ids=[f"mc-{charta_id}-{g.value}-001", f"mc-{charta_id}-{g.value}-002"],
            wirt_tags=["wirt", "makrooekonomie", g.value],
        ))
    return MakrooekonomieCharta(charta_id=charta_id, normen=normen, parent=parent)
