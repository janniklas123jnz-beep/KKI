"""#686 — NanostrukturPakt: Nanopartikel, Quantenpunkte & CNTs."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from kki.komposit_manifest import KompositManifest, build_komposit_manifest


class NanostrukturPaktGeltung(str, Enum):
    GESPERRT = "gesperrt"
    NANOSTRUKTURIERT = "nanostrukturiert"
    GRUNDLEGEND_NANOSTRUKTURIERT = "grundlegend-nanostrukturiert"


class NanostrukturPaktTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"


class NanostrukturPaktProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"


_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


@dataclass(frozen=True)
class NanostrukturPaktEintrag:
    eintrag_id: str
    geltung: NanostrukturPaktGeltung
    typ: NanostrukturPaktTyp
    prozedur: NanostrukturPaktProzedur
    material_weight: float
    material_tier: int
    material_ids: List[str]
    material_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class NanostrukturPakt:
    pakt_id: str
    eintraege: List[NanostrukturPaktEintrag]
    parent: KompositManifest


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        NanostrukturPaktGeltung.GESPERRT: 0.0,
        NanostrukturPaktGeltung.NANOSTRUKTURIERT: 0.05,
        NanostrukturPaktGeltung.GRUNDLEGEND_NANOSTRUKTURIERT: 0.1,
    })
    _TIER_DELTA.update({
        NanostrukturPaktGeltung.GESPERRT: 0,
        NanostrukturPaktGeltung.NANOSTRUKTURIERT: 1,
        NanostrukturPaktGeltung.GRUNDLEGEND_NANOSTRUKTURIERT: 2,
    })
    _TYP_MAP.update({
        NanostrukturPaktGeltung.GESPERRT: NanostrukturPaktTyp.BEOBACHTUNG,
        NanostrukturPaktGeltung.NANOSTRUKTURIERT: NanostrukturPaktTyp.ANALYSE,
        NanostrukturPaktGeltung.GRUNDLEGEND_NANOSTRUKTURIERT: NanostrukturPaktTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        NanostrukturPaktGeltung.GESPERRT: NanostrukturPaktProzedur.INITIALISIEREN,
        NanostrukturPaktGeltung.NANOSTRUKTURIERT: NanostrukturPaktProzedur.AKTIVIEREN,
        NanostrukturPaktGeltung.GRUNDLEGEND_NANOSTRUKTURIERT: NanostrukturPaktProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        NanostrukturPaktGeltung.GESPERRT: [NanostrukturPaktGeltung.GESPERRT],
        NanostrukturPaktGeltung.NANOSTRUKTURIERT: [NanostrukturPaktGeltung.NANOSTRUKTURIERT],
        NanostrukturPaktGeltung.GRUNDLEGEND_NANOSTRUKTURIERT: [NanostrukturPaktGeltung.GRUNDLEGEND_NANOSTRUKTURIERT],
    })


_init_map()


def build_nanostruktur_pakt(*, pakt_id: str = "nanostruktur-pakt") -> NanostrukturPakt:
    parent = build_komposit_manifest(manifest_id=f"{pakt_id}-parent")
    eintraege: List[NanostrukturPaktEintrag] = []
    for g in NanostrukturPaktGeltung:
        eintraege.append(NanostrukturPaktEintrag(
            eintrag_id=f"{pakt_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            material_weight=round(sum(n.material_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            material_tier=max(n.material_tier for n in parent.normen) + _TIER_DELTA[g],
            material_ids=[f"np-{pakt_id}-{g.value}-001", f"np-{pakt_id}-{g.value}-002"],
            material_tags=["material", "nanostruktur", g.value],
        ))
    return NanostrukturPakt(pakt_id=pakt_id, eintraege=eintraege, parent=parent)
