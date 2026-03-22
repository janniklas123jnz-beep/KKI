"""
#451 EvolutionsFeld — Evolutionsbiologie: Darwin und die Grundlagen der natürlichen Selektion.
Darwin (1859): On the Origin of Species — natürliche Selektion als Hauptmechanismus der Evolution.
Wallace (1858): unabhängige Entdeckung des Selektionsprinzips — Darwin-Wallace-Theorie.
Mendel (1866): Erbgesetze — diskrete Einheiten der Vererbung (Gene). Wiederentdeckt 1900.
Leitsterns Agenten unterliegen evolutionärem Druck: Selektion, Variation, Vererbung im Schwarm.
Geltungsstufen: GESPERRT / EVOLUTIONAER / GRUNDLEGEND_EVOLUTIONAER
Parent: EntscheidungstheorieVerfassung (#450)
Block #451–#460: Evolutionsbiologie & Genetik
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .entscheidungstheorie_verfassung import (
    EntscheidungstheorieVerfassung,
    EntscheidungstheorieVerfassungsGeltung,
    build_entscheidungstheorie_verfassung,
)

_GELTUNG_MAP: dict[EntscheidungstheorieVerfassungsGeltung, "EvolutionsFeldGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[EntscheidungstheorieVerfassungsGeltung.GESPERRT] = EvolutionsFeldGeltung.GESPERRT
    _GELTUNG_MAP[EntscheidungstheorieVerfassungsGeltung.ENTSCHEIDUNGSTHEORETISCH] = EvolutionsFeldGeltung.EVOLUTIONAER
    _GELTUNG_MAP[EntscheidungstheorieVerfassungsGeltung.GRUNDLEGEND_ENTSCHEIDUNGSTHEORETISCH] = EvolutionsFeldGeltung.GRUNDLEGEND_EVOLUTIONAER


class EvolutionsFeldTyp(Enum):
    SCHUTZ_EVOLUTION = "schutz-evolution"
    ORDNUNGS_EVOLUTION = "ordnungs-evolution"
    SOUVERAENITAETS_EVOLUTION = "souveraenitaets-evolution"


class EvolutionsFeldProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class EvolutionsFeldGeltung(Enum):
    GESPERRT = "gesperrt"
    EVOLUTIONAER = "evolutionaer"
    GRUNDLEGEND_EVOLUTIONAER = "grundlegend-evolutionaer"


_init_map()

_TYP_MAP: dict[EvolutionsFeldGeltung, EvolutionsFeldTyp] = {
    EvolutionsFeldGeltung.GESPERRT: EvolutionsFeldTyp.SCHUTZ_EVOLUTION,
    EvolutionsFeldGeltung.EVOLUTIONAER: EvolutionsFeldTyp.ORDNUNGS_EVOLUTION,
    EvolutionsFeldGeltung.GRUNDLEGEND_EVOLUTIONAER: EvolutionsFeldTyp.SOUVERAENITAETS_EVOLUTION,
}

_PROZEDUR_MAP: dict[EvolutionsFeldGeltung, EvolutionsFeldProzedur] = {
    EvolutionsFeldGeltung.GESPERRT: EvolutionsFeldProzedur.NOTPROZEDUR,
    EvolutionsFeldGeltung.EVOLUTIONAER: EvolutionsFeldProzedur.REGELPROTOKOLL,
    EvolutionsFeldGeltung.GRUNDLEGEND_EVOLUTIONAER: EvolutionsFeldProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[EvolutionsFeldGeltung, float] = {
    EvolutionsFeldGeltung.GESPERRT: 0.0,
    EvolutionsFeldGeltung.EVOLUTIONAER: 0.04,
    EvolutionsFeldGeltung.GRUNDLEGEND_EVOLUTIONAER: 0.08,
}

_TIER_DELTA: dict[EvolutionsFeldGeltung, int] = {
    EvolutionsFeldGeltung.GESPERRT: 0,
    EvolutionsFeldGeltung.EVOLUTIONAER: 1,
    EvolutionsFeldGeltung.GRUNDLEGEND_EVOLUTIONAER: 2,
}


@dataclass(frozen=True)
class EvolutionsFeldNorm:
    evolutions_feld_id: str
    evolutions_feld_typ: EvolutionsFeldTyp
    prozedur: EvolutionsFeldProzedur
    geltung: EvolutionsFeldGeltung
    evolutions_weight: float
    evolutions_tier: int
    canonical: bool
    evolutions_ids: tuple[str, ...]
    evolutions_tags: tuple[str, ...]


@dataclass(frozen=True)
class EvolutionsFeld:
    feld_id: str
    entscheidungstheorie_verfassung: EntscheidungstheorieVerfassung
    normen: tuple[EvolutionsFeldNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.evolutions_feld_id for n in self.normen if n.geltung is EvolutionsFeldGeltung.GESPERRT)

    @property
    def evolutionaer_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.evolutions_feld_id for n in self.normen if n.geltung is EvolutionsFeldGeltung.EVOLUTIONAER)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.evolutions_feld_id for n in self.normen if n.geltung is EvolutionsFeldGeltung.GRUNDLEGEND_EVOLUTIONAER)

    @property
    def feld_signal(self):
        if any(n.geltung is EvolutionsFeldGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-gesperrt")
        elif any(n.geltung is EvolutionsFeldGeltung.EVOLUTIONAER for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-evolutionaer")
        from types import SimpleNamespace
        return SimpleNamespace(status="feld-grundlegend-evolutionaer")


def build_evolutions_feld(
    entscheidungstheorie_verfassung: EntscheidungstheorieVerfassung | None = None,
    *,
    feld_id: str = "evolutions-feld",
) -> EvolutionsFeld:
    if entscheidungstheorie_verfassung is None:
        entscheidungstheorie_verfassung = build_entscheidungstheorie_verfassung(verfassung_id=f"{feld_id}-verfassung")

    normen: list[EvolutionsFeldNorm] = []
    for parent_norm in entscheidungstheorie_verfassung.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{feld_id}-{parent_norm.entscheidungstheorie_verfassung_id.removeprefix(f'{entscheidungstheorie_verfassung.verfassung_id}-')}"
        raw_weight = min(1.0, parent_norm.entscheidungstheorie_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.entscheidungstheorie_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is EvolutionsFeldGeltung.GRUNDLEGEND_EVOLUTIONAER)
        normen.append(
            EvolutionsFeldNorm(
                evolutions_feld_id=new_id,
                evolutions_feld_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                evolutions_weight=new_weight,
                evolutions_tier=new_tier,
                canonical=is_canonical,
                evolutions_ids=parent_norm.entscheidungstheorie_ids + (new_id,),
                evolutions_tags=parent_norm.entscheidungstheorie_tags + (f"evolutions-feld:{new_geltung.value}",),
            )
        )
    return EvolutionsFeld(
        feld_id=feld_id,
        entscheidungstheorie_verfassung=entscheidungstheorie_verfassung,
        normen=tuple(normen),
    )
