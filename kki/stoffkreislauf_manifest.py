"""#665 StoffkreislaufManifest — Biogeochemische Kreisläufe & Energie (parent: ArtenvielfaltKodex)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .artenvielfalt_kodex import ArtenvielfaltKodex, build_artenvielfalt_kodex

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class StoffkreislaufManifestGeltung(str, Enum):
    GESPERRT = "gesperrt"
    STOFFKREISLAUF_AKTIV = "stoffkreislauf-aktiv"
    GRUNDLEGEND_STOFFKREISLAUF_AKTIV = "grundlegend-stoffkreislauf-aktiv"


class StoffkreislaufManifestTyp(str, Enum):
    BEOBACHTUNG = "beobachtung"
    ANALYSE = "analyse"
    SYNTHESE = "synthese"
    SCHUTZ = "schutz"


class StoffkreislaufManifestProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class StoffkreislaufManifestNorm:
    stoffkreislauf_manifest_id: str
    geltung: StoffkreislaufManifestGeltung
    typ: StoffkreislaufManifestTyp
    prozedur: StoffkreislaufManifestProzedur
    oekologie_weight: float
    oekologie_tier: int
    oekologie_ids: List[str]
    oekologie_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class StoffkreislaufManifest:
    manifest_id: str
    normen: List[StoffkreislaufManifestNorm]
    parent: ArtenvielfaltKodex


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        StoffkreislaufManifestGeltung.GESPERRT: 0.0,
        StoffkreislaufManifestGeltung.STOFFKREISLAUF_AKTIV: 0.05,
        StoffkreislaufManifestGeltung.GRUNDLEGEND_STOFFKREISLAUF_AKTIV: 0.1,
    })
    _TIER_DELTA.update({
        StoffkreislaufManifestGeltung.GESPERRT: 0,
        StoffkreislaufManifestGeltung.STOFFKREISLAUF_AKTIV: 1,
        StoffkreislaufManifestGeltung.GRUNDLEGEND_STOFFKREISLAUF_AKTIV: 2,
    })
    _TYP_MAP.update({
        StoffkreislaufManifestGeltung.GESPERRT: StoffkreislaufManifestTyp.BEOBACHTUNG,
        StoffkreislaufManifestGeltung.STOFFKREISLAUF_AKTIV: StoffkreislaufManifestTyp.ANALYSE,
        StoffkreislaufManifestGeltung.GRUNDLEGEND_STOFFKREISLAUF_AKTIV: StoffkreislaufManifestTyp.SYNTHESE,
    })
    _PROZEDUR_MAP.update({
        StoffkreislaufManifestGeltung.GESPERRT: StoffkreislaufManifestProzedur.INITIALISIEREN,
        StoffkreislaufManifestGeltung.STOFFKREISLAUF_AKTIV: StoffkreislaufManifestProzedur.AKTIVIEREN,
        StoffkreislaufManifestGeltung.GRUNDLEGEND_STOFFKREISLAUF_AKTIV: StoffkreislaufManifestProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        StoffkreislaufManifestGeltung.GESPERRT: [StoffkreislaufManifestGeltung.GESPERRT],
        StoffkreislaufManifestGeltung.STOFFKREISLAUF_AKTIV: [StoffkreislaufManifestGeltung.STOFFKREISLAUF_AKTIV],
        StoffkreislaufManifestGeltung.GRUNDLEGEND_STOFFKREISLAUF_AKTIV: [StoffkreislaufManifestGeltung.GRUNDLEGEND_STOFFKREISLAUF_AKTIV],
    })


_init_map()


def build_stoffkreislauf_manifest(*, manifest_id: str = "stoffkreislauf-manifest") -> StoffkreislaufManifest:
    parent = build_artenvielfalt_kodex(kodex_id=f"{manifest_id}-parent")
    normen: List[StoffkreislaufManifestNorm] = []
    for g in StoffkreislaufManifestGeltung:
        normen.append(StoffkreislaufManifestNorm(
            stoffkreislauf_manifest_id=f"{manifest_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            oekologie_weight=round(sum(e.oekologie_weight for e in parent.eintraege) * (1.0 + _WEIGHT_DELTA[g]), 4),
            oekologie_tier=max(e.oekologie_tier for e in parent.eintraege) + _TIER_DELTA[g],
            oekologie_ids=[f"sm-{manifest_id}-{g.value}-001", f"sm-{manifest_id}-{g.value}-002"],
            oekologie_tags=["oekologie", "stoffkreislauf", "manifest", g.value],
        ))
    return StoffkreislaufManifest(manifest_id=manifest_id, normen=normen, parent=parent)
