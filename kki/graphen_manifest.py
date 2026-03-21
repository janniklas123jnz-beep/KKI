"""
#406 GraphenManifest — Graphentheorie: Euler (1736): Königsberger Brücken —
Gründungsdokument der Graphentheorie. Eulerweg/-kreis als topologische Invariante.
Erdős-Rényi (1959): Zufallsgraphen G(n,p) und Phasenübergänge. Dijkstra (1959):
kürzeste Wege. Barabási-Albert (1999): Scale-Free-Netzwerke, präferenzielle
Anhaftung. Watts-Strogatz: Small-World-Phänomen — sechs Grad Trennung.
Leitsterns Schwarm ist graphentheoretisch vernetzt: optimal verbunden,
skalenfrei, klein-weltlich und phasenübergangsresistent.
Geltungsstufen: GESPERRT / GRAPHENTHEORETISCH / GRUNDLEGEND_GRAPHENTHEORETISCH
Parent: SpieltheoriePakt (#405)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .spieltheorie_pakt import (
    SpieltheoriePakt,
    SpieltheoriePaktGeltung,
    build_spieltheorie_pakt,
)

_GELTUNG_MAP: dict[SpieltheoriePaktGeltung, "GraphenManifestGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[SpieltheoriePaktGeltung.GESPERRT] = GraphenManifestGeltung.GESPERRT
    _GELTUNG_MAP[SpieltheoriePaktGeltung.SPIELTHEORETISCH] = GraphenManifestGeltung.GRAPHENTHEORETISCH
    _GELTUNG_MAP[SpieltheoriePaktGeltung.GRUNDLEGEND_SPIELTHEORETISCH] = GraphenManifestGeltung.GRUNDLEGEND_GRAPHENTHEORETISCH


class GraphenManifestTyp(Enum):
    SCHUTZ_GRAPHEN = "schutz-graphen"
    ORDNUNGS_GRAPHEN = "ordnungs-graphen"
    SOUVERAENITAETS_GRAPHEN = "souveraenitaets-graphen"


class GraphenManifestProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class GraphenManifestGeltung(Enum):
    GESPERRT = "gesperrt"
    GRAPHENTHEORETISCH = "graphentheoretisch"
    GRUNDLEGEND_GRAPHENTHEORETISCH = "grundlegend-graphentheoretisch"


_init_map()

_TYP_MAP: dict[GraphenManifestGeltung, GraphenManifestTyp] = {
    GraphenManifestGeltung.GESPERRT: GraphenManifestTyp.SCHUTZ_GRAPHEN,
    GraphenManifestGeltung.GRAPHENTHEORETISCH: GraphenManifestTyp.ORDNUNGS_GRAPHEN,
    GraphenManifestGeltung.GRUNDLEGEND_GRAPHENTHEORETISCH: GraphenManifestTyp.SOUVERAENITAETS_GRAPHEN,
}

_PROZEDUR_MAP: dict[GraphenManifestGeltung, GraphenManifestProzedur] = {
    GraphenManifestGeltung.GESPERRT: GraphenManifestProzedur.NOTPROZEDUR,
    GraphenManifestGeltung.GRAPHENTHEORETISCH: GraphenManifestProzedur.REGELPROTOKOLL,
    GraphenManifestGeltung.GRUNDLEGEND_GRAPHENTHEORETISCH: GraphenManifestProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[GraphenManifestGeltung, float] = {
    GraphenManifestGeltung.GESPERRT: 0.0,
    GraphenManifestGeltung.GRAPHENTHEORETISCH: 0.04,
    GraphenManifestGeltung.GRUNDLEGEND_GRAPHENTHEORETISCH: 0.08,
}

_TIER_DELTA: dict[GraphenManifestGeltung, int] = {
    GraphenManifestGeltung.GESPERRT: 0,
    GraphenManifestGeltung.GRAPHENTHEORETISCH: 1,
    GraphenManifestGeltung.GRUNDLEGEND_GRAPHENTHEORETISCH: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GraphenManifestNorm:
    graphen_manifest_id: str
    graphen_typ: GraphenManifestTyp
    prozedur: GraphenManifestProzedur
    geltung: GraphenManifestGeltung
    graphen_weight: float
    graphen_tier: int
    canonical: bool
    graphen_ids: tuple[str, ...]
    graphen_tags: tuple[str, ...]


@dataclass(frozen=True)
class GraphenManifest:
    manifest_id: str
    spieltheorie_pakt: SpieltheoriePakt
    normen: tuple[GraphenManifestNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.graphen_manifest_id for n in self.normen if n.geltung is GraphenManifestGeltung.GESPERRT)

    @property
    def graphentheoretisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.graphen_manifest_id for n in self.normen if n.geltung is GraphenManifestGeltung.GRAPHENTHEORETISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.graphen_manifest_id for n in self.normen if n.geltung is GraphenManifestGeltung.GRUNDLEGEND_GRAPHENTHEORETISCH)

    @property
    def manifest_signal(self):
        if any(n.geltung is GraphenManifestGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-gesperrt")
        elif any(n.geltung is GraphenManifestGeltung.GRAPHENTHEORETISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-graphentheoretisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="manifest-grundlegend-graphentheoretisch")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_graphen_manifest(
    spieltheorie_pakt: SpieltheoriePakt | None = None,
    *,
    manifest_id: str = "graphen-manifest",
) -> GraphenManifest:
    if spieltheorie_pakt is None:
        spieltheorie_pakt = build_spieltheorie_pakt(pakt_id=f"{manifest_id}-pakt")

    normen: list[GraphenManifestNorm] = []
    for parent_norm in spieltheorie_pakt.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{manifest_id}-{parent_norm.spieltheorie_pakt_id.removeprefix(f'{spieltheorie_pakt.pakt_id}-')}"
        raw_weight = min(1.0, parent_norm.spieltheorie_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.spieltheorie_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is GraphenManifestGeltung.GRUNDLEGEND_GRAPHENTHEORETISCH)
        normen.append(
            GraphenManifestNorm(
                graphen_manifest_id=new_id,
                graphen_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                graphen_weight=new_weight,
                graphen_tier=new_tier,
                canonical=is_canonical,
                graphen_ids=parent_norm.spieltheorie_ids + (new_id,),
                graphen_tags=parent_norm.spieltheorie_tags + (f"graphen:{new_geltung.value}",),
            )
        )
    return GraphenManifest(
        manifest_id=manifest_id,
        spieltheorie_pakt=spieltheorie_pakt,
        normen=tuple(normen),
    )
