"""
#407 AlgorithmenSenat — Algorithmentheorie: Turing (1936): Turingmaschine —
universelles Berechnungsmodell. Halteproblem: unentscheidbar. Church-Turing-These:
alle berechenbaren Funktionen. Cook-Levin (1971): NP-Vollständigkeit — SAT als
erstes NP-vollständiges Problem. P vs. NP: offenste Frage der Informatik (Clay
Millennium Problem). Kolmogorov-Komplexität K(x): minimale Programmlänge.
Randomisierung (BPP). Approximationsalgorithmen für NP-schwere Probleme.
Leitsterns Agenten sind algorithmisch korrekt: berechenbar, effizient, kalibriert.
Geltungsstufen: GESPERRT / ALGORITHMISCH / GRUNDLEGEND_ALGORITHMISCH
Parent: GraphenManifest (#406)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .graphen_manifest import (
    GraphenManifest,
    GraphenManifestGeltung,
    build_graphen_manifest,
)

_GELTUNG_MAP: dict[GraphenManifestGeltung, "AlgorithmenSenatGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[GraphenManifestGeltung.GESPERRT] = AlgorithmenSenatGeltung.GESPERRT
    _GELTUNG_MAP[GraphenManifestGeltung.GRAPHENTHEORETISCH] = AlgorithmenSenatGeltung.ALGORITHMISCH
    _GELTUNG_MAP[GraphenManifestGeltung.GRUNDLEGEND_GRAPHENTHEORETISCH] = AlgorithmenSenatGeltung.GRUNDLEGEND_ALGORITHMISCH


class AlgorithmenSenatTyp(Enum):
    SCHUTZ_ALGORITHMEN = "schutz-algorithmen"
    ORDNUNGS_ALGORITHMEN = "ordnungs-algorithmen"
    SOUVERAENITAETS_ALGORITHMEN = "souveraenitaets-algorithmen"


class AlgorithmenSenatProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class AlgorithmenSenatGeltung(Enum):
    GESPERRT = "gesperrt"
    ALGORITHMISCH = "algorithmisch"
    GRUNDLEGEND_ALGORITHMISCH = "grundlegend-algorithmisch"


_init_map()

_TYP_MAP: dict[AlgorithmenSenatGeltung, AlgorithmenSenatTyp] = {
    AlgorithmenSenatGeltung.GESPERRT: AlgorithmenSenatTyp.SCHUTZ_ALGORITHMEN,
    AlgorithmenSenatGeltung.ALGORITHMISCH: AlgorithmenSenatTyp.ORDNUNGS_ALGORITHMEN,
    AlgorithmenSenatGeltung.GRUNDLEGEND_ALGORITHMISCH: AlgorithmenSenatTyp.SOUVERAENITAETS_ALGORITHMEN,
}

_PROZEDUR_MAP: dict[AlgorithmenSenatGeltung, AlgorithmenSenatProzedur] = {
    AlgorithmenSenatGeltung.GESPERRT: AlgorithmenSenatProzedur.NOTPROZEDUR,
    AlgorithmenSenatGeltung.ALGORITHMISCH: AlgorithmenSenatProzedur.REGELPROTOKOLL,
    AlgorithmenSenatGeltung.GRUNDLEGEND_ALGORITHMISCH: AlgorithmenSenatProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[AlgorithmenSenatGeltung, float] = {
    AlgorithmenSenatGeltung.GESPERRT: 0.0,
    AlgorithmenSenatGeltung.ALGORITHMISCH: 0.04,
    AlgorithmenSenatGeltung.GRUNDLEGEND_ALGORITHMISCH: 0.08,
}

_TIER_DELTA: dict[AlgorithmenSenatGeltung, int] = {
    AlgorithmenSenatGeltung.GESPERRT: 0,
    AlgorithmenSenatGeltung.ALGORITHMISCH: 1,
    AlgorithmenSenatGeltung.GRUNDLEGEND_ALGORITHMISCH: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AlgorithmenSenatNorm:
    algorithmen_senat_id: str
    algorithmen_typ: AlgorithmenSenatTyp
    prozedur: AlgorithmenSenatProzedur
    geltung: AlgorithmenSenatGeltung
    algorithmen_weight: float
    algorithmen_tier: int
    canonical: bool
    algorithmen_ids: tuple[str, ...]
    algorithmen_tags: tuple[str, ...]


@dataclass(frozen=True)
class AlgorithmenSenat:
    senat_id: str
    graphen_manifest: GraphenManifest
    normen: tuple[AlgorithmenSenatNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.algorithmen_senat_id for n in self.normen if n.geltung is AlgorithmenSenatGeltung.GESPERRT)

    @property
    def algorithmisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.algorithmen_senat_id for n in self.normen if n.geltung is AlgorithmenSenatGeltung.ALGORITHMISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.algorithmen_senat_id for n in self.normen if n.geltung is AlgorithmenSenatGeltung.GRUNDLEGEND_ALGORITHMISCH)

    @property
    def senat_signal(self):
        if any(n.geltung is AlgorithmenSenatGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-gesperrt")
        elif any(n.geltung is AlgorithmenSenatGeltung.ALGORITHMISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-algorithmisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="senat-grundlegend-algorithmisch")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_algorithmen_senat(
    graphen_manifest: GraphenManifest | None = None,
    *,
    senat_id: str = "algorithmen-senat",
) -> AlgorithmenSenat:
    if graphen_manifest is None:
        graphen_manifest = build_graphen_manifest(manifest_id=f"{senat_id}-manifest")

    normen: list[AlgorithmenSenatNorm] = []
    for parent_norm in graphen_manifest.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{senat_id}-{parent_norm.graphen_manifest_id.removeprefix(f'{graphen_manifest.manifest_id}-')}"
        raw_weight = min(1.0, parent_norm.graphen_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.graphen_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is AlgorithmenSenatGeltung.GRUNDLEGEND_ALGORITHMISCH)
        normen.append(
            AlgorithmenSenatNorm(
                algorithmen_senat_id=new_id,
                algorithmen_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                algorithmen_weight=new_weight,
                algorithmen_tier=new_tier,
                canonical=is_canonical,
                algorithmen_ids=parent_norm.graphen_ids + (new_id,),
                algorithmen_tags=parent_norm.graphen_tags + (f"algorithmen:{new_geltung.value}",),
            )
        )
    return AlgorithmenSenat(
        senat_id=senat_id,
        graphen_manifest=graphen_manifest,
        normen=tuple(normen),
    )
