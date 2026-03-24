from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from kki.sakrale_charta import SakraleCharta, SakraleChartaGeltung, build_sakrale_charta

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class ReligionswissenschaftVerfassungGeltung(str, Enum):
    GESPERRT = "gesperrt"
    RELWISS_SOUVERAEN = "relwiss-souveraen"
    GRUNDLEGEND_RELWISS_SOUVERAEN = "grundlegend-relwiss-souveraen"


class ReligionswissenschaftVerfassungTyp(str, Enum):
    SCHUTZ_RELIGIONSWISSENSCHAFT_VERFASSUNG = "schutz-religionswissenschaft-verfassung"
    ORDNUNGS_RELIGIONSWISSENSCHAFT_VERFASSUNG = "ordnungs-religionswissenschaft-verfassung"
    SOUVERAENITAETS_RELIGIONSWISSENSCHAFT_VERFASSUNG = "souveraenitaets-religionswissenschaft-verfassung"


class ReligionswissenschaftVerfassungProzedur(str, Enum):
    RELIGIONSWISSENSCHAFT_SITZUNG = "religionswissenschaft-sitzung"
    RELIGIONSWISSENSCHAFT_REGELPROTOKOLL = "religionswissenschaft-regelprotokoll"
    RELIGIONSWISSENSCHAFT_PLENARPROTOKOLL = "religionswissenschaft-plenarprotokoll"


@dataclass(frozen=True)
class ReligionswissenschaftVerfassungsNorm:
    religionswissenschaft_verfassung_id: str
    religions_typ: ReligionswissenschaftVerfassungTyp
    prozedur: ReligionswissenschaftVerfassungProzedur
    geltung: ReligionswissenschaftVerfassungGeltung
    religions_weight: float
    religions_tier: int
    canonical: bool
    religions_ids: tuple[str, ...]
    religions_tags: tuple[str, ...]


@dataclass(frozen=True)
class ReligionswissenschaftVerfassung:
    verfassung_id: str
    sakrale_charta: SakraleCharta
    normen: tuple[ReligionswissenschaftVerfassungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.religionswissenschaft_verfassung_id for n in self.normen if n.geltung is ReligionswissenschaftVerfassungGeltung.GESPERRT)

    @property
    def relwiss_souveraen_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.religionswissenschaft_verfassung_id for n in self.normen if n.geltung is ReligionswissenschaftVerfassungGeltung.RELWISS_SOUVERAEN)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.religionswissenschaft_verfassung_id for n in self.normen if n.geltung is ReligionswissenschaftVerfassungGeltung.GRUNDLEGEND_RELWISS_SOUVERAEN)

    def aggregates_verfassung_signal(self) -> dict:
        return {
            "verfassung_id": self.verfassung_id,
            "total_weight": sum(n.religions_weight for n in self.normen if n.canonical),
            "norm_count": len(self.normen),
        }


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        ReligionswissenschaftVerfassungGeltung.GESPERRT: 0.0,
        ReligionswissenschaftVerfassungGeltung.RELWISS_SOUVERAEN: 0.05,
        ReligionswissenschaftVerfassungGeltung.GRUNDLEGEND_RELWISS_SOUVERAEN: 0.1,
    })
    _TIER_DELTA.update({
        ReligionswissenschaftVerfassungGeltung.GESPERRT: 0,
        ReligionswissenschaftVerfassungGeltung.RELWISS_SOUVERAEN: 1,
        ReligionswissenschaftVerfassungGeltung.GRUNDLEGEND_RELWISS_SOUVERAEN: 2,
    })
    _TYP_MAP.update({
        ReligionswissenschaftVerfassungGeltung.GESPERRT: ReligionswissenschaftVerfassungTyp.SCHUTZ_RELIGIONSWISSENSCHAFT_VERFASSUNG,
        ReligionswissenschaftVerfassungGeltung.RELWISS_SOUVERAEN: ReligionswissenschaftVerfassungTyp.ORDNUNGS_RELIGIONSWISSENSCHAFT_VERFASSUNG,
        ReligionswissenschaftVerfassungGeltung.GRUNDLEGEND_RELWISS_SOUVERAEN: ReligionswissenschaftVerfassungTyp.SOUVERAENITAETS_RELIGIONSWISSENSCHAFT_VERFASSUNG,
    })
    _PROZEDUR_MAP.update({
        ReligionswissenschaftVerfassungGeltung.GESPERRT: ReligionswissenschaftVerfassungProzedur.RELIGIONSWISSENSCHAFT_SITZUNG,
        ReligionswissenschaftVerfassungGeltung.RELWISS_SOUVERAEN: ReligionswissenschaftVerfassungProzedur.RELIGIONSWISSENSCHAFT_REGELPROTOKOLL,
        ReligionswissenschaftVerfassungGeltung.GRUNDLEGEND_RELWISS_SOUVERAEN: ReligionswissenschaftVerfassungProzedur.RELIGIONSWISSENSCHAFT_PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        SakraleChartaGeltung.GESPERRT: ReligionswissenschaftVerfassungGeltung.GESPERRT,
        SakraleChartaGeltung.SAKRAL_SOUVERAEN: ReligionswissenschaftVerfassungGeltung.RELWISS_SOUVERAEN,
        SakraleChartaGeltung.GRUNDLEGEND_SAKRAL_SOUVERAEN: ReligionswissenschaftVerfassungGeltung.GRUNDLEGEND_RELWISS_SOUVERAEN,
    })


_init_map()


def build_religionswissenschaft_verfassung(
    sakrale_charta: SakraleCharta | None = None,
    *,
    verfassung_id: str = "religionswissenschaft-verfassung",
) -> ReligionswissenschaftVerfassung:
    if sakrale_charta is None:
        sakrale_charta = build_sakrale_charta(charta_id=f"{verfassung_id}-charta")

    normen: list[ReligionswissenschaftVerfassungsNorm] = []
    for parent_norm in sakrale_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{verfassung_id}-{parent_norm.sakrale_charta_id.removeprefix(f'{sakrale_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.religions_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.religions_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is ReligionswissenschaftVerfassungGeltung.GRUNDLEGEND_RELWISS_SOUVERAEN)
        normen.append(
            ReligionswissenschaftVerfassungsNorm(
                religionswissenschaft_verfassung_id=new_id,
                religions_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                religions_weight=new_weight,
                religions_tier=new_tier,
                canonical=is_canonical,
                religions_ids=parent_norm.religions_ids + (new_id,),
                religions_tags=parent_norm.religions_tags + (f"religionswissenschaft-verfassung:{new_geltung.value}",),
            )
        )
    return ReligionswissenschaftVerfassung(
        verfassung_id=verfassung_id,
        sakrale_charta=sakrale_charta,
        normen=tuple(normen),
    )
