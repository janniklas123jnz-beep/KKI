"""#726 — VerhaltensoekonomiePakt: Kognitive Verzerrungen, Nudging & Entscheidungstheorie."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.markttheorie_manifest import MarkttheorieManifest, build_markttheorie_manifest


class VerhaltensoekonomiePaktGeltung(str, Enum):
    GESPERRT = "gesperrt"
    VERHALTENSOKONOMISCH = "verhaltensokonomisch"
    GRUNDLEGEND_VERHALTENSOKONOMISCH = "grundlegend-verhaltensokonomisch"


class VerhaltensoekonomiePaktTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class VerhaltensoekonomiePaktProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class VerhaltensoekonomiePaktEintrag:
    eintrag_id: str
    geltung: VerhaltensoekonomiePaktGeltung
    typ: VerhaltensoekonomiePaktTyp
    prozedur: VerhaltensoekonomiePaktProzedur
    wirt_weight: float
    wirt_tier: int
    wirt_ids: List[str]
    wirt_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class VerhaltensoekonomiePakt:
    pakt_id: str
    eintraege: List[VerhaltensoekonomiePaktEintrag]
    parent: MarkttheorieManifest


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        VerhaltensoekonomiePaktGeltung.GESPERRT: 0.0,
        VerhaltensoekonomiePaktGeltung.VERHALTENSOKONOMISCH: 0.05,
        VerhaltensoekonomiePaktGeltung.GRUNDLEGEND_VERHALTENSOKONOMISCH: 0.1,
    })
    _TIER_DELTA.update({
        VerhaltensoekonomiePaktGeltung.GESPERRT: 0,
        VerhaltensoekonomiePaktGeltung.VERHALTENSOKONOMISCH: 1,
        VerhaltensoekonomiePaktGeltung.GRUNDLEGEND_VERHALTENSOKONOMISCH: 2,
    })
    _TYP_MAP.update({
        VerhaltensoekonomiePaktGeltung.GESPERRT: VerhaltensoekonomiePaktTyp.BEOBACHTUNG,
        VerhaltensoekonomiePaktGeltung.VERHALTENSOKONOMISCH: VerhaltensoekonomiePaktTyp.ANALYSE,
        VerhaltensoekonomiePaktGeltung.GRUNDLEGEND_VERHALTENSOKONOMISCH: VerhaltensoekonomiePaktTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        VerhaltensoekonomiePaktGeltung.GESPERRT: VerhaltensoekonomiePaktProzedur.INITIALISIEREN,
        VerhaltensoekonomiePaktGeltung.VERHALTENSOKONOMISCH: VerhaltensoekonomiePaktProzedur.AKTIVIEREN,
        VerhaltensoekonomiePaktGeltung.GRUNDLEGEND_VERHALTENSOKONOMISCH: VerhaltensoekonomiePaktProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        VerhaltensoekonomiePaktGeltung.GESPERRT: [VerhaltensoekonomiePaktGeltung.GESPERRT],
        VerhaltensoekonomiePaktGeltung.VERHALTENSOKONOMISCH: [VerhaltensoekonomiePaktGeltung.VERHALTENSOKONOMISCH],
        VerhaltensoekonomiePaktGeltung.GRUNDLEGEND_VERHALTENSOKONOMISCH: [VerhaltensoekonomiePaktGeltung.GRUNDLEGEND_VERHALTENSOKONOMISCH],
    })


_init_map()


def build_verhaltensoekonomie_pakt(*, pakt_id: str = "verhaltensoekonomie-pakt") -> VerhaltensoekonomiePakt:
    parent = build_markttheorie_manifest(manifest_id=f"{pakt_id}-parent")
    eintraege: List[VerhaltensoekonomiePaktEintrag] = []
    for g in VerhaltensoekonomiePaktGeltung:
        eintraege.append(VerhaltensoekonomiePaktEintrag(
            eintrag_id=f"{pakt_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            wirt_weight=round(sum(n.wirt_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            wirt_tier=max(n.wirt_tier for n in parent.normen) + _TIER_DELTA[g],
            wirt_ids=[f"vp-{pakt_id}-{g.value}-001", f"vp-{pakt_id}-{g.value}-002"],
            wirt_tags=["wirt", "verhaltensoekonomie", g.value],
        ))
    return VerhaltensoekonomiePakt(pakt_id=pakt_id, eintraege=eintraege, parent=parent)
