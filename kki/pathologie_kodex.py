"""#644 PathologieKodex — Pathologie & Krankheitslehre (parent: PhysiologieCharta)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .physiologie_charta import PhysiologieCharta, build_physiologie_charta

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class PathologieKodexGeltung(str, Enum):
    GESPERRT = "gesperrt"
    PATHOLOGISCH = "pathologisch"
    GRUNDLEGEND_PATHOLOGISCH = "grundlegend-pathologisch"


class PathologieKodexTyp(str, Enum):
    KLINISCH = "klinisch"
    THEORETISCH = "theoretisch"
    ANGEWANDT = "angewandt"
    PRAEVENTIV = "praeventiv"


class PathologieKodexProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class PathologieKodexEintrag:
    kodex_id: str
    geltung: PathologieKodexGeltung
    typ: PathologieKodexTyp
    prozedur: PathologieKodexProzedur
    medizin_weight: float
    medizin_tier: int
    medizin_ids: List[str]
    medizin_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class PathologieKodex:
    kodex_id: str
    eintraege: List[PathologieKodexEintrag]
    parent: PhysiologieCharta


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        PathologieKodexGeltung.GESPERRT: 0.0,
        PathologieKodexGeltung.PATHOLOGISCH: 0.05,
        PathologieKodexGeltung.GRUNDLEGEND_PATHOLOGISCH: 0.1,
    })
    _TIER_DELTA.update({
        PathologieKodexGeltung.GESPERRT: 0,
        PathologieKodexGeltung.PATHOLOGISCH: 1,
        PathologieKodexGeltung.GRUNDLEGEND_PATHOLOGISCH: 2,
    })
    _TYP_MAP.update({
        PathologieKodexGeltung.GESPERRT: PathologieKodexTyp.KLINISCH,
        PathologieKodexGeltung.PATHOLOGISCH: PathologieKodexTyp.THEORETISCH,
        PathologieKodexGeltung.GRUNDLEGEND_PATHOLOGISCH: PathologieKodexTyp.ANGEWANDT,
    })
    _PROZEDUR_MAP.update({
        PathologieKodexGeltung.GESPERRT: PathologieKodexProzedur.INITIALISIEREN,
        PathologieKodexGeltung.PATHOLOGISCH: PathologieKodexProzedur.AKTIVIEREN,
        PathologieKodexGeltung.GRUNDLEGEND_PATHOLOGISCH: PathologieKodexProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        PathologieKodexGeltung.GESPERRT: [PathologieKodexGeltung.GESPERRT],
        PathologieKodexGeltung.PATHOLOGISCH: [PathologieKodexGeltung.PATHOLOGISCH],
        PathologieKodexGeltung.GRUNDLEGEND_PATHOLOGISCH: [PathologieKodexGeltung.GRUNDLEGEND_PATHOLOGISCH],
    })


_init_map()


def build_pathologie_kodex(*, kodex_id: str = "pathologie-kodex") -> PathologieKodex:
    parent = build_physiologie_charta(charta_id=f"{kodex_id}-parent")
    eintraege: List[PathologieKodexEintrag] = []
    for g in PathologieKodexGeltung:
        eintraege.append(PathologieKodexEintrag(
            kodex_id=f"{kodex_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            medizin_weight=round(sum(n.medizin_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            medizin_tier=max(n.medizin_tier for n in parent.normen) + _TIER_DELTA[g],
            medizin_ids=[f"pk-{kodex_id}-{g.value}-001", f"pk-{kodex_id}-{g.value}-002"],
            medizin_tags=["medizin", "pathologie", g.value],
        ))
    return PathologieKodex(kodex_id=kodex_id, eintraege=eintraege, parent=parent)
