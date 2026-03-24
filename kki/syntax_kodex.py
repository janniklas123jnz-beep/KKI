from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from kki.morphologie_charta import MorphologieCharta, MorphologieChartaGeltung, build_morphologie_charta

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class SyntaxKodexGeltung(str, Enum):
    GESPERRT = "gesperrt"
    SYNTAKTISCH = "syntaktisch"
    GRUNDLEGEND_SYNTAKTISCH = "grundlegend-syntaktisch"


class SyntaxKodexTyp(str, Enum):
    SCHUTZ_SYNTAXKODEX = "schutz-syntaxkodex"
    ORDNUNGS_SYNTAXKODEX = "ordnungs-syntaxkodex"
    SOUVERAENITAETS_SYNTAXKODEX = "souveraenitaets-syntaxkodex"


class SyntaxKodexProzedur(str, Enum):
    SYNTAXKODEX_ANALYSE = "syntaxkodex-analyse"
    SYNTAXKODEX_INTEGRATION = "syntaxkodex-integration"
    SYNTAXKODEX_SYNTHESE = "syntaxkodex-synthese"


@dataclass(frozen=True)
class SyntaxKodexNorm:
    syntax_kodex_id: str
    linguistik_typ: SyntaxKodexTyp
    prozedur: SyntaxKodexProzedur
    geltung: SyntaxKodexGeltung
    linguistik_weight: float
    linguistik_tier: int
    canonical: bool
    linguistik_ids: tuple[str, ...]
    linguistik_tags: tuple[str, ...]


@dataclass(frozen=True)
class SyntaxKodex:
    kodex_id: str
    morphologie_charta: MorphologieCharta
    normen: tuple[SyntaxKodexNorm, ...]


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        SyntaxKodexGeltung.GESPERRT: 0.0,
        SyntaxKodexGeltung.SYNTAKTISCH: 0.05,
        SyntaxKodexGeltung.GRUNDLEGEND_SYNTAKTISCH: 0.1,
    })
    _TIER_DELTA.update({
        SyntaxKodexGeltung.GESPERRT: 0,
        SyntaxKodexGeltung.SYNTAKTISCH: 1,
        SyntaxKodexGeltung.GRUNDLEGEND_SYNTAKTISCH: 2,
    })
    _TYP_MAP.update({
        SyntaxKodexGeltung.GESPERRT: SyntaxKodexTyp.SCHUTZ_SYNTAXKODEX,
        SyntaxKodexGeltung.SYNTAKTISCH: SyntaxKodexTyp.ORDNUNGS_SYNTAXKODEX,
        SyntaxKodexGeltung.GRUNDLEGEND_SYNTAKTISCH: SyntaxKodexTyp.SOUVERAENITAETS_SYNTAXKODEX,
    })
    _PROZEDUR_MAP.update({
        SyntaxKodexGeltung.GESPERRT: SyntaxKodexProzedur.SYNTAXKODEX_ANALYSE,
        SyntaxKodexGeltung.SYNTAKTISCH: SyntaxKodexProzedur.SYNTAXKODEX_INTEGRATION,
        SyntaxKodexGeltung.GRUNDLEGEND_SYNTAKTISCH: SyntaxKodexProzedur.SYNTAXKODEX_SYNTHESE,
    })
    _GELTUNG_MAP.update({
        MorphologieChartaGeltung.GESPERRT: SyntaxKodexGeltung.GESPERRT,
        MorphologieChartaGeltung.MORPHOLOGISCH: SyntaxKodexGeltung.SYNTAKTISCH,
        MorphologieChartaGeltung.GRUNDLEGEND_MORPHOLOGISCH: SyntaxKodexGeltung.GRUNDLEGEND_SYNTAKTISCH,
    })


_init_map()


def build_syntax_kodex(
    morphologie_charta: MorphologieCharta | None = None,
    *,
    kodex_id: str = "syntax-kodex",
) -> SyntaxKodex:
    if morphologie_charta is None:
        morphologie_charta = build_morphologie_charta(charta_id=f"{kodex_id}-charta")

    normen: list[SyntaxKodexNorm] = []
    for parent_norm in morphologie_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{kodex_id}-{parent_norm.morphologie_charta_id.removeprefix(f'{morphologie_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.linguistik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.linguistik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SyntaxKodexGeltung.GRUNDLEGEND_SYNTAKTISCH)
        normen.append(
            SyntaxKodexNorm(
                syntax_kodex_id=new_id,
                linguistik_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                linguistik_weight=new_weight,
                linguistik_tier=new_tier,
                canonical=is_canonical,
                linguistik_ids=parent_norm.linguistik_ids + (new_id,),
                linguistik_tags=parent_norm.linguistik_tags + (f"syntax-kodex:{new_geltung.value}",),
            )
        )
    return SyntaxKodex(
        kodex_id=kodex_id,
        morphologie_charta=morphologie_charta,
        normen=tuple(normen),
    )
