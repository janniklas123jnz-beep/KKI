from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from kki.semiotik_charta import SemiotikCharta, SemiotikChartaGeltung, build_semiotik_charta

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class SprachwissenschaftVerfassungGeltung(str, Enum):
    GESPERRT = "gesperrt"
    SPRACH_SOUVERAEN = "sprach-souveraen"
    GRUNDLEGEND_SPRACH_SOUVERAEN = "grundlegend-sprach-souveraen"


class SprachwissenschaftVerfassungTyp(str, Enum):
    SCHUTZ_SPRACHWISSENSCHAFT_VERFASSUNG = "schutz-sprachwissenschaft-verfassung"
    ORDNUNGS_SPRACHWISSENSCHAFT_VERFASSUNG = "ordnungs-sprachwissenschaft-verfassung"
    SOUVERAENITAETS_SPRACHWISSENSCHAFT_VERFASSUNG = "souveraenitaets-sprachwissenschaft-verfassung"


class SprachwissenschaftVerfassungProzedur(str, Enum):
    SPRACHWISSENSCHAFT_SITZUNG = "sprachwissenschaft-sitzung"
    SPRACHWISSENSCHAFT_REGELPROTOKOLL = "sprachwissenschaft-regelprotokoll"
    SPRACHWISSENSCHAFT_PLENARPROTOKOLL = "sprachwissenschaft-plenarprotokoll"


@dataclass(frozen=True)
class SprachwissenschaftVerfassungsNorm:
    sprachwissenschaft_verfassung_id: str
    linguistik_typ: SprachwissenschaftVerfassungTyp
    prozedur: SprachwissenschaftVerfassungProzedur
    geltung: SprachwissenschaftVerfassungGeltung
    linguistik_weight: float
    linguistik_tier: int
    canonical: bool
    linguistik_ids: tuple[str, ...]
    linguistik_tags: tuple[str, ...]


@dataclass(frozen=True)
class SprachwissenschaftVerfassung:
    verfassung_id: str
    semiotik_charta: SemiotikCharta
    normen: tuple[SprachwissenschaftVerfassungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.sprachwissenschaft_verfassung_id for n in self.normen if n.geltung is SprachwissenschaftVerfassungGeltung.GESPERRT)

    @property
    def sprach_souveraen_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.sprachwissenschaft_verfassung_id for n in self.normen if n.geltung is SprachwissenschaftVerfassungGeltung.SPRACH_SOUVERAEN)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.sprachwissenschaft_verfassung_id for n in self.normen if n.geltung is SprachwissenschaftVerfassungGeltung.GRUNDLEGEND_SPRACH_SOUVERAEN)

    def aggregates_verfassung_signal(self) -> float:
        return sum(n.linguistik_weight for n in self.normen if n.canonical)


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        SprachwissenschaftVerfassungGeltung.GESPERRT: 0.0,
        SprachwissenschaftVerfassungGeltung.SPRACH_SOUVERAEN: 0.05,
        SprachwissenschaftVerfassungGeltung.GRUNDLEGEND_SPRACH_SOUVERAEN: 0.1,
    })
    _TIER_DELTA.update({
        SprachwissenschaftVerfassungGeltung.GESPERRT: 0,
        SprachwissenschaftVerfassungGeltung.SPRACH_SOUVERAEN: 1,
        SprachwissenschaftVerfassungGeltung.GRUNDLEGEND_SPRACH_SOUVERAEN: 2,
    })
    _TYP_MAP.update({
        SprachwissenschaftVerfassungGeltung.GESPERRT: SprachwissenschaftVerfassungTyp.SCHUTZ_SPRACHWISSENSCHAFT_VERFASSUNG,
        SprachwissenschaftVerfassungGeltung.SPRACH_SOUVERAEN: SprachwissenschaftVerfassungTyp.ORDNUNGS_SPRACHWISSENSCHAFT_VERFASSUNG,
        SprachwissenschaftVerfassungGeltung.GRUNDLEGEND_SPRACH_SOUVERAEN: SprachwissenschaftVerfassungTyp.SOUVERAENITAETS_SPRACHWISSENSCHAFT_VERFASSUNG,
    })
    _PROZEDUR_MAP.update({
        SprachwissenschaftVerfassungGeltung.GESPERRT: SprachwissenschaftVerfassungProzedur.SPRACHWISSENSCHAFT_SITZUNG,
        SprachwissenschaftVerfassungGeltung.SPRACH_SOUVERAEN: SprachwissenschaftVerfassungProzedur.SPRACHWISSENSCHAFT_REGELPROTOKOLL,
        SprachwissenschaftVerfassungGeltung.GRUNDLEGEND_SPRACH_SOUVERAEN: SprachwissenschaftVerfassungProzedur.SPRACHWISSENSCHAFT_PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        SemiotikChartaGeltung.GESPERRT: SprachwissenschaftVerfassungGeltung.GESPERRT,
        SemiotikChartaGeltung.SEMIOTISCH_SOUVERAEN: SprachwissenschaftVerfassungGeltung.SPRACH_SOUVERAEN,
        SemiotikChartaGeltung.GRUNDLEGEND_SEMIOTISCH_SOUVERAEN: SprachwissenschaftVerfassungGeltung.GRUNDLEGEND_SPRACH_SOUVERAEN,
    })


_init_map()


def build_sprachwissenschaft_verfassung(
    semiotik_charta: SemiotikCharta | None = None,
    *,
    verfassung_id: str = "sprachwissenschaft-verfassung",
) -> SprachwissenschaftVerfassung:
    if semiotik_charta is None:
        semiotik_charta = build_semiotik_charta(charta_id=f"{verfassung_id}-charta")

    normen: list[SprachwissenschaftVerfassungsNorm] = []
    for parent_norm in semiotik_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{verfassung_id}-{parent_norm.semiotik_charta_id.removeprefix(f'{semiotik_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.linguistik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.linguistik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SprachwissenschaftVerfassungGeltung.GRUNDLEGEND_SPRACH_SOUVERAEN)
        normen.append(
            SprachwissenschaftVerfassungsNorm(
                sprachwissenschaft_verfassung_id=new_id,
                linguistik_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                linguistik_weight=new_weight,
                linguistik_tier=new_tier,
                canonical=is_canonical,
                linguistik_ids=parent_norm.linguistik_ids + (new_id,),
                linguistik_tags=parent_norm.linguistik_tags + (f"sprachwissenschaft-verfassung:{new_geltung.value}",),
            )
        )
    return SprachwissenschaftVerfassung(
        verfassung_id=verfassung_id,
        semiotik_charta=semiotik_charta,
        normen=tuple(normen),
    )
