"""#297 – SpektralSenat: Elektromagnetisches Spektrum als Governance-Senat.

Parent: lichtgeschwindigkeits_manifest (#296)
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .lichtgeschwindigkeits_manifest import (
    LichtgeschwindigkeitsGeltung,
    LichtgeschwindigkeitsManifest,
    build_lichtgeschwindigkeits_manifest,
)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class SpektralTyp(Enum):
    SCHUTZ_SPEKTRUM = "schutz-spektrum"
    ORDNUNGS_SPEKTRUM = "ordnungs-spektrum"
    SOUVERAENITAETS_SPEKTRUM = "souveraenitaets-spektrum"


class SpektralProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class SpektralGeltung(Enum):
    GESPERRT = "gesperrt"
    SPEKTRAL = "spektral"
    GRUNDLEGEND_SPEKTRAL = "grundlegend-spektral"


# ---------------------------------------------------------------------------
# Internal maps
# ---------------------------------------------------------------------------

_GELTUNG_MAP: dict[LichtgeschwindigkeitsGeltung, SpektralGeltung] = {
    LichtgeschwindigkeitsGeltung.GESPERRT: SpektralGeltung.GESPERRT,
    LichtgeschwindigkeitsGeltung.LICHTSCHNELL: SpektralGeltung.SPEKTRAL,
    LichtgeschwindigkeitsGeltung.GRUNDLEGEND_LICHTSCHNELL: SpektralGeltung.GRUNDLEGEND_SPEKTRAL,
}

_TYP_MAP: dict[LichtgeschwindigkeitsGeltung, SpektralTyp] = {
    LichtgeschwindigkeitsGeltung.GESPERRT: SpektralTyp.SCHUTZ_SPEKTRUM,
    LichtgeschwindigkeitsGeltung.LICHTSCHNELL: SpektralTyp.ORDNUNGS_SPEKTRUM,
    LichtgeschwindigkeitsGeltung.GRUNDLEGEND_LICHTSCHNELL: SpektralTyp.SOUVERAENITAETS_SPEKTRUM,
}

_PROZEDUR_MAP: dict[LichtgeschwindigkeitsGeltung, SpektralProzedur] = {
    LichtgeschwindigkeitsGeltung.GESPERRT: SpektralProzedur.NOTPROZEDUR,
    LichtgeschwindigkeitsGeltung.LICHTSCHNELL: SpektralProzedur.REGELPROTOKOLL,
    LichtgeschwindigkeitsGeltung.GRUNDLEGEND_LICHTSCHNELL: SpektralProzedur.PLENARPROTOKOLL,
}

_WEIGHT_BONUS: dict[LichtgeschwindigkeitsGeltung, float] = {
    LichtgeschwindigkeitsGeltung.GESPERRT: 0.0,
    LichtgeschwindigkeitsGeltung.LICHTSCHNELL: 0.04,
    LichtgeschwindigkeitsGeltung.GRUNDLEGEND_LICHTSCHNELL: 0.08,
}

_TIER_BONUS: dict[LichtgeschwindigkeitsGeltung, int] = {
    LichtgeschwindigkeitsGeltung.GESPERRT: 0,
    LichtgeschwindigkeitsGeltung.LICHTSCHNELL: 1,
    LichtgeschwindigkeitsGeltung.GRUNDLEGEND_LICHTSCHNELL: 2,
}

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SpektralNorm:
    spektral_senat_id: str
    spektral_typ: SpektralTyp
    prozedur: SpektralProzedur
    geltung: SpektralGeltung
    spektral_weight: float
    spektral_tier: int
    canonical: bool
    spektral_ids: tuple[str, ...]
    spektral_tags: tuple[str, ...]


@dataclass(frozen=True)
class SpektralSenat:
    senat_id: str
    lichtgeschwindigkeits_manifest: LichtgeschwindigkeitsManifest
    normen: tuple[SpektralNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.spektral_senat_id for n in self.normen if n.geltung is SpektralGeltung.GESPERRT)

    @property
    def spektral_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.spektral_senat_id for n in self.normen if n.geltung is SpektralGeltung.SPEKTRAL)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.spektral_senat_id for n in self.normen if n.geltung is SpektralGeltung.GRUNDLEGEND_SPEKTRAL)

    @property
    def senat_signal(self):
        if any(n.geltung is SpektralGeltung.GESPERRT for n in self.normen):
            status = "senat-gesperrt"
            severity = "critical"
        elif any(n.geltung is SpektralGeltung.SPEKTRAL for n in self.normen):
            status = "senat-spektral"
            severity = "warning"
        else:
            status = "senat-grundlegend-spektral"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def build_spektral_senat(
    lichtgeschwindigkeits_manifest: LichtgeschwindigkeitsManifest | None = None,
    *,
    senat_id: str = "spektral-senat",
) -> SpektralSenat:
    if lichtgeschwindigkeits_manifest is None:
        lichtgeschwindigkeits_manifest = build_lichtgeschwindigkeits_manifest(manifest_id=f"{senat_id}-manifest")

    normen: list[SpektralNorm] = []
    for parent_norm in lichtgeschwindigkeits_manifest.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{senat_id}-{parent_norm.lichtgeschwindigkeits_manifest_id.removeprefix(f'{lichtgeschwindigkeits_manifest.manifest_id}-')}"
        raw_weight = min(1.0, round(parent_norm.lichtgeschwindigkeits_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.lichtgeschwindigkeits_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SpektralGeltung.GRUNDLEGEND_SPEKTRAL)
        normen.append(
            SpektralNorm(
                spektral_senat_id=new_id,
                spektral_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                spektral_weight=raw_weight,
                spektral_tier=new_tier,
                canonical=is_canonical,
                spektral_ids=parent_norm.lichtgeschwindigkeits_ids + (new_id,),
                spektral_tags=parent_norm.lichtgeschwindigkeits_tags + (f"spektral-senat:{new_geltung.value}",),
            )
        )

    return SpektralSenat(
        senat_id=senat_id,
        lichtgeschwindigkeits_manifest=lichtgeschwindigkeits_manifest,
        normen=tuple(normen),
    )
