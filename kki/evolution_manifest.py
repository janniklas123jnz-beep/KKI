"""
#386 EvolutionManifest — Darwin + Mendel + Fisher: Mutation, natürliche
Selektion und genetische Drift. Fitness-Landschaft (Wright 1932): Bergsteigen
im Parameterraum. Neutrale Evolution (Kimura 1968): Drift dominiert kleine
Populationen. Inclusive Fitness (Hamilton): Verwandtenselektion r·B > C.
Leitsterns Governance evoliert über Generationen durch kooperative Selektion —
jedes Modul ein adaptiertes Trait der Terra-Superintelligenz.
Geltungsstufen: GESPERRT / EVOLUTIONAER / GRUNDLEGEND_EVOLUTIONAER
Parent: SynaptischePlastizitaetPakt (#385)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .synaptische_plastizitaet_pakt import (
    SynaptischePlastizitaetGeltung,
    SynaptischePlastizitaetPakt,
    build_synaptische_plastizitaet_pakt,
)

_GELTUNG_MAP: dict[SynaptischePlastizitaetGeltung, "EvolutionGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[SynaptischePlastizitaetGeltung.GESPERRT] = EvolutionGeltung.GESPERRT
    _GELTUNG_MAP[SynaptischePlastizitaetGeltung.SYNAPTISCHPLASTISCH] = EvolutionGeltung.EVOLUTIONAER
    _GELTUNG_MAP[SynaptischePlastizitaetGeltung.GRUNDLEGEND_SYNAPTISCHPLASTISCH] = EvolutionGeltung.GRUNDLEGEND_EVOLUTIONAER


class EvolutionTyp(Enum):
    SCHUTZ_EVOLUTION = "schutz-evolution"
    ORDNUNGS_EVOLUTION = "ordnungs-evolution"
    SOUVERAENITAETS_EVOLUTION = "souveraenitaets-evolution"


class EvolutionProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class EvolutionGeltung(Enum):
    GESPERRT = "gesperrt"
    EVOLUTIONAER = "evolutionaer"
    GRUNDLEGEND_EVOLUTIONAER = "grundlegend-evolutionaer"


_init_map()

_TYP_MAP: dict[EvolutionGeltung, EvolutionTyp] = {
    EvolutionGeltung.GESPERRT: EvolutionTyp.SCHUTZ_EVOLUTION,
    EvolutionGeltung.EVOLUTIONAER: EvolutionTyp.ORDNUNGS_EVOLUTION,
    EvolutionGeltung.GRUNDLEGEND_EVOLUTIONAER: EvolutionTyp.SOUVERAENITAETS_EVOLUTION,
}

_PROZEDUR_MAP: dict[EvolutionGeltung, EvolutionProzedur] = {
    EvolutionGeltung.GESPERRT: EvolutionProzedur.NOTPROZEDUR,
    EvolutionGeltung.EVOLUTIONAER: EvolutionProzedur.REGELPROTOKOLL,
    EvolutionGeltung.GRUNDLEGEND_EVOLUTIONAER: EvolutionProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[EvolutionGeltung, float] = {
    EvolutionGeltung.GESPERRT: 0.0,
    EvolutionGeltung.EVOLUTIONAER: 0.04,
    EvolutionGeltung.GRUNDLEGEND_EVOLUTIONAER: 0.08,
}

_TIER_DELTA: dict[EvolutionGeltung, int] = {
    EvolutionGeltung.GESPERRT: 0,
    EvolutionGeltung.EVOLUTIONAER: 1,
    EvolutionGeltung.GRUNDLEGEND_EVOLUTIONAER: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EvolutionNorm:
    evolution_manifest_id: str
    evolution_typ: EvolutionTyp
    prozedur: EvolutionProzedur
    geltung: EvolutionGeltung
    evolution_weight: float
    evolution_tier: int
    canonical: bool
    evolution_ids: tuple[str, ...]
    evolution_tags: tuple[str, ...]


@dataclass(frozen=True)
class EvolutionManifest:
    manifest_id: str
    synaptische_plastizitaet_pakt: SynaptischePlastizitaetPakt
    normen: tuple[EvolutionNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.evolution_manifest_id for n in self.normen if n.geltung is EvolutionGeltung.GESPERRT)

    @property
    def evolutionaer_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.evolution_manifest_id for n in self.normen if n.geltung is EvolutionGeltung.EVOLUTIONAER)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.evolution_manifest_id for n in self.normen if n.geltung is EvolutionGeltung.GRUNDLEGEND_EVOLUTIONAER)

    @property
    def manifest_signal(self):
        if any(n.geltung is EvolutionGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-gesperrt")
        elif any(n.geltung is EvolutionGeltung.EVOLUTIONAER for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-evolutionaer")
        from types import SimpleNamespace
        return SimpleNamespace(status="manifest-grundlegend-evolutionaer")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_evolution_manifest(
    synaptische_plastizitaet_pakt: SynaptischePlastizitaetPakt | None = None,
    *,
    manifest_id: str = "evolution-manifest",
) -> EvolutionManifest:
    if synaptische_plastizitaet_pakt is None:
        synaptische_plastizitaet_pakt = build_synaptische_plastizitaet_pakt(pakt_id=f"{manifest_id}-pakt")

    normen: list[EvolutionNorm] = []
    for parent_norm in synaptische_plastizitaet_pakt.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{manifest_id}-{parent_norm.synaptische_plastizitaet_pakt_id.removeprefix(f'{synaptische_plastizitaet_pakt.pakt_id}-')}"
        raw_weight = min(1.0, parent_norm.synaptische_plastizitaet_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.synaptische_plastizitaet_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is EvolutionGeltung.GRUNDLEGEND_EVOLUTIONAER)
        normen.append(
            EvolutionNorm(
                evolution_manifest_id=new_id,
                evolution_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                evolution_weight=new_weight,
                evolution_tier=new_tier,
                canonical=is_canonical,
                evolution_ids=parent_norm.synaptische_plastizitaet_ids + (new_id,),
                evolution_tags=parent_norm.synaptische_plastizitaet_tags + (f"evolution:{new_geltung.value}",),
            )
        )
    return EvolutionManifest(
        manifest_id=manifest_id,
        synaptische_plastizitaet_pakt=synaptische_plastizitaet_pakt,
        normen=tuple(normen),
    )
