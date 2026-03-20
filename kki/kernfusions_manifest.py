"""
#306 KernfusionsManifest — Kernfusion als Governance-Manifest der Vereinigung.
Geltungsstufen: GESPERRT / KERNVERSCHMOLZEN / GRUNDLEGEND_KERNVERSCHMOLZEN
Parent: KernspaltungsPakt (#305)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from .kernspaltungs_pakt import KernspaltungsGeltung, KernspaltungsPakt, build_kernspaltungs_pakt


# ---------------------------------------------------------------------------
# Geltung-Mapping
# ---------------------------------------------------------------------------

_GELTUNG_MAP: dict[KernspaltungsGeltung, "KernfusionsGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[KernspaltungsGeltung.GESPERRT] = KernfusionsGeltung.GESPERRT
    _GELTUNG_MAP[KernspaltungsGeltung.KERNGESPALTEN] = KernfusionsGeltung.KERNVERSCHMOLZEN
    _GELTUNG_MAP[KernspaltungsGeltung.GRUNDLEGEND_KERNGESPALTEN] = KernfusionsGeltung.GRUNDLEGEND_KERNVERSCHMOLZEN


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class KernfusionsTyp(Enum):
    SCHUTZ_KERNFUSION = "schutz-kernfusion"
    ORDNUNGS_KERNFUSION = "ordnungs-kernfusion"
    SOUVERAENITAETS_KERNFUSION = "souveraenitaets-kernfusion"


class KernfusionsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KernfusionsGeltung(Enum):
    GESPERRT = "gesperrt"
    KERNVERSCHMOLZEN = "kernverschmolzen"
    GRUNDLEGEND_KERNVERSCHMOLZEN = "grundlegend-kernverschmolzen"


_init_map()

# ---------------------------------------------------------------------------
# Typ & Prozedur lookup
# ---------------------------------------------------------------------------

_TYP_MAP: dict[KernfusionsGeltung, KernfusionsTyp] = {
    KernfusionsGeltung.GESPERRT: KernfusionsTyp.SCHUTZ_KERNFUSION,
    KernfusionsGeltung.KERNVERSCHMOLZEN: KernfusionsTyp.ORDNUNGS_KERNFUSION,
    KernfusionsGeltung.GRUNDLEGEND_KERNVERSCHMOLZEN: KernfusionsTyp.SOUVERAENITAETS_KERNFUSION,
}

_PROZEDUR_MAP: dict[KernfusionsGeltung, KernfusionsProzedur] = {
    KernfusionsGeltung.GESPERRT: KernfusionsProzedur.NOTPROZEDUR,
    KernfusionsGeltung.KERNVERSCHMOLZEN: KernfusionsProzedur.REGELPROTOKOLL,
    KernfusionsGeltung.GRUNDLEGEND_KERNVERSCHMOLZEN: KernfusionsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[KernfusionsGeltung, float] = {
    KernfusionsGeltung.GESPERRT: 0.0,
    KernfusionsGeltung.KERNVERSCHMOLZEN: 0.04,
    KernfusionsGeltung.GRUNDLEGEND_KERNVERSCHMOLZEN: 0.08,
}

_TIER_DELTA: dict[KernfusionsGeltung, int] = {
    KernfusionsGeltung.GESPERRT: 0,
    KernfusionsGeltung.KERNVERSCHMOLZEN: 1,
    KernfusionsGeltung.GRUNDLEGEND_KERNVERSCHMOLZEN: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class KernfusionsNorm:
    kernfusions_manifest_id: str
    kernfusions_typ: KernfusionsTyp
    prozedur: KernfusionsProzedur
    geltung: KernfusionsGeltung
    kernfusions_weight: float
    kernfusions_tier: int
    canonical: bool
    kernfusions_ids: tuple[str, ...]
    kernfusions_tags: tuple[str, ...]


@dataclass(frozen=True)
class KernfusionsManifest:
    manifest_id: str
    kernspaltungs_pakt: KernspaltungsPakt
    normen: tuple[KernfusionsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kernfusions_manifest_id for n in self.normen if n.geltung is KernfusionsGeltung.GESPERRT)

    @property
    def kernverschmolzen_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kernfusions_manifest_id for n in self.normen if n.geltung is KernfusionsGeltung.KERNVERSCHMOLZEN)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kernfusions_manifest_id for n in self.normen if n.geltung is KernfusionsGeltung.GRUNDLEGEND_KERNVERSCHMOLZEN)

    @property
    def manifest_signal(self):
        if any(n.geltung is KernfusionsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-gesperrt")
        elif any(n.geltung is KernfusionsGeltung.KERNVERSCHMOLZEN for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-kernverschmolzen")
        from types import SimpleNamespace
        return SimpleNamespace(status="manifest-grundlegend-kernverschmolzen")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_kernfusions_manifest(
    kernspaltungs_pakt: KernspaltungsPakt | None = None,
    *,
    manifest_id: str = "kernfusions-manifest",
) -> KernfusionsManifest:
    if kernspaltungs_pakt is None:
        kernspaltungs_pakt = build_kernspaltungs_pakt(pakt_id=f"{manifest_id}-pakt")

    normen: list[KernfusionsNorm] = []
    for parent_norm in kernspaltungs_pakt.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{manifest_id}-{parent_norm.kernspaltungs_pakt_id.removeprefix(f'{kernspaltungs_pakt.pakt_id}-')}"
        raw_weight = min(1.0, parent_norm.kernspaltungs_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kernspaltungs_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KernfusionsGeltung.GRUNDLEGEND_KERNVERSCHMOLZEN)
        normen.append(
            KernfusionsNorm(
                kernfusions_manifest_id=new_id,
                kernfusions_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kernfusions_weight=new_weight,
                kernfusions_tier=new_tier,
                canonical=is_canonical,
                kernfusions_ids=parent_norm.kernspaltungs_ids + (new_id,),
                kernfusions_tags=parent_norm.kernspaltungs_tags + (f"kernfusions-manifest:{new_geltung.value}",),
            )
        )
    return KernfusionsManifest(
        manifest_id=manifest_id,
        kernspaltungs_pakt=kernspaltungs_pakt,
        normen=tuple(normen),
    )
