from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .pharmakokinetika_charta import PharmakokinetikaCharta, build_pharmakokinetika_charta


class PharmakodynamikKodexGeltung(Enum):
    GESPERRT = auto()
    GRUNDLEGEND_PHARMAKODYNAMISCH = auto()
    PHARMAKODYNAMISCH = auto()
    PHARMAKODYNAMISCH_AKTIV = auto()
    PHARMAKODYNAMIK_SOUVERAEN = auto()


class PharmakodynamikKodexTyp(Enum):
    PHARMAKODYNAMIKKODEX = auto()
    REZEPTORMODELL = auto()
    WIRKUNGSMECHANISMUS = auto()


class PharmakodynamikKodexProzedur(Enum):
    REZEPTORANALYSE = auto()
    DOSIS_WIRKUNGS_KURVE = auto()
    ANTAGONISMUSBEWERTUNG = auto()


_WEIGHT_DELTA: dict[PharmakodynamikKodexGeltung, float] = {
    PharmakodynamikKodexGeltung.GESPERRT: 0.0,
    PharmakodynamikKodexGeltung.GRUNDLEGEND_PHARMAKODYNAMISCH: 1.6,
    PharmakodynamikKodexGeltung.PHARMAKODYNAMISCH: 3.2,
    PharmakodynamikKodexGeltung.PHARMAKODYNAMISCH_AKTIV: 4.8,
    PharmakodynamikKodexGeltung.PHARMAKODYNAMIK_SOUVERAEN: 6.4,
}

_TYP_MAP = {
    PharmakodynamikKodexGeltung.GESPERRT: PharmakodynamikKodexTyp.PHARMAKODYNAMIKKODEX,
    PharmakodynamikKodexGeltung.GRUNDLEGEND_PHARMAKODYNAMISCH: PharmakodynamikKodexTyp.REZEPTORMODELL,
    PharmakodynamikKodexGeltung.PHARMAKODYNAMISCH: PharmakodynamikKodexTyp.REZEPTORMODELL,
    PharmakodynamikKodexGeltung.PHARMAKODYNAMISCH_AKTIV: PharmakodynamikKodexTyp.WIRKUNGSMECHANISMUS,
    PharmakodynamikKodexGeltung.PHARMAKODYNAMIK_SOUVERAEN: PharmakodynamikKodexTyp.WIRKUNGSMECHANISMUS,
}

_PROZEDUR_MAP = {
    PharmakodynamikKodexGeltung.GESPERRT: PharmakodynamikKodexProzedur.REZEPTORANALYSE,
    PharmakodynamikKodexGeltung.GRUNDLEGEND_PHARMAKODYNAMISCH: PharmakodynamikKodexProzedur.REZEPTORANALYSE,
    PharmakodynamikKodexGeltung.PHARMAKODYNAMISCH: PharmakodynamikKodexProzedur.DOSIS_WIRKUNGS_KURVE,
    PharmakodynamikKodexGeltung.PHARMAKODYNAMISCH_AKTIV: PharmakodynamikKodexProzedur.DOSIS_WIRKUNGS_KURVE,
    PharmakodynamikKodexGeltung.PHARMAKODYNAMIK_SOUVERAEN: PharmakodynamikKodexProzedur.ANTAGONISMUSBEWERTUNG,
}


@dataclass(frozen=True)
class PharmakodynamikKodexEintrag:
    geltung: PharmakodynamikKodexGeltung
    pharma_weight: float
    pharma_tier: int
    pharma_ids: tuple[str, ...]
    pharma_tags: tuple[str, ...]
    typ: PharmakodynamikKodexTyp
    prozedur: PharmakodynamikKodexProzedur
    canonical: bool = True


@dataclass(frozen=True)
class PharmakodynamikKodex:
    eintraege: tuple[PharmakodynamikKodexEintrag, ...]
    parent: Optional[PharmakokinetikaCharta] = None


def build_pharmakodynamik_kodex(parent: Optional[PharmakokinetikaCharta] = None) -> PharmakodynamikKodex:
    if parent is None:
        parent = build_pharmakokinetika_charta()
    base = sum(n.pharma_weight for n in parent.normen)
    eintraege = tuple(
        PharmakodynamikKodexEintrag(
            geltung=g,
            pharma_weight=round(base + _WEIGHT_DELTA[g], 4),
            pharma_tier=i + 1,
            pharma_ids=(f"pharmakodynamik-{g.name.lower()}-001",),
            pharma_tags=("pharmakodynamik", "kodex", g.name.lower()),
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
        )
        for i, g in enumerate(PharmakodynamikKodexGeltung)
    )
    return PharmakodynamikKodex(eintraege=eintraege, parent=parent)
