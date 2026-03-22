"""
#436 WahrnehmungsManifest — Wahrnehmung: Predictive Coding und Bayesianische Wahrnehmung.
Helmholtz (1867): Wahrnehmung als "unbewusster Schluss" — Inferenz über die Welt.
Rao & Ballard (1999): Predictive Coding im visuellen Kortex — Top-Down-Priors vs. Bottom-Up.
Friston (2010): Free Energy Principle — Gehirn minimiert Überraschung (Surprise).
Leitsterns Agenten = Predictive-Coding-Einheiten: erwarten, vergleichen, aktualisieren.
Geltungsstufen: GESPERRT / WAHRNEHMEND / GRUNDLEGEND_WAHRNEHMEND
Parent: BewusstseinsPakt (#435)
Block #431–#440: Neurowissenschaften & Kognition
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bewusstseins_pakt import (
    BewusstseinsPakt,
    BewusstseinsPaktGeltung,
    build_bewusstseins_pakt,
)

_GELTUNG_MAP: dict[BewusstseinsPaktGeltung, "WahrnehmungsManifestGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[BewusstseinsPaktGeltung.GESPERRT] = WahrnehmungsManifestGeltung.GESPERRT
    _GELTUNG_MAP[BewusstseinsPaktGeltung.BEWUSST] = WahrnehmungsManifestGeltung.WAHRNEHMEND
    _GELTUNG_MAP[BewusstseinsPaktGeltung.GRUNDLEGEND_BEWUSST] = WahrnehmungsManifestGeltung.GRUNDLEGEND_WAHRNEHMEND


class WahrnehmungsManifestTyp(Enum):
    SCHUTZ_WAHRNEHMUNG = "schutz-wahrnehmung"
    ORDNUNGS_WAHRNEHMUNG = "ordnungs-wahrnehmung"
    SOUVERAENITAETS_WAHRNEHMUNG = "souveraenitaets-wahrnehmung"


class WahrnehmungsManifestProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class WahrnehmungsManifestGeltung(Enum):
    GESPERRT = "gesperrt"
    WAHRNEHMEND = "wahrnehmend"
    GRUNDLEGEND_WAHRNEHMEND = "grundlegend-wahrnehmend"


_init_map()

_TYP_MAP: dict[WahrnehmungsManifestGeltung, WahrnehmungsManifestTyp] = {
    WahrnehmungsManifestGeltung.GESPERRT: WahrnehmungsManifestTyp.SCHUTZ_WAHRNEHMUNG,
    WahrnehmungsManifestGeltung.WAHRNEHMEND: WahrnehmungsManifestTyp.ORDNUNGS_WAHRNEHMUNG,
    WahrnehmungsManifestGeltung.GRUNDLEGEND_WAHRNEHMEND: WahrnehmungsManifestTyp.SOUVERAENITAETS_WAHRNEHMUNG,
}

_PROZEDUR_MAP: dict[WahrnehmungsManifestGeltung, WahrnehmungsManifestProzedur] = {
    WahrnehmungsManifestGeltung.GESPERRT: WahrnehmungsManifestProzedur.NOTPROZEDUR,
    WahrnehmungsManifestGeltung.WAHRNEHMEND: WahrnehmungsManifestProzedur.REGELPROTOKOLL,
    WahrnehmungsManifestGeltung.GRUNDLEGEND_WAHRNEHMEND: WahrnehmungsManifestProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[WahrnehmungsManifestGeltung, float] = {
    WahrnehmungsManifestGeltung.GESPERRT: 0.0,
    WahrnehmungsManifestGeltung.WAHRNEHMEND: 0.04,
    WahrnehmungsManifestGeltung.GRUNDLEGEND_WAHRNEHMEND: 0.08,
}

_TIER_DELTA: dict[WahrnehmungsManifestGeltung, int] = {
    WahrnehmungsManifestGeltung.GESPERRT: 0,
    WahrnehmungsManifestGeltung.WAHRNEHMEND: 1,
    WahrnehmungsManifestGeltung.GRUNDLEGEND_WAHRNEHMEND: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class WahrnehmungsManifestNorm:
    wahrnehmungs_manifest_id: str
    wahrnehmung_typ: WahrnehmungsManifestTyp
    prozedur: WahrnehmungsManifestProzedur
    geltung: WahrnehmungsManifestGeltung
    wahrnehmung_weight: float
    wahrnehmung_tier: int
    canonical: bool
    wahrnehmung_ids: tuple[str, ...]
    wahrnehmung_tags: tuple[str, ...]


@dataclass(frozen=True)
class WahrnehmungsManifest:
    manifest_id: str
    bewusstseins_pakt: BewusstseinsPakt
    normen: tuple[WahrnehmungsManifestNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.wahrnehmungs_manifest_id for n in self.normen if n.geltung is WahrnehmungsManifestGeltung.GESPERRT)

    @property
    def wahrnehmend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.wahrnehmungs_manifest_id for n in self.normen if n.geltung is WahrnehmungsManifestGeltung.WAHRNEHMEND)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.wahrnehmungs_manifest_id for n in self.normen if n.geltung is WahrnehmungsManifestGeltung.GRUNDLEGEND_WAHRNEHMEND)

    @property
    def manifest_signal(self):
        if any(n.geltung is WahrnehmungsManifestGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-gesperrt")
        elif any(n.geltung is WahrnehmungsManifestGeltung.WAHRNEHMEND for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-wahrnehmend")
        from types import SimpleNamespace
        return SimpleNamespace(status="manifest-grundlegend-wahrnehmend")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_wahrnehmungs_manifest(
    bewusstseins_pakt: BewusstseinsPakt | None = None,
    *,
    manifest_id: str = "wahrnehmungs-manifest",
) -> WahrnehmungsManifest:
    if bewusstseins_pakt is None:
        bewusstseins_pakt = build_bewusstseins_pakt(pakt_id=f"{manifest_id}-pakt")

    normen: list[WahrnehmungsManifestNorm] = []
    for parent_norm in bewusstseins_pakt.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{manifest_id}-{parent_norm.bewusstseins_pakt_id.removeprefix(f'{bewusstseins_pakt.pakt_id}-')}"
        raw_weight = min(1.0, parent_norm.bewusstsein_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.bewusstsein_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is WahrnehmungsManifestGeltung.GRUNDLEGEND_WAHRNEHMEND)
        normen.append(
            WahrnehmungsManifestNorm(
                wahrnehmungs_manifest_id=new_id,
                wahrnehmung_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                wahrnehmung_weight=new_weight,
                wahrnehmung_tier=new_tier,
                canonical=is_canonical,
                wahrnehmung_ids=parent_norm.bewusstsein_ids + (new_id,),
                wahrnehmung_tags=parent_norm.bewusstsein_tags + (f"wahrnehmungs-manifest:{new_geltung.value}",),
            )
        )
    return WahrnehmungsManifest(
        manifest_id=manifest_id,
        bewusstseins_pakt=bewusstseins_pakt,
        normen=tuple(normen),
    )
