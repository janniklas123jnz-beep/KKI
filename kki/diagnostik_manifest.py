"""#645 DiagnostikManifest — Diagnostik & klinische Untersuchung (parent: PathologieKodex)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List
from .pathologie_kodex import PathologieKodex, build_pathologie_kodex

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class DiagnostikManifestGeltung(str, Enum):
    GESPERRT = "gesperrt"
    DIAGNOSTISCH = "diagnostisch"
    GRUNDLEGEND_DIAGNOSTISCH = "grundlegend-diagnostisch"


class DiagnostikManifestTyp(str, Enum):
    KLINISCH = "klinisch"
    THEORETISCH = "theoretisch"
    ANGEWANDT = "angewandt"
    PRAEVENTIV = "praeventiv"


class DiagnostikManifestProzedur(str, Enum):
    INITIALISIEREN = "initialisieren"
    AKTIVIEREN = "aktivieren"
    INTEGRIEREN = "integrieren"
    VALIDIEREN = "validieren"


@dataclass(frozen=True)
class DiagnostikManifestNorm:
    manifest_id: str
    geltung: DiagnostikManifestGeltung
    typ: DiagnostikManifestTyp
    prozedur: DiagnostikManifestProzedur
    medizin_weight: float
    medizin_tier: int
    medizin_ids: List[str]
    medizin_tags: List[str]
    canonical: bool = True


@dataclass(frozen=True)
class DiagnostikManifest:
    manifest_id: str
    normen: List[DiagnostikManifestNorm]
    parent: PathologieKodex


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        DiagnostikManifestGeltung.GESPERRT: 0.0,
        DiagnostikManifestGeltung.DIAGNOSTISCH: 0.05,
        DiagnostikManifestGeltung.GRUNDLEGEND_DIAGNOSTISCH: 0.1,
    })
    _TIER_DELTA.update({
        DiagnostikManifestGeltung.GESPERRT: 0,
        DiagnostikManifestGeltung.DIAGNOSTISCH: 1,
        DiagnostikManifestGeltung.GRUNDLEGEND_DIAGNOSTISCH: 2,
    })
    _TYP_MAP.update({
        DiagnostikManifestGeltung.GESPERRT: DiagnostikManifestTyp.KLINISCH,
        DiagnostikManifestGeltung.DIAGNOSTISCH: DiagnostikManifestTyp.THEORETISCH,
        DiagnostikManifestGeltung.GRUNDLEGEND_DIAGNOSTISCH: DiagnostikManifestTyp.ANGEWANDT,
    })
    _PROZEDUR_MAP.update({
        DiagnostikManifestGeltung.GESPERRT: DiagnostikManifestProzedur.INITIALISIEREN,
        DiagnostikManifestGeltung.DIAGNOSTISCH: DiagnostikManifestProzedur.AKTIVIEREN,
        DiagnostikManifestGeltung.GRUNDLEGEND_DIAGNOSTISCH: DiagnostikManifestProzedur.INTEGRIEREN,
    })
    _GELTUNG_MAP.update({
        DiagnostikManifestGeltung.GESPERRT: [DiagnostikManifestGeltung.GESPERRT],
        DiagnostikManifestGeltung.DIAGNOSTISCH: [DiagnostikManifestGeltung.DIAGNOSTISCH],
        DiagnostikManifestGeltung.GRUNDLEGEND_DIAGNOSTISCH: [DiagnostikManifestGeltung.GRUNDLEGEND_DIAGNOSTISCH],
    })


_init_map()


def build_diagnostik_manifest(*, manifest_id: str = "diagnostik-manifest") -> DiagnostikManifest:
    parent = build_pathologie_kodex(kodex_id=f"{manifest_id}-parent")
    normen: List[DiagnostikManifestNorm] = []
    for g in DiagnostikManifestGeltung:
        normen.append(DiagnostikManifestNorm(
            manifest_id=f"{manifest_id}-{g.value}",
            geltung=g,
            typ=_TYP_MAP[g],
            prozedur=_PROZEDUR_MAP[g],
            medizin_weight=round(sum(e.medizin_weight for e in parent.eintraege) * (1.0 + _WEIGHT_DELTA[g]), 4),
            medizin_tier=max(e.medizin_tier for e in parent.eintraege) + _TIER_DELTA[g],
            medizin_ids=[f"dm-{manifest_id}-{g.value}-001", f"dm-{manifest_id}-{g.value}-002"],
            medizin_tags=["medizin", "diagnostik", g.value],
        ))
    return DiagnostikManifest(manifest_id=manifest_id, normen=normen, parent=parent)
