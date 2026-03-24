from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from kki.semantik_manifest import SemantikManifest, SemantikManifestGeltung, build_semantik_manifest

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class PragmatikPaktGeltung(str, Enum):
    GESPERRT = "gesperrt"
    PRAGMATISCH = "pragmatisch"
    GRUNDLEGEND_PRAGMATISCH = "grundlegend-pragmatisch"


class PragmatikPaktTyp(str, Enum):
    SCHUTZ_PRAGMATIKPAKT = "schutz-pragmatikpakt"
    ORDNUNGS_PRAGMATIKPAKT = "ordnungs-pragmatikpakt"
    SOUVERAENITAETS_PRAGMATIKPAKT = "souveraenitaets-pragmatikpakt"


class PragmatikPaktProzedur(str, Enum):
    PRAGMATIK_ANALYSE = "pragmatik-analyse"
    PRAGMATIK_INTEGRATION = "pragmatik-integration"
    PRAGMATIK_SYNTHESE = "pragmatik-synthese"


@dataclass(frozen=True)
class PragmatikPaktNorm:
    pragmatik_pakt_id: str
    linguistik_typ: PragmatikPaktTyp
    prozedur: PragmatikPaktProzedur
    geltung: PragmatikPaktGeltung
    linguistik_weight: float
    linguistik_tier: int
    canonical: bool
    linguistik_ids: tuple[str, ...]
    linguistik_tags: tuple[str, ...]


@dataclass(frozen=True)
class PragmatikPakt:
    pakt_id: str
    semantik_manifest: SemantikManifest
    normen: tuple[PragmatikPaktNorm, ...]


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        PragmatikPaktGeltung.GESPERRT: 0.0,
        PragmatikPaktGeltung.PRAGMATISCH: 0.05,
        PragmatikPaktGeltung.GRUNDLEGEND_PRAGMATISCH: 0.1,
    })
    _TIER_DELTA.update({
        PragmatikPaktGeltung.GESPERRT: 0,
        PragmatikPaktGeltung.PRAGMATISCH: 1,
        PragmatikPaktGeltung.GRUNDLEGEND_PRAGMATISCH: 2,
    })
    _TYP_MAP.update({
        PragmatikPaktGeltung.GESPERRT: PragmatikPaktTyp.SCHUTZ_PRAGMATIKPAKT,
        PragmatikPaktGeltung.PRAGMATISCH: PragmatikPaktTyp.ORDNUNGS_PRAGMATIKPAKT,
        PragmatikPaktGeltung.GRUNDLEGEND_PRAGMATISCH: PragmatikPaktTyp.SOUVERAENITAETS_PRAGMATIKPAKT,
    })
    _PROZEDUR_MAP.update({
        PragmatikPaktGeltung.GESPERRT: PragmatikPaktProzedur.PRAGMATIK_ANALYSE,
        PragmatikPaktGeltung.PRAGMATISCH: PragmatikPaktProzedur.PRAGMATIK_INTEGRATION,
        PragmatikPaktGeltung.GRUNDLEGEND_PRAGMATISCH: PragmatikPaktProzedur.PRAGMATIK_SYNTHESE,
    })
    _GELTUNG_MAP.update({
        SemantikManifestGeltung.GESPERRT: PragmatikPaktGeltung.GESPERRT,
        SemantikManifestGeltung.SEMANTISCH: PragmatikPaktGeltung.PRAGMATISCH,
        SemantikManifestGeltung.GRUNDLEGEND_SEMANTISCH: PragmatikPaktGeltung.GRUNDLEGEND_PRAGMATISCH,
    })


_init_map()


def build_pragmatik_pakt(
    semantik_manifest: SemantikManifest | None = None,
    *,
    pakt_id: str = "diskurs-pakt",
) -> PragmatikPakt:
    if semantik_manifest is None:
        semantik_manifest = build_semantik_manifest(manifest_id=f"{pakt_id}-manifest")

    normen: list[PragmatikPaktNorm] = []
    for parent_norm in semantik_manifest.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{pakt_id}-{parent_norm.semantik_manifest_id.removeprefix(f'{semantik_manifest.manifest_id}-')}"
        raw_weight = min(1.0, parent_norm.linguistik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.linguistik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is PragmatikPaktGeltung.GRUNDLEGEND_PRAGMATISCH)
        normen.append(
            PragmatikPaktNorm(
                pragmatik_pakt_id=new_id,
                linguistik_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                linguistik_weight=new_weight,
                linguistik_tier=new_tier,
                canonical=is_canonical,
                linguistik_ids=parent_norm.linguistik_ids + (new_id,),
                linguistik_tags=parent_norm.linguistik_tags + (f"diskurs-pakt:{new_geltung.value}",),
            )
        )
    return PragmatikPakt(
        pakt_id=pakt_id,
        semantik_manifest=semantik_manifest,
        normen=tuple(normen),
    )
