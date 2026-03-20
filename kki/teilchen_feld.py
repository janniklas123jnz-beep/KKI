"""
#311 TeilchenFeld — Teilchenfelder als Governance-Wurzel des Teilchenphysik-Blocks.
Geltungsstufen: GESPERRT / TEILCHENGEBUNDEN / GRUNDLEGEND_TEILCHENGEBUNDEN
Parent: KernphysikVerfassung (#310)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kernphysik_verfassung import (
    KernphysikVerfassung,
    KernphysikVerfassungsGeltung,
    build_kernphysik_verfassung,
)

_GELTUNG_MAP: dict[KernphysikVerfassungsGeltung, "TeilchenGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[KernphysikVerfassungsGeltung.GESPERRT] = TeilchenGeltung.GESPERRT
    _GELTUNG_MAP[KernphysikVerfassungsGeltung.KERNPHYSIKVERFASST] = TeilchenGeltung.TEILCHENGEBUNDEN
    _GELTUNG_MAP[KernphysikVerfassungsGeltung.GRUNDLEGEND_KERNPHYSIKVERFASST] = TeilchenGeltung.GRUNDLEGEND_TEILCHENGEBUNDEN


class TeilchenTyp(Enum):
    SCHUTZ_TEILCHEN = "schutz-teilchen"
    ORDNUNGS_TEILCHEN = "ordnungs-teilchen"
    SOUVERAENITAETS_TEILCHEN = "souveraenitaets-teilchen"


class TeilchenProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class TeilchenGeltung(Enum):
    GESPERRT = "gesperrt"
    TEILCHENGEBUNDEN = "teilchengebunden"
    GRUNDLEGEND_TEILCHENGEBUNDEN = "grundlegend-teilchengebunden"


_init_map()

_TYP_MAP: dict[TeilchenGeltung, TeilchenTyp] = {
    TeilchenGeltung.GESPERRT: TeilchenTyp.SCHUTZ_TEILCHEN,
    TeilchenGeltung.TEILCHENGEBUNDEN: TeilchenTyp.ORDNUNGS_TEILCHEN,
    TeilchenGeltung.GRUNDLEGEND_TEILCHENGEBUNDEN: TeilchenTyp.SOUVERAENITAETS_TEILCHEN,
}

_PROZEDUR_MAP: dict[TeilchenGeltung, TeilchenProzedur] = {
    TeilchenGeltung.GESPERRT: TeilchenProzedur.NOTPROZEDUR,
    TeilchenGeltung.TEILCHENGEBUNDEN: TeilchenProzedur.REGELPROTOKOLL,
    TeilchenGeltung.GRUNDLEGEND_TEILCHENGEBUNDEN: TeilchenProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[TeilchenGeltung, float] = {
    TeilchenGeltung.GESPERRT: 0.0,
    TeilchenGeltung.TEILCHENGEBUNDEN: 0.04,
    TeilchenGeltung.GRUNDLEGEND_TEILCHENGEBUNDEN: 0.08,
}

_TIER_DELTA: dict[TeilchenGeltung, int] = {
    TeilchenGeltung.GESPERRT: 0,
    TeilchenGeltung.TEILCHENGEBUNDEN: 1,
    TeilchenGeltung.GRUNDLEGEND_TEILCHENGEBUNDEN: 2,
}


@dataclass(frozen=True)
class TeilchenNorm:
    teilchen_feld_id: str
    teilchen_typ: TeilchenTyp
    prozedur: TeilchenProzedur
    geltung: TeilchenGeltung
    teilchen_weight: float
    teilchen_tier: int
    canonical: bool
    teilchen_ids: tuple[str, ...]
    teilchen_tags: tuple[str, ...]


@dataclass(frozen=True)
class TeilchenFeld:
    feld_id: str
    kernphysik_verfassung: KernphysikVerfassung
    normen: tuple[TeilchenNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.teilchen_feld_id for n in self.normen if n.geltung is TeilchenGeltung.GESPERRT)

    @property
    def teilchengebunden_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.teilchen_feld_id for n in self.normen if n.geltung is TeilchenGeltung.TEILCHENGEBUNDEN)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.teilchen_feld_id for n in self.normen if n.geltung is TeilchenGeltung.GRUNDLEGEND_TEILCHENGEBUNDEN)

    @property
    def feld_signal(self):
        if any(n.geltung is TeilchenGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-gesperrt")
        elif any(n.geltung is TeilchenGeltung.TEILCHENGEBUNDEN for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-teilchengebunden")
        from types import SimpleNamespace
        return SimpleNamespace(status="feld-grundlegend-teilchengebunden")


def build_teilchen_feld(
    kernphysik_verfassung: KernphysikVerfassung | None = None,
    *,
    feld_id: str = "teilchen-feld",
) -> TeilchenFeld:
    if kernphysik_verfassung is None:
        kernphysik_verfassung = build_kernphysik_verfassung(verfassung_id=f"{feld_id}-verfassung")

    normen: list[TeilchenNorm] = []
    for parent_norm in kernphysik_verfassung.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{feld_id}-{parent_norm.kernphysikverfassungs_id.removeprefix(f'{kernphysik_verfassung.verfassung_id}-')}"
        raw_weight = min(1.0, parent_norm.kernphysikverfassungs_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kernphysikverfassungs_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is TeilchenGeltung.GRUNDLEGEND_TEILCHENGEBUNDEN)
        normen.append(
            TeilchenNorm(
                teilchen_feld_id=new_id,
                teilchen_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                teilchen_weight=new_weight,
                teilchen_tier=new_tier,
                canonical=is_canonical,
                teilchen_ids=parent_norm.kernphysikverfassungs_ids + (new_id,),
                teilchen_tags=parent_norm.kernphysikverfassungs_tags + (f"teilchen-feld:{new_geltung.value}",),
            )
        )
    return TeilchenFeld(
        feld_id=feld_id,
        kernphysik_verfassung=kernphysik_verfassung,
        normen=tuple(normen),
    )
