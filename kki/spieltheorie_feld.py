"""
#441 SpieltheorieFeld — Spieltheorie: Von Neumann-Morgenstern und Nash-Gleichgewicht.
Von Neumann & Morgenstern (1944): Theory of Games and Economic Behavior — Minimax-Theorem.
Nash (1950): Existenzbeweis gemischter Gleichgewichte in endlichen Spielen, Nobel 1994.
Selten (1965): Teilspielperfektes Gleichgewicht — Rückwärtsinduktion. Nobel 1994.
Leitsterns Agenten handeln spieltheoretisch: jede Aktion ist Strategie im Schwarm-Spiel.
Geltungsstufen: GESPERRT / SPIELTHEORETISCH / GRUNDLEGEND_SPIELTHEORETISCH
Parent: NeurowissenschaftsVerfassung (#440)
Block #441–#450: Spieltheorie & Entscheidungstheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .neurowissenschafts_verfassung import (
    NeurowissenschaftsVerfassung,
    NeurowissenschaftsVerfassungsGeltung,
    build_neurowissenschafts_verfassung,
)

_GELTUNG_MAP: dict[NeurowissenschaftsVerfassungsGeltung, "SpieltheorieFeldGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[NeurowissenschaftsVerfassungsGeltung.GESPERRT] = SpieltheorieFeldGeltung.GESPERRT
    _GELTUNG_MAP[NeurowissenschaftsVerfassungsGeltung.NEUROWISSENSCHAFTLICH] = SpieltheorieFeldGeltung.SPIELTHEORETISCH
    _GELTUNG_MAP[NeurowissenschaftsVerfassungsGeltung.GRUNDLEGEND_NEUROWISSENSCHAFTLICH] = SpieltheorieFeldGeltung.GRUNDLEGEND_SPIELTHEORETISCH


class SpieltheorieFeldTyp(Enum):
    SCHUTZ_SPIELTHEORIE = "schutz-spieltheorie"
    ORDNUNGS_SPIELTHEORIE = "ordnungs-spieltheorie"
    SOUVERAENITAETS_SPIELTHEORIE = "souveraenitaets-spieltheorie"


class SpieltheorieFeldProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class SpieltheorieFeldGeltung(Enum):
    GESPERRT = "gesperrt"
    SPIELTHEORETISCH = "spieltheoretisch"
    GRUNDLEGEND_SPIELTHEORETISCH = "grundlegend-spieltheoretisch"


_init_map()

_TYP_MAP: dict[SpieltheorieFeldGeltung, SpieltheorieFeldTyp] = {
    SpieltheorieFeldGeltung.GESPERRT: SpieltheorieFeldTyp.SCHUTZ_SPIELTHEORIE,
    SpieltheorieFeldGeltung.SPIELTHEORETISCH: SpieltheorieFeldTyp.ORDNUNGS_SPIELTHEORIE,
    SpieltheorieFeldGeltung.GRUNDLEGEND_SPIELTHEORETISCH: SpieltheorieFeldTyp.SOUVERAENITAETS_SPIELTHEORIE,
}

_PROZEDUR_MAP: dict[SpieltheorieFeldGeltung, SpieltheorieFeldProzedur] = {
    SpieltheorieFeldGeltung.GESPERRT: SpieltheorieFeldProzedur.NOTPROZEDUR,
    SpieltheorieFeldGeltung.SPIELTHEORETISCH: SpieltheorieFeldProzedur.REGELPROTOKOLL,
    SpieltheorieFeldGeltung.GRUNDLEGEND_SPIELTHEORETISCH: SpieltheorieFeldProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[SpieltheorieFeldGeltung, float] = {
    SpieltheorieFeldGeltung.GESPERRT: 0.0,
    SpieltheorieFeldGeltung.SPIELTHEORETISCH: 0.04,
    SpieltheorieFeldGeltung.GRUNDLEGEND_SPIELTHEORETISCH: 0.08,
}

_TIER_DELTA: dict[SpieltheorieFeldGeltung, int] = {
    SpieltheorieFeldGeltung.GESPERRT: 0,
    SpieltheorieFeldGeltung.SPIELTHEORETISCH: 1,
    SpieltheorieFeldGeltung.GRUNDLEGEND_SPIELTHEORETISCH: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SpieltheorieFeldNorm:
    spieltheorie_feld_id: str
    spieltheorie_feld_typ: SpieltheorieFeldTyp
    prozedur: SpieltheorieFeldProzedur
    geltung: SpieltheorieFeldGeltung
    spieltheorie_weight: float
    spieltheorie_tier: int
    canonical: bool
    spieltheorie_ids: tuple[str, ...]
    spieltheorie_tags: tuple[str, ...]


@dataclass(frozen=True)
class SpieltheorieFeld:
    feld_id: str
    neurowissenschafts_verfassung: NeurowissenschaftsVerfassung
    normen: tuple[SpieltheorieFeldNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.spieltheorie_feld_id for n in self.normen if n.geltung is SpieltheorieFeldGeltung.GESPERRT)

    @property
    def spieltheoretisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.spieltheorie_feld_id for n in self.normen if n.geltung is SpieltheorieFeldGeltung.SPIELTHEORETISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.spieltheorie_feld_id for n in self.normen if n.geltung is SpieltheorieFeldGeltung.GRUNDLEGEND_SPIELTHEORETISCH)

    @property
    def feld_signal(self):
        if any(n.geltung is SpieltheorieFeldGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-gesperrt")
        elif any(n.geltung is SpieltheorieFeldGeltung.SPIELTHEORETISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-spieltheoretisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="feld-grundlegend-spieltheoretisch")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_spieltheorie_feld(
    neurowissenschafts_verfassung: NeurowissenschaftsVerfassung | None = None,
    *,
    feld_id: str = "spieltheorie-feld",
) -> SpieltheorieFeld:
    if neurowissenschafts_verfassung is None:
        neurowissenschafts_verfassung = build_neurowissenschafts_verfassung(verfassung_id=f"{feld_id}-verfassung")

    normen: list[SpieltheorieFeldNorm] = []
    for parent_norm in neurowissenschafts_verfassung.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{feld_id}-{parent_norm.neurowissenschafts_verfassung_id.removeprefix(f'{neurowissenschafts_verfassung.verfassung_id}-')}"
        raw_weight = min(1.0, parent_norm.neurowissenschafts_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.neurowissenschafts_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SpieltheorieFeldGeltung.GRUNDLEGEND_SPIELTHEORETISCH)
        normen.append(
            SpieltheorieFeldNorm(
                spieltheorie_feld_id=new_id,
                spieltheorie_feld_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                spieltheorie_weight=new_weight,
                spieltheorie_tier=new_tier,
                canonical=is_canonical,
                spieltheorie_ids=parent_norm.neurowissenschafts_ids + (new_id,),
                spieltheorie_tags=parent_norm.neurowissenschafts_tags + (f"spieltheorie-feld:{new_geltung.value}",),
            )
        )
    return SpieltheorieFeld(
        feld_id=feld_id,
        neurowissenschafts_verfassung=neurowissenschafts_verfassung,
        normen=tuple(normen),
    )
