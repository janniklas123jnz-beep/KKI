"""#687 — QuantenmaterialSenat: Supraleitung, topologische Isolatoren & Quanteneffekte."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.nanostruktur_pakt import NanostrukturPakt, build_nanostruktur_pakt


class QuantenmaterialSenatGeltung(str, Enum):
    GESPERRT = "gesperrt"
    QUANTENMATERIAL_AKTIV = "quantenmaterial-aktiv"
    GRUNDLEGEND_QUANTENMATERIAL_AKTIV = "grundlegend-quantenmaterial-aktiv"


class QuantenmaterialSenatTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class QuantenmaterialSenatProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class QuantenmaterialSenatNorm:
    norm_id: str
    geltung: QuantenmaterialSenatGeltung
    typ: QuantenmaterialSenatTyp
    prozedur: QuantenmaterialSenatProzedur
    material_weight: float
    material_tier: int
    material_ids: List[str]
    material_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class QuantenmaterialSenat:
    senat_id: str
    normen: List[QuantenmaterialSenatNorm]
    parent: NanostrukturPakt


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        QuantenmaterialSenatGeltung.GESPERRT: 0.0,
        QuantenmaterialSenatGeltung.QUANTENMATERIAL_AKTIV: 0.05,
        QuantenmaterialSenatGeltung.GRUNDLEGEND_QUANTENMATERIAL_AKTIV: 0.1,
    })
    _TIER_DELTA.update({
        QuantenmaterialSenatGeltung.GESPERRT: 0,
        QuantenmaterialSenatGeltung.QUANTENMATERIAL_AKTIV: 1,
        QuantenmaterialSenatGeltung.GRUNDLEGEND_QUANTENMATERIAL_AKTIV: 2,
    })
    _TYP_MAP.update({
        QuantenmaterialSenatGeltung.GESPERRT: QuantenmaterialSenatTyp.BEOBACHTUNG,
        QuantenmaterialSenatGeltung.QUANTENMATERIAL_AKTIV: QuantenmaterialSenatTyp.ANALYSE,
        QuantenmaterialSenatGeltung.GRUNDLEGEND_QUANTENMATERIAL_AKTIV: QuantenmaterialSenatTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        QuantenmaterialSenatGeltung.GESPERRT: QuantenmaterialSenatProzedur.INITIALISIEREN,
        QuantenmaterialSenatGeltung.QUANTENMATERIAL_AKTIV: QuantenmaterialSenatProzedur.AKTIVIEREN,
        QuantenmaterialSenatGeltung.GRUNDLEGEND_QUANTENMATERIAL_AKTIV: QuantenmaterialSenatProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        QuantenmaterialSenatGeltung.GESPERRT: [QuantenmaterialSenatGeltung.GESPERRT],
        QuantenmaterialSenatGeltung.QUANTENMATERIAL_AKTIV: [QuantenmaterialSenatGeltung.QUANTENMATERIAL_AKTIV],
        QuantenmaterialSenatGeltung.GRUNDLEGEND_QUANTENMATERIAL_AKTIV: [QuantenmaterialSenatGeltung.GRUNDLEGEND_QUANTENMATERIAL_AKTIV],
    })


_init_map()


def build_quantenmaterial_senat(*, senat_id: str = "quantenmaterial-senat") -> QuantenmaterialSenat:
    parent = build_nanostruktur_pakt(pakt_id=f"{senat_id}-parent")
    normen: List[QuantenmaterialSenatNorm] = []
    for g in QuantenmaterialSenatGeltung:
        normen.append(QuantenmaterialSenatNorm(
            norm_id=f"{senat_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            material_weight=round(sum(e.material_weight for e in parent.eintraege) * (1.0 + _WEIGHT_DELTA[g]), 4),
            material_tier=max(e.material_tier for e in parent.eintraege) + _TIER_DELTA[g],
            material_ids=[f"qs-{senat_id}-{g.value}-001", f"qs-{senat_id}-{g.value}-002"],
            material_tags=["material", "quantenmaterial", g.value],
        ))
    return QuantenmaterialSenat(senat_id=senat_id, normen=normen, parent=parent)
