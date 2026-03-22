"""
#455 FitnessPakt — Fitness-Landschaften und genetische Algorithmen.
Holland (1975): Genetische Algorithmen — Selektion, Crossover, Mutation als Optimierung.
Goldberg (1989): Genetic Algorithms in Search, Optimization and Machine Learning.
Wright (1932): Fitness-Landschaft — Sewall Wright's Konzept der adaptiven Topographie.
Leitsterns Fitness-Pakt: GA-inspirierte Schwarm-Optimierung über dynamische Fitness-Räume.
Geltungsstufen: GESPERRT / FITNESSORIENTIERT / GRUNDLEGEND_FITNESSORIENTIERT
Parent: MutationsKodex (#454)
Block #451–#460: Evolutionsbiologie & Genetik
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .mutations_kodex import (
    MutationsKodex,
    MutationsKodexGeltung,
    build_mutations_kodex,
)

_GELTUNG_MAP: dict[MutationsKodexGeltung, "FitnessPaktGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[MutationsKodexGeltung.GESPERRT] = FitnessPaktGeltung.GESPERRT
    _GELTUNG_MAP[MutationsKodexGeltung.MUTATIV] = FitnessPaktGeltung.FITNESSORIENTIERT
    _GELTUNG_MAP[MutationsKodexGeltung.GRUNDLEGEND_MUTATIV] = FitnessPaktGeltung.GRUNDLEGEND_FITNESSORIENTIERT


class FitnessPaktTyp(Enum):
    SCHUTZ_FITNESS = "schutz-fitness"
    ORDNUNGS_FITNESS = "ordnungs-fitness"
    SOUVERAENITAETS_FITNESS = "souveraenitaets-fitness"


class FitnessPaktProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class FitnessPaktGeltung(Enum):
    GESPERRT = "gesperrt"
    FITNESSORIENTIERT = "fitnessorientiert"
    GRUNDLEGEND_FITNESSORIENTIERT = "grundlegend-fitnessorientiert"


_init_map()

_TYP_MAP: dict[FitnessPaktGeltung, FitnessPaktTyp] = {
    FitnessPaktGeltung.GESPERRT: FitnessPaktTyp.SCHUTZ_FITNESS,
    FitnessPaktGeltung.FITNESSORIENTIERT: FitnessPaktTyp.ORDNUNGS_FITNESS,
    FitnessPaktGeltung.GRUNDLEGEND_FITNESSORIENTIERT: FitnessPaktTyp.SOUVERAENITAETS_FITNESS,
}

_PROZEDUR_MAP: dict[FitnessPaktGeltung, FitnessPaktProzedur] = {
    FitnessPaktGeltung.GESPERRT: FitnessPaktProzedur.NOTPROZEDUR,
    FitnessPaktGeltung.FITNESSORIENTIERT: FitnessPaktProzedur.REGELPROTOKOLL,
    FitnessPaktGeltung.GRUNDLEGEND_FITNESSORIENTIERT: FitnessPaktProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[FitnessPaktGeltung, float] = {
    FitnessPaktGeltung.GESPERRT: 0.0,
    FitnessPaktGeltung.FITNESSORIENTIERT: 0.04,
    FitnessPaktGeltung.GRUNDLEGEND_FITNESSORIENTIERT: 0.08,
}

_TIER_DELTA: dict[FitnessPaktGeltung, int] = {
    FitnessPaktGeltung.GESPERRT: 0,
    FitnessPaktGeltung.FITNESSORIENTIERT: 1,
    FitnessPaktGeltung.GRUNDLEGEND_FITNESSORIENTIERT: 2,
}


@dataclass(frozen=True)
class FitnessPaktNorm:
    fitness_pakt_id: str
    fitness_pakt_typ: FitnessPaktTyp
    prozedur: FitnessPaktProzedur
    geltung: FitnessPaktGeltung
    fitness_weight: float
    fitness_tier: int
    canonical: bool
    fitness_ids: tuple[str, ...]
    fitness_tags: tuple[str, ...]


@dataclass(frozen=True)
class FitnessPakt:
    pakt_id: str
    mutations_kodex: MutationsKodex
    normen: tuple[FitnessPaktNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.fitness_pakt_id for n in self.normen if n.geltung is FitnessPaktGeltung.GESPERRT)

    @property
    def fitnessorientiert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.fitness_pakt_id for n in self.normen if n.geltung is FitnessPaktGeltung.FITNESSORIENTIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.fitness_pakt_id for n in self.normen if n.geltung is FitnessPaktGeltung.GRUNDLEGEND_FITNESSORIENTIERT)

    @property
    def pakt_signal(self):
        if any(n.geltung is FitnessPaktGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-gesperrt")
        elif any(n.geltung is FitnessPaktGeltung.FITNESSORIENTIERT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-fitnessorientiert")
        from types import SimpleNamespace
        return SimpleNamespace(status="pakt-grundlegend-fitnessorientiert")


def build_fitness_pakt(
    mutations_kodex: MutationsKodex | None = None,
    *,
    pakt_id: str = "fitness-pakt",
) -> FitnessPakt:
    if mutations_kodex is None:
        mutations_kodex = build_mutations_kodex(kodex_id=f"{pakt_id}-kodex")

    normen: list[FitnessPaktNorm] = []
    for parent_norm in mutations_kodex.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{pakt_id}-{parent_norm.mutations_kodex_id.removeprefix(f'{mutations_kodex.kodex_id}-')}"
        raw_weight = min(1.0, parent_norm.mutations_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.mutations_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is FitnessPaktGeltung.GRUNDLEGEND_FITNESSORIENTIERT)
        normen.append(
            FitnessPaktNorm(
                fitness_pakt_id=new_id,
                fitness_pakt_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                fitness_weight=new_weight,
                fitness_tier=new_tier,
                canonical=is_canonical,
                fitness_ids=parent_norm.mutations_ids + (new_id,),
                fitness_tags=parent_norm.mutations_tags + (f"fitness-pakt:{new_geltung.value}",),
            )
        )
    return FitnessPakt(
        pakt_id=pakt_id,
        mutations_kodex=mutations_kodex,
        normen=tuple(normen),
    )
