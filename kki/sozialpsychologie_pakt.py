from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from kki.entwicklungs_manifest import (
    EntwicklungsManifest,
    EntwicklungsManifestGeltung,
    build_entwicklungs_manifest,
)

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class SozialpsychologiePaktGeltung(str, Enum):
    GESPERRT = "gesperrt"
    SOZIALPSYCHOLOGISCH = "sozialpsychologisch"
    GRUNDLEGEND_SOZIALPSYCHOLOGISCH = "grundlegend-sozialpsychologisch"


class SozialpsychologiePaktTyp(str, Enum):
    SCHUTZ_SOZIALPSYCHOLOGIEPAKT = "schutz-sozialpsychologiepakt"
    ORDNUNGS_SOZIALPSYCHOLOGIEPAKT = "ordnungs-sozialpsychologiepakt"
    SOUVERAENITAETS_SOZIALPSYCHOLOGIEPAKT = "souveraenitaets-sozialpsychologiepakt"


class SozialpsychologiePaktProzedur(str, Enum):
    SOZIALPSYCHOLOGIEPAKT_ANALYSE = "sozialpsychologiepakt-analyse"
    SOZIALPSYCHOLOGIEPAKT_INTEGRATION = "sozialpsychologiepakt-integration"
    SOZIALPSYCHOLOGIEPAKT_SYNTHESE = "sozialpsychologiepakt-synthese"


@dataclass(frozen=True)
class SozialpsychologiePaktNorm:
    sozialpsychologie_pakt_id: str
    psychologie_typ: SozialpsychologiePaktTyp
    prozedur: SozialpsychologiePaktProzedur
    geltung: SozialpsychologiePaktGeltung
    psychologie_weight: float
    psychologie_tier: int
    canonical: bool
    psychologie_ids: tuple[str, ...]
    psychologie_tags: tuple[str, ...]


@dataclass(frozen=True)
class SozialpsychologiePakt:
    pakt_id: str
    entwicklungs_manifest: EntwicklungsManifest
    normen: tuple[SozialpsychologiePaktNorm, ...]


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        SozialpsychologiePaktGeltung.GESPERRT: 0.0,
        SozialpsychologiePaktGeltung.SOZIALPSYCHOLOGISCH: 0.05,
        SozialpsychologiePaktGeltung.GRUNDLEGEND_SOZIALPSYCHOLOGISCH: 0.1,
    })
    _TIER_DELTA.update({
        SozialpsychologiePaktGeltung.GESPERRT: 0,
        SozialpsychologiePaktGeltung.SOZIALPSYCHOLOGISCH: 1,
        SozialpsychologiePaktGeltung.GRUNDLEGEND_SOZIALPSYCHOLOGISCH: 2,
    })
    _TYP_MAP.update({
        SozialpsychologiePaktGeltung.GESPERRT: SozialpsychologiePaktTyp.SCHUTZ_SOZIALPSYCHOLOGIEPAKT,
        SozialpsychologiePaktGeltung.SOZIALPSYCHOLOGISCH: SozialpsychologiePaktTyp.ORDNUNGS_SOZIALPSYCHOLOGIEPAKT,
        SozialpsychologiePaktGeltung.GRUNDLEGEND_SOZIALPSYCHOLOGISCH: SozialpsychologiePaktTyp.SOUVERAENITAETS_SOZIALPSYCHOLOGIEPAKT,
    })
    _PROZEDUR_MAP.update({
        SozialpsychologiePaktGeltung.GESPERRT: SozialpsychologiePaktProzedur.SOZIALPSYCHOLOGIEPAKT_ANALYSE,
        SozialpsychologiePaktGeltung.SOZIALPSYCHOLOGISCH: SozialpsychologiePaktProzedur.SOZIALPSYCHOLOGIEPAKT_INTEGRATION,
        SozialpsychologiePaktGeltung.GRUNDLEGEND_SOZIALPSYCHOLOGISCH: SozialpsychologiePaktProzedur.SOZIALPSYCHOLOGIEPAKT_SYNTHESE,
    })
    _GELTUNG_MAP.update({
        EntwicklungsManifestGeltung.GESPERRT: SozialpsychologiePaktGeltung.GESPERRT,
        EntwicklungsManifestGeltung.ENTWICKLUNGSPSYCHOLOGISCH: SozialpsychologiePaktGeltung.SOZIALPSYCHOLOGISCH,
        EntwicklungsManifestGeltung.GRUNDLEGEND_ENTWICKLUNGSPSYCHOLOGISCH: SozialpsychologiePaktGeltung.GRUNDLEGEND_SOZIALPSYCHOLOGISCH,
    })


_init_map()


def build_sozialpsychologie_pakt(
    entwicklungs_manifest: EntwicklungsManifest | None = None,
    *,
    pakt_id: str = "sozialpsychologie-pakt",
) -> SozialpsychologiePakt:
    if entwicklungs_manifest is None:
        entwicklungs_manifest = build_entwicklungs_manifest(
            manifest_id=f"{pakt_id}-manifest"
        )

    normen: list[SozialpsychologiePaktNorm] = []
    for parent_norm in entwicklungs_manifest.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{pakt_id}-{parent_norm.entwicklungs_manifest_id.removeprefix(f'{entwicklungs_manifest.manifest_id}-')}"
        raw_weight = min(1.0, parent_norm.psychologie_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.psychologie_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SozialpsychologiePaktGeltung.GRUNDLEGEND_SOZIALPSYCHOLOGISCH)
        normen.append(
            SozialpsychologiePaktNorm(
                sozialpsychologie_pakt_id=new_id,
                psychologie_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                psychologie_weight=new_weight,
                psychologie_tier=new_tier,
                canonical=is_canonical,
                psychologie_ids=parent_norm.psychologie_ids + (new_id,),
                psychologie_tags=parent_norm.psychologie_tags + (f"sozialpsychologie-pakt:{new_geltung.value}",),
            )
        )
    return SozialpsychologiePakt(
        pakt_id=pakt_id,
        entwicklungs_manifest=entwicklungs_manifest,
        normen=tuple(normen),
    )
