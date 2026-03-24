from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .linguistik_norm import LinguistikNormGeltung, LinguistikNormSatz, build_linguistik_norm

_WEIGHT_DELTA: dict["SemiotikChartaGeltung", float] = {}
_TIER_DELTA: dict["SemiotikChartaGeltung", int] = {}
_TYP_MAP: dict["SemiotikChartaGeltung", "SemiotikChartaTyp"] = {}
_PROZEDUR_MAP: dict["SemiotikChartaGeltung", "SemiotikChartaProzedur"] = {}
_GELTUNG_MAP: dict[LinguistikNormGeltung, "SemiotikChartaGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        SemiotikChartaGeltung.GESPERRT: 0.0,
        SemiotikChartaGeltung.SEMIOTISCH_SOUVERAEN: 0.05,
        SemiotikChartaGeltung.GRUNDLEGEND_SEMIOTISCH_SOUVERAEN: 0.1,
    })
    _TIER_DELTA.update({
        SemiotikChartaGeltung.GESPERRT: 0,
        SemiotikChartaGeltung.SEMIOTISCH_SOUVERAEN: 1,
        SemiotikChartaGeltung.GRUNDLEGEND_SEMIOTISCH_SOUVERAEN: 2,
    })
    _TYP_MAP.update({
        SemiotikChartaGeltung.GESPERRT: SemiotikChartaTyp.SCHUTZ_SEMIOTIKCHARTA,
        SemiotikChartaGeltung.SEMIOTISCH_SOUVERAEN: SemiotikChartaTyp.ORDNUNGS_SEMIOTIKCHARTA,
        SemiotikChartaGeltung.GRUNDLEGEND_SEMIOTISCH_SOUVERAEN: SemiotikChartaTyp.SOUVERAENITAETS_SEMIOTIKCHARTA,
    })
    _PROZEDUR_MAP.update({
        SemiotikChartaGeltung.GESPERRT: SemiotikChartaProzedur.NOTPROZEDUR,
        SemiotikChartaGeltung.SEMIOTISCH_SOUVERAEN: SemiotikChartaProzedur.REGELPROTOKOLL,
        SemiotikChartaGeltung.GRUNDLEGEND_SEMIOTISCH_SOUVERAEN: SemiotikChartaProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        LinguistikNormGeltung.GESPERRT: SemiotikChartaGeltung.GESPERRT,
        LinguistikNormGeltung.LINGUISTISCH_NORMATIV: SemiotikChartaGeltung.SEMIOTISCH_SOUVERAEN,
        LinguistikNormGeltung.GRUNDLEGEND_LINGUISTISCH_NORMATIV: SemiotikChartaGeltung.GRUNDLEGEND_SEMIOTISCH_SOUVERAEN,
    })


class SemiotikChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    SEMIOTISCH_SOUVERAEN = "semiotisch-souverän"
    GRUNDLEGEND_SEMIOTISCH_SOUVERAEN = "grundlegend-semiotisch-souverän"


class SemiotikChartaTyp(Enum):
    SCHUTZ_SEMIOTIKCHARTA = "schutz-semiotikcharta"
    ORDNUNGS_SEMIOTIKCHARTA = "ordnungs-semiotikcharta"
    SOUVERAENITAETS_SEMIOTIKCHARTA = "souveraenitaets-semiotikcharta"


class SemiotikChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class SemiotikChartaNorm:
    semiotik_charta_id: str
    linguistik_typ: SemiotikChartaTyp
    prozedur: SemiotikChartaProzedur
    geltung: SemiotikChartaGeltung
    linguistik_weight: float
    linguistik_tier: int
    canonical: bool
    linguistik_ids: tuple[str, ...]
    linguistik_tags: tuple[str, ...]


@dataclass(frozen=True)
class SemiotikCharta:
    charta_id: str
    linguistik_norm: LinguistikNormSatz
    normen: tuple[SemiotikChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.semiotik_charta_id for n in self.normen if n.geltung is SemiotikChartaGeltung.GESPERRT)

    @property
    def semiotisch_souveraen_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.semiotik_charta_id for n in self.normen if n.geltung is SemiotikChartaGeltung.SEMIOTISCH_SOUVERAEN)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.semiotik_charta_id for n in self.normen if n.geltung is SemiotikChartaGeltung.GRUNDLEGEND_SEMIOTISCH_SOUVERAEN)

    @property
    def charta_signal(self):
        if any(n.geltung is SemiotikChartaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is SemiotikChartaGeltung.SEMIOTISCH_SOUVERAEN for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-semiotisch-souveraen")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-semiotisch-souveraen")


_init_map()


def build_semiotik_charta(
    linguistik_norm: LinguistikNormSatz | None = None,
    *,
    charta_id: str = "semiotik-charta",
) -> SemiotikCharta:
    if linguistik_norm is None:
        linguistik_norm = build_linguistik_norm(norm_id=f"{charta_id}-norm")

    normen: list[SemiotikChartaNorm] = []
    for parent_norm in linguistik_norm.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.norm_id.removeprefix(f'{linguistik_norm.norm_id}-')}"
        raw_weight = min(1.0, parent_norm.linguistik_norm_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.linguistik_norm_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SemiotikChartaGeltung.GRUNDLEGEND_SEMIOTISCH_SOUVERAEN)
        normen.append(
            SemiotikChartaNorm(
                semiotik_charta_id=new_id,
                linguistik_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                linguistik_weight=new_weight,
                linguistik_tier=new_tier,
                canonical=is_canonical,
                linguistik_ids=parent_norm.linguistik_norm_ids + (new_id,),
                linguistik_tags=parent_norm.linguistik_norm_tags + (f"semiotik-charta:{new_geltung.value}",),
            )
        )
    return SemiotikCharta(
        charta_id=charta_id,
        linguistik_norm=linguistik_norm,
        normen=tuple(normen),
    )
