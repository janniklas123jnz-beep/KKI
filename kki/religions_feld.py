from __future__ import annotations

# Leitsterns ReligionsFeld: GESPERRT schützt religiöse Grundprinzipien,
# RELIGIOES_SOUVERAEN aktiviert religiöse Souveränität,
# GRUNDLEGEND_RELIGIOES_SOUVERAEN verankert universelles Glaubensfundament.
# Geltungsstufen: GESPERRT / RELIGIOES_SOUVERAEN / GRUNDLEGEND_RELIGIOES_SOUVERAEN

from dataclasses import dataclass
from enum import Enum

from kki.sprachwissenschaft_verfassung import (
    SprachwissenschaftVerfassung,
    SprachwissenschaftVerfassungGeltung,
    build_sprachwissenschaft_verfassung,
)

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class ReligionsFeldGeltung(str, Enum):
    GESPERRT = "gesperrt"
    RELIGIOES_SOUVERAEN = "religioes-souveraen"
    GRUNDLEGEND_RELIGIOES_SOUVERAEN = "grundlegend-religioes-souveraen"


class ReligionsFeldTyp(str, Enum):
    SCHUTZ_RELIGIONSFELD = "schutz-religionsfeld"
    ORDNUNGS_RELIGIONSFELD = "ordnungs-religionsfeld"
    SOUVERAENITAETS_RELIGIONSFELD = "souveraenitaets-religionsfeld"


class ReligionsFeldProzedur(str, Enum):
    RELIGIONS_INITIIERUNG = "religions-initiierung"
    RELIGIONS_AKTIVIERUNG = "religions-aktivierung"
    RELIGIONS_VERANKERUNG = "religions-verankerung"


@dataclass(frozen=True)
class ReligionsFeldNorm:
    religions_feld_id: str
    religions_typ: ReligionsFeldTyp
    prozedur: ReligionsFeldProzedur
    geltung: ReligionsFeldGeltung
    religions_weight: float
    religions_tier: int
    canonical: bool
    religions_ids: tuple[str, ...]
    religions_tags: tuple[str, ...]


@dataclass(frozen=True)
class ReligionsFeld:
    feld_id: str
    sprachwissenschaft_verfassung: SprachwissenschaftVerfassung
    normen: tuple[ReligionsFeldNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.religions_feld_id for n in self.normen if n.geltung is ReligionsFeldGeltung.GESPERRT)

    @property
    def religioes_souveraen_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.religions_feld_id for n in self.normen if n.geltung is ReligionsFeldGeltung.RELIGIOES_SOUVERAEN)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.religions_feld_id for n in self.normen if n.geltung is ReligionsFeldGeltung.GRUNDLEGEND_RELIGIOES_SOUVERAEN)


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        ReligionsFeldGeltung.GESPERRT: 0.0,
        ReligionsFeldGeltung.RELIGIOES_SOUVERAEN: 0.05,
        ReligionsFeldGeltung.GRUNDLEGEND_RELIGIOES_SOUVERAEN: 0.1,
    })
    _TIER_DELTA.update({
        ReligionsFeldGeltung.GESPERRT: 0,
        ReligionsFeldGeltung.RELIGIOES_SOUVERAEN: 1,
        ReligionsFeldGeltung.GRUNDLEGEND_RELIGIOES_SOUVERAEN: 2,
    })
    _TYP_MAP.update({
        ReligionsFeldGeltung.GESPERRT: ReligionsFeldTyp.SCHUTZ_RELIGIONSFELD,
        ReligionsFeldGeltung.RELIGIOES_SOUVERAEN: ReligionsFeldTyp.ORDNUNGS_RELIGIONSFELD,
        ReligionsFeldGeltung.GRUNDLEGEND_RELIGIOES_SOUVERAEN: ReligionsFeldTyp.SOUVERAENITAETS_RELIGIONSFELD,
    })
    _PROZEDUR_MAP.update({
        ReligionsFeldGeltung.GESPERRT: ReligionsFeldProzedur.RELIGIONS_INITIIERUNG,
        ReligionsFeldGeltung.RELIGIOES_SOUVERAEN: ReligionsFeldProzedur.RELIGIONS_AKTIVIERUNG,
        ReligionsFeldGeltung.GRUNDLEGEND_RELIGIOES_SOUVERAEN: ReligionsFeldProzedur.RELIGIONS_VERANKERUNG,
    })
    _GELTUNG_MAP.update({
        SprachwissenschaftVerfassungGeltung.GESPERRT: ReligionsFeldGeltung.GESPERRT,
        SprachwissenschaftVerfassungGeltung.SPRACH_SOUVERAEN: ReligionsFeldGeltung.RELIGIOES_SOUVERAEN,
        SprachwissenschaftVerfassungGeltung.GRUNDLEGEND_SPRACH_SOUVERAEN: ReligionsFeldGeltung.GRUNDLEGEND_RELIGIOES_SOUVERAEN,
    })


_init_map()


def build_religions_feld(
    sprachwissenschaft_verfassung: SprachwissenschaftVerfassung | None = None,
    *,
    feld_id: str = "religions-feld",
) -> ReligionsFeld:
    if sprachwissenschaft_verfassung is None:
        sprachwissenschaft_verfassung = build_sprachwissenschaft_verfassung(
            verfassung_id=f"{feld_id}-verfassung"
        )

    normen: list[ReligionsFeldNorm] = []
    for parent_norm in sprachwissenschaft_verfassung.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{feld_id}-{parent_norm.sprachwissenschaft_verfassung_id.removeprefix(f'{sprachwissenschaft_verfassung.verfassung_id}-')}"
        raw_weight = min(1.0, parent_norm.linguistik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.linguistik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is ReligionsFeldGeltung.GRUNDLEGEND_RELIGIOES_SOUVERAEN)
        normen.append(
            ReligionsFeldNorm(
                religions_feld_id=new_id,
                religions_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                religions_weight=new_weight,
                religions_tier=new_tier,
                canonical=is_canonical,
                religions_ids=parent_norm.linguistik_ids + (new_id,),
                religions_tags=parent_norm.linguistik_tags + (f"religions-feld:{new_geltung.value}",),
            )
        )
    return ReligionsFeld(
        feld_id=feld_id,
        sprachwissenschaft_verfassung=sprachwissenschaft_verfassung,
        normen=tuple(normen),
    )
