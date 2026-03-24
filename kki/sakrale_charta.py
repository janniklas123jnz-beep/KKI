from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from kki.religions_norm import ReligionsNormSatz, ReligionsNormGeltung, build_religions_norm

_WEIGHT_DELTA: dict = {}
_TIER_DELTA: dict = {}
_TYP_MAP: dict = {}
_PROZEDUR_MAP: dict = {}
_GELTUNG_MAP: dict = {}


class SakraleChartaGeltung(str, Enum):
    GESPERRT = "gesperrt"
    SAKRAL_SOUVERAEN = "sakral-souveraen"
    GRUNDLEGEND_SAKRAL_SOUVERAEN = "grundlegend-sakral-souveraen"


class SakraleChartaTyp(str, Enum):
    SCHUTZ_SAKRALECHARTA = "schutz-sakralecharta"
    ORDNUNGS_SAKRALECHARTA = "ordnungs-sakralecharta"
    SOUVERAENITAETS_SAKRALECHARTA = "souveraenitaets-sakralecharta"


class SakraleChartaProzedur(str, Enum):
    SAKRAL_SITZUNG = "sakral-sitzung"
    SAKRAL_REGELPROTOKOLL = "sakral-regelprotokoll"
    SAKRAL_PLENARPROTOKOLL = "sakral-plenarprotokoll"


@dataclass(frozen=True)
class SakraleChartaNorm:
    sakrale_charta_id: str
    religions_typ: SakraleChartaTyp
    prozedur: SakraleChartaProzedur
    geltung: SakraleChartaGeltung
    religions_weight: float
    religions_tier: int
    canonical: bool
    religions_ids: tuple[str, ...]
    religions_tags: tuple[str, ...]


@dataclass(frozen=True)
class SakraleCharta:
    charta_id: str
    religions_norm: ReligionsNormSatz
    normen: tuple[SakraleChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.sakrale_charta_id for n in self.normen if n.geltung is SakraleChartaGeltung.GESPERRT)

    @property
    def sakral_souveraen_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.sakrale_charta_id for n in self.normen if n.geltung is SakraleChartaGeltung.SAKRAL_SOUVERAEN)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.sakrale_charta_id for n in self.normen if n.geltung is SakraleChartaGeltung.GRUNDLEGEND_SAKRAL_SOUVERAEN)


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        SakraleChartaGeltung.GESPERRT: 0.0,
        SakraleChartaGeltung.SAKRAL_SOUVERAEN: 0.05,
        SakraleChartaGeltung.GRUNDLEGEND_SAKRAL_SOUVERAEN: 0.1,
    })
    _TIER_DELTA.update({
        SakraleChartaGeltung.GESPERRT: 0,
        SakraleChartaGeltung.SAKRAL_SOUVERAEN: 1,
        SakraleChartaGeltung.GRUNDLEGEND_SAKRAL_SOUVERAEN: 2,
    })
    _TYP_MAP.update({
        SakraleChartaGeltung.GESPERRT: SakraleChartaTyp.SCHUTZ_SAKRALECHARTA,
        SakraleChartaGeltung.SAKRAL_SOUVERAEN: SakraleChartaTyp.ORDNUNGS_SAKRALECHARTA,
        SakraleChartaGeltung.GRUNDLEGEND_SAKRAL_SOUVERAEN: SakraleChartaTyp.SOUVERAENITAETS_SAKRALECHARTA,
    })
    _PROZEDUR_MAP.update({
        SakraleChartaGeltung.GESPERRT: SakraleChartaProzedur.SAKRAL_SITZUNG,
        SakraleChartaGeltung.SAKRAL_SOUVERAEN: SakraleChartaProzedur.SAKRAL_REGELPROTOKOLL,
        SakraleChartaGeltung.GRUNDLEGEND_SAKRAL_SOUVERAEN: SakraleChartaProzedur.SAKRAL_PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        ReligionsNormGeltung.GESPERRT: SakraleChartaGeltung.GESPERRT,
        ReligionsNormGeltung.RELIGIOES_NORMATIV: SakraleChartaGeltung.SAKRAL_SOUVERAEN,
        ReligionsNormGeltung.GRUNDLEGEND_RELIGIOES_NORMATIV: SakraleChartaGeltung.GRUNDLEGEND_SAKRAL_SOUVERAEN,
    })


_init_map()


def build_sakrale_charta(
    religions_norm: ReligionsNormSatz | None = None,
    *,
    charta_id: str = "sakrale-charta",
) -> SakraleCharta:
    if religions_norm is None:
        religions_norm = build_religions_norm(norm_id=f"{charta_id}-norm")

    normen: list[SakraleChartaNorm] = []
    for parent_norm in religions_norm.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.norm_id.removeprefix(f'{religions_norm.norm_id}-')}"
        raw_weight = min(1.0, parent_norm.religions_norm_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.religions_norm_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SakraleChartaGeltung.GRUNDLEGEND_SAKRAL_SOUVERAEN)
        normen.append(
            SakraleChartaNorm(
                sakrale_charta_id=new_id,
                religions_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                religions_weight=new_weight,
                religions_tier=new_tier,
                canonical=is_canonical,
                religions_ids=parent_norm.religions_norm_ids + (new_id,),
                religions_tags=parent_norm.religions_norm_tags + (f"sakrale-charta:{new_geltung.value}",),
            )
        )
    return SakraleCharta(
        charta_id=charta_id,
        religions_norm=religions_norm,
        normen=tuple(normen),
    )
