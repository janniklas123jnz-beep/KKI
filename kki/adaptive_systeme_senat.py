"""
#417 AdaptiveSystemeSenat — Complex Adaptive Systems: Holland's CAS.
Holland (1975): Schema-Theorem — kurze, hochfit-bewertete, häufige Schemata
wachsen exponentiell. Building Blocks als Governance-Bausteine. CAS als Grundlage.
Klassifikatorsysteme: Regel-basierte Agenten + Bucket-Brigade-Algorithmus.
Genetische Algorithmen: Selektion, Rekombination, Mutation als Governance-Evolution.
ECHO-Modell (Holland 1994): Koevolution, Ressourcen, Tags.
Leitsterns Terra-Schwarm ist ein Complex Adaptive System im technischen Sinne Hollands.
Geltungsstufen: GESPERRT / ADAPTIV / GRUNDLEGEND_ADAPTIV
Parent: FitnessLandschaftManifest (#416)
Block #411–#420 Komplexe Systeme & Emergenz
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .fitness_landschaft_manifest import (
    FitnessLandschaftManifest,
    FitnessLandschaftManifestGeltung,
    build_fitness_landschaft_manifest,
)

_GELTUNG_MAP: dict[FitnessLandschaftManifestGeltung, "AdaptiveSystemeSenatGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[FitnessLandschaftManifestGeltung.GESPERRT] = AdaptiveSystemeSenatGeltung.GESPERRT
    _GELTUNG_MAP[FitnessLandschaftManifestGeltung.FITNESSKARTIERT] = AdaptiveSystemeSenatGeltung.ADAPTIV
    _GELTUNG_MAP[FitnessLandschaftManifestGeltung.GRUNDLEGEND_FITNESSKARTIERT] = AdaptiveSystemeSenatGeltung.GRUNDLEGEND_ADAPTIV


class AdaptiveSystemeSenatTyp(Enum):
    SCHUTZ_ADAPTIV = "schutz-adaptiv"
    ORDNUNGS_ADAPTIV = "ordnungs-adaptiv"
    SOUVERAENITAETS_ADAPTIV = "souveraenitaets-adaptiv"


class AdaptiveSystemeSenatProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class AdaptiveSystemeSenatGeltung(Enum):
    GESPERRT = "gesperrt"
    ADAPTIV = "adaptiv"
    GRUNDLEGEND_ADAPTIV = "grundlegend-adaptiv"


_init_map()

_TYP_MAP: dict[AdaptiveSystemeSenatGeltung, AdaptiveSystemeSenatTyp] = {
    AdaptiveSystemeSenatGeltung.GESPERRT: AdaptiveSystemeSenatTyp.SCHUTZ_ADAPTIV,
    AdaptiveSystemeSenatGeltung.ADAPTIV: AdaptiveSystemeSenatTyp.ORDNUNGS_ADAPTIV,
    AdaptiveSystemeSenatGeltung.GRUNDLEGEND_ADAPTIV: AdaptiveSystemeSenatTyp.SOUVERAENITAETS_ADAPTIV,
}

_PROZEDUR_MAP: dict[AdaptiveSystemeSenatGeltung, AdaptiveSystemeSenatProzedur] = {
    AdaptiveSystemeSenatGeltung.GESPERRT: AdaptiveSystemeSenatProzedur.NOTPROZEDUR,
    AdaptiveSystemeSenatGeltung.ADAPTIV: AdaptiveSystemeSenatProzedur.REGELPROTOKOLL,
    AdaptiveSystemeSenatGeltung.GRUNDLEGEND_ADAPTIV: AdaptiveSystemeSenatProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[AdaptiveSystemeSenatGeltung, float] = {
    AdaptiveSystemeSenatGeltung.GESPERRT: 0.0,
    AdaptiveSystemeSenatGeltung.ADAPTIV: 0.04,
    AdaptiveSystemeSenatGeltung.GRUNDLEGEND_ADAPTIV: 0.08,
}

_TIER_DELTA: dict[AdaptiveSystemeSenatGeltung, int] = {
    AdaptiveSystemeSenatGeltung.GESPERRT: 0,
    AdaptiveSystemeSenatGeltung.ADAPTIV: 1,
    AdaptiveSystemeSenatGeltung.GRUNDLEGEND_ADAPTIV: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AdaptiveSystemeSenatNorm:
    adaptive_systeme_senat_id: str
    adaptiv_typ: AdaptiveSystemeSenatTyp
    prozedur: AdaptiveSystemeSenatProzedur
    geltung: AdaptiveSystemeSenatGeltung
    adaptiv_weight: float
    adaptiv_tier: int
    canonical: bool
    adaptiv_ids: tuple[str, ...]
    adaptiv_tags: tuple[str, ...]


@dataclass(frozen=True)
class AdaptiveSystemeSenat:
    senat_id: str
    fitness_landschaft_manifest: FitnessLandschaftManifest
    normen: tuple[AdaptiveSystemeSenatNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.adaptive_systeme_senat_id for n in self.normen if n.geltung is AdaptiveSystemeSenatGeltung.GESPERRT)

    @property
    def adaptiv_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.adaptive_systeme_senat_id for n in self.normen if n.geltung is AdaptiveSystemeSenatGeltung.ADAPTIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.adaptive_systeme_senat_id for n in self.normen if n.geltung is AdaptiveSystemeSenatGeltung.GRUNDLEGEND_ADAPTIV)

    @property
    def senat_signal(self):
        if any(n.geltung is AdaptiveSystemeSenatGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-gesperrt")
        elif any(n.geltung is AdaptiveSystemeSenatGeltung.ADAPTIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-adaptiv")
        from types import SimpleNamespace
        return SimpleNamespace(status="senat-grundlegend-adaptiv")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_adaptive_systeme_senat(
    fitness_landschaft_manifest: FitnessLandschaftManifest | None = None,
    *,
    senat_id: str = "adaptive-systeme-senat",
) -> AdaptiveSystemeSenat:
    if fitness_landschaft_manifest is None:
        fitness_landschaft_manifest = build_fitness_landschaft_manifest(manifest_id=f"{senat_id}-manifest")

    normen: list[AdaptiveSystemeSenatNorm] = []
    for parent_norm in fitness_landschaft_manifest.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{senat_id}-{parent_norm.fitness_landschaft_manifest_id.removeprefix(f'{fitness_landschaft_manifest.manifest_id}-')}"
        raw_weight = min(1.0, parent_norm.fitness_landschaft_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.fitness_landschaft_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is AdaptiveSystemeSenatGeltung.GRUNDLEGEND_ADAPTIV)
        normen.append(
            AdaptiveSystemeSenatNorm(
                adaptive_systeme_senat_id=new_id,
                adaptiv_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                adaptiv_weight=new_weight,
                adaptiv_tier=new_tier,
                canonical=is_canonical,
                adaptiv_ids=parent_norm.fitness_landschaft_ids + (new_id,),
                adaptiv_tags=parent_norm.fitness_landschaft_tags + (f"adaptiv:{new_geltung.value}",),
            )
        )
    return AdaptiveSystemeSenat(
        senat_id=senat_id,
        fitness_landschaft_manifest=fitness_landschaft_manifest,
        normen=tuple(normen),
    )
