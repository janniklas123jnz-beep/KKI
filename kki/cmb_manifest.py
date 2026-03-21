"""
#326 CmbManifest — Kosmische Mikrowellen-Hintergrundstrahlung als Basiswissen-Manifest.
Geltungsstufen: GESPERRT / CMBRADIIERT / GRUNDLEGEND_CMBRADIIERT
Parent: DunkleEnergiePakt (#325)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .dunkle_energie_pakt import (
    DunkleEnergieGeltung,
    DunkleEnergiePakt,
    build_dunkle_energie_pakt,
)

_GELTUNG_MAP: dict[DunkleEnergieGeltung, "CmbGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[DunkleEnergieGeltung.GESPERRT] = CmbGeltung.GESPERRT
    _GELTUNG_MAP[DunkleEnergieGeltung.DUNKELENERGISCH] = CmbGeltung.CMBRADIIERT
    _GELTUNG_MAP[DunkleEnergieGeltung.GRUNDLEGEND_DUNKELENERGISCH] = CmbGeltung.GRUNDLEGEND_CMBRADIIERT


class CmbTyp(Enum):
    SCHUTZ_CMB = "schutz-cmb"
    ORDNUNGS_CMB = "ordnungs-cmb"
    SOUVERAENITAETS_CMB = "souveraenitaets-cmb"


class CmbProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class CmbGeltung(Enum):
    GESPERRT = "gesperrt"
    CMBRADIIERT = "cmbradiiert"
    GRUNDLEGEND_CMBRADIIERT = "grundlegend-cmbradiiert"


_init_map()

_TYP_MAP: dict[CmbGeltung, CmbTyp] = {
    CmbGeltung.GESPERRT: CmbTyp.SCHUTZ_CMB,
    CmbGeltung.CMBRADIIERT: CmbTyp.ORDNUNGS_CMB,
    CmbGeltung.GRUNDLEGEND_CMBRADIIERT: CmbTyp.SOUVERAENITAETS_CMB,
}

_PROZEDUR_MAP: dict[CmbGeltung, CmbProzedur] = {
    CmbGeltung.GESPERRT: CmbProzedur.NOTPROZEDUR,
    CmbGeltung.CMBRADIIERT: CmbProzedur.REGELPROTOKOLL,
    CmbGeltung.GRUNDLEGEND_CMBRADIIERT: CmbProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[CmbGeltung, float] = {
    CmbGeltung.GESPERRT: 0.0,
    CmbGeltung.CMBRADIIERT: 0.04,
    CmbGeltung.GRUNDLEGEND_CMBRADIIERT: 0.08,
}

_TIER_DELTA: dict[CmbGeltung, int] = {
    CmbGeltung.GESPERRT: 0,
    CmbGeltung.CMBRADIIERT: 1,
    CmbGeltung.GRUNDLEGEND_CMBRADIIERT: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CmbNorm:
    cmb_manifest_id: str
    cmb_typ: CmbTyp
    prozedur: CmbProzedur
    geltung: CmbGeltung
    cmb_weight: float
    cmb_tier: int
    canonical: bool
    cmb_ids: tuple[str, ...]
    cmb_tags: tuple[str, ...]


@dataclass(frozen=True)
class CmbManifest:
    manifest_id: str
    dunkle_energie_pakt: DunkleEnergiePakt
    normen: tuple[CmbNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.cmb_manifest_id for n in self.normen if n.geltung is CmbGeltung.GESPERRT)

    @property
    def cmbradiiert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.cmb_manifest_id for n in self.normen if n.geltung is CmbGeltung.CMBRADIIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.cmb_manifest_id for n in self.normen if n.geltung is CmbGeltung.GRUNDLEGEND_CMBRADIIERT)

    @property
    def manifest_signal(self):
        if any(n.geltung is CmbGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-gesperrt")
        elif any(n.geltung is CmbGeltung.CMBRADIIERT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-cmbradiiert")
        from types import SimpleNamespace
        return SimpleNamespace(status="manifest-grundlegend-cmbradiiert")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_cmb_manifest(
    dunkle_energie_pakt: DunkleEnergiePakt | None = None,
    *,
    manifest_id: str = "cmb-manifest",
) -> CmbManifest:
    if dunkle_energie_pakt is None:
        dunkle_energie_pakt = build_dunkle_energie_pakt(pakt_id=f"{manifest_id}-pakt")

    normen: list[CmbNorm] = []
    for parent_norm in dunkle_energie_pakt.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{manifest_id}-{parent_norm.dunkle_energie_pakt_id.removeprefix(f'{dunkle_energie_pakt.pakt_id}-')}"
        raw_weight = min(1.0, parent_norm.dunkle_energie_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.dunkle_energie_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is CmbGeltung.GRUNDLEGEND_CMBRADIIERT)
        normen.append(
            CmbNorm(
                cmb_manifest_id=new_id,
                cmb_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                cmb_weight=new_weight,
                cmb_tier=new_tier,
                canonical=is_canonical,
                cmb_ids=parent_norm.dunkle_energie_ids + (new_id,),
                cmb_tags=parent_norm.dunkle_energie_tags + (f"cmb-manifest:{new_geltung.value}",),
            )
        )
    return CmbManifest(
        manifest_id=manifest_id,
        dunkle_energie_pakt=dunkle_energie_pakt,
        normen=tuple(normen),
    )
