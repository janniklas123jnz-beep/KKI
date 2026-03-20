"""dimensions_register — Quantenfelder & Dimensionen layer 2 (#262)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .quanten_feld import (
    QuantenFeld,
    QuantenFeldGeltung,
    QuantenFeldNorm,
    QuantenFeldProzedur,
    QuantenFeldTyp,
    build_quanten_feld,
)

__all__ = [
    "DimensionsRang",
    "DimensionsProzedur",
    "DimensionsGeltung",
    "DimensionsNorm",
    "DimensionsRegister",
    "build_dimensions_register",
]


class DimensionsRang(str, Enum):
    SCHUTZ_DIMENSION = "schutz-dimension"
    ORDNUNGS_DIMENSION = "ordnungs-dimension"
    SOUVERAENITAETS_DIMENSION = "souveraenitaets-dimension"


class DimensionsProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class DimensionsGeltung(str, Enum):
    GESPERRT = "gesperrt"
    DIMENSIONIERT = "dimensioniert"
    GRUNDLEGEND_DIMENSIONIERT = "grundlegend-dimensioniert"


_RANG_MAP: dict[QuantenFeldGeltung, DimensionsRang] = {
    QuantenFeldGeltung.GESPERRT: DimensionsRang.SCHUTZ_DIMENSION,
    QuantenFeldGeltung.QUANTISIERT: DimensionsRang.ORDNUNGS_DIMENSION,
    QuantenFeldGeltung.GRUNDLEGEND_QUANTISIERT: DimensionsRang.SOUVERAENITAETS_DIMENSION,
}
_PROZEDUR_MAP: dict[QuantenFeldGeltung, DimensionsProzedur] = {
    QuantenFeldGeltung.GESPERRT: DimensionsProzedur.NOTPROZEDUR,
    QuantenFeldGeltung.QUANTISIERT: DimensionsProzedur.REGELPROTOKOLL,
    QuantenFeldGeltung.GRUNDLEGEND_QUANTISIERT: DimensionsProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[QuantenFeldGeltung, DimensionsGeltung] = {
    QuantenFeldGeltung.GESPERRT: DimensionsGeltung.GESPERRT,
    QuantenFeldGeltung.QUANTISIERT: DimensionsGeltung.DIMENSIONIERT,
    QuantenFeldGeltung.GRUNDLEGEND_QUANTISIERT: DimensionsGeltung.GRUNDLEGEND_DIMENSIONIERT,
}
_WEIGHT_BONUS: dict[QuantenFeldGeltung, float] = {
    QuantenFeldGeltung.GESPERRT: 0.0,
    QuantenFeldGeltung.QUANTISIERT: 0.04,
    QuantenFeldGeltung.GRUNDLEGEND_QUANTISIERT: 0.08,
}
_TIER_BONUS: dict[QuantenFeldGeltung, int] = {
    QuantenFeldGeltung.GESPERRT: 0,
    QuantenFeldGeltung.QUANTISIERT: 1,
    QuantenFeldGeltung.GRUNDLEGEND_QUANTISIERT: 2,
}


@dataclass(frozen=True)
class DimensionsNorm:
    dimensions_register_id: str
    dimensions_rang: DimensionsRang
    prozedur: DimensionsProzedur
    geltung: DimensionsGeltung
    dimensions_weight: float
    dimensions_tier: int
    canonical: bool
    dimensions_register_ids: tuple[str, ...]
    dimensions_register_tags: tuple[str, ...]


@dataclass(frozen=True)
class DimensionsRegister:
    register_id: str
    quanten_feld: QuantenFeld
    normen: tuple[DimensionsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.dimensions_register_id for n in self.normen if n.geltung is DimensionsGeltung.GESPERRT)

    @property
    def dimensioniert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.dimensions_register_id for n in self.normen if n.geltung is DimensionsGeltung.DIMENSIONIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.dimensions_register_id for n in self.normen if n.geltung is DimensionsGeltung.GRUNDLEGEND_DIMENSIONIERT)

    @property
    def register_signal(self):
        if any(n.geltung is DimensionsGeltung.GESPERRT for n in self.normen):
            status = "register-gesperrt"
            severity = "critical"
        elif any(n.geltung is DimensionsGeltung.DIMENSIONIERT for n in self.normen):
            status = "register-dimensioniert"
            severity = "warning"
        else:
            status = "register-grundlegend-dimensioniert"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_dimensions_register(
    quanten_feld: QuantenFeld | None = None,
    *,
    register_id: str = "dimensions-register",
) -> DimensionsRegister:
    if quanten_feld is None:
        quanten_feld = build_quanten_feld(feld_id=f"{register_id}-feld")

    normen: list[DimensionsNorm] = []
    for parent_norm in quanten_feld.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{register_id}-{parent_norm.quanten_feld_id.removeprefix(f'{quanten_feld.feld_id}-')}"
        raw_weight = min(1.0, round(parent_norm.quanten_feld_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.quanten_feld_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is DimensionsGeltung.GRUNDLEGEND_DIMENSIONIERT)
        normen.append(
            DimensionsNorm(
                dimensions_register_id=new_id,
                dimensions_rang=_RANG_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                dimensions_weight=raw_weight,
                dimensions_tier=new_tier,
                canonical=is_canonical,
                dimensions_register_ids=parent_norm.quanten_feld_ids + (new_id,),
                dimensions_register_tags=parent_norm.quanten_feld_tags + (f"dimensions-register:{new_geltung.value}",),
            )
        )

    return DimensionsRegister(
        register_id=register_id,
        quanten_feld=quanten_feld,
        normen=tuple(normen),
    )
