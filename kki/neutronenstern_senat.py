"""
#337 NeutronensternSenat — Neutronenstern / Pulsar als hochkomprimierter Präzisions-Senat:
maximale Governance-Dichte bei höchster Taktpräzision (Chandrasekhar übersteigt TOV-Limit).
Geltungsstufen: GESPERRT / NEUTRONENDICHT / GRUNDLEGEND_NEUTRONENDICHT
Parent: SupernovaManifest (#336)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .supernova_manifest import (
    SupernovaGeltung,
    SupernovaManifest,
    build_supernova_manifest,
)

_GELTUNG_MAP: dict[SupernovaGeltung, "NeutronensternGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[SupernovaGeltung.GESPERRT] = NeutronensternGeltung.GESPERRT
    _GELTUNG_MAP[SupernovaGeltung.SUPERNOVAEXPLOSIV] = NeutronensternGeltung.NEUTRONENDICHT
    _GELTUNG_MAP[SupernovaGeltung.GRUNDLEGEND_SUPERNOVAEXPLOSIV] = NeutronensternGeltung.GRUNDLEGEND_NEUTRONENDICHT


class NeutronensternTyp(Enum):
    SCHUTZ_NEUTRONENSTERN = "schutz-neutronenstern"
    ORDNUNGS_NEUTRONENSTERN = "ordnungs-neutronenstern"
    SOUVERAENITAETS_NEUTRONENSTERN = "souveraenitaets-neutronenstern"


class NeutronensternProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class NeutronensternGeltung(Enum):
    GESPERRT = "gesperrt"
    NEUTRONENDICHT = "neutronendicht"
    GRUNDLEGEND_NEUTRONENDICHT = "grundlegend-neutronendicht"


_init_map()

_TYP_MAP: dict[NeutronensternGeltung, NeutronensternTyp] = {
    NeutronensternGeltung.GESPERRT: NeutronensternTyp.SCHUTZ_NEUTRONENSTERN,
    NeutronensternGeltung.NEUTRONENDICHT: NeutronensternTyp.ORDNUNGS_NEUTRONENSTERN,
    NeutronensternGeltung.GRUNDLEGEND_NEUTRONENDICHT: NeutronensternTyp.SOUVERAENITAETS_NEUTRONENSTERN,
}

_PROZEDUR_MAP: dict[NeutronensternGeltung, NeutronensternProzedur] = {
    NeutronensternGeltung.GESPERRT: NeutronensternProzedur.NOTPROZEDUR,
    NeutronensternGeltung.NEUTRONENDICHT: NeutronensternProzedur.REGELPROTOKOLL,
    NeutronensternGeltung.GRUNDLEGEND_NEUTRONENDICHT: NeutronensternProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[NeutronensternGeltung, float] = {
    NeutronensternGeltung.GESPERRT: 0.0,
    NeutronensternGeltung.NEUTRONENDICHT: 0.04,
    NeutronensternGeltung.GRUNDLEGEND_NEUTRONENDICHT: 0.08,
}

_TIER_DELTA: dict[NeutronensternGeltung, int] = {
    NeutronensternGeltung.GESPERRT: 0,
    NeutronensternGeltung.NEUTRONENDICHT: 1,
    NeutronensternGeltung.GRUNDLEGEND_NEUTRONENDICHT: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class NeutronensternNorm:
    neutronenstern_senat_id: str
    neutronenstern_typ: NeutronensternTyp
    prozedur: NeutronensternProzedur
    geltung: NeutronensternGeltung
    neutronenstern_weight: float
    neutronenstern_tier: int
    canonical: bool
    neutronenstern_ids: tuple[str, ...]
    neutronenstern_tags: tuple[str, ...]


@dataclass(frozen=True)
class NeutronensternSenat:
    senat_id: str
    supernova_manifest: SupernovaManifest
    normen: tuple[NeutronensternNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.neutronenstern_senat_id for n in self.normen if n.geltung is NeutronensternGeltung.GESPERRT)

    @property
    def neutronendicht_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.neutronenstern_senat_id for n in self.normen if n.geltung is NeutronensternGeltung.NEUTRONENDICHT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.neutronenstern_senat_id for n in self.normen if n.geltung is NeutronensternGeltung.GRUNDLEGEND_NEUTRONENDICHT)

    @property
    def senat_signal(self):
        if any(n.geltung is NeutronensternGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-gesperrt")
        elif any(n.geltung is NeutronensternGeltung.NEUTRONENDICHT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-neutronendicht")
        from types import SimpleNamespace
        return SimpleNamespace(status="senat-grundlegend-neutronendicht")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_neutronenstern_senat(
    supernova_manifest: SupernovaManifest | None = None,
    *,
    senat_id: str = "neutronenstern-senat",
) -> NeutronensternSenat:
    if supernova_manifest is None:
        supernova_manifest = build_supernova_manifest(manifest_id=f"{senat_id}-manifest")

    normen: list[NeutronensternNorm] = []
    for parent_norm in supernova_manifest.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{senat_id}-{parent_norm.supernova_manifest_id.removeprefix(f'{supernova_manifest.manifest_id}-')}"
        raw_weight = min(1.0, parent_norm.supernova_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.supernova_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is NeutronensternGeltung.GRUNDLEGEND_NEUTRONENDICHT)
        normen.append(
            NeutronensternNorm(
                neutronenstern_senat_id=new_id,
                neutronenstern_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                neutronenstern_weight=new_weight,
                neutronenstern_tier=new_tier,
                canonical=is_canonical,
                neutronenstern_ids=parent_norm.supernova_ids + (new_id,),
                neutronenstern_tags=parent_norm.supernova_tags + (f"neutronenstern:{new_geltung.value}",),
            )
        )
    return NeutronensternSenat(
        senat_id=senat_id,
        supernova_manifest=supernova_manifest,
        normen=tuple(normen),
    )
