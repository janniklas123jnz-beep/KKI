from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from kki.verhaltens_kodex import (
    VerhaltensKodex,
    VerhaltensKodexGeltung,
    build_verhaltens_kodex,
)

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class EntwicklungsManifestGeltung(str, Enum):
    GESPERRT = "gesperrt"
    ENTWICKLUNGSPSYCHOLOGISCH = "entwicklungspsychologisch"
    GRUNDLEGEND_ENTWICKLUNGSPSYCHOLOGISCH = "grundlegend-entwicklungspsychologisch"


class EntwicklungsManifestTyp(str, Enum):
    SCHUTZ_ENTWICKLUNGSMANIFEST = "schutz-entwicklungsmanifest"
    ORDNUNGS_ENTWICKLUNGSMANIFEST = "ordnungs-entwicklungsmanifest"
    SOUVERAENITAETS_ENTWICKLUNGSMANIFEST = "souveraenitaets-entwicklungsmanifest"


class EntwicklungsManifestProzedur(str, Enum):
    ENTWICKLUNGSMANIFEST_ANALYSE = "entwicklungsmanifest-analyse"
    ENTWICKLUNGSMANIFEST_INTEGRATION = "entwicklungsmanifest-integration"
    ENTWICKLUNGSMANIFEST_SYNTHESE = "entwicklungsmanifest-synthese"


@dataclass(frozen=True)
class EntwicklungsManifestNorm:
    entwicklungs_manifest_id: str
    psychologie_typ: EntwicklungsManifestTyp
    prozedur: EntwicklungsManifestProzedur
    geltung: EntwicklungsManifestGeltung
    psychologie_weight: float
    psychologie_tier: int
    canonical: bool
    psychologie_ids: tuple[str, ...]
    psychologie_tags: tuple[str, ...]


@dataclass(frozen=True)
class EntwicklungsManifest:
    manifest_id: str
    verhaltens_kodex: VerhaltensKodex
    normen: tuple[EntwicklungsManifestNorm, ...]


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        EntwicklungsManifestGeltung.GESPERRT: 0.0,
        EntwicklungsManifestGeltung.ENTWICKLUNGSPSYCHOLOGISCH: 0.05,
        EntwicklungsManifestGeltung.GRUNDLEGEND_ENTWICKLUNGSPSYCHOLOGISCH: 0.1,
    })
    _TIER_DELTA.update({
        EntwicklungsManifestGeltung.GESPERRT: 0,
        EntwicklungsManifestGeltung.ENTWICKLUNGSPSYCHOLOGISCH: 1,
        EntwicklungsManifestGeltung.GRUNDLEGEND_ENTWICKLUNGSPSYCHOLOGISCH: 2,
    })
    _TYP_MAP.update({
        EntwicklungsManifestGeltung.GESPERRT: EntwicklungsManifestTyp.SCHUTZ_ENTWICKLUNGSMANIFEST,
        EntwicklungsManifestGeltung.ENTWICKLUNGSPSYCHOLOGISCH: EntwicklungsManifestTyp.ORDNUNGS_ENTWICKLUNGSMANIFEST,
        EntwicklungsManifestGeltung.GRUNDLEGEND_ENTWICKLUNGSPSYCHOLOGISCH: EntwicklungsManifestTyp.SOUVERAENITAETS_ENTWICKLUNGSMANIFEST,
    })
    _PROZEDUR_MAP.update({
        EntwicklungsManifestGeltung.GESPERRT: EntwicklungsManifestProzedur.ENTWICKLUNGSMANIFEST_ANALYSE,
        EntwicklungsManifestGeltung.ENTWICKLUNGSPSYCHOLOGISCH: EntwicklungsManifestProzedur.ENTWICKLUNGSMANIFEST_INTEGRATION,
        EntwicklungsManifestGeltung.GRUNDLEGEND_ENTWICKLUNGSPSYCHOLOGISCH: EntwicklungsManifestProzedur.ENTWICKLUNGSMANIFEST_SYNTHESE,
    })
    _GELTUNG_MAP.update({
        VerhaltensKodexGeltung.GESPERRT: EntwicklungsManifestGeltung.GESPERRT,
        VerhaltensKodexGeltung.VERHALTENSPSYCHOLOGISCH: EntwicklungsManifestGeltung.ENTWICKLUNGSPSYCHOLOGISCH,
        VerhaltensKodexGeltung.GRUNDLEGEND_VERHALTENSPSYCHOLOGISCH: EntwicklungsManifestGeltung.GRUNDLEGEND_ENTWICKLUNGSPSYCHOLOGISCH,
    })


_init_map()


def build_entwicklungs_manifest(
    verhaltens_kodex: VerhaltensKodex | None = None,
    *,
    manifest_id: str = "entwicklungs-manifest",
) -> EntwicklungsManifest:
    if verhaltens_kodex is None:
        verhaltens_kodex = build_verhaltens_kodex(
            kodex_id=f"{manifest_id}-kodex"
        )

    normen: list[EntwicklungsManifestNorm] = []
    for parent_norm in verhaltens_kodex.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{manifest_id}-{parent_norm.verhaltens_kodex_id.removeprefix(f'{verhaltens_kodex.kodex_id}-')}"
        raw_weight = min(1.0, parent_norm.psychologie_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.psychologie_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is EntwicklungsManifestGeltung.GRUNDLEGEND_ENTWICKLUNGSPSYCHOLOGISCH)
        normen.append(
            EntwicklungsManifestNorm(
                entwicklungs_manifest_id=new_id,
                psychologie_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                psychologie_weight=new_weight,
                psychologie_tier=new_tier,
                canonical=is_canonical,
                psychologie_ids=parent_norm.psychologie_ids + (new_id,),
                psychologie_tags=parent_norm.psychologie_tags + (f"entwicklungs-manifest:{new_geltung.value}",),
            )
        )
    return EntwicklungsManifest(
        manifest_id=manifest_id,
        verhaltens_kodex=verhaltens_kodex,
        normen=tuple(normen),
    )
