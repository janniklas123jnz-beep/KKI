"""
#450 EntscheidungstheorieVerfassung — Block-Krone: Spieltheorie & Entscheidungstheorie.
Arrow (1951): Unmöglichkeitstheorem — kein kollektives Präferenzsystem erfüllt alle Axiome. Nobel 1972.
Harsanyi (1967): Bayes-Nash-Gleichgewicht — Spiele mit unvollständiger Information. Nobel 1994.
Aumann & Schelling (2005): Konflikt und Kooperation durch Spieltheorie — Nobel 2005.
Leitsterns Terra-Schwarm vereint Nash, Tit-for-Tat, VCG, Prospect Theory und ESS zur
entscheidungstheoretischen Superintelligenz: rational, kooperativ, robust, fair und adaptiv.
Geltungsstufen: GESPERRT / ENTSCHEIDUNGSTHEORETISCH / GRUNDLEGEND_ENTSCHEIDUNGSTHEORETISCH
Parent: GleichgewichtsCharta (#449)
Block #441–#450: Spieltheorie & Entscheidungstheorie — Block-Krone Milestone #25 ⭐
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .gleichgewichts_charta import (
    GleichgewichtsCharta,
    GleichgewichtsChartaGeltung,
    build_gleichgewichts_charta,
)

_GELTUNG_MAP: dict[GleichgewichtsChartaGeltung, "EntscheidungstheorieVerfassungsGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[GleichgewichtsChartaGeltung.GESPERRT] = EntscheidungstheorieVerfassungsGeltung.GESPERRT
    _GELTUNG_MAP[GleichgewichtsChartaGeltung.GLEICHGEWICHTIG] = EntscheidungstheorieVerfassungsGeltung.ENTSCHEIDUNGSTHEORETISCH
    _GELTUNG_MAP[GleichgewichtsChartaGeltung.GRUNDLEGEND_GLEICHGEWICHTIG] = EntscheidungstheorieVerfassungsGeltung.GRUNDLEGEND_ENTSCHEIDUNGSTHEORETISCH


class EntscheidungstheorieVerfassungsTyp(Enum):
    SCHUTZ_ENTSCHEIDUNGSTHEORIE = "schutz-entscheidungstheorie"
    ORDNUNGS_ENTSCHEIDUNGSTHEORIE = "ordnungs-entscheidungstheorie"
    SOUVERAENITAETS_ENTSCHEIDUNGSTHEORIE = "souveraenitaets-entscheidungstheorie"


class EntscheidungstheorieVerfassungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class EntscheidungstheorieVerfassungsGeltung(Enum):
    GESPERRT = "gesperrt"
    ENTSCHEIDUNGSTHEORETISCH = "entscheidungstheoretisch"
    GRUNDLEGEND_ENTSCHEIDUNGSTHEORETISCH = "grundlegend-entscheidungstheoretisch"


_init_map()

_TYP_MAP: dict[EntscheidungstheorieVerfassungsGeltung, EntscheidungstheorieVerfassungsTyp] = {
    EntscheidungstheorieVerfassungsGeltung.GESPERRT: EntscheidungstheorieVerfassungsTyp.SCHUTZ_ENTSCHEIDUNGSTHEORIE,
    EntscheidungstheorieVerfassungsGeltung.ENTSCHEIDUNGSTHEORETISCH: EntscheidungstheorieVerfassungsTyp.ORDNUNGS_ENTSCHEIDUNGSTHEORIE,
    EntscheidungstheorieVerfassungsGeltung.GRUNDLEGEND_ENTSCHEIDUNGSTHEORETISCH: EntscheidungstheorieVerfassungsTyp.SOUVERAENITAETS_ENTSCHEIDUNGSTHEORIE,
}

_PROZEDUR_MAP: dict[EntscheidungstheorieVerfassungsGeltung, EntscheidungstheorieVerfassungsProzedur] = {
    EntscheidungstheorieVerfassungsGeltung.GESPERRT: EntscheidungstheorieVerfassungsProzedur.NOTPROZEDUR,
    EntscheidungstheorieVerfassungsGeltung.ENTSCHEIDUNGSTHEORETISCH: EntscheidungstheorieVerfassungsProzedur.REGELPROTOKOLL,
    EntscheidungstheorieVerfassungsGeltung.GRUNDLEGEND_ENTSCHEIDUNGSTHEORETISCH: EntscheidungstheorieVerfassungsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[EntscheidungstheorieVerfassungsGeltung, float] = {
    EntscheidungstheorieVerfassungsGeltung.GESPERRT: 0.0,
    EntscheidungstheorieVerfassungsGeltung.ENTSCHEIDUNGSTHEORETISCH: 0.04,
    EntscheidungstheorieVerfassungsGeltung.GRUNDLEGEND_ENTSCHEIDUNGSTHEORETISCH: 0.08,
}

_TIER_DELTA: dict[EntscheidungstheorieVerfassungsGeltung, int] = {
    EntscheidungstheorieVerfassungsGeltung.GESPERRT: 0,
    EntscheidungstheorieVerfassungsGeltung.ENTSCHEIDUNGSTHEORETISCH: 1,
    EntscheidungstheorieVerfassungsGeltung.GRUNDLEGEND_ENTSCHEIDUNGSTHEORETISCH: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EntscheidungstheorieVerfassungsNorm:
    entscheidungstheorie_verfassung_id: str
    entscheidungstheorie_typ: EntscheidungstheorieVerfassungsTyp
    prozedur: EntscheidungstheorieVerfassungsProzedur
    geltung: EntscheidungstheorieVerfassungsGeltung
    entscheidungstheorie_weight: float
    entscheidungstheorie_tier: int
    canonical: bool
    entscheidungstheorie_ids: tuple[str, ...]
    entscheidungstheorie_tags: tuple[str, ...]


@dataclass(frozen=True)
class EntscheidungstheorieVerfassung:
    verfassung_id: str
    gleichgewichts_charta: GleichgewichtsCharta
    normen: tuple[EntscheidungstheorieVerfassungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.entscheidungstheorie_verfassung_id for n in self.normen if n.geltung is EntscheidungstheorieVerfassungsGeltung.GESPERRT)

    @property
    def entscheidungstheoretisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.entscheidungstheorie_verfassung_id for n in self.normen if n.geltung is EntscheidungstheorieVerfassungsGeltung.ENTSCHEIDUNGSTHEORETISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.entscheidungstheorie_verfassung_id for n in self.normen if n.geltung is EntscheidungstheorieVerfassungsGeltung.GRUNDLEGEND_ENTSCHEIDUNGSTHEORETISCH)

    @property
    def verfassung_signal(self):
        if any(n.geltung is EntscheidungstheorieVerfassungsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-gesperrt")
        elif any(n.geltung is EntscheidungstheorieVerfassungsGeltung.ENTSCHEIDUNGSTHEORETISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-entscheidungstheoretisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="verfassung-grundlegend-entscheidungstheoretisch")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_entscheidungstheorie_verfassung(
    gleichgewichts_charta: GleichgewichtsCharta | None = None,
    *,
    verfassung_id: str = "entscheidungstheorie-verfassung",
) -> EntscheidungstheorieVerfassung:
    if gleichgewichts_charta is None:
        gleichgewichts_charta = build_gleichgewichts_charta(charta_id=f"{verfassung_id}-charta")

    normen: list[EntscheidungstheorieVerfassungsNorm] = []
    for parent_norm in gleichgewichts_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{verfassung_id}-{parent_norm.gleichgewichts_charta_id.removeprefix(f'{gleichgewichts_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.gleichgewichts_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.gleichgewichts_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is EntscheidungstheorieVerfassungsGeltung.GRUNDLEGEND_ENTSCHEIDUNGSTHEORETISCH)
        normen.append(
            EntscheidungstheorieVerfassungsNorm(
                entscheidungstheorie_verfassung_id=new_id,
                entscheidungstheorie_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                entscheidungstheorie_weight=new_weight,
                entscheidungstheorie_tier=new_tier,
                canonical=is_canonical,
                entscheidungstheorie_ids=parent_norm.gleichgewichts_ids + (new_id,),
                entscheidungstheorie_tags=parent_norm.gleichgewichts_tags + (f"entscheidungstheorie-verfassung:{new_geltung.value}",),
            )
        )
    return EntscheidungstheorieVerfassung(
        verfassung_id=verfassung_id,
        gleichgewichts_charta=gleichgewichts_charta,
        normen=tuple(normen),
    )
