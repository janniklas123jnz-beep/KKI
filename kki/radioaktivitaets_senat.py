"""
#307 RadioaktivitaetsSenat — Radioaktivität als Governance-Senat des Zerfalls.
Geltungsstufen: GESPERRT / RADIOAKTIV / GRUNDLEGEND_RADIOAKTIV
Parent: KernfusionsManifest (#306)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from .kernfusions_manifest import KernfusionsGeltung, KernfusionsManifest, build_kernfusions_manifest


# ---------------------------------------------------------------------------
# Geltung-Mapping
# ---------------------------------------------------------------------------

_GELTUNG_MAP: dict[KernfusionsGeltung, "RadioaktivitaetsGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[KernfusionsGeltung.GESPERRT] = RadioaktivitaetsGeltung.GESPERRT
    _GELTUNG_MAP[KernfusionsGeltung.KERNVERSCHMOLZEN] = RadioaktivitaetsGeltung.RADIOAKTIV
    _GELTUNG_MAP[KernfusionsGeltung.GRUNDLEGEND_KERNVERSCHMOLZEN] = RadioaktivitaetsGeltung.GRUNDLEGEND_RADIOAKTIV


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class RadioaktivitaetsTyp(Enum):
    SCHUTZ_RADIOAKTIVITAET = "schutz-radioaktivitaet"
    ORDNUNGS_RADIOAKTIVITAET = "ordnungs-radioaktivitaet"
    SOUVERAENITAETS_RADIOAKTIVITAET = "souveraenitaets-radioaktivitaet"


class RadioaktivitaetsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class RadioaktivitaetsGeltung(Enum):
    GESPERRT = "gesperrt"
    RADIOAKTIV = "radioaktiv"
    GRUNDLEGEND_RADIOAKTIV = "grundlegend-radioaktiv"


_init_map()

# ---------------------------------------------------------------------------
# Typ & Prozedur lookup
# ---------------------------------------------------------------------------

_TYP_MAP: dict[RadioaktivitaetsGeltung, RadioaktivitaetsTyp] = {
    RadioaktivitaetsGeltung.GESPERRT: RadioaktivitaetsTyp.SCHUTZ_RADIOAKTIVITAET,
    RadioaktivitaetsGeltung.RADIOAKTIV: RadioaktivitaetsTyp.ORDNUNGS_RADIOAKTIVITAET,
    RadioaktivitaetsGeltung.GRUNDLEGEND_RADIOAKTIV: RadioaktivitaetsTyp.SOUVERAENITAETS_RADIOAKTIVITAET,
}

_PROZEDUR_MAP: dict[RadioaktivitaetsGeltung, RadioaktivitaetsProzedur] = {
    RadioaktivitaetsGeltung.GESPERRT: RadioaktivitaetsProzedur.NOTPROZEDUR,
    RadioaktivitaetsGeltung.RADIOAKTIV: RadioaktivitaetsProzedur.REGELPROTOKOLL,
    RadioaktivitaetsGeltung.GRUNDLEGEND_RADIOAKTIV: RadioaktivitaetsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[RadioaktivitaetsGeltung, float] = {
    RadioaktivitaetsGeltung.GESPERRT: 0.0,
    RadioaktivitaetsGeltung.RADIOAKTIV: 0.04,
    RadioaktivitaetsGeltung.GRUNDLEGEND_RADIOAKTIV: 0.08,
}

_TIER_DELTA: dict[RadioaktivitaetsGeltung, int] = {
    RadioaktivitaetsGeltung.GESPERRT: 0,
    RadioaktivitaetsGeltung.RADIOAKTIV: 1,
    RadioaktivitaetsGeltung.GRUNDLEGEND_RADIOAKTIV: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RadioaktivitaetsNorm:
    radioaktivitaets_senat_id: str
    radioaktivitaets_typ: RadioaktivitaetsTyp
    prozedur: RadioaktivitaetsProzedur
    geltung: RadioaktivitaetsGeltung
    radioaktivitaets_weight: float
    radioaktivitaets_tier: int
    canonical: bool
    radioaktivitaets_ids: tuple[str, ...]
    radioaktivitaets_tags: tuple[str, ...]


@dataclass(frozen=True)
class RadioaktivitaetsSenat:
    senat_id: str
    kernfusions_manifest: KernfusionsManifest
    normen: tuple[RadioaktivitaetsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.radioaktivitaets_senat_id for n in self.normen if n.geltung is RadioaktivitaetsGeltung.GESPERRT)

    @property
    def radioaktiv_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.radioaktivitaets_senat_id for n in self.normen if n.geltung is RadioaktivitaetsGeltung.RADIOAKTIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.radioaktivitaets_senat_id for n in self.normen if n.geltung is RadioaktivitaetsGeltung.GRUNDLEGEND_RADIOAKTIV)

    @property
    def senat_signal(self):
        if any(n.geltung is RadioaktivitaetsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-gesperrt")
        elif any(n.geltung is RadioaktivitaetsGeltung.RADIOAKTIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-radioaktiv")
        from types import SimpleNamespace
        return SimpleNamespace(status="senat-grundlegend-radioaktiv")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_radioaktivitaets_senat(
    kernfusions_manifest: KernfusionsManifest | None = None,
    *,
    senat_id: str = "radioaktivitaets-senat",
) -> RadioaktivitaetsSenat:
    if kernfusions_manifest is None:
        kernfusions_manifest = build_kernfusions_manifest(manifest_id=f"{senat_id}-manifest")

    normen: list[RadioaktivitaetsNorm] = []
    for parent_norm in kernfusions_manifest.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{senat_id}-{parent_norm.kernfusions_manifest_id.removeprefix(f'{kernfusions_manifest.manifest_id}-')}"
        raw_weight = min(1.0, parent_norm.kernfusions_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kernfusions_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is RadioaktivitaetsGeltung.GRUNDLEGEND_RADIOAKTIV)
        normen.append(
            RadioaktivitaetsNorm(
                radioaktivitaets_senat_id=new_id,
                radioaktivitaets_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                radioaktivitaets_weight=new_weight,
                radioaktivitaets_tier=new_tier,
                canonical=is_canonical,
                radioaktivitaets_ids=parent_norm.kernfusions_ids + (new_id,),
                radioaktivitaets_tags=parent_norm.kernfusions_tags + (f"radioaktivitaets-senat:{new_geltung.value}",),
            )
        )
    return RadioaktivitaetsSenat(
        senat_id=senat_id,
        kernfusions_manifest=kernfusions_manifest,
        normen=tuple(normen),
    )
