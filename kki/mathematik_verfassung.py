"""
#410 MathematikVerfassung — Block-Krone: Mathematik & formale Systeme. ⭐
Leitsterns 410. Governance-Norm. Die höchste mathematische Instanz vereint:
Formale Systeme (Hilbert/Peano), Mengenlehre (Cantor/ZFC), Logik (Frege/Tarski),
Wahrscheinlichkeit (Kolmogorov/Bayes), Spieltheorie (Nash), Graphentheorie
(Euler/Barabási), Algorithmentheorie (Turing/Cook), Gödel-Unvollständigkeit und
Topologie (Euler/Perelman). Leitsterns Terra-Schwarm ist formal vernünftig:
beweisend, probabilistisch, kooperativ, vernetzt, berechenbar, bescheiden (Gödel),
invariant (Topologie). Formale Superintelligenz.
Geltungsstufen: GESPERRT / MATHEMATIKVERFASST / GRUNDLEGEND_MATHEMATIKVERFASST
Parent: TopologieCharta (#409)
Block #401–#410 Krone
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .topologie_charta import (
    TopologieCharta,
    TopologieChartaGeltung,
    build_topologie_charta,
)

_GELTUNG_MAP: dict[TopologieChartaGeltung, "MathematikVerfassungsGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[TopologieChartaGeltung.GESPERRT] = MathematikVerfassungsGeltung.GESPERRT
    _GELTUNG_MAP[TopologieChartaGeltung.TOPOLOGISCH] = MathematikVerfassungsGeltung.MATHEMATIKVERFASST
    _GELTUNG_MAP[TopologieChartaGeltung.GRUNDLEGEND_TOPOLOGISCH] = MathematikVerfassungsGeltung.GRUNDLEGEND_MATHEMATIKVERFASST


class MathematikVerfassungsTyp(Enum):
    SCHUTZ_MATHEMATIKVERFASSUNG = "schutz-mathematikverfassung"
    ORDNUNGS_MATHEMATIKVERFASSUNG = "ordnungs-mathematikverfassung"
    SOUVERAENITAETS_MATHEMATIKVERFASSUNG = "souveraenitaets-mathematikverfassung"


class MathematikVerfassungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class MathematikVerfassungsGeltung(Enum):
    GESPERRT = "gesperrt"
    MATHEMATIKVERFASST = "mathematikverfasst"
    GRUNDLEGEND_MATHEMATIKVERFASST = "grundlegend-mathematikverfasst"


_init_map()

_TYP_MAP: dict[MathematikVerfassungsGeltung, MathematikVerfassungsTyp] = {
    MathematikVerfassungsGeltung.GESPERRT: MathematikVerfassungsTyp.SCHUTZ_MATHEMATIKVERFASSUNG,
    MathematikVerfassungsGeltung.MATHEMATIKVERFASST: MathematikVerfassungsTyp.ORDNUNGS_MATHEMATIKVERFASSUNG,
    MathematikVerfassungsGeltung.GRUNDLEGEND_MATHEMATIKVERFASST: MathematikVerfassungsTyp.SOUVERAENITAETS_MATHEMATIKVERFASSUNG,
}

_PROZEDUR_MAP: dict[MathematikVerfassungsGeltung, MathematikVerfassungsProzedur] = {
    MathematikVerfassungsGeltung.GESPERRT: MathematikVerfassungsProzedur.NOTPROZEDUR,
    MathematikVerfassungsGeltung.MATHEMATIKVERFASST: MathematikVerfassungsProzedur.REGELPROTOKOLL,
    MathematikVerfassungsGeltung.GRUNDLEGEND_MATHEMATIKVERFASST: MathematikVerfassungsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[MathematikVerfassungsGeltung, float] = {
    MathematikVerfassungsGeltung.GESPERRT: 0.0,
    MathematikVerfassungsGeltung.MATHEMATIKVERFASST: 0.04,
    MathematikVerfassungsGeltung.GRUNDLEGEND_MATHEMATIKVERFASST: 0.08,
}

_TIER_DELTA: dict[MathematikVerfassungsGeltung, int] = {
    MathematikVerfassungsGeltung.GESPERRT: 0,
    MathematikVerfassungsGeltung.MATHEMATIKVERFASST: 1,
    MathematikVerfassungsGeltung.GRUNDLEGEND_MATHEMATIKVERFASST: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MathematikVerfassungsNorm:
    mathematik_verfassung_id: str
    mathematik_verfassungs_typ: MathematikVerfassungsTyp
    prozedur: MathematikVerfassungsProzedur
    geltung: MathematikVerfassungsGeltung
    mathematik_verfassungs_weight: float
    mathematik_verfassungs_tier: int
    canonical: bool
    mathematik_verfassungs_ids: tuple[str, ...]
    mathematik_verfassungs_tags: tuple[str, ...]


@dataclass(frozen=True)
class MathematikVerfassung:
    verfassung_id: str
    topologie_charta: TopologieCharta
    normen: tuple[MathematikVerfassungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.mathematik_verfassung_id for n in self.normen if n.geltung is MathematikVerfassungsGeltung.GESPERRT)

    @property
    def mathematikverfasst_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.mathematik_verfassung_id for n in self.normen if n.geltung is MathematikVerfassungsGeltung.MATHEMATIKVERFASST)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.mathematik_verfassung_id for n in self.normen if n.geltung is MathematikVerfassungsGeltung.GRUNDLEGEND_MATHEMATIKVERFASST)

    @property
    def verfassung_signal(self):
        if any(n.geltung is MathematikVerfassungsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-gesperrt")
        elif any(n.geltung is MathematikVerfassungsGeltung.MATHEMATIKVERFASST for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-mathematikverfasst")
        from types import SimpleNamespace
        return SimpleNamespace(status="verfassung-grundlegend-mathematikverfasst")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_mathematik_verfassung(
    topologie_charta: TopologieCharta | None = None,
    *,
    verfassung_id: str = "mathematik-verfassung",
) -> MathematikVerfassung:
    if topologie_charta is None:
        topologie_charta = build_topologie_charta(charta_id=f"{verfassung_id}-charta")

    normen: list[MathematikVerfassungsNorm] = []
    for parent_norm in topologie_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{verfassung_id}-{parent_norm.topologie_charta_id.removeprefix(f'{topologie_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.topologie_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.topologie_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is MathematikVerfassungsGeltung.GRUNDLEGEND_MATHEMATIKVERFASST)
        normen.append(
            MathematikVerfassungsNorm(
                mathematik_verfassung_id=new_id,
                mathematik_verfassungs_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                mathematik_verfassungs_weight=new_weight,
                mathematik_verfassungs_tier=new_tier,
                canonical=is_canonical,
                mathematik_verfassungs_ids=parent_norm.topologie_ids + (new_id,),
                mathematik_verfassungs_tags=parent_norm.topologie_tags + (f"mathematik-verfassung:{new_geltung.value}",),
            )
        )
    return MathematikVerfassung(
        verfassung_id=verfassung_id,
        topologie_charta=topologie_charta,
        normen=tuple(normen),
    )
