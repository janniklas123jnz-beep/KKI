"""
#416 FitnessLandschaftManifest — Fitness-Landschaften: Evolvierbarkeit als Governance.
Kauffman (1993): NK-Fitness-Landschaften — N Gene, K Epistasis-Parameter.
K=0: glatte Landschaft; K=N-1: chaotische Landschaft. Evolvierbarkeit als Governance-Ziel.
Wright (1932): Adaptive Landscape — Evolution als Bergsteigen.
Epistasis: Gen-Interaktionen formen Landschaft. Neutrale Netze: gleiche Fitness,
verschiedene Genotypen.
Funnel Landscapes (Protein-Faltung): strukturiertes Suchen. Rough Landscapes:
viele lokale Optima. Leitsterns Normenraum: NK-Fitness-Landschaft der Governance.
Geltungsstufen: GESPERRT / FITNESSKARTIERT / GRUNDLEGEND_FITNESSKARTIERT
Parent: ZellulaereAutomatenPakt (#415)
Block #411–#420 Komplexe Systeme & Emergenz
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .zellulaere_automaten_pakt import (
    ZellulaereAutomatenPakt,
    ZellulaereAutomatenPaktGeltung,
    build_zellulaere_automaten_pakt,
)

_GELTUNG_MAP: dict[ZellulaereAutomatenPaktGeltung, "FitnessLandschaftManifestGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[ZellulaereAutomatenPaktGeltung.GESPERRT] = FitnessLandschaftManifestGeltung.GESPERRT
    _GELTUNG_MAP[ZellulaereAutomatenPaktGeltung.ZELLULAERAUTOMAT] = FitnessLandschaftManifestGeltung.FITNESSKARTIERT
    _GELTUNG_MAP[ZellulaereAutomatenPaktGeltung.GRUNDLEGEND_ZELLULAERAUTOMAT] = FitnessLandschaftManifestGeltung.GRUNDLEGEND_FITNESSKARTIERT


class FitnessLandschaftManifestTyp(Enum):
    SCHUTZ_FITNESS_LANDSCHAFT = "schutz-fitness-landschaft"
    ORDNUNGS_FITNESS_LANDSCHAFT = "ordnungs-fitness-landschaft"
    SOUVERAENITAETS_FITNESS_LANDSCHAFT = "souveraenitaets-fitness-landschaft"


class FitnessLandschaftManifestProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class FitnessLandschaftManifestGeltung(Enum):
    GESPERRT = "gesperrt"
    FITNESSKARTIERT = "fitnesskartiert"
    GRUNDLEGEND_FITNESSKARTIERT = "grundlegend-fitnesskartiert"


_init_map()

_TYP_MAP: dict[FitnessLandschaftManifestGeltung, FitnessLandschaftManifestTyp] = {
    FitnessLandschaftManifestGeltung.GESPERRT: FitnessLandschaftManifestTyp.SCHUTZ_FITNESS_LANDSCHAFT,
    FitnessLandschaftManifestGeltung.FITNESSKARTIERT: FitnessLandschaftManifestTyp.ORDNUNGS_FITNESS_LANDSCHAFT,
    FitnessLandschaftManifestGeltung.GRUNDLEGEND_FITNESSKARTIERT: FitnessLandschaftManifestTyp.SOUVERAENITAETS_FITNESS_LANDSCHAFT,
}

_PROZEDUR_MAP: dict[FitnessLandschaftManifestGeltung, FitnessLandschaftManifestProzedur] = {
    FitnessLandschaftManifestGeltung.GESPERRT: FitnessLandschaftManifestProzedur.NOTPROZEDUR,
    FitnessLandschaftManifestGeltung.FITNESSKARTIERT: FitnessLandschaftManifestProzedur.REGELPROTOKOLL,
    FitnessLandschaftManifestGeltung.GRUNDLEGEND_FITNESSKARTIERT: FitnessLandschaftManifestProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[FitnessLandschaftManifestGeltung, float] = {
    FitnessLandschaftManifestGeltung.GESPERRT: 0.0,
    FitnessLandschaftManifestGeltung.FITNESSKARTIERT: 0.04,
    FitnessLandschaftManifestGeltung.GRUNDLEGEND_FITNESSKARTIERT: 0.08,
}

_TIER_DELTA: dict[FitnessLandschaftManifestGeltung, int] = {
    FitnessLandschaftManifestGeltung.GESPERRT: 0,
    FitnessLandschaftManifestGeltung.FITNESSKARTIERT: 1,
    FitnessLandschaftManifestGeltung.GRUNDLEGEND_FITNESSKARTIERT: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FitnessLandschaftManifestNorm:
    fitness_landschaft_manifest_id: str
    fitness_landschaft_typ: FitnessLandschaftManifestTyp
    prozedur: FitnessLandschaftManifestProzedur
    geltung: FitnessLandschaftManifestGeltung
    fitness_landschaft_weight: float
    fitness_landschaft_tier: int
    canonical: bool
    fitness_landschaft_ids: tuple[str, ...]
    fitness_landschaft_tags: tuple[str, ...]


@dataclass(frozen=True)
class FitnessLandschaftManifest:
    manifest_id: str
    zellulaere_automaten_pakt: ZellulaereAutomatenPakt
    normen: tuple[FitnessLandschaftManifestNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.fitness_landschaft_manifest_id for n in self.normen if n.geltung is FitnessLandschaftManifestGeltung.GESPERRT)

    @property
    def fitnesskartiert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.fitness_landschaft_manifest_id for n in self.normen if n.geltung is FitnessLandschaftManifestGeltung.FITNESSKARTIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.fitness_landschaft_manifest_id for n in self.normen if n.geltung is FitnessLandschaftManifestGeltung.GRUNDLEGEND_FITNESSKARTIERT)

    @property
    def manifest_signal(self):
        if any(n.geltung is FitnessLandschaftManifestGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-gesperrt")
        elif any(n.geltung is FitnessLandschaftManifestGeltung.FITNESSKARTIERT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-fitnesskartiert")
        from types import SimpleNamespace
        return SimpleNamespace(status="manifest-grundlegend-fitnesskartiert")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_fitness_landschaft_manifest(
    zellulaere_automaten_pakt: ZellulaereAutomatenPakt | None = None,
    *,
    manifest_id: str = "fitness-landschaft-manifest",
) -> FitnessLandschaftManifest:
    if zellulaere_automaten_pakt is None:
        zellulaere_automaten_pakt = build_zellulaere_automaten_pakt(pakt_id=f"{manifest_id}-pakt")

    normen: list[FitnessLandschaftManifestNorm] = []
    for parent_norm in zellulaere_automaten_pakt.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{manifest_id}-{parent_norm.zellulaere_automaten_pakt_id.removeprefix(f'{zellulaere_automaten_pakt.pakt_id}-')}"
        raw_weight = min(1.0, parent_norm.zellulaerautomat_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.zellulaerautomat_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is FitnessLandschaftManifestGeltung.GRUNDLEGEND_FITNESSKARTIERT)
        normen.append(
            FitnessLandschaftManifestNorm(
                fitness_landschaft_manifest_id=new_id,
                fitness_landschaft_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                fitness_landschaft_weight=new_weight,
                fitness_landschaft_tier=new_tier,
                canonical=is_canonical,
                fitness_landschaft_ids=parent_norm.zellulaerautomat_ids + (new_id,),
                fitness_landschaft_tags=parent_norm.zellulaerautomat_tags + (f"fitness-landschaft:{new_geltung.value}",),
            )
        )
    return FitnessLandschaftManifest(
        manifest_id=manifest_id,
        zellulaere_automaten_pakt=zellulaere_automaten_pakt,
        normen=tuple(normen),
    )
