"""
#350 FestkoerperVerfassung — Block-Krone: Festkörperphysik & Quantenmaterialien
als höchste Governance-Instanz. Vom Kristallgitter über Supraleitung und
Quanten-Hall-Effekt bis zum Bose-Einstein-Kondensat — Leitsterns Terra-Schwarm
erreicht maximale kollektive Quantenkohärenz und topologisch geschützte Ordnung.
Geltungsstufen: GESPERRT / FESTKOERPERVERFASST / GRUNDLEGEND_FESTKOERPERVERFASST
Parent: BoseEinsteinCharta (#349)
Block #341–#350 Krone
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bose_einstein_charta import (
    BoseEinsteinCharta,
    BoseEinsteinGeltung,
    build_bose_einstein_charta,
)

_GELTUNG_MAP: dict[BoseEinsteinGeltung, "FestkoerperVerfassungsGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[BoseEinsteinGeltung.GESPERRT] = FestkoerperVerfassungsGeltung.GESPERRT
    _GELTUNG_MAP[BoseEinsteinGeltung.BOSEEINSTEINKONDENSIERT] = FestkoerperVerfassungsGeltung.FESTKOERPERVERFASST
    _GELTUNG_MAP[BoseEinsteinGeltung.GRUNDLEGEND_BOSEEINSTEINKONDENSIERT] = FestkoerperVerfassungsGeltung.GRUNDLEGEND_FESTKOERPERVERFASST


class FestkoerperVerfassungsTyp(Enum):
    SCHUTZ_FESTKOERPERVERFASSUNG = "schutz-festkoerperverfassung"
    ORDNUNGS_FESTKOERPERVERFASSUNG = "ordnungs-festkoerperverfassung"
    SOUVERAENITAETS_FESTKOERPERVERFASSUNG = "souveraenitaets-festkoerperverfassung"


class FestkoerperVerfassungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class FestkoerperVerfassungsGeltung(Enum):
    GESPERRT = "gesperrt"
    FESTKOERPERVERFASST = "festkoerperverfasst"
    GRUNDLEGEND_FESTKOERPERVERFASST = "grundlegend-festkoerperverfasst"


_init_map()

_TYP_MAP: dict[FestkoerperVerfassungsGeltung, FestkoerperVerfassungsTyp] = {
    FestkoerperVerfassungsGeltung.GESPERRT: FestkoerperVerfassungsTyp.SCHUTZ_FESTKOERPERVERFASSUNG,
    FestkoerperVerfassungsGeltung.FESTKOERPERVERFASST: FestkoerperVerfassungsTyp.ORDNUNGS_FESTKOERPERVERFASSUNG,
    FestkoerperVerfassungsGeltung.GRUNDLEGEND_FESTKOERPERVERFASST: FestkoerperVerfassungsTyp.SOUVERAENITAETS_FESTKOERPERVERFASSUNG,
}

_PROZEDUR_MAP: dict[FestkoerperVerfassungsGeltung, FestkoerperVerfassungsProzedur] = {
    FestkoerperVerfassungsGeltung.GESPERRT: FestkoerperVerfassungsProzedur.NOTPROZEDUR,
    FestkoerperVerfassungsGeltung.FESTKOERPERVERFASST: FestkoerperVerfassungsProzedur.REGELPROTOKOLL,
    FestkoerperVerfassungsGeltung.GRUNDLEGEND_FESTKOERPERVERFASST: FestkoerperVerfassungsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[FestkoerperVerfassungsGeltung, float] = {
    FestkoerperVerfassungsGeltung.GESPERRT: 0.0,
    FestkoerperVerfassungsGeltung.FESTKOERPERVERFASST: 0.04,
    FestkoerperVerfassungsGeltung.GRUNDLEGEND_FESTKOERPERVERFASST: 0.08,
}

_TIER_DELTA: dict[FestkoerperVerfassungsGeltung, int] = {
    FestkoerperVerfassungsGeltung.GESPERRT: 0,
    FestkoerperVerfassungsGeltung.FESTKOERPERVERFASST: 1,
    FestkoerperVerfassungsGeltung.GRUNDLEGEND_FESTKOERPERVERFASST: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FestkoerperVerfassungsNorm:
    festkoerper_verfassung_id: str
    festkoerper_verfassungs_typ: FestkoerperVerfassungsTyp
    prozedur: FestkoerperVerfassungsProzedur
    geltung: FestkoerperVerfassungsGeltung
    festkoerper_verfassungs_weight: float
    festkoerper_verfassungs_tier: int
    canonical: bool
    festkoerper_verfassungs_ids: tuple[str, ...]
    festkoerper_verfassungs_tags: tuple[str, ...]


@dataclass(frozen=True)
class FestkoerperVerfassung:
    verfassung_id: str
    bose_einstein_charta: BoseEinsteinCharta
    normen: tuple[FestkoerperVerfassungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.festkoerper_verfassung_id for n in self.normen if n.geltung is FestkoerperVerfassungsGeltung.GESPERRT)

    @property
    def festkoerperverfasst_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.festkoerper_verfassung_id for n in self.normen if n.geltung is FestkoerperVerfassungsGeltung.FESTKOERPERVERFASST)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.festkoerper_verfassung_id for n in self.normen if n.geltung is FestkoerperVerfassungsGeltung.GRUNDLEGEND_FESTKOERPERVERFASST)

    @property
    def verfassung_signal(self):
        if any(n.geltung is FestkoerperVerfassungsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-gesperrt")
        elif any(n.geltung is FestkoerperVerfassungsGeltung.FESTKOERPERVERFASST for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-festkoerperverfasst")
        from types import SimpleNamespace
        return SimpleNamespace(status="verfassung-grundlegend-festkoerperverfasst")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_festkoerper_verfassung(
    bose_einstein_charta: BoseEinsteinCharta | None = None,
    *,
    verfassung_id: str = "festkoerper-verfassung",
) -> FestkoerperVerfassung:
    if bose_einstein_charta is None:
        bose_einstein_charta = build_bose_einstein_charta(charta_id=f"{verfassung_id}-charta")

    normen: list[FestkoerperVerfassungsNorm] = []
    for parent_norm in bose_einstein_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{verfassung_id}-{parent_norm.bose_einstein_charta_id.removeprefix(f'{bose_einstein_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.bose_einstein_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.bose_einstein_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is FestkoerperVerfassungsGeltung.GRUNDLEGEND_FESTKOERPERVERFASST)
        normen.append(
            FestkoerperVerfassungsNorm(
                festkoerper_verfassung_id=new_id,
                festkoerper_verfassungs_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                festkoerper_verfassungs_weight=new_weight,
                festkoerper_verfassungs_tier=new_tier,
                canonical=is_canonical,
                festkoerper_verfassungs_ids=parent_norm.bose_einstein_ids + (new_id,),
                festkoerper_verfassungs_tags=parent_norm.bose_einstein_tags + (f"festkoerper-verfassung:{new_geltung.value}",),
            )
        )
    return FestkoerperVerfassung(
        verfassung_id=verfassung_id,
        bose_einstein_charta=bose_einstein_charta,
        normen=tuple(normen),
    )
