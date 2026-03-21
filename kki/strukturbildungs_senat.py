"""
#327 StrukturbildungsSenat — Emergente Großstruktur des Universums als Governance-Senat.
Geltungsstufen: GESPERRT / STRUKTURBILDEND / GRUNDLEGEND_STRUKTURBILDEND
Parent: CmbManifest (#326)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .cmb_manifest import (
    CmbGeltung,
    CmbManifest,
    build_cmb_manifest,
)

_GELTUNG_MAP: dict[CmbGeltung, "StrukturbildungsGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[CmbGeltung.GESPERRT] = StrukturbildungsGeltung.GESPERRT
    _GELTUNG_MAP[CmbGeltung.CMBRADIIERT] = StrukturbildungsGeltung.STRUKTURBILDEND
    _GELTUNG_MAP[CmbGeltung.GRUNDLEGEND_CMBRADIIERT] = StrukturbildungsGeltung.GRUNDLEGEND_STRUKTURBILDEND


class StrukturbildungsTyp(Enum):
    SCHUTZ_STRUKTURBILDUNG = "schutz-strukturbildung"
    ORDNUNGS_STRUKTURBILDUNG = "ordnungs-strukturbildung"
    SOUVERAENITAETS_STRUKTURBILDUNG = "souveraenitaets-strukturbildung"


class StrukturbildungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class StrukturbildungsGeltung(Enum):
    GESPERRT = "gesperrt"
    STRUKTURBILDEND = "strukturbildend"
    GRUNDLEGEND_STRUKTURBILDEND = "grundlegend-strukturbildend"


_init_map()

_TYP_MAP: dict[StrukturbildungsGeltung, StrukturbildungsTyp] = {
    StrukturbildungsGeltung.GESPERRT: StrukturbildungsTyp.SCHUTZ_STRUKTURBILDUNG,
    StrukturbildungsGeltung.STRUKTURBILDEND: StrukturbildungsTyp.ORDNUNGS_STRUKTURBILDUNG,
    StrukturbildungsGeltung.GRUNDLEGEND_STRUKTURBILDEND: StrukturbildungsTyp.SOUVERAENITAETS_STRUKTURBILDUNG,
}

_PROZEDUR_MAP: dict[StrukturbildungsGeltung, StrukturbildungsProzedur] = {
    StrukturbildungsGeltung.GESPERRT: StrukturbildungsProzedur.NOTPROZEDUR,
    StrukturbildungsGeltung.STRUKTURBILDEND: StrukturbildungsProzedur.REGELPROTOKOLL,
    StrukturbildungsGeltung.GRUNDLEGEND_STRUKTURBILDEND: StrukturbildungsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[StrukturbildungsGeltung, float] = {
    StrukturbildungsGeltung.GESPERRT: 0.0,
    StrukturbildungsGeltung.STRUKTURBILDEND: 0.04,
    StrukturbildungsGeltung.GRUNDLEGEND_STRUKTURBILDEND: 0.08,
}

_TIER_DELTA: dict[StrukturbildungsGeltung, int] = {
    StrukturbildungsGeltung.GESPERRT: 0,
    StrukturbildungsGeltung.STRUKTURBILDEND: 1,
    StrukturbildungsGeltung.GRUNDLEGEND_STRUKTURBILDEND: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class StrukturbildungsNorm:
    strukturbildungs_senat_id: str
    strukturbildungs_typ: StrukturbildungsTyp
    prozedur: StrukturbildungsProzedur
    geltung: StrukturbildungsGeltung
    strukturbildungs_weight: float
    strukturbildungs_tier: int
    canonical: bool
    strukturbildungs_ids: tuple[str, ...]
    strukturbildungs_tags: tuple[str, ...]


@dataclass(frozen=True)
class StrukturbildungsSenat:
    senat_id: str
    cmb_manifest: CmbManifest
    normen: tuple[StrukturbildungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.strukturbildungs_senat_id for n in self.normen if n.geltung is StrukturbildungsGeltung.GESPERRT)

    @property
    def strukturbildend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.strukturbildungs_senat_id for n in self.normen if n.geltung is StrukturbildungsGeltung.STRUKTURBILDEND)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.strukturbildungs_senat_id for n in self.normen if n.geltung is StrukturbildungsGeltung.GRUNDLEGEND_STRUKTURBILDEND)

    @property
    def senat_signal(self):
        if any(n.geltung is StrukturbildungsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-gesperrt")
        elif any(n.geltung is StrukturbildungsGeltung.STRUKTURBILDEND for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-strukturbildend")
        from types import SimpleNamespace
        return SimpleNamespace(status="senat-grundlegend-strukturbildend")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_strukturbildungs_senat(
    cmb_manifest: CmbManifest | None = None,
    *,
    senat_id: str = "strukturbildungs-senat",
) -> StrukturbildungsSenat:
    if cmb_manifest is None:
        cmb_manifest = build_cmb_manifest(manifest_id=f"{senat_id}-manifest")

    normen: list[StrukturbildungsNorm] = []
    for parent_norm in cmb_manifest.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{senat_id}-{parent_norm.cmb_manifest_id.removeprefix(f'{cmb_manifest.manifest_id}-')}"
        raw_weight = min(1.0, parent_norm.cmb_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.cmb_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is StrukturbildungsGeltung.GRUNDLEGEND_STRUKTURBILDEND)
        normen.append(
            StrukturbildungsNorm(
                strukturbildungs_senat_id=new_id,
                strukturbildungs_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                strukturbildungs_weight=new_weight,
                strukturbildungs_tier=new_tier,
                canonical=is_canonical,
                strukturbildungs_ids=parent_norm.cmb_ids + (new_id,),
                strukturbildungs_tags=parent_norm.cmb_tags + (f"strukturbildungs-senat:{new_geltung.value}",),
            )
        )
    return StrukturbildungsSenat(
        senat_id=senat_id,
        cmb_manifest=cmb_manifest,
        normen=tuple(normen),
    )
