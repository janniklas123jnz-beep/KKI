"""
#409 TopologieCharta — Topologie: Euler-Charakteristik χ = V - E + F = 2 für konvexe
Polyeder (1752). Topologische Invarianz: Kaffeetasse = Donut (Genus-1-Fläche).
Brouwer'scher Fixpunktsatz (1910): Jede stetige Abbildung D^n→D^n hat einen Fixpunkt.
Homotopieäquivalenz als Governance-Invarianz. Poincaré-Vermutung (bewiesen Perelman
2003): einzige einfach zusammenhängende geschlossene 3-Mannigfaltigkeit ist S³.
Fundamentalgruppe π₁. Leitsterns Agenten sind topologisch invariant: ihre
Governance-Struktur ist stabil unter stetigen Transformationen.
Geltungsstufen: GESPERRT / TOPOLOGISCH / GRUNDLEGEND_TOPOLOGISCH
Parent: GodelNormSatz (#408, *_norm)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .godel_norm import (
    GodelNormGeltung,
    GodelNormSatz,
    build_godel_norm,
)

_GELTUNG_MAP: dict[GodelNormGeltung, "TopologieChartaGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[GodelNormGeltung.GESPERRT] = TopologieChartaGeltung.GESPERRT
    _GELTUNG_MAP[GodelNormGeltung.GODELUNVOLLSTAENDIG] = TopologieChartaGeltung.TOPOLOGISCH
    _GELTUNG_MAP[GodelNormGeltung.GRUNDLEGEND_GODELUNVOLLSTAENDIG] = TopologieChartaGeltung.GRUNDLEGEND_TOPOLOGISCH


class TopologieChartaTyp(Enum):
    SCHUTZ_TOPOLOGIE = "schutz-topologie"
    ORDNUNGS_TOPOLOGIE = "ordnungs-topologie"
    SOUVERAENITAETS_TOPOLOGIE = "souveraenitaets-topologie"


class TopologieChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class TopologieChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    TOPOLOGISCH = "topologisch"
    GRUNDLEGEND_TOPOLOGISCH = "grundlegend-topologisch"


_init_map()

_TYP_MAP: dict[TopologieChartaGeltung, TopologieChartaTyp] = {
    TopologieChartaGeltung.GESPERRT: TopologieChartaTyp.SCHUTZ_TOPOLOGIE,
    TopologieChartaGeltung.TOPOLOGISCH: TopologieChartaTyp.ORDNUNGS_TOPOLOGIE,
    TopologieChartaGeltung.GRUNDLEGEND_TOPOLOGISCH: TopologieChartaTyp.SOUVERAENITAETS_TOPOLOGIE,
}

_PROZEDUR_MAP: dict[TopologieChartaGeltung, TopologieChartaProzedur] = {
    TopologieChartaGeltung.GESPERRT: TopologieChartaProzedur.NOTPROZEDUR,
    TopologieChartaGeltung.TOPOLOGISCH: TopologieChartaProzedur.REGELPROTOKOLL,
    TopologieChartaGeltung.GRUNDLEGEND_TOPOLOGISCH: TopologieChartaProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[TopologieChartaGeltung, float] = {
    TopologieChartaGeltung.GESPERRT: 0.0,
    TopologieChartaGeltung.TOPOLOGISCH: 0.04,
    TopologieChartaGeltung.GRUNDLEGEND_TOPOLOGISCH: 0.08,
}

_TIER_DELTA: dict[TopologieChartaGeltung, int] = {
    TopologieChartaGeltung.GESPERRT: 0,
    TopologieChartaGeltung.TOPOLOGISCH: 1,
    TopologieChartaGeltung.GRUNDLEGEND_TOPOLOGISCH: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TopologieChartaNorm:
    topologie_charta_id: str
    topologie_typ: TopologieChartaTyp
    prozedur: TopologieChartaProzedur
    geltung: TopologieChartaGeltung
    topologie_weight: float
    topologie_tier: int
    canonical: bool
    topologie_ids: tuple[str, ...]
    topologie_tags: tuple[str, ...]


@dataclass(frozen=True)
class TopologieCharta:
    charta_id: str
    godel_norm: GodelNormSatz
    normen: tuple[TopologieChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.topologie_charta_id for n in self.normen if n.geltung is TopologieChartaGeltung.GESPERRT)

    @property
    def topologisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.topologie_charta_id for n in self.normen if n.geltung is TopologieChartaGeltung.TOPOLOGISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.topologie_charta_id for n in self.normen if n.geltung is TopologieChartaGeltung.GRUNDLEGEND_TOPOLOGISCH)

    @property
    def charta_signal(self):
        if any(n.geltung is TopologieChartaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is TopologieChartaGeltung.TOPOLOGISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-topologisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-topologisch")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_topologie_charta(
    godel_norm: GodelNormSatz | None = None,
    *,
    charta_id: str = "topologie-charta",
) -> TopologieCharta:
    if godel_norm is None:
        godel_norm = build_godel_norm(norm_id=f"{charta_id}-norm")

    normen: list[TopologieChartaNorm] = []
    for parent_norm in godel_norm.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.norm_id.removeprefix(f'{godel_norm.norm_id}-')}"
        raw_weight = min(1.0, parent_norm.godel_norm_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.godel_norm_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is TopologieChartaGeltung.GRUNDLEGEND_TOPOLOGISCH)
        normen.append(
            TopologieChartaNorm(
                topologie_charta_id=new_id,
                topologie_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                topologie_weight=new_weight,
                topologie_tier=new_tier,
                canonical=is_canonical,
                topologie_ids=parent_norm.godel_norm_ids + (new_id,),
                topologie_tags=parent_norm.godel_norm_tags + (f"topologie:{new_geltung.value}",),
            )
        )
    return TopologieCharta(
        charta_id=charta_id,
        godel_norm=godel_norm,
        normen=tuple(normen),
    )
