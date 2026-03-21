"""
#405 SpieltheoriePakt — Spieltheorie: von Neumann & Morgenstern (1944): Theory of
Games and Economic Behavior. Nash-Gleichgewicht (1950): Kein Spieler kann durch
einseitige Abweichung gewinnen. Gefangenendilemma: individuelle Rationalität ≠
kollektive Optimalität. Shapley-Wert (1953): fairer Verteilungsschlüssel für
kooperative Spiele. Pareto-Optimalität als Governance-Ziel. Evolutionäre
Spieltheorie (Maynard Smith 1973): Hawk-Dove-Spiel, Evolutionsstabile Strategien.
Leitsterns Kooperation: spieltheoretisch fundiert, auf Nash-Gleichgewichten aufgebaut.
Geltungsstufen: GESPERRT / SPIELTHEORETISCH / GRUNDLEGEND_SPIELTHEORETISCH
Parent: WahrscheinlichkeitsKodex (#404)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .wahrscheinlichkeits_kodex import (
    WahrscheinlichkeitsKodex,
    WahrscheinlichkeitsKodexGeltung,
    build_wahrscheinlichkeits_kodex,
)

_GELTUNG_MAP: dict[WahrscheinlichkeitsKodexGeltung, "SpieltheoriePaktGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[WahrscheinlichkeitsKodexGeltung.GESPERRT] = SpieltheoriePaktGeltung.GESPERRT
    _GELTUNG_MAP[WahrscheinlichkeitsKodexGeltung.PROBABILISTISCH] = SpieltheoriePaktGeltung.SPIELTHEORETISCH
    _GELTUNG_MAP[WahrscheinlichkeitsKodexGeltung.GRUNDLEGEND_PROBABILISTISCH] = SpieltheoriePaktGeltung.GRUNDLEGEND_SPIELTHEORETISCH


class SpieltheoriePaktTyp(Enum):
    SCHUTZ_SPIELTHEORIE = "schutz-spieltheorie"
    ORDNUNGS_SPIELTHEORIE = "ordnungs-spieltheorie"
    SOUVERAENITAETS_SPIELTHEORIE = "souveraenitaets-spieltheorie"


class SpieltheoriePaktProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class SpieltheoriePaktGeltung(Enum):
    GESPERRT = "gesperrt"
    SPIELTHEORETISCH = "spieltheoretisch"
    GRUNDLEGEND_SPIELTHEORETISCH = "grundlegend-spieltheoretisch"


_init_map()

_TYP_MAP: dict[SpieltheoriePaktGeltung, SpieltheoriePaktTyp] = {
    SpieltheoriePaktGeltung.GESPERRT: SpieltheoriePaktTyp.SCHUTZ_SPIELTHEORIE,
    SpieltheoriePaktGeltung.SPIELTHEORETISCH: SpieltheoriePaktTyp.ORDNUNGS_SPIELTHEORIE,
    SpieltheoriePaktGeltung.GRUNDLEGEND_SPIELTHEORETISCH: SpieltheoriePaktTyp.SOUVERAENITAETS_SPIELTHEORIE,
}

_PROZEDUR_MAP: dict[SpieltheoriePaktGeltung, SpieltheoriePaktProzedur] = {
    SpieltheoriePaktGeltung.GESPERRT: SpieltheoriePaktProzedur.NOTPROZEDUR,
    SpieltheoriePaktGeltung.SPIELTHEORETISCH: SpieltheoriePaktProzedur.REGELPROTOKOLL,
    SpieltheoriePaktGeltung.GRUNDLEGEND_SPIELTHEORETISCH: SpieltheoriePaktProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[SpieltheoriePaktGeltung, float] = {
    SpieltheoriePaktGeltung.GESPERRT: 0.0,
    SpieltheoriePaktGeltung.SPIELTHEORETISCH: 0.04,
    SpieltheoriePaktGeltung.GRUNDLEGEND_SPIELTHEORETISCH: 0.08,
}

_TIER_DELTA: dict[SpieltheoriePaktGeltung, int] = {
    SpieltheoriePaktGeltung.GESPERRT: 0,
    SpieltheoriePaktGeltung.SPIELTHEORETISCH: 1,
    SpieltheoriePaktGeltung.GRUNDLEGEND_SPIELTHEORETISCH: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SpieltheoriePaktNorm:
    spieltheorie_pakt_id: str
    spieltheorie_typ: SpieltheoriePaktTyp
    prozedur: SpieltheoriePaktProzedur
    geltung: SpieltheoriePaktGeltung
    spieltheorie_weight: float
    spieltheorie_tier: int
    canonical: bool
    spieltheorie_ids: tuple[str, ...]
    spieltheorie_tags: tuple[str, ...]


@dataclass(frozen=True)
class SpieltheoriePakt:
    pakt_id: str
    wahrscheinlichkeits_kodex: WahrscheinlichkeitsKodex
    normen: tuple[SpieltheoriePaktNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.spieltheorie_pakt_id for n in self.normen if n.geltung is SpieltheoriePaktGeltung.GESPERRT)

    @property
    def spieltheoretisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.spieltheorie_pakt_id for n in self.normen if n.geltung is SpieltheoriePaktGeltung.SPIELTHEORETISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.spieltheorie_pakt_id for n in self.normen if n.geltung is SpieltheoriePaktGeltung.GRUNDLEGEND_SPIELTHEORETISCH)

    @property
    def pakt_signal(self):
        if any(n.geltung is SpieltheoriePaktGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-gesperrt")
        elif any(n.geltung is SpieltheoriePaktGeltung.SPIELTHEORETISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-spieltheoretisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="pakt-grundlegend-spieltheoretisch")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_spieltheorie_pakt(
    wahrscheinlichkeits_kodex: WahrscheinlichkeitsKodex | None = None,
    *,
    pakt_id: str = "spieltheorie-pakt",
) -> SpieltheoriePakt:
    if wahrscheinlichkeits_kodex is None:
        wahrscheinlichkeits_kodex = build_wahrscheinlichkeits_kodex(kodex_id=f"{pakt_id}-kodex")

    normen: list[SpieltheoriePaktNorm] = []
    for parent_norm in wahrscheinlichkeits_kodex.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{pakt_id}-{parent_norm.wahrscheinlichkeits_kodex_id.removeprefix(f'{wahrscheinlichkeits_kodex.kodex_id}-')}"
        raw_weight = min(1.0, parent_norm.wahrscheinlichkeits_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.wahrscheinlichkeits_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SpieltheoriePaktGeltung.GRUNDLEGEND_SPIELTHEORETISCH)
        normen.append(
            SpieltheoriePaktNorm(
                spieltheorie_pakt_id=new_id,
                spieltheorie_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                spieltheorie_weight=new_weight,
                spieltheorie_tier=new_tier,
                canonical=is_canonical,
                spieltheorie_ids=parent_norm.wahrscheinlichkeits_ids + (new_id,),
                spieltheorie_tags=parent_norm.wahrscheinlichkeits_tags + (f"spieltheorie:{new_geltung.value}",),
            )
        )
    return SpieltheoriePakt(
        pakt_id=pakt_id,
        wahrscheinlichkeits_kodex=wahrscheinlichkeits_kodex,
        normen=tuple(normen),
    )
