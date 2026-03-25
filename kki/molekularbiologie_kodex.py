"""#704 — MolekularbiologieKodex: Transkription, Translation & Proteinbiosynthese."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.genetik_charta import GenetikCharta, build_genetik_charta


class MolekularbiologieKodexGeltung(str, Enum):
    GESPERRT = "gesperrt"
    MOLEKULARBIOLOGISCH = "molekularbiologisch"
    GRUNDLEGEND_MOLEKULARBIOLOGISCH = "grundlegend-molekularbiologisch"


class MolekularbiologieKodexTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class MolekularbiologieKodexProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class MolekularbiologieKodexEintrag:
    eintrag_id: str
    geltung: MolekularbiologieKodexGeltung
    typ: MolekularbiologieKodexTyp
    prozedur: MolekularbiologieKodexProzedur
    bio_weight: float
    bio_tier: int
    bio_ids: List[str]
    bio_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class MolekularbiologieKodex:
    kodex_id: str
    eintraege: List[MolekularbiologieKodexEintrag]
    parent: GenetikCharta


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        MolekularbiologieKodexGeltung.GESPERRT: 0.0,
        MolekularbiologieKodexGeltung.MOLEKULARBIOLOGISCH: 0.05,
        MolekularbiologieKodexGeltung.GRUNDLEGEND_MOLEKULARBIOLOGISCH: 0.1,
    })
    _TIER_DELTA.update({
        MolekularbiologieKodexGeltung.GESPERRT: 0,
        MolekularbiologieKodexGeltung.MOLEKULARBIOLOGISCH: 1,
        MolekularbiologieKodexGeltung.GRUNDLEGEND_MOLEKULARBIOLOGISCH: 2,
    })
    _TYP_MAP.update({
        MolekularbiologieKodexGeltung.GESPERRT: MolekularbiologieKodexTyp.BEOBACHTUNG,
        MolekularbiologieKodexGeltung.MOLEKULARBIOLOGISCH: MolekularbiologieKodexTyp.ANALYSE,
        MolekularbiologieKodexGeltung.GRUNDLEGEND_MOLEKULARBIOLOGISCH: MolekularbiologieKodexTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        MolekularbiologieKodexGeltung.GESPERRT: MolekularbiologieKodexProzedur.INITIALISIEREN,
        MolekularbiologieKodexGeltung.MOLEKULARBIOLOGISCH: MolekularbiologieKodexProzedur.AKTIVIEREN,
        MolekularbiologieKodexGeltung.GRUNDLEGEND_MOLEKULARBIOLOGISCH: MolekularbiologieKodexProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        MolekularbiologieKodexGeltung.GESPERRT: [MolekularbiologieKodexGeltung.GESPERRT],
        MolekularbiologieKodexGeltung.MOLEKULARBIOLOGISCH: [MolekularbiologieKodexGeltung.MOLEKULARBIOLOGISCH],
        MolekularbiologieKodexGeltung.GRUNDLEGEND_MOLEKULARBIOLOGISCH: [MolekularbiologieKodexGeltung.GRUNDLEGEND_MOLEKULARBIOLOGISCH],
    })


_init_map()


def build_molekularbiologie_kodex(*, kodex_id: str = "molekularbiologie-kodex") -> MolekularbiologieKodex:
    parent = build_genetik_charta(charta_id=f"{kodex_id}-parent")
    eintraege: List[MolekularbiologieKodexEintrag] = []
    for g in MolekularbiologieKodexGeltung:
        eintraege.append(MolekularbiologieKodexEintrag(
            eintrag_id=f"{kodex_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            bio_weight=round(sum(n.bio_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            bio_tier=max(n.bio_tier for n in parent.normen) + _TIER_DELTA[g],
            bio_ids=[f"mk-{kodex_id}-{g.value}-001", f"mk-{kodex_id}-{g.value}-002"],
            bio_tags=["bio", "molekularbiologie", g.value],
        ))
    return MolekularbiologieKodex(kodex_id=kodex_id, eintraege=eintraege, parent=parent)
