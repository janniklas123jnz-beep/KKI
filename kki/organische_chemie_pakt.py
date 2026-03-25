"""#676 OrganischeChemiePakt — Organische Chemie & Kohlenstoffverbindungen (parent: ThermochemieManifest)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .thermochemie_manifest import ThermochemieManifest, build_thermochemie_manifest

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class OrganischeChemiePaktGeltung(str, Enum):
    GESPERRT = "gesperrt"
    ORGANISCH_VERBUNDEN = "organisch-verbunden"
    GRUNDLEGEND_ORGANISCH_VERBUNDEN = "grundlegend-organisch-verbunden"


class OrganischeChemiePaktTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"
    KATALYSE = "katalyse"


class OrganischeChemiePaktProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class OrganischeChemiePaktEintrag:
    organische_chemie_pakt_id: str
    geltung: OrganischeChemiePaktGeltung
    typ: OrganischeChemiePaktTyp
    prozedur: OrganischeChemiePaktProzedur
    chemie_weight: float
    chemie_tier: int
    chemie_ids: List[str]
    chemie_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class OrganischeChemiePakt:
    pakt_id: str
    eintraege: List[OrganischeChemiePaktEintrag]
    parent: ThermochemieManifest


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        OrganischeChemiePaktGeltung.GESPERRT: 0.0,
        OrganischeChemiePaktGeltung.ORGANISCH_VERBUNDEN: 0.05,
        OrganischeChemiePaktGeltung.GRUNDLEGEND_ORGANISCH_VERBUNDEN: 0.1,
    })
    _TIER_DELTA.update({
        OrganischeChemiePaktGeltung.GESPERRT: 0,
        OrganischeChemiePaktGeltung.ORGANISCH_VERBUNDEN: 1,
        OrganischeChemiePaktGeltung.GRUNDLEGEND_ORGANISCH_VERBUNDEN: 2,
    })
    _TYP_MAP.update({
        OrganischeChemiePaktGeltung.GESPERRT: OrganischeChemiePaktTyp.BEOBACHTUNG,
        OrganischeChemiePaktGeltung.ORGANISCH_VERBUNDEN: OrganischeChemiePaktTyp.ANALYSE,
        OrganischeChemiePaktGeltung.GRUNDLEGEND_ORGANISCH_VERBUNDEN: OrganischeChemiePaktTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        OrganischeChemiePaktGeltung.GESPERRT: OrganischeChemiePaktProzedur.INITIALISIEREN,
        OrganischeChemiePaktGeltung.ORGANISCH_VERBUNDEN: OrganischeChemiePaktProzedur.AKTIVIEREN,
        OrganischeChemiePaktGeltung.GRUNDLEGEND_ORGANISCH_VERBUNDEN: OrganischeChemiePaktProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        OrganischeChemiePaktGeltung.GESPERRT: [OrganischeChemiePaktGeltung.GESPERRT],
        OrganischeChemiePaktGeltung.ORGANISCH_VERBUNDEN: [OrganischeChemiePaktGeltung.ORGANISCH_VERBUNDEN],
        OrganischeChemiePaktGeltung.GRUNDLEGEND_ORGANISCH_VERBUNDEN: [OrganischeChemiePaktGeltung.GRUNDLEGEND_ORGANISCH_VERBUNDEN],
    })


_init_map()


def build_organische_chemie_pakt(*, pakt_id: str = "organische-chemie-pakt") -> OrganischeChemiePakt:
    parent = build_thermochemie_manifest(manifest_id=f"{pakt_id}-parent")
    eintraege: List[OrganischeChemiePaktEintrag] = []
    for g in OrganischeChemiePaktGeltung:
        eintraege.append(OrganischeChemiePaktEintrag(
            organische_chemie_pakt_id=f"{pakt_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            chemie_weight=round(sum(n.chemie_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            chemie_tier=max(n.chemie_tier for n in parent.normen) + _TIER_DELTA[g],
            chemie_ids=[f"ocp-{pakt_id}-{g.value}-001", f"ocp-{pakt_id}-{g.value}-002"],
            chemie_tags=["chemie", "organisch", "pakt", g.value],
        ))
    return OrganischeChemiePakt(pakt_id=pakt_id, eintraege=eintraege, parent=parent)
