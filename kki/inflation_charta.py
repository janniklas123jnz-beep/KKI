"""
#323 InflationCharta — Kosmische Inflation als exponentielles Wachstums-Governance.
Geltungsstufen: GESPERRT / INFLATIONAER / GRUNDLEGEND_INFLATIONAER
Parent: UrknallRegister (#322)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .urknall_register import (
    UrknallGeltung,
    UrknallRegister,
    build_urknall_register,
)

_GELTUNG_MAP: dict[UrknallGeltung, "InflationGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[UrknallGeltung.GESPERRT] = InflationGeltung.GESPERRT
    _GELTUNG_MAP[UrknallGeltung.URKNALLGEBUNDEN] = InflationGeltung.INFLATIONAER
    _GELTUNG_MAP[UrknallGeltung.GRUNDLEGEND_URKNALLGEBUNDEN] = InflationGeltung.GRUNDLEGEND_INFLATIONAER


class InflationTyp(Enum):
    SCHUTZ_INFLATION = "schutz-inflation"
    ORDNUNGS_INFLATION = "ordnungs-inflation"
    SOUVERAENITAETS_INFLATION = "souveraenitaets-inflation"


class InflationProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class InflationGeltung(Enum):
    GESPERRT = "gesperrt"
    INFLATIONAER = "inflationaer"
    GRUNDLEGEND_INFLATIONAER = "grundlegend-inflationaer"


_init_map()

_TYP_MAP: dict[InflationGeltung, InflationTyp] = {
    InflationGeltung.GESPERRT: InflationTyp.SCHUTZ_INFLATION,
    InflationGeltung.INFLATIONAER: InflationTyp.ORDNUNGS_INFLATION,
    InflationGeltung.GRUNDLEGEND_INFLATIONAER: InflationTyp.SOUVERAENITAETS_INFLATION,
}

_PROZEDUR_MAP: dict[InflationGeltung, InflationProzedur] = {
    InflationGeltung.GESPERRT: InflationProzedur.NOTPROZEDUR,
    InflationGeltung.INFLATIONAER: InflationProzedur.REGELPROTOKOLL,
    InflationGeltung.GRUNDLEGEND_INFLATIONAER: InflationProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[InflationGeltung, float] = {
    InflationGeltung.GESPERRT: 0.0,
    InflationGeltung.INFLATIONAER: 0.04,
    InflationGeltung.GRUNDLEGEND_INFLATIONAER: 0.08,
}

_TIER_DELTA: dict[InflationGeltung, int] = {
    InflationGeltung.GESPERRT: 0,
    InflationGeltung.INFLATIONAER: 1,
    InflationGeltung.GRUNDLEGEND_INFLATIONAER: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class InflationNorm:
    inflation_charta_id: str
    inflation_typ: InflationTyp
    prozedur: InflationProzedur
    geltung: InflationGeltung
    inflation_weight: float
    inflation_tier: int
    canonical: bool
    inflation_ids: tuple[str, ...]
    inflation_tags: tuple[str, ...]


@dataclass(frozen=True)
class InflationCharta:
    charta_id: str
    urknall_register: UrknallRegister
    normen: tuple[InflationNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.inflation_charta_id for n in self.normen if n.geltung is InflationGeltung.GESPERRT)

    @property
    def inflationaer_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.inflation_charta_id for n in self.normen if n.geltung is InflationGeltung.INFLATIONAER)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.inflation_charta_id for n in self.normen if n.geltung is InflationGeltung.GRUNDLEGEND_INFLATIONAER)

    @property
    def charta_signal(self):
        if any(n.geltung is InflationGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is InflationGeltung.INFLATIONAER for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-inflationaer")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-inflationaer")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_inflation_charta(
    urknall_register: UrknallRegister | None = None,
    *,
    charta_id: str = "inflation-charta",
) -> InflationCharta:
    if urknall_register is None:
        urknall_register = build_urknall_register(register_id=f"{charta_id}-register")

    normen: list[InflationNorm] = []
    for parent_norm in urknall_register.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.urknall_register_id.removeprefix(f'{urknall_register.register_id}-')}"
        raw_weight = min(1.0, parent_norm.urknall_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.urknall_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is InflationGeltung.GRUNDLEGEND_INFLATIONAER)
        normen.append(
            InflationNorm(
                inflation_charta_id=new_id,
                inflation_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                inflation_weight=new_weight,
                inflation_tier=new_tier,
                canonical=is_canonical,
                inflation_ids=parent_norm.urknall_ids + (new_id,),
                inflation_tags=parent_norm.urknall_tags + (f"inflation-charta:{new_geltung.value}",),
            )
        )
    return InflationCharta(
        charta_id=charta_id,
        urknall_register=urknall_register,
        normen=tuple(normen),
    )
