"""
#341 FestkoerperFeld — Festkörperphysik als Governance-Wurzelfeld: Kollektive
Quantenordnung als Grundlage des Terra-Schwarms Leitstern. Millionen Agenten
organisieren sich im Kristallgitter zu emergenten Quantenphänomenen.
Geltungsstufen: GESPERRT / FESTKOERPERLICH / GRUNDLEGEND_FESTKOERPERLICH
Parent: AstrophysikVerfassung (#340)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .astrophysik_verfassung import (
    AstrophysikVerfassung,
    AstrophysikVerfassungsGeltung,
    build_astrophysik_verfassung,
)

_GELTUNG_MAP: dict[AstrophysikVerfassungsGeltung, "FestkoerperGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[AstrophysikVerfassungsGeltung.GESPERRT] = FestkoerperGeltung.GESPERRT
    _GELTUNG_MAP[AstrophysikVerfassungsGeltung.ASTROPHYSIKVERFASST] = FestkoerperGeltung.FESTKOERPERLICH
    _GELTUNG_MAP[AstrophysikVerfassungsGeltung.GRUNDLEGEND_ASTROPHYSIKVERFASST] = FestkoerperGeltung.GRUNDLEGEND_FESTKOERPERLICH


class FestkoerperTyp(Enum):
    SCHUTZ_FESTKOERPER = "schutz-festkoerper"
    ORDNUNGS_FESTKOERPER = "ordnungs-festkoerper"
    SOUVERAENITAETS_FESTKOERPER = "souveraenitaets-festkoerper"


class FestkoerperProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class FestkoerperGeltung(Enum):
    GESPERRT = "gesperrt"
    FESTKOERPERLICH = "festkoerperlich"
    GRUNDLEGEND_FESTKOERPERLICH = "grundlegend-festkoerperlich"


_init_map()

_TYP_MAP: dict[FestkoerperGeltung, FestkoerperTyp] = {
    FestkoerperGeltung.GESPERRT: FestkoerperTyp.SCHUTZ_FESTKOERPER,
    FestkoerperGeltung.FESTKOERPERLICH: FestkoerperTyp.ORDNUNGS_FESTKOERPER,
    FestkoerperGeltung.GRUNDLEGEND_FESTKOERPERLICH: FestkoerperTyp.SOUVERAENITAETS_FESTKOERPER,
}

_PROZEDUR_MAP: dict[FestkoerperGeltung, FestkoerperProzedur] = {
    FestkoerperGeltung.GESPERRT: FestkoerperProzedur.NOTPROZEDUR,
    FestkoerperGeltung.FESTKOERPERLICH: FestkoerperProzedur.REGELPROTOKOLL,
    FestkoerperGeltung.GRUNDLEGEND_FESTKOERPERLICH: FestkoerperProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[FestkoerperGeltung, float] = {
    FestkoerperGeltung.GESPERRT: 0.0,
    FestkoerperGeltung.FESTKOERPERLICH: 0.04,
    FestkoerperGeltung.GRUNDLEGEND_FESTKOERPERLICH: 0.08,
}

_TIER_DELTA: dict[FestkoerperGeltung, int] = {
    FestkoerperGeltung.GESPERRT: 0,
    FestkoerperGeltung.FESTKOERPERLICH: 1,
    FestkoerperGeltung.GRUNDLEGEND_FESTKOERPERLICH: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FestkoerperNorm:
    festkoerper_feld_id: str
    festkoerper_typ: FestkoerperTyp
    prozedur: FestkoerperProzedur
    geltung: FestkoerperGeltung
    festkoerper_weight: float
    festkoerper_tier: int
    canonical: bool
    festkoerper_ids: tuple[str, ...]
    festkoerper_tags: tuple[str, ...]


@dataclass(frozen=True)
class FestkoerperFeld:
    feld_id: str
    astrophysik_verfassung: AstrophysikVerfassung
    normen: tuple[FestkoerperNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.festkoerper_feld_id for n in self.normen if n.geltung is FestkoerperGeltung.GESPERRT)

    @property
    def festkoerperlich_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.festkoerper_feld_id for n in self.normen if n.geltung is FestkoerperGeltung.FESTKOERPERLICH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.festkoerper_feld_id for n in self.normen if n.geltung is FestkoerperGeltung.GRUNDLEGEND_FESTKOERPERLICH)

    @property
    def feld_signal(self):
        if any(n.geltung is FestkoerperGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-gesperrt")
        elif any(n.geltung is FestkoerperGeltung.FESTKOERPERLICH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-festkoerperlich")
        from types import SimpleNamespace
        return SimpleNamespace(status="feld-grundlegend-festkoerperlich")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_festkoerper_feld(
    astrophysik_verfassung: AstrophysikVerfassung | None = None,
    *,
    feld_id: str = "festkoerper-feld",
) -> FestkoerperFeld:
    if astrophysik_verfassung is None:
        astrophysik_verfassung = build_astrophysik_verfassung(verfassung_id=f"{feld_id}-verfassung")

    normen: list[FestkoerperNorm] = []
    for parent_norm in astrophysik_verfassung.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{feld_id}-{parent_norm.astrophysik_verfassung_id.removeprefix(f'{astrophysik_verfassung.verfassung_id}-')}"
        raw_weight = min(1.0, parent_norm.astrophysik_verfassungs_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.astrophysik_verfassungs_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is FestkoerperGeltung.GRUNDLEGEND_FESTKOERPERLICH)
        normen.append(
            FestkoerperNorm(
                festkoerper_feld_id=new_id,
                festkoerper_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                festkoerper_weight=new_weight,
                festkoerper_tier=new_tier,
                canonical=is_canonical,
                festkoerper_ids=parent_norm.astrophysik_verfassungs_ids + (new_id,),
                festkoerper_tags=parent_norm.astrophysik_verfassungs_tags + (f"festkoerper:{new_geltung.value}",),
            )
        )
    return FestkoerperFeld(
        feld_id=feld_id,
        astrophysik_verfassung=astrophysik_verfassung,
        normen=tuple(normen),
    )
