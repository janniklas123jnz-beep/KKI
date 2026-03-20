"""
#310 KernphysikVerfassung — Block-Krone des Kernphysik-Blocks #301–#310.
Verfassung der Nuklearstruktur als höchste Governance-Instanz des Blocks.
Geltungsstufen: GESPERRT / KERNPHYSIKVERFASST / GRUNDLEGEND_KERNPHYSIKVERFASST
Parent: NuklearCharta (#309)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from .nuklear_charta import NuklearCharta, NuklearChartaGeltung, build_nuklear_charta


# ---------------------------------------------------------------------------
# Geltung-Mapping
# ---------------------------------------------------------------------------

_GELTUNG_MAP: dict[NuklearChartaGeltung, "KernphysikVerfassungsGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[NuklearChartaGeltung.GESPERRT] = KernphysikVerfassungsGeltung.GESPERRT
    _GELTUNG_MAP[NuklearChartaGeltung.NUKLEARCHARTIERT] = KernphysikVerfassungsGeltung.KERNPHYSIKVERFASST
    _GELTUNG_MAP[NuklearChartaGeltung.GRUNDLEGEND_NUKLEARCHARTIERT] = KernphysikVerfassungsGeltung.GRUNDLEGEND_KERNPHYSIKVERFASST


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class KernphysikVerfassungsTyp(Enum):
    SCHUTZ_KERNPHYSIKVERFASSUNG = "schutz-kernphysikverfassung"
    ORDNUNGS_KERNPHYSIKVERFASSUNG = "ordnungs-kernphysikverfassung"
    SOUVERAENITAETS_KERNPHYSIKVERFASSUNG = "souveraenitaets-kernphysikverfassung"


class KernphysikVerfassungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KernphysikVerfassungsGeltung(Enum):
    GESPERRT = "gesperrt"
    KERNPHYSIKVERFASST = "kernphysikverfasst"
    GRUNDLEGEND_KERNPHYSIKVERFASST = "grundlegend-kernphysikverfasst"


_init_map()

# ---------------------------------------------------------------------------
# Typ & Prozedur lookup
# ---------------------------------------------------------------------------

_TYP_MAP: dict[KernphysikVerfassungsGeltung, KernphysikVerfassungsTyp] = {
    KernphysikVerfassungsGeltung.GESPERRT: KernphysikVerfassungsTyp.SCHUTZ_KERNPHYSIKVERFASSUNG,
    KernphysikVerfassungsGeltung.KERNPHYSIKVERFASST: KernphysikVerfassungsTyp.ORDNUNGS_KERNPHYSIKVERFASSUNG,
    KernphysikVerfassungsGeltung.GRUNDLEGEND_KERNPHYSIKVERFASST: KernphysikVerfassungsTyp.SOUVERAENITAETS_KERNPHYSIKVERFASSUNG,
}

_PROZEDUR_MAP: dict[KernphysikVerfassungsGeltung, KernphysikVerfassungsProzedur] = {
    KernphysikVerfassungsGeltung.GESPERRT: KernphysikVerfassungsProzedur.NOTPROZEDUR,
    KernphysikVerfassungsGeltung.KERNPHYSIKVERFASST: KernphysikVerfassungsProzedur.REGELPROTOKOLL,
    KernphysikVerfassungsGeltung.GRUNDLEGEND_KERNPHYSIKVERFASST: KernphysikVerfassungsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[KernphysikVerfassungsGeltung, float] = {
    KernphysikVerfassungsGeltung.GESPERRT: 0.0,
    KernphysikVerfassungsGeltung.KERNPHYSIKVERFASST: 0.04,
    KernphysikVerfassungsGeltung.GRUNDLEGEND_KERNPHYSIKVERFASST: 0.08,
}

_TIER_DELTA: dict[KernphysikVerfassungsGeltung, int] = {
    KernphysikVerfassungsGeltung.GESPERRT: 0,
    KernphysikVerfassungsGeltung.KERNPHYSIKVERFASST: 1,
    KernphysikVerfassungsGeltung.GRUNDLEGEND_KERNPHYSIKVERFASST: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class KernphysikVerfassungsNorm:
    kernphysikverfassungs_id: str
    kernphysikverfassungs_typ: KernphysikVerfassungsTyp
    prozedur: KernphysikVerfassungsProzedur
    geltung: KernphysikVerfassungsGeltung
    kernphysikverfassungs_weight: float
    kernphysikverfassungs_tier: int
    canonical: bool
    kernphysikverfassungs_ids: tuple[str, ...]
    kernphysikverfassungs_tags: tuple[str, ...]


@dataclass(frozen=True)
class KernphysikVerfassung:
    verfassung_id: str
    nuklear_charta: NuklearCharta
    normen: tuple[KernphysikVerfassungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kernphysikverfassungs_id for n in self.normen if n.geltung is KernphysikVerfassungsGeltung.GESPERRT)

    @property
    def kernphysikverfasst_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kernphysikverfassungs_id for n in self.normen if n.geltung is KernphysikVerfassungsGeltung.KERNPHYSIKVERFASST)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kernphysikverfassungs_id for n in self.normen if n.geltung is KernphysikVerfassungsGeltung.GRUNDLEGEND_KERNPHYSIKVERFASST)

    @property
    def verfassung_signal(self):
        if any(n.geltung is KernphysikVerfassungsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-gesperrt")
        elif any(n.geltung is KernphysikVerfassungsGeltung.KERNPHYSIKVERFASST for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-kernphysikverfasst")
        from types import SimpleNamespace
        return SimpleNamespace(status="verfassung-grundlegend-kernphysikverfasst")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_kernphysik_verfassung(
    nuklear_charta: NuklearCharta | None = None,
    *,
    verfassung_id: str = "kernphysik-verfassung",
) -> KernphysikVerfassung:
    if nuklear_charta is None:
        nuklear_charta = build_nuklear_charta(charta_id=f"{verfassung_id}-charta")

    normen: list[KernphysikVerfassungsNorm] = []
    for parent_norm in nuklear_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{verfassung_id}-{parent_norm.nuklear_charta_id.removeprefix(f'{nuklear_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.nuklear_charta_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.nuklear_charta_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KernphysikVerfassungsGeltung.GRUNDLEGEND_KERNPHYSIKVERFASST)
        normen.append(
            KernphysikVerfassungsNorm(
                kernphysikverfassungs_id=new_id,
                kernphysikverfassungs_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kernphysikverfassungs_weight=new_weight,
                kernphysikverfassungs_tier=new_tier,
                canonical=is_canonical,
                kernphysikverfassungs_ids=parent_norm.nuklear_charta_ids + (new_id,),
                kernphysikverfassungs_tags=parent_norm.nuklear_charta_tags + (f"kernphysik-verfassung:{new_geltung.value}",),
            )
        )
    return KernphysikVerfassung(
        verfassung_id=verfassung_id,
        nuklear_charta=nuklear_charta,
        normen=tuple(normen),
    )
