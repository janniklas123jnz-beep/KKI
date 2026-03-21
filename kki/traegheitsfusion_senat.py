"""
#357 TraegheitsfusionSenat — Trägheitsfusion (ICF): 192 synchronisierte Laser
des NIF komprimieren ein Deuterium-Tritium-Pellet in Nanosekunden auf
Sterndichte. 2022 erstmals Q > 1 — beneficial energy out > energy in.
Governance unter extremem Zeitdruck erfordert präzise synchronisierte
kollektive Entscheidungsfindung.
Geltungsstufen: GESPERRT / TRAEGHEITSFUSIONIEREND / GRUNDLEGEND_TRAEGHEITSFUSIONIEREND
Parent: TokamakManifest (#356)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .tokamak_manifest import (
    TokamakGeltung,
    TokamakManifest,
    build_tokamak_manifest,
)

_GELTUNG_MAP: dict[TokamakGeltung, "TraegheitsfusionGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[TokamakGeltung.GESPERRT] = TraegheitsfusionGeltung.GESPERRT
    _GELTUNG_MAP[TokamakGeltung.TOKAMAKISCH] = TraegheitsfusionGeltung.TRAEGHEITSFUSIONIEREND
    _GELTUNG_MAP[TokamakGeltung.GRUNDLEGEND_TOKAMAKISCH] = TraegheitsfusionGeltung.GRUNDLEGEND_TRAEGHEITSFUSIONIEREND


class TraegheitsfusionTyp(Enum):
    SCHUTZ_TRAEGHEITSFUSION = "schutz-traegheitsfusion"
    ORDNUNGS_TRAEGHEITSFUSION = "ordnungs-traegheitsfusion"
    SOUVERAENITAETS_TRAEGHEITSFUSION = "souveraenitaets-traegheitsfusion"


class TraegheitsfusionProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class TraegheitsfusionGeltung(Enum):
    GESPERRT = "gesperrt"
    TRAEGHEITSFUSIONIEREND = "traegheitsfusionierend"
    GRUNDLEGEND_TRAEGHEITSFUSIONIEREND = "grundlegend-traegheitsfusionierend"


_init_map()

_TYP_MAP: dict[TraegheitsfusionGeltung, TraegheitsfusionTyp] = {
    TraegheitsfusionGeltung.GESPERRT: TraegheitsfusionTyp.SCHUTZ_TRAEGHEITSFUSION,
    TraegheitsfusionGeltung.TRAEGHEITSFUSIONIEREND: TraegheitsfusionTyp.ORDNUNGS_TRAEGHEITSFUSION,
    TraegheitsfusionGeltung.GRUNDLEGEND_TRAEGHEITSFUSIONIEREND: TraegheitsfusionTyp.SOUVERAENITAETS_TRAEGHEITSFUSION,
}

_PROZEDUR_MAP: dict[TraegheitsfusionGeltung, TraegheitsfusionProzedur] = {
    TraegheitsfusionGeltung.GESPERRT: TraegheitsfusionProzedur.NOTPROZEDUR,
    TraegheitsfusionGeltung.TRAEGHEITSFUSIONIEREND: TraegheitsfusionProzedur.REGELPROTOKOLL,
    TraegheitsfusionGeltung.GRUNDLEGEND_TRAEGHEITSFUSIONIEREND: TraegheitsfusionProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[TraegheitsfusionGeltung, float] = {
    TraegheitsfusionGeltung.GESPERRT: 0.0,
    TraegheitsfusionGeltung.TRAEGHEITSFUSIONIEREND: 0.04,
    TraegheitsfusionGeltung.GRUNDLEGEND_TRAEGHEITSFUSIONIEREND: 0.08,
}

_TIER_DELTA: dict[TraegheitsfusionGeltung, int] = {
    TraegheitsfusionGeltung.GESPERRT: 0,
    TraegheitsfusionGeltung.TRAEGHEITSFUSIONIEREND: 1,
    TraegheitsfusionGeltung.GRUNDLEGEND_TRAEGHEITSFUSIONIEREND: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TraegheitsfusionNorm:
    traegheitsfusion_senat_id: str
    traegheitsfusion_typ: TraegheitsfusionTyp
    prozedur: TraegheitsfusionProzedur
    geltung: TraegheitsfusionGeltung
    traegheitsfusion_weight: float
    traegheitsfusion_tier: int
    canonical: bool
    traegheitsfusion_ids: tuple[str, ...]
    traegheitsfusion_tags: tuple[str, ...]


@dataclass(frozen=True)
class TraegheitsfusionSenat:
    senat_id: str
    tokamak_manifest: TokamakManifest
    normen: tuple[TraegheitsfusionNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.traegheitsfusion_senat_id for n in self.normen if n.geltung is TraegheitsfusionGeltung.GESPERRT)

    @property
    def traegheitsfusionierend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.traegheitsfusion_senat_id for n in self.normen if n.geltung is TraegheitsfusionGeltung.TRAEGHEITSFUSIONIEREND)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.traegheitsfusion_senat_id for n in self.normen if n.geltung is TraegheitsfusionGeltung.GRUNDLEGEND_TRAEGHEITSFUSIONIEREND)

    @property
    def senat_signal(self):
        if any(n.geltung is TraegheitsfusionGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-gesperrt")
        elif any(n.geltung is TraegheitsfusionGeltung.TRAEGHEITSFUSIONIEREND for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-traegheitsfusionierend")
        from types import SimpleNamespace
        return SimpleNamespace(status="senat-grundlegend-traegheitsfusionierend")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_traegheitsfusion_senat(
    tokamak_manifest: TokamakManifest | None = None,
    *,
    senat_id: str = "traegheitsfusion-senat",
) -> TraegheitsfusionSenat:
    if tokamak_manifest is None:
        tokamak_manifest = build_tokamak_manifest(manifest_id=f"{senat_id}-manifest")

    normen: list[TraegheitsfusionNorm] = []
    for parent_norm in tokamak_manifest.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{senat_id}-{parent_norm.tokamak_manifest_id.removeprefix(f'{tokamak_manifest.manifest_id}-')}"
        raw_weight = min(1.0, parent_norm.tokamak_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.tokamak_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is TraegheitsfusionGeltung.GRUNDLEGEND_TRAEGHEITSFUSIONIEREND)
        normen.append(
            TraegheitsfusionNorm(
                traegheitsfusion_senat_id=new_id,
                traegheitsfusion_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                traegheitsfusion_weight=new_weight,
                traegheitsfusion_tier=new_tier,
                canonical=is_canonical,
                traegheitsfusion_ids=parent_norm.tokamak_ids + (new_id,),
                traegheitsfusion_tags=parent_norm.tokamak_tags + (f"traegheitsfusion:{new_geltung.value}",),
            )
        )
    return TraegheitsfusionSenat(
        senat_id=senat_id,
        tokamak_manifest=tokamak_manifest,
        normen=tuple(normen),
    )
