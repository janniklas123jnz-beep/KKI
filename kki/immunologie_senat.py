"""#707 — ImmunologieSenat: Immunsystem, Antikörper & adaptive Immunantwort."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.entwicklungsbiologie_pakt import EntwicklungsbiologiePakt, build_entwicklungsbiologie_pakt


class ImmunologieSenatGeltung(str, Enum):
    GESPERRT = "gesperrt"
    IMMUNOLOGISCH_AKTIV = "immunologisch-aktiv"
    GRUNDLEGEND_IMMUNOLOGISCH_AKTIV = "grundlegend-immunologisch-aktiv"


class ImmunologieSenatTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class ImmunologieSenatProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class ImmunologieSenatNorm:
    senat_id: str
    geltung: ImmunologieSenatGeltung
    typ: ImmunologieSenatTyp
    prozedur: ImmunologieSenatProzedur
    bio_weight: float
    bio_tier: int
    bio_ids: List[str]
    bio_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class ImmunologieSenat:
    senat_id: str
    normen: List[ImmunologieSenatNorm]
    parent: EntwicklungsbiologiePakt


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        ImmunologieSenatGeltung.GESPERRT: 0.0,
        ImmunologieSenatGeltung.IMMUNOLOGISCH_AKTIV: 0.05,
        ImmunologieSenatGeltung.GRUNDLEGEND_IMMUNOLOGISCH_AKTIV: 0.1,
    })
    _TIER_DELTA.update({
        ImmunologieSenatGeltung.GESPERRT: 0,
        ImmunologieSenatGeltung.IMMUNOLOGISCH_AKTIV: 1,
        ImmunologieSenatGeltung.GRUNDLEGEND_IMMUNOLOGISCH_AKTIV: 2,
    })
    _TYP_MAP.update({
        ImmunologieSenatGeltung.GESPERRT: ImmunologieSenatTyp.BEOBACHTUNG,
        ImmunologieSenatGeltung.IMMUNOLOGISCH_AKTIV: ImmunologieSenatTyp.ANALYSE,
        ImmunologieSenatGeltung.GRUNDLEGEND_IMMUNOLOGISCH_AKTIV: ImmunologieSenatTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        ImmunologieSenatGeltung.GESPERRT: ImmunologieSenatProzedur.INITIALISIEREN,
        ImmunologieSenatGeltung.IMMUNOLOGISCH_AKTIV: ImmunologieSenatProzedur.AKTIVIEREN,
        ImmunologieSenatGeltung.GRUNDLEGEND_IMMUNOLOGISCH_AKTIV: ImmunologieSenatProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        ImmunologieSenatGeltung.GESPERRT: [ImmunologieSenatGeltung.GESPERRT],
        ImmunologieSenatGeltung.IMMUNOLOGISCH_AKTIV: [ImmunologieSenatGeltung.IMMUNOLOGISCH_AKTIV],
        ImmunologieSenatGeltung.GRUNDLEGEND_IMMUNOLOGISCH_AKTIV: [ImmunologieSenatGeltung.GRUNDLEGEND_IMMUNOLOGISCH_AKTIV],
    })


_init_map()


def build_immunologie_senat(*, senat_id: str = "immunologie-senat") -> ImmunologieSenat:
    parent = build_entwicklungsbiologie_pakt(pakt_id=f"{senat_id}-parent")
    normen: List[ImmunologieSenatNorm] = []
    for g in ImmunologieSenatGeltung:
        normen.append(ImmunologieSenatNorm(
            senat_id=f"{senat_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            bio_weight=round(sum(e.bio_weight for e in parent.eintraege) * (1.0 + _WEIGHT_DELTA[g]), 4),
            bio_tier=max(e.bio_tier for e in parent.eintraege) + _TIER_DELTA[g],
            bio_ids=[f"is-{senat_id}-{g.value}-001", f"is-{senat_id}-{g.value}-002"],
            bio_tags=["bio", "immunologie", g.value],
        ))
    return ImmunologieSenat(senat_id=senat_id, normen=normen, parent=parent)
