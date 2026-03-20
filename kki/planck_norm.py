"""planck_norm — Quantenfelder & Dimensionen layer 8 (#268).

Uses *_norm naming pattern: container PlanckNorm (norm_id), entry PlanckNormEintrag.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .quanten_senat import (
    QuantenSenat,
    QuantenSenatGeltung,
    QuantenSenatNorm,
    QuantenSenatProzedur,
    QuantenSenatTyp,
    build_quanten_senat,
)

__all__ = [
    "PlanckTyp",
    "PlanckProzedur",
    "PlanckGeltung",
    "PlanckNormEintrag",
    "PlanckNorm",
    "build_planck_norm",
]


class PlanckTyp(str, Enum):
    SCHUTZ_PLANCK = "schutz-planck"
    ORDNUNGS_PLANCK = "ordnungs-planck"
    SOUVERAENITAETS_PLANCK = "souveraenitaets-planck"


class PlanckProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class PlanckGeltung(str, Enum):
    GESPERRT = "gesperrt"
    PLANCK_GEBUNDEN = "planck-gebunden"
    GRUNDLEGEND_PLANCK = "grundlegend-planck"


_TYP_MAP: dict[QuantenSenatGeltung, PlanckTyp] = {
    QuantenSenatGeltung.GESPERRT: PlanckTyp.SCHUTZ_PLANCK,
    QuantenSenatGeltung.SENATSREIF: PlanckTyp.ORDNUNGS_PLANCK,
    QuantenSenatGeltung.GRUNDLEGEND_SENATSREIF: PlanckTyp.SOUVERAENITAETS_PLANCK,
}
_PROZEDUR_MAP: dict[QuantenSenatGeltung, PlanckProzedur] = {
    QuantenSenatGeltung.GESPERRT: PlanckProzedur.NOTPROZEDUR,
    QuantenSenatGeltung.SENATSREIF: PlanckProzedur.REGELPROTOKOLL,
    QuantenSenatGeltung.GRUNDLEGEND_SENATSREIF: PlanckProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[QuantenSenatGeltung, PlanckGeltung] = {
    QuantenSenatGeltung.GESPERRT: PlanckGeltung.GESPERRT,
    QuantenSenatGeltung.SENATSREIF: PlanckGeltung.PLANCK_GEBUNDEN,
    QuantenSenatGeltung.GRUNDLEGEND_SENATSREIF: PlanckGeltung.GRUNDLEGEND_PLANCK,
}
_WEIGHT_BONUS: dict[QuantenSenatGeltung, float] = {
    QuantenSenatGeltung.GESPERRT: 0.0,
    QuantenSenatGeltung.SENATSREIF: 0.04,
    QuantenSenatGeltung.GRUNDLEGEND_SENATSREIF: 0.08,
}
_TIER_BONUS: dict[QuantenSenatGeltung, int] = {
    QuantenSenatGeltung.GESPERRT: 0,
    QuantenSenatGeltung.SENATSREIF: 1,
    QuantenSenatGeltung.GRUNDLEGEND_SENATSREIF: 2,
}


@dataclass(frozen=True)
class PlanckNormEintrag:
    planck_norm_id: str
    planck_typ: PlanckTyp
    prozedur: PlanckProzedur
    geltung: PlanckGeltung
    planck_weight: float
    planck_tier: int
    canonical: bool
    planck_norm_ids: tuple[str, ...]
    planck_norm_tags: tuple[str, ...]


@dataclass(frozen=True)
class PlanckNorm:
    norm_id: str
    quanten_senat: QuantenSenat
    normen: tuple[PlanckNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.planck_norm_id for n in self.normen if n.geltung is PlanckGeltung.GESPERRT)

    @property
    def planck_gebunden_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.planck_norm_id for n in self.normen if n.geltung is PlanckGeltung.PLANCK_GEBUNDEN)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.planck_norm_id for n in self.normen if n.geltung is PlanckGeltung.GRUNDLEGEND_PLANCK)

    @property
    def norm_signal(self):
        if any(n.geltung is PlanckGeltung.GESPERRT for n in self.normen):
            status = "norm-gesperrt"
            severity = "critical"
        elif any(n.geltung is PlanckGeltung.PLANCK_GEBUNDEN for n in self.normen):
            status = "norm-planck-gebunden"
            severity = "warning"
        else:
            status = "norm-grundlegend-planck"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_planck_norm(
    quanten_senat: QuantenSenat | None = None,
    *,
    norm_id: str = "planck-norm",
) -> PlanckNorm:
    if quanten_senat is None:
        quanten_senat = build_quanten_senat(senat_id=f"{norm_id}-senat")

    normen: list[PlanckNormEintrag] = []
    for parent_norm in quanten_senat.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{norm_id}-{parent_norm.quanten_senat_id.removeprefix(f'{quanten_senat.senat_id}-')}"
        raw_weight = min(1.0, round(parent_norm.quanten_senat_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.quanten_senat_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is PlanckGeltung.GRUNDLEGEND_PLANCK)
        normen.append(
            PlanckNormEintrag(
                planck_norm_id=new_id,
                planck_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                planck_weight=raw_weight,
                planck_tier=new_tier,
                canonical=is_canonical,
                planck_norm_ids=parent_norm.quanten_senat_ids + (new_id,),
                planck_norm_tags=parent_norm.quanten_senat_tags + (f"planck-norm:{new_geltung.value}",),
            )
        )

    return PlanckNorm(
        norm_id=norm_id,
        quanten_senat=quanten_senat,
        normen=tuple(normen),
    )
