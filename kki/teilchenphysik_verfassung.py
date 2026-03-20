"""
#320 TeilchenphysikVerfassung — Block-Krone: Teilchenphysik als höchste Governance-Instanz.
Geltungsstufen: GESPERRT / TEILCHENPHYSIKVERFASST / GRUNDLEGEND_TEILCHENPHYSIKVERFASST
Parent: StandardmodellCharta (#319)
Block #311–#320 Krone
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .standardmodell_charta import (
    StandardmodellCharta,
    StandardmodellGeltung,
    build_standardmodell_charta,
)

_GELTUNG_MAP: dict[StandardmodellGeltung, "TeilchenphysikGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[StandardmodellGeltung.GESPERRT] = TeilchenphysikGeltung.GESPERRT
    _GELTUNG_MAP[StandardmodellGeltung.STANDARDMODELLIERT] = TeilchenphysikGeltung.TEILCHENPHYSIKVERFASST
    _GELTUNG_MAP[StandardmodellGeltung.GRUNDLEGEND_STANDARDMODELLIERT] = TeilchenphysikGeltung.GRUNDLEGEND_TEILCHENPHYSIKVERFASST


class TeilchenphysikTyp(Enum):
    SCHUTZ_TEILCHENPHYSIK = "schutz-teilchenphysik"
    ORDNUNGS_TEILCHENPHYSIK = "ordnungs-teilchenphysik"
    SOUVERAENITAETS_TEILCHENPHYSIK = "souveraenitaets-teilchenphysik"


class TeilchenphysikProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class TeilchenphysikGeltung(Enum):
    GESPERRT = "gesperrt"
    TEILCHENPHYSIKVERFASST = "teilchenphysikverfasst"
    GRUNDLEGEND_TEILCHENPHYSIKVERFASST = "grundlegend-teilchenphysikverfasst"


_init_map()

_TYP_MAP: dict[TeilchenphysikGeltung, TeilchenphysikTyp] = {
    TeilchenphysikGeltung.GESPERRT: TeilchenphysikTyp.SCHUTZ_TEILCHENPHYSIK,
    TeilchenphysikGeltung.TEILCHENPHYSIKVERFASST: TeilchenphysikTyp.ORDNUNGS_TEILCHENPHYSIK,
    TeilchenphysikGeltung.GRUNDLEGEND_TEILCHENPHYSIKVERFASST: TeilchenphysikTyp.SOUVERAENITAETS_TEILCHENPHYSIK,
}

_PROZEDUR_MAP: dict[TeilchenphysikGeltung, TeilchenphysikProzedur] = {
    TeilchenphysikGeltung.GESPERRT: TeilchenphysikProzedur.NOTPROZEDUR,
    TeilchenphysikGeltung.TEILCHENPHYSIKVERFASST: TeilchenphysikProzedur.REGELPROTOKOLL,
    TeilchenphysikGeltung.GRUNDLEGEND_TEILCHENPHYSIKVERFASST: TeilchenphysikProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[TeilchenphysikGeltung, float] = {
    TeilchenphysikGeltung.GESPERRT: 0.0,
    TeilchenphysikGeltung.TEILCHENPHYSIKVERFASST: 0.04,
    TeilchenphysikGeltung.GRUNDLEGEND_TEILCHENPHYSIKVERFASST: 0.08,
}

_TIER_DELTA: dict[TeilchenphysikGeltung, int] = {
    TeilchenphysikGeltung.GESPERRT: 0,
    TeilchenphysikGeltung.TEILCHENPHYSIKVERFASST: 1,
    TeilchenphysikGeltung.GRUNDLEGEND_TEILCHENPHYSIKVERFASST: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TeilchenphysikNorm:
    teilchenphysik_verfassung_id: str
    teilchenphysik_typ: TeilchenphysikTyp
    prozedur: TeilchenphysikProzedur
    geltung: TeilchenphysikGeltung
    teilchenphysik_weight: float
    teilchenphysik_tier: int
    canonical: bool
    teilchenphysik_ids: tuple[str, ...]
    teilchenphysik_tags: tuple[str, ...]


@dataclass(frozen=True)
class TeilchenphysikVerfassung:
    verfassung_id: str
    standardmodell_charta: StandardmodellCharta
    normen: tuple[TeilchenphysikNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.teilchenphysik_verfassung_id for n in self.normen if n.geltung is TeilchenphysikGeltung.GESPERRT)

    @property
    def teilchenphysikverfasst_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.teilchenphysik_verfassung_id for n in self.normen if n.geltung is TeilchenphysikGeltung.TEILCHENPHYSIKVERFASST)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.teilchenphysik_verfassung_id for n in self.normen if n.geltung is TeilchenphysikGeltung.GRUNDLEGEND_TEILCHENPHYSIKVERFASST)

    @property
    def verfassung_signal(self):
        if any(n.geltung is TeilchenphysikGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-gesperrt")
        elif any(n.geltung is TeilchenphysikGeltung.TEILCHENPHYSIKVERFASST for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-teilchenphysikverfasst")
        from types import SimpleNamespace
        return SimpleNamespace(status="verfassung-grundlegend-teilchenphysikverfasst")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_teilchenphysik_verfassung(
    standardmodell_charta: StandardmodellCharta | None = None,
    *,
    verfassung_id: str = "teilchenphysik-verfassung",
) -> TeilchenphysikVerfassung:
    if standardmodell_charta is None:
        standardmodell_charta = build_standardmodell_charta(charta_id=f"{verfassung_id}-charta")

    normen: list[TeilchenphysikNorm] = []
    for parent_norm in standardmodell_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{verfassung_id}-{parent_norm.standardmodell_charta_id.removeprefix(f'{standardmodell_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.standardmodell_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.standardmodell_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is TeilchenphysikGeltung.GRUNDLEGEND_TEILCHENPHYSIKVERFASST)
        normen.append(
            TeilchenphysikNorm(
                teilchenphysik_verfassung_id=new_id,
                teilchenphysik_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                teilchenphysik_weight=new_weight,
                teilchenphysik_tier=new_tier,
                canonical=is_canonical,
                teilchenphysik_ids=parent_norm.standardmodell_ids + (new_id,),
                teilchenphysik_tags=parent_norm.standardmodell_tags + (f"teilchenphysik-verfassung:{new_geltung.value}",),
            )
        )
    return TeilchenphysikVerfassung(
        verfassung_id=verfassung_id,
        standardmodell_charta=standardmodell_charta,
        normen=tuple(normen),
    )
