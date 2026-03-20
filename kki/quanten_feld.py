"""quanten_feld — Quantenfelder & Dimensionen layer 1 (#261)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kosmos_verfassung import (
    KosmosVerfassung,
    KosmosVerfassungsGeltung,
    KosmosVerfassungsNorm,
    KosmosVerfassungsProzedur,
    KosmosVerfassungsTyp,
    build_kosmos_verfassung,
)

__all__ = [
    "QuantenFeldTyp",
    "QuantenFeldProzedur",
    "QuantenFeldGeltung",
    "QuantenFeldNorm",
    "QuantenFeld",
    "build_quanten_feld",
]


class QuantenFeldTyp(str, Enum):
    SCHUTZ_QUANT = "schutz-quant"
    ORDNUNGS_QUANT = "ordnungs-quant"
    SOUVERAENITAETS_QUANT = "souveraenitaets-quant"


class QuantenFeldProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class QuantenFeldGeltung(str, Enum):
    GESPERRT = "gesperrt"
    QUANTISIERT = "quantisiert"
    GRUNDLEGEND_QUANTISIERT = "grundlegend-quantisiert"


_TYP_MAP: dict[KosmosVerfassungsGeltung, QuantenFeldTyp] = {
    KosmosVerfassungsGeltung.GESPERRT: QuantenFeldTyp.SCHUTZ_QUANT,
    KosmosVerfassungsGeltung.VERFASST: QuantenFeldTyp.ORDNUNGS_QUANT,
    KosmosVerfassungsGeltung.GRUNDLEGEND_VERFASST: QuantenFeldTyp.SOUVERAENITAETS_QUANT,
}
_PROZEDUR_MAP: dict[KosmosVerfassungsGeltung, QuantenFeldProzedur] = {
    KosmosVerfassungsGeltung.GESPERRT: QuantenFeldProzedur.NOTPROZEDUR,
    KosmosVerfassungsGeltung.VERFASST: QuantenFeldProzedur.REGELPROTOKOLL,
    KosmosVerfassungsGeltung.GRUNDLEGEND_VERFASST: QuantenFeldProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[KosmosVerfassungsGeltung, QuantenFeldGeltung] = {
    KosmosVerfassungsGeltung.GESPERRT: QuantenFeldGeltung.GESPERRT,
    KosmosVerfassungsGeltung.VERFASST: QuantenFeldGeltung.QUANTISIERT,
    KosmosVerfassungsGeltung.GRUNDLEGEND_VERFASST: QuantenFeldGeltung.GRUNDLEGEND_QUANTISIERT,
}
_WEIGHT_BONUS: dict[KosmosVerfassungsGeltung, float] = {
    KosmosVerfassungsGeltung.GESPERRT: 0.0,
    KosmosVerfassungsGeltung.VERFASST: 0.04,
    KosmosVerfassungsGeltung.GRUNDLEGEND_VERFASST: 0.08,
}
_TIER_BONUS: dict[KosmosVerfassungsGeltung, int] = {
    KosmosVerfassungsGeltung.GESPERRT: 0,
    KosmosVerfassungsGeltung.VERFASST: 1,
    KosmosVerfassungsGeltung.GRUNDLEGEND_VERFASST: 2,
}


@dataclass(frozen=True)
class QuantenFeldNorm:
    quanten_feld_id: str
    quanten_feld_typ: QuantenFeldTyp
    prozedur: QuantenFeldProzedur
    geltung: QuantenFeldGeltung
    quanten_feld_weight: float
    quanten_feld_tier: int
    canonical: bool
    quanten_feld_ids: tuple[str, ...]
    quanten_feld_tags: tuple[str, ...]


@dataclass(frozen=True)
class QuantenFeld:
    feld_id: str
    kosmos_verfassung: KosmosVerfassung
    normen: tuple[QuantenFeldNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.quanten_feld_id for n in self.normen if n.geltung is QuantenFeldGeltung.GESPERRT)

    @property
    def quantisiert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.quanten_feld_id for n in self.normen if n.geltung is QuantenFeldGeltung.QUANTISIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.quanten_feld_id for n in self.normen if n.geltung is QuantenFeldGeltung.GRUNDLEGEND_QUANTISIERT)

    @property
    def feld_signal(self):
        if any(n.geltung is QuantenFeldGeltung.GESPERRT for n in self.normen):
            status = "feld-gesperrt"
            severity = "critical"
        elif any(n.geltung is QuantenFeldGeltung.QUANTISIERT for n in self.normen):
            status = "feld-quantisiert"
            severity = "warning"
        else:
            status = "feld-grundlegend-quantisiert"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_quanten_feld(
    kosmos_verfassung: KosmosVerfassung | None = None,
    *,
    feld_id: str = "quanten-feld",
) -> QuantenFeld:
    if kosmos_verfassung is None:
        kosmos_verfassung = build_kosmos_verfassung(verfassung_id=f"{feld_id}-verfassung")

    normen: list[QuantenFeldNorm] = []
    for parent_norm in kosmos_verfassung.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{feld_id}-{parent_norm.kosmos_verfassung_id.removeprefix(f'{kosmos_verfassung.verfassung_id}-')}"
        raw_weight = min(1.0, round(parent_norm.kosmos_verfassungs_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.kosmos_verfassungs_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is QuantenFeldGeltung.GRUNDLEGEND_QUANTISIERT)
        normen.append(
            QuantenFeldNorm(
                quanten_feld_id=new_id,
                quanten_feld_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                quanten_feld_weight=raw_weight,
                quanten_feld_tier=new_tier,
                canonical=is_canonical,
                quanten_feld_ids=parent_norm.kosmos_verfassung_ids + (new_id,),
                quanten_feld_tags=parent_norm.kosmos_verfassung_tags + (f"quanten-feld:{new_geltung.value}",),
            )
        )

    return QuantenFeld(
        feld_id=feld_id,
        kosmos_verfassung=kosmos_verfassung,
        normen=tuple(normen),
    )
