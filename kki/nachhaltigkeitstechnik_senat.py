"""#737 — NachhaltigkeitstechnikSenat: Erneuerbare Energien, Kreislaufwirtschaft & Klimatechnik."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.steuerungstechnik_pakt import SteuerungstechnikPakt, build_steuerungstechnik_pakt


class NachhaltigkeitstechnikSenatGeltung(str, Enum):
    GESPERRT = "gesperrt"
    NACHHALTIGKEITSTECHNISCH = "nachhaltigkeitstechnisch"
    GRUNDLEGEND_NACHHALTIGKEITSTECHNISCH = "grundlegend-nachhaltigkeitstechnisch"


class NachhaltigkeitstechnikSenatTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class NachhaltigkeitstechnikSenatProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class NachhaltigkeitstechnikSenatNorm:
    senat_id: str
    geltung: NachhaltigkeitstechnikSenatGeltung
    typ: NachhaltigkeitstechnikSenatTyp
    prozedur: NachhaltigkeitstechnikSenatProzedur
    ing_weight: float
    ing_tier: int
    ing_ids: List[str]
    ing_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class NachhaltigkeitstechnikSenat:
    senat_id: str
    normen: List[NachhaltigkeitstechnikSenatNorm]
    parent: SteuerungstechnikPakt


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        NachhaltigkeitstechnikSenatGeltung.GESPERRT: 0.0,
        NachhaltigkeitstechnikSenatGeltung.NACHHALTIGKEITSTECHNISCH: 0.05,
        NachhaltigkeitstechnikSenatGeltung.GRUNDLEGEND_NACHHALTIGKEITSTECHNISCH: 0.1,
    })
    _TIER_DELTA.update({
        NachhaltigkeitstechnikSenatGeltung.GESPERRT: 0,
        NachhaltigkeitstechnikSenatGeltung.NACHHALTIGKEITSTECHNISCH: 1,
        NachhaltigkeitstechnikSenatGeltung.GRUNDLEGEND_NACHHALTIGKEITSTECHNISCH: 2,
    })
    _TYP_MAP.update({
        NachhaltigkeitstechnikSenatGeltung.GESPERRT: NachhaltigkeitstechnikSenatTyp.BEOBACHTUNG,
        NachhaltigkeitstechnikSenatGeltung.NACHHALTIGKEITSTECHNISCH: NachhaltigkeitstechnikSenatTyp.ANALYSE,
        NachhaltigkeitstechnikSenatGeltung.GRUNDLEGEND_NACHHALTIGKEITSTECHNISCH: NachhaltigkeitstechnikSenatTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        NachhaltigkeitstechnikSenatGeltung.GESPERRT: NachhaltigkeitstechnikSenatProzedur.INITIALISIEREN,
        NachhaltigkeitstechnikSenatGeltung.NACHHALTIGKEITSTECHNISCH: NachhaltigkeitstechnikSenatProzedur.AKTIVIEREN,
        NachhaltigkeitstechnikSenatGeltung.GRUNDLEGEND_NACHHALTIGKEITSTECHNISCH: NachhaltigkeitstechnikSenatProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        NachhaltigkeitstechnikSenatGeltung.GESPERRT: [NachhaltigkeitstechnikSenatGeltung.GESPERRT],
        NachhaltigkeitstechnikSenatGeltung.NACHHALTIGKEITSTECHNISCH: [NachhaltigkeitstechnikSenatGeltung.NACHHALTIGKEITSTECHNISCH],
        NachhaltigkeitstechnikSenatGeltung.GRUNDLEGEND_NACHHALTIGKEITSTECHNISCH: [NachhaltigkeitstechnikSenatGeltung.GRUNDLEGEND_NACHHALTIGKEITSTECHNISCH],
    })


_init_map()


def build_nachhaltigkeitstechnik_senat(*, senat_id: str = "nachhaltigkeitstechnik-senat") -> NachhaltigkeitstechnikSenat:
    parent = build_steuerungstechnik_pakt(pakt_id=f"{senat_id}-parent")
    normen: List[NachhaltigkeitstechnikSenatNorm] = []
    for g in NachhaltigkeitstechnikSenatGeltung:
        normen.append(NachhaltigkeitstechnikSenatNorm(
            senat_id=f"{senat_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            ing_weight=round(sum(e.ing_weight for e in parent.eintraege) * (1.0 + _WEIGHT_DELTA[g]), 4),
            ing_tier=max(e.ing_tier for e in parent.eintraege) + _TIER_DELTA[g],
            ing_ids=[f"ns-{senat_id}-{g.value}-001", f"ns-{senat_id}-{g.value}-002"],
            ing_tags=["ing", "nachhaltigkeitstechnik", g.value],
        ))
    return NachhaltigkeitstechnikSenat(senat_id=senat_id, normen=normen, parent=parent)
