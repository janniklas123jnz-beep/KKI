"""
#387 HomoostaseSenat — Kybernetik (Norbert Wiener 1948): negative Rückkopplung
als universelles Regulationsprinzip. Regelkreis: Sollwert (set point),
Istwert (measured variable), Regler (controller), Stellgröße (actuator).
Körpertemperatur 37°C ± 0,5°C, Blutglukose 5 mM, pH 7,4 ± 0,05.
Fehler: e(t) = Sollwert - Istwert → Korrektur proportional zu e(t).
Leitsterns Governance-Senat reguliert Systemparameter auf optimale Sollwerte —
Abweichung erzeugt automatische Gegensteuerung.
Geltungsstufen: GESPERRT / HOMOOSTATISCH / GRUNDLEGEND_HOMOOSTATISCH
Parent: EvolutionManifest (#386)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .evolution_manifest import (
    EvolutionGeltung,
    EvolutionManifest,
    build_evolution_manifest,
)

_GELTUNG_MAP: dict[EvolutionGeltung, "HomoostaseGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[EvolutionGeltung.GESPERRT] = HomoostaseGeltung.GESPERRT
    _GELTUNG_MAP[EvolutionGeltung.EVOLUTIONAER] = HomoostaseGeltung.HOMOOSTATISCH
    _GELTUNG_MAP[EvolutionGeltung.GRUNDLEGEND_EVOLUTIONAER] = HomoostaseGeltung.GRUNDLEGEND_HOMOOSTATISCH


class HomoostaseTyp(Enum):
    SCHUTZ_HOMOOSTASE = "schutz-homoostase"
    ORDNUNGS_HOMOOSTASE = "ordnungs-homoostase"
    SOUVERAENITAETS_HOMOOSTASE = "souveraenitaets-homoostase"


class HomoostasProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class HomoostaseGeltung(Enum):
    GESPERRT = "gesperrt"
    HOMOOSTATISCH = "homoostatisch"
    GRUNDLEGEND_HOMOOSTATISCH = "grundlegend-homoostatisch"


_init_map()

_TYP_MAP: dict[HomoostaseGeltung, HomoostaseTyp] = {
    HomoostaseGeltung.GESPERRT: HomoostaseTyp.SCHUTZ_HOMOOSTASE,
    HomoostaseGeltung.HOMOOSTATISCH: HomoostaseTyp.ORDNUNGS_HOMOOSTASE,
    HomoostaseGeltung.GRUNDLEGEND_HOMOOSTATISCH: HomoostaseTyp.SOUVERAENITAETS_HOMOOSTASE,
}

_PROZEDUR_MAP: dict[HomoostaseGeltung, HomoostasProzedur] = {
    HomoostaseGeltung.GESPERRT: HomoostasProzedur.NOTPROZEDUR,
    HomoostaseGeltung.HOMOOSTATISCH: HomoostasProzedur.REGELPROTOKOLL,
    HomoostaseGeltung.GRUNDLEGEND_HOMOOSTATISCH: HomoostasProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[HomoostaseGeltung, float] = {
    HomoostaseGeltung.GESPERRT: 0.0,
    HomoostaseGeltung.HOMOOSTATISCH: 0.04,
    HomoostaseGeltung.GRUNDLEGEND_HOMOOSTATISCH: 0.08,
}

_TIER_DELTA: dict[HomoostaseGeltung, int] = {
    HomoostaseGeltung.GESPERRT: 0,
    HomoostaseGeltung.HOMOOSTATISCH: 1,
    HomoostaseGeltung.GRUNDLEGEND_HOMOOSTATISCH: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class HomoostaseNorm:
    homoostase_senat_id: str
    homoostase_typ: HomoostaseTyp
    prozedur: HomoostasProzedur
    geltung: HomoostaseGeltung
    homoostase_weight: float
    homoostase_tier: int
    canonical: bool
    homoostase_ids: tuple[str, ...]
    homoostase_tags: tuple[str, ...]


@dataclass(frozen=True)
class HomoostaseSenat:
    senat_id: str
    evolution_manifest: EvolutionManifest
    normen: tuple[HomoostaseNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.homoostase_senat_id for n in self.normen if n.geltung is HomoostaseGeltung.GESPERRT)

    @property
    def homoostatisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.homoostase_senat_id for n in self.normen if n.geltung is HomoostaseGeltung.HOMOOSTATISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.homoostase_senat_id for n in self.normen if n.geltung is HomoostaseGeltung.GRUNDLEGEND_HOMOOSTATISCH)

    @property
    def senat_signal(self):
        if any(n.geltung is HomoostaseGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-gesperrt")
        elif any(n.geltung is HomoostaseGeltung.HOMOOSTATISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-homoostatisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="senat-grundlegend-homoostatisch")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_homoostase_senat(
    evolution_manifest: EvolutionManifest | None = None,
    *,
    senat_id: str = "homoostase-senat",
) -> HomoostaseSenat:
    if evolution_manifest is None:
        evolution_manifest = build_evolution_manifest(manifest_id=f"{senat_id}-manifest")

    normen: list[HomoostaseNorm] = []
    for parent_norm in evolution_manifest.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{senat_id}-{parent_norm.evolution_manifest_id.removeprefix(f'{evolution_manifest.manifest_id}-')}"
        raw_weight = min(1.0, parent_norm.evolution_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.evolution_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is HomoostaseGeltung.GRUNDLEGEND_HOMOOSTATISCH)
        normen.append(
            HomoostaseNorm(
                homoostase_senat_id=new_id,
                homoostase_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                homoostase_weight=new_weight,
                homoostase_tier=new_tier,
                canonical=is_canonical,
                homoostase_ids=parent_norm.evolution_ids + (new_id,),
                homoostase_tags=parent_norm.evolution_tags + (f"homoostase:{new_geltung.value}",),
            )
        )
    return HomoostaseSenat(
        senat_id=senat_id,
        evolution_manifest=evolution_manifest,
        normen=tuple(normen),
    )
