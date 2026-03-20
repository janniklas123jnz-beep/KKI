"""wellen_charta — Quantenfelder & Dimensionen layer 3 (#263)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .dimensions_register import (
    DimensionsGeltung,
    DimensionsNorm,
    DimensionsProzedur,
    DimensionsRang,
    DimensionsRegister,
    build_dimensions_register,
)

__all__ = [
    "WellenTyp",
    "WellenProzedur",
    "WellenGeltung",
    "WellenNorm",
    "WellenCharta",
    "build_wellen_charta",
]


class WellenTyp(str, Enum):
    SCHUTZ_WELLE = "schutz-welle"
    ORDNUNGS_WELLE = "ordnungs-welle"
    SOUVERAENITAETS_WELLE = "souveraenitaets-welle"


class WellenProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class WellenGeltung(str, Enum):
    GESPERRT = "gesperrt"
    WELLEND = "wellend"
    GRUNDLEGEND_WELLEND = "grundlegend-wellend"


_TYP_MAP: dict[DimensionsGeltung, WellenTyp] = {
    DimensionsGeltung.GESPERRT: WellenTyp.SCHUTZ_WELLE,
    DimensionsGeltung.DIMENSIONIERT: WellenTyp.ORDNUNGS_WELLE,
    DimensionsGeltung.GRUNDLEGEND_DIMENSIONIERT: WellenTyp.SOUVERAENITAETS_WELLE,
}
_PROZEDUR_MAP: dict[DimensionsGeltung, WellenProzedur] = {
    DimensionsGeltung.GESPERRT: WellenProzedur.NOTPROZEDUR,
    DimensionsGeltung.DIMENSIONIERT: WellenProzedur.REGELPROTOKOLL,
    DimensionsGeltung.GRUNDLEGEND_DIMENSIONIERT: WellenProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[DimensionsGeltung, WellenGeltung] = {
    DimensionsGeltung.GESPERRT: WellenGeltung.GESPERRT,
    DimensionsGeltung.DIMENSIONIERT: WellenGeltung.WELLEND,
    DimensionsGeltung.GRUNDLEGEND_DIMENSIONIERT: WellenGeltung.GRUNDLEGEND_WELLEND,
}
_WEIGHT_BONUS: dict[DimensionsGeltung, float] = {
    DimensionsGeltung.GESPERRT: 0.0,
    DimensionsGeltung.DIMENSIONIERT: 0.04,
    DimensionsGeltung.GRUNDLEGEND_DIMENSIONIERT: 0.08,
}
_TIER_BONUS: dict[DimensionsGeltung, int] = {
    DimensionsGeltung.GESPERRT: 0,
    DimensionsGeltung.DIMENSIONIERT: 1,
    DimensionsGeltung.GRUNDLEGEND_DIMENSIONIERT: 2,
}


@dataclass(frozen=True)
class WellenNorm:
    wellen_charta_id: str
    wellen_typ: WellenTyp
    prozedur: WellenProzedur
    geltung: WellenGeltung
    wellen_weight: float
    wellen_tier: int
    canonical: bool
    wellen_charta_ids: tuple[str, ...]
    wellen_charta_tags: tuple[str, ...]


@dataclass(frozen=True)
class WellenCharta:
    charta_id: str
    dimensions_register: DimensionsRegister
    normen: tuple[WellenNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.wellen_charta_id for n in self.normen if n.geltung is WellenGeltung.GESPERRT)

    @property
    def wellend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.wellen_charta_id for n in self.normen if n.geltung is WellenGeltung.WELLEND)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.wellen_charta_id for n in self.normen if n.geltung is WellenGeltung.GRUNDLEGEND_WELLEND)

    @property
    def charta_signal(self):
        if any(n.geltung is WellenGeltung.GESPERRT for n in self.normen):
            status = "charta-gesperrt"
            severity = "critical"
        elif any(n.geltung is WellenGeltung.WELLEND for n in self.normen):
            status = "charta-wellend"
            severity = "warning"
        else:
            status = "charta-grundlegend-wellend"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_wellen_charta(
    dimensions_register: DimensionsRegister | None = None,
    *,
    charta_id: str = "wellen-charta",
) -> WellenCharta:
    if dimensions_register is None:
        dimensions_register = build_dimensions_register(register_id=f"{charta_id}-register")

    normen: list[WellenNorm] = []
    for parent_norm in dimensions_register.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{charta_id}-{parent_norm.dimensions_register_id.removeprefix(f'{dimensions_register.register_id}-')}"
        raw_weight = min(1.0, round(parent_norm.dimensions_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.dimensions_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is WellenGeltung.GRUNDLEGEND_WELLEND)
        normen.append(
            WellenNorm(
                wellen_charta_id=new_id,
                wellen_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                wellen_weight=raw_weight,
                wellen_tier=new_tier,
                canonical=is_canonical,
                wellen_charta_ids=parent_norm.dimensions_register_ids + (new_id,),
                wellen_charta_tags=parent_norm.dimensions_register_tags + (f"wellen-charta:{new_geltung.value}",),
            )
        )

    return WellenCharta(
        charta_id=charta_id,
        dimensions_register=dimensions_register,
        normen=tuple(normen),
    )
