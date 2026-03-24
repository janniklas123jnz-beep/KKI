"""#625 KompositionsManifest — Komposition & Form (parent: MelodieKodex)."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List
from .melodie_kodex import MelodieKodex, build_melodie_kodex

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class KompositionsManifestGeltung(str, Enum):
    GESPERRT = "gesperrt"
    KOMPOSITORISCH = "kompositorisch"
    GRUNDLEGEND_KOMPOSITORISCH = "grundlegend-kompositorisch"


class KompositionsManifestTyp(str, Enum):
    ANALYTISCH = "analytisch"
    SYNTHETISCH = "synthetisch"
    HISTORISCH = "historisch"
    KOMPARATIV = "komparativ"


class KompositionsManifestProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class KompositionsManifestNorm:
    kompositions_manifest_id: str
    geltung: KompositionsManifestGeltung
    typ: KompositionsManifestTyp
    musik_weight: float
    musik_tier: int
    musik_ids: List[str]
    musik_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class KompositionsManifest:
    manifest_id: str
    normen: List[KompositionsManifestNorm]
    parent: MelodieKodex


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        KompositionsManifestGeltung.GESPERRT: 0.0,
        KompositionsManifestGeltung.KOMPOSITORISCH: 0.05,
        KompositionsManifestGeltung.GRUNDLEGEND_KOMPOSITORISCH: 0.1,
    })
    _TIER_DELTA.update({
        KompositionsManifestGeltung.GESPERRT: 0,
        KompositionsManifestGeltung.KOMPOSITORISCH: 1,
        KompositionsManifestGeltung.GRUNDLEGEND_KOMPOSITORISCH: 2,
    })
    _TYP_MAP.update({
        KompositionsManifestGeltung.GESPERRT: KompositionsManifestTyp.ANALYTISCH,
        KompositionsManifestGeltung.KOMPOSITORISCH: KompositionsManifestTyp.SYNTHETISCH,
        KompositionsManifestGeltung.GRUNDLEGEND_KOMPOSITORISCH: KompositionsManifestTyp.HISTORISCH,
    })
    _PROZEDUR_MAP.update({
        KompositionsManifestGeltung.GESPERRT: KompositionsManifestProzedur.INITIALISIEREN,
        KompositionsManifestGeltung.KOMPOSITORISCH: KompositionsManifestProzedur.AKTIVIEREN,
        KompositionsManifestGeltung.GRUNDLEGEND_KOMPOSITORISCH: KompositionsManifestProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        KompositionsManifestGeltung.GESPERRT: [KompositionsManifestGeltung.GESPERRT],
        KompositionsManifestGeltung.KOMPOSITORISCH: [KompositionsManifestGeltung.KOMPOSITORISCH],
        KompositionsManifestGeltung.GRUNDLEGEND_KOMPOSITORISCH: [KompositionsManifestGeltung.GRUNDLEGEND_KOMPOSITORISCH],
    })


_init_map()


def build_kompositions_manifest(*, manifest_id: str = "kompositions-manifest") -> KompositionsManifest:
    parent = build_melodie_kodex(kodex_id=f"{manifest_id}-parent")
    normen: List[KompositionsManifestNorm] = []
    for g in KompositionsManifestGeltung:
        normen.append(KompositionsManifestNorm(
            kompositions_manifest_id=f"{manifest_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            musik_weight=round(sum(n.musik_weight for n in parent.normen) * (1.0 + _WEIGHT_DELTA[g]), 4),
            musik_tier=max(n.musik_tier for n in parent.normen) + _TIER_DELTA[g],
            musik_ids=[f"km-{manifest_id}-{g.value}-001", f"km-{manifest_id}-{g.value}-002"],
            musik_tags=["musikwissenschaft", "komposition", g.value],
        ))
    return KompositionsManifest(manifest_id=manifest_id, normen=normen, parent=parent)
