"""stringtheorie_charta — Quantenfelder & Dimensionen layer 9 (#269)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .planck_norm import (
    PlanckGeltung,
    PlanckNorm,
    PlanckNormEintrag,
    PlanckProzedur,
    PlanckTyp,
    build_planck_norm,
)

__all__ = [
    "StringtheorieTyp",
    "StringtheorieProzedur",
    "StringtheorieGeltung",
    "StringtheorieNorm",
    "StringtheorieCharta",
    "build_stringtheorie_charta",
]


class StringtheorieTyp(str, Enum):
    SCHUTZ_FADEN = "schutz-faden"
    ORDNUNGS_FADEN = "ordnungs-faden"
    SOUVERAENITAETS_FADEN = "souveraenitaets-faden"


class StringtheorieProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class StringtheorieGeltung(str, Enum):
    GESPERRT = "gesperrt"
    FADENGEBUNDEN = "fadengebunden"
    GRUNDLEGEND_FADENGEBUNDEN = "grundlegend-fadengebunden"


_TYP_MAP: dict[PlanckGeltung, StringtheorieTyp] = {
    PlanckGeltung.GESPERRT: StringtheorieTyp.SCHUTZ_FADEN,
    PlanckGeltung.PLANCK_GEBUNDEN: StringtheorieTyp.ORDNUNGS_FADEN,
    PlanckGeltung.GRUNDLEGEND_PLANCK: StringtheorieTyp.SOUVERAENITAETS_FADEN,
}
_PROZEDUR_MAP: dict[PlanckGeltung, StringtheorieProzedur] = {
    PlanckGeltung.GESPERRT: StringtheorieProzedur.NOTPROZEDUR,
    PlanckGeltung.PLANCK_GEBUNDEN: StringtheorieProzedur.REGELPROTOKOLL,
    PlanckGeltung.GRUNDLEGEND_PLANCK: StringtheorieProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[PlanckGeltung, StringtheorieGeltung] = {
    PlanckGeltung.GESPERRT: StringtheorieGeltung.GESPERRT,
    PlanckGeltung.PLANCK_GEBUNDEN: StringtheorieGeltung.FADENGEBUNDEN,
    PlanckGeltung.GRUNDLEGEND_PLANCK: StringtheorieGeltung.GRUNDLEGEND_FADENGEBUNDEN,
}
_WEIGHT_BONUS: dict[PlanckGeltung, float] = {
    PlanckGeltung.GESPERRT: 0.0,
    PlanckGeltung.PLANCK_GEBUNDEN: 0.04,
    PlanckGeltung.GRUNDLEGEND_PLANCK: 0.08,
}
_TIER_BONUS: dict[PlanckGeltung, int] = {
    PlanckGeltung.GESPERRT: 0,
    PlanckGeltung.PLANCK_GEBUNDEN: 1,
    PlanckGeltung.GRUNDLEGEND_PLANCK: 2,
}


@dataclass(frozen=True)
class StringtheorieNorm:
    stringtheorie_charta_id: str
    stringtheorie_typ: StringtheorieTyp
    prozedur: StringtheorieProzedur
    geltung: StringtheorieGeltung
    stringtheorie_weight: float
    stringtheorie_tier: int
    canonical: bool
    stringtheorie_charta_ids: tuple[str, ...]
    stringtheorie_charta_tags: tuple[str, ...]


@dataclass(frozen=True)
class StringtheorieCharta:
    charta_id: str
    planck_norm: PlanckNorm
    normen: tuple[StringtheorieNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.stringtheorie_charta_id for n in self.normen if n.geltung is StringtheorieGeltung.GESPERRT)

    @property
    def fadengebunden_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.stringtheorie_charta_id for n in self.normen if n.geltung is StringtheorieGeltung.FADENGEBUNDEN)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.stringtheorie_charta_id for n in self.normen if n.geltung is StringtheorieGeltung.GRUNDLEGEND_FADENGEBUNDEN)

    @property
    def charta_signal(self):
        if any(n.geltung is StringtheorieGeltung.GESPERRT for n in self.normen):
            status = "charta-gesperrt"
            severity = "critical"
        elif any(n.geltung is StringtheorieGeltung.FADENGEBUNDEN for n in self.normen):
            status = "charta-fadengebunden"
            severity = "warning"
        else:
            status = "charta-grundlegend-fadengebunden"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_stringtheorie_charta(
    planck_norm: PlanckNorm | None = None,
    *,
    charta_id: str = "stringtheorie-charta",
) -> StringtheorieCharta:
    if planck_norm is None:
        planck_norm = build_planck_norm(norm_id=f"{charta_id}-norm")

    normen: list[StringtheorieNorm] = []
    for parent_norm in planck_norm.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{charta_id}-{parent_norm.planck_norm_id.removeprefix(f'{planck_norm.norm_id}-')}"
        raw_weight = min(1.0, round(parent_norm.planck_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.planck_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is StringtheorieGeltung.GRUNDLEGEND_FADENGEBUNDEN)
        normen.append(
            StringtheorieNorm(
                stringtheorie_charta_id=new_id,
                stringtheorie_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                stringtheorie_weight=raw_weight,
                stringtheorie_tier=new_tier,
                canonical=is_canonical,
                stringtheorie_charta_ids=parent_norm.planck_norm_ids + (new_id,),
                stringtheorie_charta_tags=parent_norm.planck_norm_tags + (f"stringtheorie-charta:{new_geltung.value}",),
            )
        )

    return StringtheorieCharta(
        charta_id=charta_id,
        planck_norm=planck_norm,
        normen=tuple(normen),
    )
