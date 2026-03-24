from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from kki.syntax_kodex import SyntaxKodex, SyntaxKodexGeltung, build_syntax_kodex

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class SemantikManifestGeltung(str, Enum):
    GESPERRT = "gesperrt"
    SEMANTISCH = "semantisch"
    GRUNDLEGEND_SEMANTISCH = "grundlegend-semantisch"


class SemantikManifestTyp(str, Enum):
    SCHUTZ_SEMANTIKMANIFEST = "schutz-semantikmanifest"
    ORDNUNGS_SEMANTIKMANIFEST = "ordnungs-semantikmanifest"
    SOUVERAENITAETS_SEMANTIKMANIFEST = "souveraenitaets-semantikmanifest"


class SemantikManifestProzedur(str, Enum):
    SEMANTIKMANIFEST_ANALYSE = "semantikmanifest-analyse"
    SEMANTIKMANIFEST_INTEGRATION = "semantikmanifest-integration"
    SEMANTIKMANIFEST_SYNTHESE = "semantikmanifest-synthese"


@dataclass(frozen=True)
class SemantikManifestNorm:
    semantik_manifest_id: str
    linguistik_typ: SemantikManifestTyp
    prozedur: SemantikManifestProzedur
    geltung: SemantikManifestGeltung
    linguistik_weight: float
    linguistik_tier: int
    canonical: bool
    linguistik_ids: tuple[str, ...]
    linguistik_tags: tuple[str, ...]


@dataclass(frozen=True)
class SemantikManifest:
    manifest_id: str
    syntax_kodex: SyntaxKodex
    normen: tuple[SemantikManifestNorm, ...]


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        SemantikManifestGeltung.GESPERRT: 0.0,
        SemantikManifestGeltung.SEMANTISCH: 0.05,
        SemantikManifestGeltung.GRUNDLEGEND_SEMANTISCH: 0.1,
    })
    _TIER_DELTA.update({
        SemantikManifestGeltung.GESPERRT: 0,
        SemantikManifestGeltung.SEMANTISCH: 1,
        SemantikManifestGeltung.GRUNDLEGEND_SEMANTISCH: 2,
    })
    _TYP_MAP.update({
        SemantikManifestGeltung.GESPERRT: SemantikManifestTyp.SCHUTZ_SEMANTIKMANIFEST,
        SemantikManifestGeltung.SEMANTISCH: SemantikManifestTyp.ORDNUNGS_SEMANTIKMANIFEST,
        SemantikManifestGeltung.GRUNDLEGEND_SEMANTISCH: SemantikManifestTyp.SOUVERAENITAETS_SEMANTIKMANIFEST,
    })
    _PROZEDUR_MAP.update({
        SemantikManifestGeltung.GESPERRT: SemantikManifestProzedur.SEMANTIKMANIFEST_ANALYSE,
        SemantikManifestGeltung.SEMANTISCH: SemantikManifestProzedur.SEMANTIKMANIFEST_INTEGRATION,
        SemantikManifestGeltung.GRUNDLEGEND_SEMANTISCH: SemantikManifestProzedur.SEMANTIKMANIFEST_SYNTHESE,
    })
    _GELTUNG_MAP.update({
        SyntaxKodexGeltung.GESPERRT: SemantikManifestGeltung.GESPERRT,
        SyntaxKodexGeltung.SYNTAKTISCH: SemantikManifestGeltung.SEMANTISCH,
        SyntaxKodexGeltung.GRUNDLEGEND_SYNTAKTISCH: SemantikManifestGeltung.GRUNDLEGEND_SEMANTISCH,
    })


_init_map()


def build_semantik_manifest(
    syntax_kodex: SyntaxKodex | None = None,
    *,
    manifest_id: str = "semantik-manifest",
) -> SemantikManifest:
    if syntax_kodex is None:
        syntax_kodex = build_syntax_kodex(kodex_id=f"{manifest_id}-kodex")

    normen: list[SemantikManifestNorm] = []
    for parent_norm in syntax_kodex.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{manifest_id}-{parent_norm.syntax_kodex_id.removeprefix(f'{syntax_kodex.kodex_id}-')}"
        raw_weight = min(1.0, parent_norm.linguistik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.linguistik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SemantikManifestGeltung.GRUNDLEGEND_SEMANTISCH)
        normen.append(
            SemantikManifestNorm(
                semantik_manifest_id=new_id,
                linguistik_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                linguistik_weight=new_weight,
                linguistik_tier=new_tier,
                canonical=is_canonical,
                linguistik_ids=parent_norm.linguistik_ids + (new_id,),
                linguistik_tags=parent_norm.linguistik_tags + (f"semantik-manifest:{new_geltung.value}",),
            )
        )
    return SemantikManifest(
        manifest_id=manifest_id,
        syntax_kodex=syntax_kodex,
        normen=tuple(normen),
    )
