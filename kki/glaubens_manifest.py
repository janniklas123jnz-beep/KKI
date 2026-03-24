from __future__ import annotations

# Leitsterns GlaubensManifest: GESPERRT schützt Glaubensgrundprinzipien,
# GLAEUBIG aktiviert gläubige Souveränität,
# GRUNDLEGEND_GLAEUBIG verankert universelles Glaubensfundament.
# Geltungsstufen: GESPERRT / GLAEUBIG / GRUNDLEGEND_GLAEUBIG

from dataclasses import dataclass
from enum import Enum

from kki.theologie_kodex import (
    TheologieKodex,
    TheologieKodexGeltung,
    build_theologie_kodex,
)

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class GlaubensManifestGeltung(str, Enum):
    GESPERRT = "gesperrt"
    GLAEUBIG = "glaeubig"
    GRUNDLEGEND_GLAEUBIG = "grundlegend-glaeubig"


class GlaubensManifestTyp(str, Enum):
    SCHUTZ_GLAUBENSMANIFEST = "schutz-glaubensmanifest"
    ORDNUNGS_GLAUBENSMANIFEST = "ordnungs-glaubensmanifest"
    SOUVERAENITAETS_GLAUBENSMANIFEST = "souveraenitaets-glaubensmanifest"


class GlaubensManifestProzedur(str, Enum):
    GLAUBEN_SITZUNG = "glauben-sitzung"
    GLAUBEN_REGELPROTOKOLL = "glauben-regelprotokoll"
    GLAUBEN_PLENARPROTOKOLL = "glauben-plenarprotokoll"


@dataclass(frozen=True)
class GlaubensManifestNorm:
    glaubens_manifest_id: str
    religions_typ: GlaubensManifestTyp
    prozedur: GlaubensManifestProzedur
    geltung: GlaubensManifestGeltung
    religions_weight: float
    religions_tier: int
    canonical: bool
    religions_ids: tuple[str, ...]
    religions_tags: tuple[str, ...]


@dataclass(frozen=True)
class GlaubensManifest:
    manifest_id: str
    theologie_kodex: TheologieKodex
    normen: tuple[GlaubensManifestNorm, ...]


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        GlaubensManifestGeltung.GESPERRT: 0.0,
        GlaubensManifestGeltung.GLAEUBIG: 0.05,
        GlaubensManifestGeltung.GRUNDLEGEND_GLAEUBIG: 0.1,
    })
    _TIER_DELTA.update({
        GlaubensManifestGeltung.GESPERRT: 0,
        GlaubensManifestGeltung.GLAEUBIG: 1,
        GlaubensManifestGeltung.GRUNDLEGEND_GLAEUBIG: 2,
    })
    _TYP_MAP.update({
        GlaubensManifestGeltung.GESPERRT: GlaubensManifestTyp.SCHUTZ_GLAUBENSMANIFEST,
        GlaubensManifestGeltung.GLAEUBIG: GlaubensManifestTyp.ORDNUNGS_GLAUBENSMANIFEST,
        GlaubensManifestGeltung.GRUNDLEGEND_GLAEUBIG: GlaubensManifestTyp.SOUVERAENITAETS_GLAUBENSMANIFEST,
    })
    _PROZEDUR_MAP.update({
        GlaubensManifestGeltung.GESPERRT: GlaubensManifestProzedur.GLAUBEN_SITZUNG,
        GlaubensManifestGeltung.GLAEUBIG: GlaubensManifestProzedur.GLAUBEN_REGELPROTOKOLL,
        GlaubensManifestGeltung.GRUNDLEGEND_GLAEUBIG: GlaubensManifestProzedur.GLAUBEN_PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        TheologieKodexGeltung.GESPERRT: GlaubensManifestGeltung.GESPERRT,
        TheologieKodexGeltung.THEOLOGISCH: GlaubensManifestGeltung.GLAEUBIG,
        TheologieKodexGeltung.GRUNDLEGEND_THEOLOGISCH: GlaubensManifestGeltung.GRUNDLEGEND_GLAEUBIG,
    })


_init_map()


def build_glaubens_manifest(
    theologie_kodex: TheologieKodex | None = None,
    *,
    manifest_id: str = "glaubens-manifest",
) -> GlaubensManifest:
    if theologie_kodex is None:
        theologie_kodex = build_theologie_kodex(kodex_id=f"{manifest_id}-theologie-kodex")

    normen: list[GlaubensManifestNorm] = []
    for parent_norm in theologie_kodex.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{manifest_id}-{parent_norm.theologie_kodex_id.removeprefix(f'{theologie_kodex.kodex_id}-')}"
        raw_weight = min(1.0, parent_norm.religions_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.religions_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is GlaubensManifestGeltung.GRUNDLEGEND_GLAEUBIG)
        normen.append(
            GlaubensManifestNorm(
                glaubens_manifest_id=new_id,
                religions_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                religions_weight=new_weight,
                religions_tier=new_tier,
                canonical=is_canonical,
                religions_ids=parent_norm.religions_ids + (new_id,),
                religions_tags=parent_norm.religions_tags + (f"glaubens-manifest:{new_geltung.value}",),
            )
        )
    return GlaubensManifest(
        manifest_id=manifest_id,
        theologie_kodex=theologie_kodex,
        normen=tuple(normen),
    )
