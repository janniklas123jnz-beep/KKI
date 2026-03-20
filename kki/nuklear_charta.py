"""
#309 NuklearCharta — Nukleare Struktur als Governance-Charta der Kernkräfte.
Geltungsstufen: GESPERRT / NUKLEARCHARTIERT / GRUNDLEGEND_NUKLEARCHARTIERT
Parent: ZerfallsNormSatz (#308)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from .zerfalls_norm import ZerfallsNormGeltung, ZerfallsNormSatz, build_zerfalls_norm


# ---------------------------------------------------------------------------
# Geltung-Mapping
# ---------------------------------------------------------------------------

_GELTUNG_MAP: dict[ZerfallsNormGeltung, "NuklearChartaGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[ZerfallsNormGeltung.GESPERRT] = NuklearChartaGeltung.GESPERRT
    _GELTUNG_MAP[ZerfallsNormGeltung.ZERFALLEN] = NuklearChartaGeltung.NUKLEARCHARTIERT
    _GELTUNG_MAP[ZerfallsNormGeltung.GRUNDLEGEND_ZERFALLEN] = NuklearChartaGeltung.GRUNDLEGEND_NUKLEARCHARTIERT


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class NuklearChartaTyp(Enum):
    SCHUTZ_NUKLEARSTRUKTUR = "schutz-nuklearstruktur"
    ORDNUNGS_NUKLEARSTRUKTUR = "ordnungs-nuklearstruktur"
    SOUVERAENITAETS_NUKLEARSTRUKTUR = "souveraenitaets-nuklearstruktur"


class NuklearChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class NuklearChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    NUKLEARCHARTIERT = "nuklearchartiert"
    GRUNDLEGEND_NUKLEARCHARTIERT = "grundlegend-nuklearchartiert"


_init_map()

# ---------------------------------------------------------------------------
# Typ & Prozedur lookup
# ---------------------------------------------------------------------------

_TYP_MAP: dict[NuklearChartaGeltung, NuklearChartaTyp] = {
    NuklearChartaGeltung.GESPERRT: NuklearChartaTyp.SCHUTZ_NUKLEARSTRUKTUR,
    NuklearChartaGeltung.NUKLEARCHARTIERT: NuklearChartaTyp.ORDNUNGS_NUKLEARSTRUKTUR,
    NuklearChartaGeltung.GRUNDLEGEND_NUKLEARCHARTIERT: NuklearChartaTyp.SOUVERAENITAETS_NUKLEARSTRUKTUR,
}

_PROZEDUR_MAP: dict[NuklearChartaGeltung, NuklearChartaProzedur] = {
    NuklearChartaGeltung.GESPERRT: NuklearChartaProzedur.NOTPROZEDUR,
    NuklearChartaGeltung.NUKLEARCHARTIERT: NuklearChartaProzedur.REGELPROTOKOLL,
    NuklearChartaGeltung.GRUNDLEGEND_NUKLEARCHARTIERT: NuklearChartaProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[NuklearChartaGeltung, float] = {
    NuklearChartaGeltung.GESPERRT: 0.0,
    NuklearChartaGeltung.NUKLEARCHARTIERT: 0.04,
    NuklearChartaGeltung.GRUNDLEGEND_NUKLEARCHARTIERT: 0.08,
}

_TIER_DELTA: dict[NuklearChartaGeltung, int] = {
    NuklearChartaGeltung.GESPERRT: 0,
    NuklearChartaGeltung.NUKLEARCHARTIERT: 1,
    NuklearChartaGeltung.GRUNDLEGEND_NUKLEARCHARTIERT: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class NuklearChartaNorm:
    nuklear_charta_id: str
    nuklear_charta_typ: NuklearChartaTyp
    prozedur: NuklearChartaProzedur
    geltung: NuklearChartaGeltung
    nuklear_charta_weight: float
    nuklear_charta_tier: int
    canonical: bool
    nuklear_charta_ids: tuple[str, ...]
    nuklear_charta_tags: tuple[str, ...]


@dataclass(frozen=True)
class NuklearCharta:
    charta_id: str
    zerfalls_norm: ZerfallsNormSatz
    normen: tuple[NuklearChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.nuklear_charta_id for n in self.normen if n.geltung is NuklearChartaGeltung.GESPERRT)

    @property
    def nuklearchartiert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.nuklear_charta_id for n in self.normen if n.geltung is NuklearChartaGeltung.NUKLEARCHARTIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.nuklear_charta_id for n in self.normen if n.geltung is NuklearChartaGeltung.GRUNDLEGEND_NUKLEARCHARTIERT)

    @property
    def charta_signal(self):
        if any(n.geltung is NuklearChartaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is NuklearChartaGeltung.NUKLEARCHARTIERT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-nuklearchartiert")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-nuklearchartiert")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_nuklear_charta(
    zerfalls_norm: ZerfallsNormSatz | None = None,
    *,
    charta_id: str = "nuklear-charta",
) -> NuklearCharta:
    if zerfalls_norm is None:
        zerfalls_norm = build_zerfalls_norm(norm_id=f"{charta_id}-norm")

    normen: list[NuklearChartaNorm] = []
    for parent_norm in zerfalls_norm.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.norm_id.removeprefix(f'{zerfalls_norm.norm_id}-')}"
        raw_weight = min(1.0, parent_norm.zerfalls_norm_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.zerfalls_norm_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is NuklearChartaGeltung.GRUNDLEGEND_NUKLEARCHARTIERT)
        normen.append(
            NuklearChartaNorm(
                nuklear_charta_id=new_id,
                nuklear_charta_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                nuklear_charta_weight=new_weight,
                nuklear_charta_tier=new_tier,
                canonical=is_canonical,
                nuklear_charta_ids=parent_norm.zerfalls_norm_ids + (new_id,),
                nuklear_charta_tags=parent_norm.zerfalls_norm_tags + (f"nuklear-charta:{new_geltung.value}",),
            )
        )
    return NuklearCharta(
        charta_id=charta_id,
        zerfalls_norm=zerfalls_norm,
        normen=tuple(normen),
    )
