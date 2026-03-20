"""
#305 KernspaltungsPakt — Kernspaltung als Governance-Pakt der Kettenreaktion.
Geltungsstufen: GESPERRT / KERNGESPALTEN / GRUNDLEGEND_KERNGESPALTEN
Parent: SchwachKodex (#304)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from .schwach_kodex import SchwachGeltung, SchwachKodex, build_schwach_kodex


# ---------------------------------------------------------------------------
# Geltung-Mapping
# ---------------------------------------------------------------------------

_GELTUNG_MAP: dict[SchwachGeltung, "KernspaltungsGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[SchwachGeltung.GESPERRT] = KernspaltungsGeltung.GESPERRT
    _GELTUNG_MAP[SchwachGeltung.SCHWACH] = KernspaltungsGeltung.KERNGESPALTEN
    _GELTUNG_MAP[SchwachGeltung.GRUNDLEGEND_SCHWACH] = KernspaltungsGeltung.GRUNDLEGEND_KERNGESPALTEN


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class KernspaltungsTyp(Enum):
    SCHUTZ_KERNSPALTUNG = "schutz-kernspaltung"
    ORDNUNGS_KERNSPALTUNG = "ordnungs-kernspaltung"
    SOUVERAENITAETS_KERNSPALTUNG = "souveraenitaets-kernspaltung"


class KernspaltungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KernspaltungsGeltung(Enum):
    GESPERRT = "gesperrt"
    KERNGESPALTEN = "kerngespalten"
    GRUNDLEGEND_KERNGESPALTEN = "grundlegend-kerngespalten"


_init_map()

# ---------------------------------------------------------------------------
# Typ & Prozedur lookup
# ---------------------------------------------------------------------------

_TYP_MAP: dict[KernspaltungsGeltung, KernspaltungsTyp] = {
    KernspaltungsGeltung.GESPERRT: KernspaltungsTyp.SCHUTZ_KERNSPALTUNG,
    KernspaltungsGeltung.KERNGESPALTEN: KernspaltungsTyp.ORDNUNGS_KERNSPALTUNG,
    KernspaltungsGeltung.GRUNDLEGEND_KERNGESPALTEN: KernspaltungsTyp.SOUVERAENITAETS_KERNSPALTUNG,
}

_PROZEDUR_MAP: dict[KernspaltungsGeltung, KernspaltungsProzedur] = {
    KernspaltungsGeltung.GESPERRT: KernspaltungsProzedur.NOTPROZEDUR,
    KernspaltungsGeltung.KERNGESPALTEN: KernspaltungsProzedur.REGELPROTOKOLL,
    KernspaltungsGeltung.GRUNDLEGEND_KERNGESPALTEN: KernspaltungsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[KernspaltungsGeltung, float] = {
    KernspaltungsGeltung.GESPERRT: 0.0,
    KernspaltungsGeltung.KERNGESPALTEN: 0.04,
    KernspaltungsGeltung.GRUNDLEGEND_KERNGESPALTEN: 0.08,
}

_TIER_DELTA: dict[KernspaltungsGeltung, int] = {
    KernspaltungsGeltung.GESPERRT: 0,
    KernspaltungsGeltung.KERNGESPALTEN: 1,
    KernspaltungsGeltung.GRUNDLEGEND_KERNGESPALTEN: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class KernspaltungsNorm:
    kernspaltungs_pakt_id: str
    kernspaltungs_typ: KernspaltungsTyp
    prozedur: KernspaltungsProzedur
    geltung: KernspaltungsGeltung
    kernspaltungs_weight: float
    kernspaltungs_tier: int
    canonical: bool
    kernspaltungs_ids: tuple[str, ...]
    kernspaltungs_tags: tuple[str, ...]


@dataclass(frozen=True)
class KernspaltungsPakt:
    pakt_id: str
    schwach_kodex: SchwachKodex
    normen: tuple[KernspaltungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kernspaltungs_pakt_id for n in self.normen if n.geltung is KernspaltungsGeltung.GESPERRT)

    @property
    def kerngespalten_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kernspaltungs_pakt_id for n in self.normen if n.geltung is KernspaltungsGeltung.KERNGESPALTEN)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kernspaltungs_pakt_id for n in self.normen if n.geltung is KernspaltungsGeltung.GRUNDLEGEND_KERNGESPALTEN)

    @property
    def pakt_signal(self):
        if any(n.geltung is KernspaltungsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-gesperrt")
        elif any(n.geltung is KernspaltungsGeltung.KERNGESPALTEN for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-kerngespalten")
        from types import SimpleNamespace
        return SimpleNamespace(status="pakt-grundlegend-kerngespalten")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_kernspaltungs_pakt(
    schwach_kodex: SchwachKodex | None = None,
    *,
    pakt_id: str = "kernspaltungs-pakt",
) -> KernspaltungsPakt:
    if schwach_kodex is None:
        schwach_kodex = build_schwach_kodex(kodex_id=f"{pakt_id}-kodex")

    normen: list[KernspaltungsNorm] = []
    for parent_norm in schwach_kodex.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{pakt_id}-{parent_norm.schwach_kodex_id.removeprefix(f'{schwach_kodex.kodex_id}-')}"
        raw_weight = min(1.0, parent_norm.schwach_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.schwach_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KernspaltungsGeltung.GRUNDLEGEND_KERNGESPALTEN)
        normen.append(
            KernspaltungsNorm(
                kernspaltungs_pakt_id=new_id,
                kernspaltungs_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kernspaltungs_weight=new_weight,
                kernspaltungs_tier=new_tier,
                canonical=is_canonical,
                kernspaltungs_ids=parent_norm.schwach_ids + (new_id,),
                kernspaltungs_tags=parent_norm.schwach_tags + (f"kernspaltungs-pakt:{new_geltung.value}",),
            )
        )
    return KernspaltungsPakt(
        pakt_id=pakt_id,
        schwach_kodex=schwach_kodex,
        normen=tuple(normen),
    )
