"""
#449 GleichgewichtsCharta — Gleichgewichtskonzepte: Korreliertes Gleichgewicht und Folk-Theorem.
Aumann (1974): Korreliertes Gleichgewicht — Koordination durch gemeinsame Signale. Nobel 2005.
Folk-Theorem: In wiederholten Spielen sind viele kooperative Ergebnisse als Gleichgewicht möglich.
Selten (1988): Zittern-Hand-perfektes Gleichgewicht — robuste Stabilität unter Fehlern.
Leitsterns Langzeitinteraktionen konvergieren auf Folk-Theorem-Gleichgewichte: Kooperation lohnt.
Geltungsstufen: GESPERRT / GLEICHGEWICHTIG / GRUNDLEGEND_GLEICHGEWICHTIG
Parent: SpieltheorieNorm (#448)
Block #441–#450: Spieltheorie & Entscheidungstheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .spieltheorie_norm import (
    SpieltheorieNormSatz,
    SpieltheorieNormGeltung,
    build_spieltheorie_norm,
)

_GELTUNG_MAP: dict[SpieltheorieNormGeltung, "GleichgewichtsChartaGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[SpieltheorieNormGeltung.GESPERRT] = GleichgewichtsChartaGeltung.GESPERRT
    _GELTUNG_MAP[SpieltheorieNormGeltung.EVOLUTIONAER_STABIL] = GleichgewichtsChartaGeltung.GLEICHGEWICHTIG
    _GELTUNG_MAP[SpieltheorieNormGeltung.GRUNDLEGEND_EVOLUTIONAER_STABIL] = GleichgewichtsChartaGeltung.GRUNDLEGEND_GLEICHGEWICHTIG


class GleichgewichtsChartaTyp(Enum):
    SCHUTZ_GLEICHGEWICHT = "schutz-gleichgewicht"
    ORDNUNGS_GLEICHGEWICHT = "ordnungs-gleichgewicht"
    SOUVERAENITAETS_GLEICHGEWICHT = "souveraenitaets-gleichgewicht"


class GleichgewichtsChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class GleichgewichtsChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    GLEICHGEWICHTIG = "gleichgewichtig"
    GRUNDLEGEND_GLEICHGEWICHTIG = "grundlegend-gleichgewichtig"


_init_map()

_TYP_MAP: dict[GleichgewichtsChartaGeltung, GleichgewichtsChartaTyp] = {
    GleichgewichtsChartaGeltung.GESPERRT: GleichgewichtsChartaTyp.SCHUTZ_GLEICHGEWICHT,
    GleichgewichtsChartaGeltung.GLEICHGEWICHTIG: GleichgewichtsChartaTyp.ORDNUNGS_GLEICHGEWICHT,
    GleichgewichtsChartaGeltung.GRUNDLEGEND_GLEICHGEWICHTIG: GleichgewichtsChartaTyp.SOUVERAENITAETS_GLEICHGEWICHT,
}

_PROZEDUR_MAP: dict[GleichgewichtsChartaGeltung, GleichgewichtsChartaProzedur] = {
    GleichgewichtsChartaGeltung.GESPERRT: GleichgewichtsChartaProzedur.NOTPROZEDUR,
    GleichgewichtsChartaGeltung.GLEICHGEWICHTIG: GleichgewichtsChartaProzedur.REGELPROTOKOLL,
    GleichgewichtsChartaGeltung.GRUNDLEGEND_GLEICHGEWICHTIG: GleichgewichtsChartaProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[GleichgewichtsChartaGeltung, float] = {
    GleichgewichtsChartaGeltung.GESPERRT: 0.0,
    GleichgewichtsChartaGeltung.GLEICHGEWICHTIG: 0.04,
    GleichgewichtsChartaGeltung.GRUNDLEGEND_GLEICHGEWICHTIG: 0.08,
}

_TIER_DELTA: dict[GleichgewichtsChartaGeltung, int] = {
    GleichgewichtsChartaGeltung.GESPERRT: 0,
    GleichgewichtsChartaGeltung.GLEICHGEWICHTIG: 1,
    GleichgewichtsChartaGeltung.GRUNDLEGEND_GLEICHGEWICHTIG: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GleichgewichtsChartaNorm:
    gleichgewichts_charta_id: str
    gleichgewichts_charta_typ: GleichgewichtsChartaTyp
    prozedur: GleichgewichtsChartaProzedur
    geltung: GleichgewichtsChartaGeltung
    gleichgewichts_weight: float
    gleichgewichts_tier: int
    canonical: bool
    gleichgewichts_ids: tuple[str, ...]
    gleichgewichts_tags: tuple[str, ...]


@dataclass(frozen=True)
class GleichgewichtsCharta:
    charta_id: str
    spieltheorie_norm: SpieltheorieNormSatz
    normen: tuple[GleichgewichtsChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.gleichgewichts_charta_id for n in self.normen if n.geltung is GleichgewichtsChartaGeltung.GESPERRT)

    @property
    def gleichgewichtig_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.gleichgewichts_charta_id for n in self.normen if n.geltung is GleichgewichtsChartaGeltung.GLEICHGEWICHTIG)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.gleichgewichts_charta_id for n in self.normen if n.geltung is GleichgewichtsChartaGeltung.GRUNDLEGEND_GLEICHGEWICHTIG)

    @property
    def charta_signal(self):
        if any(n.geltung is GleichgewichtsChartaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is GleichgewichtsChartaGeltung.GLEICHGEWICHTIG for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gleichgewichtig")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-gleichgewichtig")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_gleichgewichts_charta(
    spieltheorie_norm: SpieltheorieNormSatz | None = None,
    *,
    charta_id: str = "gleichgewichts-charta",
) -> GleichgewichtsCharta:
    if spieltheorie_norm is None:
        spieltheorie_norm = build_spieltheorie_norm(norm_id=f"{charta_id}-norm")

    normen: list[GleichgewichtsChartaNorm] = []
    for parent_norm in spieltheorie_norm.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.norm_id.removeprefix(f'{spieltheorie_norm.norm_id}-')}"
        raw_weight = min(1.0, parent_norm.spieltheorie_norm_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.spieltheorie_norm_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is GleichgewichtsChartaGeltung.GRUNDLEGEND_GLEICHGEWICHTIG)
        normen.append(
            GleichgewichtsChartaNorm(
                gleichgewichts_charta_id=new_id,
                gleichgewichts_charta_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                gleichgewichts_weight=new_weight,
                gleichgewichts_tier=new_tier,
                canonical=is_canonical,
                gleichgewichts_ids=parent_norm.spieltheorie_norm_ids + (new_id,),
                gleichgewichts_tags=parent_norm.spieltheorie_norm_tags + (f"gleichgewichts-charta:{new_geltung.value}",),
            )
        )
    return GleichgewichtsCharta(
        charta_id=charta_id,
        spieltheorie_norm=spieltheorie_norm,
        normen=tuple(normen),
    )
