"""relativitaets_feld — Relativität & Raumzeit layer 1 (#271)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .quanten_verfassung import (
    QuantenVerfassung,
    QuantenVerfassungsGeltung,
    QuantenVerfassungsNorm,
    QuantenVerfassungsProzedur,
    QuantenVerfassungsTyp,
    build_quanten_verfassung,
)

__all__ = [
    "RelativitaetsTyp",
    "RelativitaetsProzedur",
    "RelativitaetsGeltung",
    "RelativitaetsNorm",
    "RelativitaetsFeld",
    "build_relativitaets_feld",
]


class RelativitaetsTyp(str, Enum):
    SCHUTZ_RELATIVITAET = "schutz-relativitaet"
    ORDNUNGS_RELATIVITAET = "ordnungs-relativitaet"
    SOUVERAENITAETS_RELATIVITAET = "souveraenitaets-relativitaet"


class RelativitaetsProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class RelativitaetsGeltung(str, Enum):
    GESPERRT = "gesperrt"
    RELATIV = "relativ"
    GRUNDLEGEND_RELATIV = "grundlegend-relativ"


_TYP_MAP: dict[QuantenVerfassungsGeltung, RelativitaetsTyp] = {
    QuantenVerfassungsGeltung.GESPERRT: RelativitaetsTyp.SCHUTZ_RELATIVITAET,
    QuantenVerfassungsGeltung.QUANTENVERFASST: RelativitaetsTyp.ORDNUNGS_RELATIVITAET,
    QuantenVerfassungsGeltung.GRUNDLEGEND_QUANTENVERFASST: RelativitaetsTyp.SOUVERAENITAETS_RELATIVITAET,
}
_PROZEDUR_MAP: dict[QuantenVerfassungsGeltung, RelativitaetsProzedur] = {
    QuantenVerfassungsGeltung.GESPERRT: RelativitaetsProzedur.NOTPROZEDUR,
    QuantenVerfassungsGeltung.QUANTENVERFASST: RelativitaetsProzedur.REGELPROTOKOLL,
    QuantenVerfassungsGeltung.GRUNDLEGEND_QUANTENVERFASST: RelativitaetsProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[QuantenVerfassungsGeltung, RelativitaetsGeltung] = {
    QuantenVerfassungsGeltung.GESPERRT: RelativitaetsGeltung.GESPERRT,
    QuantenVerfassungsGeltung.QUANTENVERFASST: RelativitaetsGeltung.RELATIV,
    QuantenVerfassungsGeltung.GRUNDLEGEND_QUANTENVERFASST: RelativitaetsGeltung.GRUNDLEGEND_RELATIV,
}
_WEIGHT_BONUS: dict[QuantenVerfassungsGeltung, float] = {
    QuantenVerfassungsGeltung.GESPERRT: 0.0,
    QuantenVerfassungsGeltung.QUANTENVERFASST: 0.04,
    QuantenVerfassungsGeltung.GRUNDLEGEND_QUANTENVERFASST: 0.08,
}
_TIER_BONUS: dict[QuantenVerfassungsGeltung, int] = {
    QuantenVerfassungsGeltung.GESPERRT: 0,
    QuantenVerfassungsGeltung.QUANTENVERFASST: 1,
    QuantenVerfassungsGeltung.GRUNDLEGEND_QUANTENVERFASST: 2,
}


@dataclass(frozen=True)
class RelativitaetsNorm:
    relativitaets_feld_id: str
    relativitaets_typ: RelativitaetsTyp
    prozedur: RelativitaetsProzedur
    geltung: RelativitaetsGeltung
    relativitaets_weight: float
    relativitaets_tier: int
    canonical: bool
    relativitaets_feld_ids: tuple[str, ...]
    relativitaets_feld_tags: tuple[str, ...]


@dataclass(frozen=True)
class RelativitaetsFeld:
    feld_id: str
    quanten_verfassung: QuantenVerfassung
    normen: tuple[RelativitaetsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.relativitaets_feld_id for n in self.normen if n.geltung is RelativitaetsGeltung.GESPERRT)

    @property
    def relativ_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.relativitaets_feld_id for n in self.normen if n.geltung is RelativitaetsGeltung.RELATIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.relativitaets_feld_id for n in self.normen if n.geltung is RelativitaetsGeltung.GRUNDLEGEND_RELATIV)

    @property
    def feld_signal(self):
        if any(n.geltung is RelativitaetsGeltung.GESPERRT for n in self.normen):
            status = "feld-gesperrt"
            severity = "critical"
        elif any(n.geltung is RelativitaetsGeltung.RELATIV for n in self.normen):
            status = "feld-relativ"
            severity = "warning"
        else:
            status = "feld-grundlegend-relativ"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_relativitaets_feld(
    quanten_verfassung: QuantenVerfassung | None = None,
    *,
    feld_id: str = "relativitaets-feld",
) -> RelativitaetsFeld:
    if quanten_verfassung is None:
        quanten_verfassung = build_quanten_verfassung(verfassung_id=f"{feld_id}-verfassung")

    normen: list[RelativitaetsNorm] = []
    for parent_norm in quanten_verfassung.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{feld_id}-{parent_norm.quanten_verfassung_id.removeprefix(f'{quanten_verfassung.verfassung_id}-')}"
        raw_weight = min(1.0, round(parent_norm.quanten_verfassungs_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.quanten_verfassungs_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is RelativitaetsGeltung.GRUNDLEGEND_RELATIV)
        normen.append(
            RelativitaetsNorm(
                relativitaets_feld_id=new_id,
                relativitaets_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                relativitaets_weight=raw_weight,
                relativitaets_tier=new_tier,
                canonical=is_canonical,
                relativitaets_feld_ids=parent_norm.quanten_verfassung_ids + (new_id,),
                relativitaets_feld_tags=parent_norm.quanten_verfassung_tags + (f"relativitaets-feld:{new_geltung.value}",),
            )
        )

    return RelativitaetsFeld(
        feld_id=feld_id,
        quanten_verfassung=quanten_verfassung,
        normen=tuple(normen),
    )
