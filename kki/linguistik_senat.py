from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from kki.diskurs_pakt import PragmatikPakt, PragmatikPaktGeltung, build_pragmatik_pakt

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class LinguistikSenatGeltung(str, Enum):
    GESPERRT = "gesperrt"
    LINGUISTISCH_SENATORISCH = "linguistisch-senatorisch"
    GRUNDLEGEND_LINGUISTISCH_SENATORISCH = "grundlegend-linguistisch-senatorisch"


class LinguistikSenatTyp(str, Enum):
    SCHUTZ_LINGUISTIKSENAT = "schutz-linguistiksenat"
    ORDNUNGS_LINGUISTIKSENAT = "ordnungs-linguistiksenat"
    SOUVERAENITAETS_LINGUISTIKSENAT = "souveraenitaets-linguistiksenat"


class LinguistikSenatProzedur(str, Enum):
    LINGUISTIKSENAT_ANALYSE = "linguistiksenat-analyse"
    LINGUISTIKSENAT_INTEGRATION = "linguistiksenat-integration"
    LINGUISTIKSENAT_SYNTHESE = "linguistiksenat-synthese"


@dataclass(frozen=True)
class LinguistikSenatNorm:
    linguistik_senat_id: str
    linguistik_typ: LinguistikSenatTyp
    prozedur: LinguistikSenatProzedur
    geltung: LinguistikSenatGeltung
    linguistik_weight: float
    linguistik_tier: int
    canonical: bool
    linguistik_ids: tuple[str, ...]
    linguistik_tags: tuple[str, ...]


@dataclass(frozen=True)
class LinguistikSenat:
    senat_id: str
    pragmatik_pakt: PragmatikPakt
    normen: tuple[LinguistikSenatNorm, ...]


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        LinguistikSenatGeltung.GESPERRT: 0.0,
        LinguistikSenatGeltung.LINGUISTISCH_SENATORISCH: 0.05,
        LinguistikSenatGeltung.GRUNDLEGEND_LINGUISTISCH_SENATORISCH: 0.1,
    })
    _TIER_DELTA.update({
        LinguistikSenatGeltung.GESPERRT: 0,
        LinguistikSenatGeltung.LINGUISTISCH_SENATORISCH: 1,
        LinguistikSenatGeltung.GRUNDLEGEND_LINGUISTISCH_SENATORISCH: 2,
    })
    _TYP_MAP.update({
        LinguistikSenatGeltung.GESPERRT: LinguistikSenatTyp.SCHUTZ_LINGUISTIKSENAT,
        LinguistikSenatGeltung.LINGUISTISCH_SENATORISCH: LinguistikSenatTyp.ORDNUNGS_LINGUISTIKSENAT,
        LinguistikSenatGeltung.GRUNDLEGEND_LINGUISTISCH_SENATORISCH: LinguistikSenatTyp.SOUVERAENITAETS_LINGUISTIKSENAT,
    })
    _PROZEDUR_MAP.update({
        LinguistikSenatGeltung.GESPERRT: LinguistikSenatProzedur.LINGUISTIKSENAT_ANALYSE,
        LinguistikSenatGeltung.LINGUISTISCH_SENATORISCH: LinguistikSenatProzedur.LINGUISTIKSENAT_INTEGRATION,
        LinguistikSenatGeltung.GRUNDLEGEND_LINGUISTISCH_SENATORISCH: LinguistikSenatProzedur.LINGUISTIKSENAT_SYNTHESE,
    })
    _GELTUNG_MAP.update({
        PragmatikPaktGeltung.GESPERRT: LinguistikSenatGeltung.GESPERRT,
        PragmatikPaktGeltung.PRAGMATISCH: LinguistikSenatGeltung.LINGUISTISCH_SENATORISCH,
        PragmatikPaktGeltung.GRUNDLEGEND_PRAGMATISCH: LinguistikSenatGeltung.GRUNDLEGEND_LINGUISTISCH_SENATORISCH,
    })


_init_map()


def build_linguistik_senat(
    pragmatik_pakt: PragmatikPakt | None = None,
    *,
    senat_id: str = "linguistik-senat",
) -> LinguistikSenat:
    if pragmatik_pakt is None:
        pragmatik_pakt = build_pragmatik_pakt(pakt_id=f"{senat_id}-pakt")

    normen: list[LinguistikSenatNorm] = []
    for parent_norm in pragmatik_pakt.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{senat_id}-{parent_norm.pragmatik_pakt_id.removeprefix(f'{pragmatik_pakt.pakt_id}-')}"
        raw_weight = min(1.0, parent_norm.linguistik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.linguistik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is LinguistikSenatGeltung.GRUNDLEGEND_LINGUISTISCH_SENATORISCH)
        normen.append(
            LinguistikSenatNorm(
                linguistik_senat_id=new_id,
                linguistik_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                linguistik_weight=new_weight,
                linguistik_tier=new_tier,
                canonical=is_canonical,
                linguistik_ids=parent_norm.linguistik_ids + (new_id,),
                linguistik_tags=parent_norm.linguistik_tags + (f"linguistik-senat:{new_geltung.value}",),
            )
        )
    return LinguistikSenat(
        senat_id=senat_id,
        pragmatik_pakt=pragmatik_pakt,
        normen=tuple(normen),
    )
