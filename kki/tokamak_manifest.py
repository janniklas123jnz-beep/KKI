"""
#356 TokamakManifest — Der Tokamak (toroidale Kammer + Magnetspulen) löst das
Confinement-Problem durch toroidale Topologie. Das Grad-Shafranov-Gleichgewicht
ist vollständig berechenbar — Interpretierbarkeit als Voraussetzung für Kontrolle.
ITER: 35 Nationen × 20 Mrd € × 60 Jahre Geduld = kooperative Governance.
Geltungsstufen: GESPERRT / TOKAMAKISCH / GRUNDLEGEND_TOKAMAKISCH
Parent: ZPinchPakt (#355)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .z_pinch_pakt import (
    ZPinchGeltung,
    ZPinchPakt,
    build_z_pinch_pakt,
)

_GELTUNG_MAP: dict[ZPinchGeltung, "TokamakGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[ZPinchGeltung.GESPERRT] = TokamakGeltung.GESPERRT
    _GELTUNG_MAP[ZPinchGeltung.ZPINCHEND] = TokamakGeltung.TOKAMAKISCH
    _GELTUNG_MAP[ZPinchGeltung.GRUNDLEGEND_ZPINCHEND] = TokamakGeltung.GRUNDLEGEND_TOKAMAKISCH


class TokamakTyp(Enum):
    SCHUTZ_TOKAMAK = "schutz-tokamak"
    ORDNUNGS_TOKAMAK = "ordnungs-tokamak"
    SOUVERAENITAETS_TOKAMAK = "souveraenitaets-tokamak"


class TokamakProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class TokamakGeltung(Enum):
    GESPERRT = "gesperrt"
    TOKAMAKISCH = "tokamakisch"
    GRUNDLEGEND_TOKAMAKISCH = "grundlegend-tokamakisch"


_init_map()

_TYP_MAP: dict[TokamakGeltung, TokamakTyp] = {
    TokamakGeltung.GESPERRT: TokamakTyp.SCHUTZ_TOKAMAK,
    TokamakGeltung.TOKAMAKISCH: TokamakTyp.ORDNUNGS_TOKAMAK,
    TokamakGeltung.GRUNDLEGEND_TOKAMAKISCH: TokamakTyp.SOUVERAENITAETS_TOKAMAK,
}

_PROZEDUR_MAP: dict[TokamakGeltung, TokamakProzedur] = {
    TokamakGeltung.GESPERRT: TokamakProzedur.NOTPROZEDUR,
    TokamakGeltung.TOKAMAKISCH: TokamakProzedur.REGELPROTOKOLL,
    TokamakGeltung.GRUNDLEGEND_TOKAMAKISCH: TokamakProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[TokamakGeltung, float] = {
    TokamakGeltung.GESPERRT: 0.0,
    TokamakGeltung.TOKAMAKISCH: 0.04,
    TokamakGeltung.GRUNDLEGEND_TOKAMAKISCH: 0.08,
}

_TIER_DELTA: dict[TokamakGeltung, int] = {
    TokamakGeltung.GESPERRT: 0,
    TokamakGeltung.TOKAMAKISCH: 1,
    TokamakGeltung.GRUNDLEGEND_TOKAMAKISCH: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TokamakNorm:
    tokamak_manifest_id: str
    tokamak_typ: TokamakTyp
    prozedur: TokamakProzedur
    geltung: TokamakGeltung
    tokamak_weight: float
    tokamak_tier: int
    canonical: bool
    tokamak_ids: tuple[str, ...]
    tokamak_tags: tuple[str, ...]


@dataclass(frozen=True)
class TokamakManifest:
    manifest_id: str
    z_pinch_pakt: ZPinchPakt
    normen: tuple[TokamakNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.tokamak_manifest_id for n in self.normen if n.geltung is TokamakGeltung.GESPERRT)

    @property
    def tokamakisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.tokamak_manifest_id for n in self.normen if n.geltung is TokamakGeltung.TOKAMAKISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.tokamak_manifest_id for n in self.normen if n.geltung is TokamakGeltung.GRUNDLEGEND_TOKAMAKISCH)

    @property
    def manifest_signal(self):
        if any(n.geltung is TokamakGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-gesperrt")
        elif any(n.geltung is TokamakGeltung.TOKAMAKISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-tokamakisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="manifest-grundlegend-tokamakisch")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_tokamak_manifest(
    z_pinch_pakt: ZPinchPakt | None = None,
    *,
    manifest_id: str = "tokamak-manifest",
) -> TokamakManifest:
    if z_pinch_pakt is None:
        z_pinch_pakt = build_z_pinch_pakt(pakt_id=f"{manifest_id}-pakt")

    normen: list[TokamakNorm] = []
    for parent_norm in z_pinch_pakt.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{manifest_id}-{parent_norm.z_pinch_pakt_id.removeprefix(f'{z_pinch_pakt.pakt_id}-')}"
        raw_weight = min(1.0, parent_norm.z_pinch_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.z_pinch_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is TokamakGeltung.GRUNDLEGEND_TOKAMAKISCH)
        normen.append(
            TokamakNorm(
                tokamak_manifest_id=new_id,
                tokamak_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                tokamak_weight=new_weight,
                tokamak_tier=new_tier,
                canonical=is_canonical,
                tokamak_ids=parent_norm.z_pinch_ids + (new_id,),
                tokamak_tags=parent_norm.z_pinch_tags + (f"tokamak:{new_geltung.value}",),
            )
        )
    return TokamakManifest(
        manifest_id=manifest_id,
        z_pinch_pakt=z_pinch_pakt,
        normen=tuple(normen),
    )
