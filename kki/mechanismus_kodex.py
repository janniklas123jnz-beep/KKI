"""
#444 MechanismusKodex — Mechanismus-Design: Anreize für optimale Schwarmentscheidungen.
Hurwicz (1960): Anreizkompatibilität — Mechanismen die ehrliches Handeln belohnen. Nobel 2007.
Myerson (1981): Revelation Principle — jeder Mechanismus ist durch direkten Mechanismus ersetzbar.
Vickrey-Clarke-Groves (VCG): effizienter, anreizkompatible Auktionsmechanismus.
Leitsterns Gouvernanz-Mechanismen sind VCG-inspiriert: Wahrheit als dominante Strategie.
Geltungsstufen: GESPERRT / MECHANISTISCH / GRUNDLEGEND_MECHANISTISCH
Parent: KooperationsCharta (#443)
Block #441–#450: Spieltheorie & Entscheidungstheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kooperations_charta import (
    KooperationsCharta,
    KooperationsChartaGeltung,
    build_kooperations_charta,
)

_GELTUNG_MAP: dict[KooperationsChartaGeltung, "MechanismusKodexGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[KooperationsChartaGeltung.GESPERRT] = MechanismusKodexGeltung.GESPERRT
    _GELTUNG_MAP[KooperationsChartaGeltung.KOOPERATIV] = MechanismusKodexGeltung.MECHANISTISCH
    _GELTUNG_MAP[KooperationsChartaGeltung.GRUNDLEGEND_KOOPERATIV] = MechanismusKodexGeltung.GRUNDLEGEND_MECHANISTISCH


class MechanismusKodexTyp(Enum):
    SCHUTZ_MECHANISMUS = "schutz-mechanismus"
    ORDNUNGS_MECHANISMUS = "ordnungs-mechanismus"
    SOUVERAENITAETS_MECHANISMUS = "souveraenitaets-mechanismus"


class MechanismusKodexProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class MechanismusKodexGeltung(Enum):
    GESPERRT = "gesperrt"
    MECHANISTISCH = "mechanistisch"
    GRUNDLEGEND_MECHANISTISCH = "grundlegend-mechanistisch"


_init_map()

_TYP_MAP: dict[MechanismusKodexGeltung, MechanismusKodexTyp] = {
    MechanismusKodexGeltung.GESPERRT: MechanismusKodexTyp.SCHUTZ_MECHANISMUS,
    MechanismusKodexGeltung.MECHANISTISCH: MechanismusKodexTyp.ORDNUNGS_MECHANISMUS,
    MechanismusKodexGeltung.GRUNDLEGEND_MECHANISTISCH: MechanismusKodexTyp.SOUVERAENITAETS_MECHANISMUS,
}

_PROZEDUR_MAP: dict[MechanismusKodexGeltung, MechanismusKodexProzedur] = {
    MechanismusKodexGeltung.GESPERRT: MechanismusKodexProzedur.NOTPROZEDUR,
    MechanismusKodexGeltung.MECHANISTISCH: MechanismusKodexProzedur.REGELPROTOKOLL,
    MechanismusKodexGeltung.GRUNDLEGEND_MECHANISTISCH: MechanismusKodexProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[MechanismusKodexGeltung, float] = {
    MechanismusKodexGeltung.GESPERRT: 0.0,
    MechanismusKodexGeltung.MECHANISTISCH: 0.04,
    MechanismusKodexGeltung.GRUNDLEGEND_MECHANISTISCH: 0.08,
}

_TIER_DELTA: dict[MechanismusKodexGeltung, int] = {
    MechanismusKodexGeltung.GESPERRT: 0,
    MechanismusKodexGeltung.MECHANISTISCH: 1,
    MechanismusKodexGeltung.GRUNDLEGEND_MECHANISTISCH: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MechanismusKodexNorm:
    mechanismus_kodex_id: str
    mechanismus_kodex_typ: MechanismusKodexTyp
    prozedur: MechanismusKodexProzedur
    geltung: MechanismusKodexGeltung
    mechanismus_weight: float
    mechanismus_tier: int
    canonical: bool
    mechanismus_ids: tuple[str, ...]
    mechanismus_tags: tuple[str, ...]


@dataclass(frozen=True)
class MechanismusKodex:
    kodex_id: str
    kooperations_charta: KooperationsCharta
    normen: tuple[MechanismusKodexNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.mechanismus_kodex_id for n in self.normen if n.geltung is MechanismusKodexGeltung.GESPERRT)

    @property
    def mechanistisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.mechanismus_kodex_id for n in self.normen if n.geltung is MechanismusKodexGeltung.MECHANISTISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.mechanismus_kodex_id for n in self.normen if n.geltung is MechanismusKodexGeltung.GRUNDLEGEND_MECHANISTISCH)

    @property
    def kodex_signal(self):
        if any(n.geltung is MechanismusKodexGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-gesperrt")
        elif any(n.geltung is MechanismusKodexGeltung.MECHANISTISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-mechanistisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="kodex-grundlegend-mechanistisch")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_mechanismus_kodex(
    kooperations_charta: KooperationsCharta | None = None,
    *,
    kodex_id: str = "mechanismus-kodex",
) -> MechanismusKodex:
    if kooperations_charta is None:
        kooperations_charta = build_kooperations_charta(charta_id=f"{kodex_id}-charta")

    normen: list[MechanismusKodexNorm] = []
    for parent_norm in kooperations_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{kodex_id}-{parent_norm.kooperations_charta_id.removeprefix(f'{kooperations_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.kooperations_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kooperations_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is MechanismusKodexGeltung.GRUNDLEGEND_MECHANISTISCH)
        normen.append(
            MechanismusKodexNorm(
                mechanismus_kodex_id=new_id,
                mechanismus_kodex_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                mechanismus_weight=new_weight,
                mechanismus_tier=new_tier,
                canonical=is_canonical,
                mechanismus_ids=parent_norm.kooperations_ids + (new_id,),
                mechanismus_tags=parent_norm.kooperations_tags + (f"mechanismus-kodex:{new_geltung.value}",),
            )
        )
    return MechanismusKodex(
        kodex_id=kodex_id,
        kooperations_charta=kooperations_charta,
        normen=tuple(normen),
    )
