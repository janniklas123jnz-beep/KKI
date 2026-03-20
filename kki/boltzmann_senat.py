"""#287 – BoltzmannSenat: Statistische Mechanik als Senat der Wahrscheinlichkeit.

Parent: carnot_manifest (#286)
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .carnot_manifest import (
    CarnotGeltung,
    CarnotManifest,
    build_carnot_manifest,
)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class BoltzmannTyp(Enum):
    SCHUTZ_BOLTZMANN = "schutz-boltzmann"
    ORDNUNGS_BOLTZMANN = "ordnungs-boltzmann"
    SOUVERAENITAETS_BOLTZMANN = "souveraenitaets-boltzmann"


class BoltzmannProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class BoltzmannGeltung(Enum):
    GESPERRT = "gesperrt"
    STATISTISCH = "statistisch"
    GRUNDLEGEND_STATISTISCH = "grundlegend-statistisch"


# ---------------------------------------------------------------------------
# Internal maps
# ---------------------------------------------------------------------------

_GELTUNG_MAP: dict[CarnotGeltung, BoltzmannGeltung] = {
    CarnotGeltung.GESPERRT: BoltzmannGeltung.GESPERRT,
    CarnotGeltung.CARNOTISCH: BoltzmannGeltung.STATISTISCH,
    CarnotGeltung.GRUNDLEGEND_CARNOTISCH: BoltzmannGeltung.GRUNDLEGEND_STATISTISCH,
}

_TYP_MAP: dict[CarnotGeltung, BoltzmannTyp] = {
    CarnotGeltung.GESPERRT: BoltzmannTyp.SCHUTZ_BOLTZMANN,
    CarnotGeltung.CARNOTISCH: BoltzmannTyp.ORDNUNGS_BOLTZMANN,
    CarnotGeltung.GRUNDLEGEND_CARNOTISCH: BoltzmannTyp.SOUVERAENITAETS_BOLTZMANN,
}

_PROZEDUR_MAP: dict[CarnotGeltung, BoltzmannProzedur] = {
    CarnotGeltung.GESPERRT: BoltzmannProzedur.NOTPROZEDUR,
    CarnotGeltung.CARNOTISCH: BoltzmannProzedur.REGELPROTOKOLL,
    CarnotGeltung.GRUNDLEGEND_CARNOTISCH: BoltzmannProzedur.PLENARPROTOKOLL,
}

_WEIGHT_BONUS: dict[CarnotGeltung, float] = {
    CarnotGeltung.GESPERRT: 0.0,
    CarnotGeltung.CARNOTISCH: 0.04,
    CarnotGeltung.GRUNDLEGEND_CARNOTISCH: 0.08,
}

_TIER_BONUS: dict[CarnotGeltung, int] = {
    CarnotGeltung.GESPERRT: 0,
    CarnotGeltung.CARNOTISCH: 1,
    CarnotGeltung.GRUNDLEGEND_CARNOTISCH: 2,
}

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class BoltzmannNorm:
    boltzmann_senat_id: str
    boltzmann_typ: BoltzmannTyp
    prozedur: BoltzmannProzedur
    geltung: BoltzmannGeltung
    boltzmann_weight: float
    boltzmann_tier: int
    canonical: bool
    boltzmann_ids: tuple[str, ...]
    boltzmann_tags: tuple[str, ...]


@dataclass(frozen=True)
class BoltzmannSenat:
    senat_id: str
    carnot_manifest: CarnotManifest
    normen: tuple[BoltzmannNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.boltzmann_senat_id for n in self.normen if n.geltung is BoltzmannGeltung.GESPERRT)

    @property
    def statistisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.boltzmann_senat_id for n in self.normen if n.geltung is BoltzmannGeltung.STATISTISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.boltzmann_senat_id for n in self.normen if n.geltung is BoltzmannGeltung.GRUNDLEGEND_STATISTISCH)

    @property
    def senat_signal(self):
        if any(n.geltung is BoltzmannGeltung.GESPERRT for n in self.normen):
            status = "senat-gesperrt"
            severity = "critical"
        elif any(n.geltung is BoltzmannGeltung.STATISTISCH for n in self.normen):
            status = "senat-statistisch"
            severity = "warning"
        else:
            status = "senat-grundlegend-statistisch"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def build_boltzmann_senat(
    carnot_manifest: CarnotManifest | None = None,
    *,
    senat_id: str = "boltzmann-senat",
) -> BoltzmannSenat:
    if carnot_manifest is None:
        carnot_manifest = build_carnot_manifest(manifest_id=f"{senat_id}-manifest")

    normen: list[BoltzmannNorm] = []
    for parent_norm in carnot_manifest.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{senat_id}-{parent_norm.carnot_manifest_id.removeprefix(f'{carnot_manifest.manifest_id}-')}"
        raw_weight = min(1.0, round(parent_norm.carnot_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.carnot_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is BoltzmannGeltung.GRUNDLEGEND_STATISTISCH)
        normen.append(
            BoltzmannNorm(
                boltzmann_senat_id=new_id,
                boltzmann_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                boltzmann_weight=raw_weight,
                boltzmann_tier=new_tier,
                canonical=is_canonical,
                boltzmann_ids=parent_norm.carnot_ids + (new_id,),
                boltzmann_tags=parent_norm.carnot_tags + (f"boltzmann-senat:{new_geltung.value}",),
            )
        )

    return BoltzmannSenat(
        senat_id=senat_id,
        carnot_manifest=carnot_manifest,
        normen=tuple(normen),
    )
