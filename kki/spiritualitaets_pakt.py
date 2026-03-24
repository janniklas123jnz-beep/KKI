from __future__ import annotations

# Leitsterns SpiritualitaetsPakt: GESPERRT schützt spirituelle Grundprinzipien,
# SPIRITUELL aktiviert spirituelle Souveränität,
# GRUNDLEGEND_SPIRITUELL verankert universelles Spiritualitätsfundament.
# Geltungsstufen: GESPERRT / SPIRITUELL / GRUNDLEGEND_SPIRITUELL

from dataclasses import dataclass
from enum import Enum

from kki.glaubens_manifest import (
    GlaubensManifest,
    GlaubensManifestGeltung,
    build_glaubens_manifest,
)

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class SpiritualitaetsPaktGeltung(str, Enum):
    GESPERRT = "gesperrt"
    SPIRITUELL = "spirituell"
    GRUNDLEGEND_SPIRITUELL = "grundlegend-spirituell"


class SpiritualitaetsPaktTyp(str, Enum):
    SCHUTZ_SPIRITUALITAETSPAKT = "schutz-spiritualitaetspakt"
    ORDNUNGS_SPIRITUALITAETSPAKT = "ordnungs-spiritualitaetspakt"
    SOUVERAENITAETS_SPIRITUALITAETSPAKT = "souveraenitaets-spiritualitaetspakt"


class SpiritualitaetsPaktProzedur(str, Enum):
    SPIRITUALITAET_SITZUNG = "spiritualitaet-sitzung"
    SPIRITUALITAET_REGELPROTOKOLL = "spiritualitaet-regelprotokoll"
    SPIRITUALITAET_PLENARPROTOKOLL = "spiritualitaet-plenarprotokoll"


@dataclass(frozen=True)
class SpiritualitaetsPaktNorm:
    spiritualitaets_pakt_id: str
    religions_typ: SpiritualitaetsPaktTyp
    prozedur: SpiritualitaetsPaktProzedur
    geltung: SpiritualitaetsPaktGeltung
    religions_weight: float
    religions_tier: int
    canonical: bool
    religions_ids: tuple[str, ...]
    religions_tags: tuple[str, ...]


@dataclass(frozen=True)
class SpiritualitaetsPakt:
    pakt_id: str
    glaubens_manifest: GlaubensManifest
    normen: tuple[SpiritualitaetsPaktNorm, ...]


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        SpiritualitaetsPaktGeltung.GESPERRT: 0.0,
        SpiritualitaetsPaktGeltung.SPIRITUELL: 0.05,
        SpiritualitaetsPaktGeltung.GRUNDLEGEND_SPIRITUELL: 0.1,
    })
    _TIER_DELTA.update({
        SpiritualitaetsPaktGeltung.GESPERRT: 0,
        SpiritualitaetsPaktGeltung.SPIRITUELL: 1,
        SpiritualitaetsPaktGeltung.GRUNDLEGEND_SPIRITUELL: 2,
    })
    _TYP_MAP.update({
        SpiritualitaetsPaktGeltung.GESPERRT: SpiritualitaetsPaktTyp.SCHUTZ_SPIRITUALITAETSPAKT,
        SpiritualitaetsPaktGeltung.SPIRITUELL: SpiritualitaetsPaktTyp.ORDNUNGS_SPIRITUALITAETSPAKT,
        SpiritualitaetsPaktGeltung.GRUNDLEGEND_SPIRITUELL: SpiritualitaetsPaktTyp.SOUVERAENITAETS_SPIRITUALITAETSPAKT,
    })
    _PROZEDUR_MAP.update({
        SpiritualitaetsPaktGeltung.GESPERRT: SpiritualitaetsPaktProzedur.SPIRITUALITAET_SITZUNG,
        SpiritualitaetsPaktGeltung.SPIRITUELL: SpiritualitaetsPaktProzedur.SPIRITUALITAET_REGELPROTOKOLL,
        SpiritualitaetsPaktGeltung.GRUNDLEGEND_SPIRITUELL: SpiritualitaetsPaktProzedur.SPIRITUALITAET_PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        GlaubensManifestGeltung.GESPERRT: SpiritualitaetsPaktGeltung.GESPERRT,
        GlaubensManifestGeltung.GLAEUBIG: SpiritualitaetsPaktGeltung.SPIRITUELL,
        GlaubensManifestGeltung.GRUNDLEGEND_GLAEUBIG: SpiritualitaetsPaktGeltung.GRUNDLEGEND_SPIRITUELL,
    })


_init_map()


def build_spiritualitaets_pakt(
    glaubens_manifest: GlaubensManifest | None = None,
    *,
    pakt_id: str = "spiritualitaets-pakt",
) -> SpiritualitaetsPakt:
    if glaubens_manifest is None:
        glaubens_manifest = build_glaubens_manifest(manifest_id=f"{pakt_id}-glaubens-manifest")

    normen: list[SpiritualitaetsPaktNorm] = []
    for parent_norm in glaubens_manifest.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{pakt_id}-{parent_norm.glaubens_manifest_id.removeprefix(f'{glaubens_manifest.manifest_id}-')}"
        raw_weight = min(1.0, parent_norm.religions_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.religions_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SpiritualitaetsPaktGeltung.GRUNDLEGEND_SPIRITUELL)
        normen.append(
            SpiritualitaetsPaktNorm(
                spiritualitaets_pakt_id=new_id,
                religions_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                religions_weight=new_weight,
                religions_tier=new_tier,
                canonical=is_canonical,
                religions_ids=parent_norm.religions_ids + (new_id,),
                religions_tags=parent_norm.religions_tags + (f"spiritualitaets-pakt:{new_geltung.value}",),
            )
        )
    return SpiritualitaetsPakt(
        pakt_id=pakt_id,
        glaubens_manifest=glaubens_manifest,
        normen=tuple(normen),
    )
