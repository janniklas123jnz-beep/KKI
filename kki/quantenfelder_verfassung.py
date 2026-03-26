"""quanten_verfassung — Quantenfelder & Dimensionen layer 10 (#270) — Block Crown."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .stringtheorie_charta import (
    StringtheorieCharta,
    StringtheorieGeltung,
    StringtheorieNorm,
    StringtheorieProzedur,
    StringtheorieTyp,
    build_stringtheorie_charta,
)

__all__ = [
    "QuantenVerfassungsTyp",
    "QuantenVerfassungsProzedur",
    "QuantenVerfassungsGeltung",
    "QuantenVerfassungsNorm",
    "QuantenVerfassung",
    "build_quanten_verfassung",
]


class QuantenVerfassungsTyp(str, Enum):
    SCHUTZ_QUANTENVERFASSUNG = "schutz-quantenverfassung"
    ORDNUNGS_QUANTENVERFASSUNG = "ordnungs-quantenverfassung"
    SOUVERAENITAETS_QUANTENVERFASSUNG = "souveraenitaets-quantenverfassung"


class QuantenVerfassungsProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class QuantenVerfassungsGeltung(str, Enum):
    GESPERRT = "gesperrt"
    QUANTENVERFASST = "quantenverfasst"
    GRUNDLEGEND_QUANTENVERFASST = "grundlegend-quantenverfasst"


_TYP_MAP: dict[StringtheorieGeltung, QuantenVerfassungsTyp] = {
    StringtheorieGeltung.GESPERRT: QuantenVerfassungsTyp.SCHUTZ_QUANTENVERFASSUNG,
    StringtheorieGeltung.FADENGEBUNDEN: QuantenVerfassungsTyp.ORDNUNGS_QUANTENVERFASSUNG,
    StringtheorieGeltung.GRUNDLEGEND_FADENGEBUNDEN: QuantenVerfassungsTyp.SOUVERAENITAETS_QUANTENVERFASSUNG,
}
_PROZEDUR_MAP: dict[StringtheorieGeltung, QuantenVerfassungsProzedur] = {
    StringtheorieGeltung.GESPERRT: QuantenVerfassungsProzedur.NOTPROZEDUR,
    StringtheorieGeltung.FADENGEBUNDEN: QuantenVerfassungsProzedur.REGELPROTOKOLL,
    StringtheorieGeltung.GRUNDLEGEND_FADENGEBUNDEN: QuantenVerfassungsProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[StringtheorieGeltung, QuantenVerfassungsGeltung] = {
    StringtheorieGeltung.GESPERRT: QuantenVerfassungsGeltung.GESPERRT,
    StringtheorieGeltung.FADENGEBUNDEN: QuantenVerfassungsGeltung.QUANTENVERFASST,
    StringtheorieGeltung.GRUNDLEGEND_FADENGEBUNDEN: QuantenVerfassungsGeltung.GRUNDLEGEND_QUANTENVERFASST,
}
_WEIGHT_BONUS: dict[StringtheorieGeltung, float] = {
    StringtheorieGeltung.GESPERRT: 0.0,
    StringtheorieGeltung.FADENGEBUNDEN: 0.04,
    StringtheorieGeltung.GRUNDLEGEND_FADENGEBUNDEN: 0.08,
}
_TIER_BONUS: dict[StringtheorieGeltung, int] = {
    StringtheorieGeltung.GESPERRT: 0,
    StringtheorieGeltung.FADENGEBUNDEN: 1,
    StringtheorieGeltung.GRUNDLEGEND_FADENGEBUNDEN: 2,
}


@dataclass(frozen=True)
class QuantenVerfassungsNorm:
    quanten_verfassung_id: str
    quanten_verfassungs_typ: QuantenVerfassungsTyp
    prozedur: QuantenVerfassungsProzedur
    geltung: QuantenVerfassungsGeltung
    quanten_verfassungs_weight: float
    quanten_verfassungs_tier: int
    canonical: bool
    quanten_verfassung_ids: tuple[str, ...]
    quanten_verfassung_tags: tuple[str, ...]


@dataclass(frozen=True)
class QuantenVerfassung:
    verfassung_id: str
    stringtheorie_charta: StringtheorieCharta
    normen: tuple[QuantenVerfassungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.quanten_verfassung_id for n in self.normen if n.geltung is QuantenVerfassungsGeltung.GESPERRT)

    @property
    def quantenverfasst_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.quanten_verfassung_id for n in self.normen if n.geltung is QuantenVerfassungsGeltung.QUANTENVERFASST)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.quanten_verfassung_id for n in self.normen if n.geltung is QuantenVerfassungsGeltung.GRUNDLEGEND_QUANTENVERFASST)

    @property
    def verfassung_signal(self):
        if any(n.geltung is QuantenVerfassungsGeltung.GESPERRT for n in self.normen):
            status = "verfassung-gesperrt"
            severity = "critical"
        elif any(n.geltung is QuantenVerfassungsGeltung.QUANTENVERFASST for n in self.normen):
            status = "verfassung-quantenverfasst"
            severity = "warning"
        else:
            status = "verfassung-grundlegend-quantenverfasst"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_quanten_verfassung(
    stringtheorie_charta: StringtheorieCharta | None = None,
    *,
    verfassung_id: str = "quanten-verfassung",
) -> QuantenVerfassung:
    if stringtheorie_charta is None:
        stringtheorie_charta = build_stringtheorie_charta(charta_id=f"{verfassung_id}-charta")

    normen: list[QuantenVerfassungsNorm] = []
    for parent_norm in stringtheorie_charta.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{verfassung_id}-{parent_norm.stringtheorie_charta_id.removeprefix(f'{stringtheorie_charta.charta_id}-')}"
        raw_weight = min(1.0, round(parent_norm.stringtheorie_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.stringtheorie_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is QuantenVerfassungsGeltung.GRUNDLEGEND_QUANTENVERFASST)
        normen.append(
            QuantenVerfassungsNorm(
                quanten_verfassung_id=new_id,
                quanten_verfassungs_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                quanten_verfassungs_weight=raw_weight,
                quanten_verfassungs_tier=new_tier,
                canonical=is_canonical,
                quanten_verfassung_ids=parent_norm.stringtheorie_charta_ids + (new_id,),
                quanten_verfassung_tags=parent_norm.stringtheorie_charta_tags + (f"quanten-verfassung:{new_geltung.value}",),
            )
        )

    return QuantenVerfassung(
        verfassung_id=verfassung_id,
        stringtheorie_charta=stringtheorie_charta,
        normen=tuple(normen),
    )
