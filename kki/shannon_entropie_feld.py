"""
#371 ShannonEntropieFeld — Shannon-Entropie H = -Σ p·log₂(p): Das fundamentale
Maß der Ungewissheit. Claude Shannon 1948 bewies mathematisch, dass Information
quantifizierbar ist. Leitsterns Entropie-Feld misst den Informationsgehalt jeder
Agentenentscheidung: maximale Entropie = maximale Freiheit, null Entropie = absolute
Gewissheit. Keine Governance-Entscheidung ohne Entropiebilanz.
Geltungsstufen: GESPERRT / ENTROPISCH / GRUNDLEGEND_ENTROPISCH
Parent: ChaosVerfassung (#370)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .chaos_verfassung import (
    ChaosVerfassung,
    ChaosVerfassungsGeltung,
    build_chaos_verfassung,
)

_GELTUNG_MAP: dict[ChaosVerfassungsGeltung, "ShannonEntropieGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[ChaosVerfassungsGeltung.GESPERRT] = ShannonEntropieGeltung.GESPERRT
    _GELTUNG_MAP[ChaosVerfassungsGeltung.CHAOSVERFASST] = ShannonEntropieGeltung.ENTROPISCH
    _GELTUNG_MAP[ChaosVerfassungsGeltung.GRUNDLEGEND_CHAOSVERFASST] = ShannonEntropieGeltung.GRUNDLEGEND_ENTROPISCH


class ShannonEntropieTyp(Enum):
    SCHUTZ_SHANNON_ENTROPIE = "schutz-shannon-entropie"
    ORDNUNGS_SHANNON_ENTROPIE = "ordnungs-shannon-entropie"
    SOUVERAENITAETS_SHANNON_ENTROPIE = "souveraenitaets-shannon-entropie"


class ShannonEntropieProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class ShannonEntropieGeltung(Enum):
    GESPERRT = "gesperrt"
    ENTROPISCH = "entropisch"
    GRUNDLEGEND_ENTROPISCH = "grundlegend-entropisch"


_init_map()

_TYP_MAP: dict[ShannonEntropieGeltung, ShannonEntropieTyp] = {
    ShannonEntropieGeltung.GESPERRT: ShannonEntropieTyp.SCHUTZ_SHANNON_ENTROPIE,
    ShannonEntropieGeltung.ENTROPISCH: ShannonEntropieTyp.ORDNUNGS_SHANNON_ENTROPIE,
    ShannonEntropieGeltung.GRUNDLEGEND_ENTROPISCH: ShannonEntropieTyp.SOUVERAENITAETS_SHANNON_ENTROPIE,
}

_PROZEDUR_MAP: dict[ShannonEntropieGeltung, ShannonEntropieProzedur] = {
    ShannonEntropieGeltung.GESPERRT: ShannonEntropieProzedur.NOTPROZEDUR,
    ShannonEntropieGeltung.ENTROPISCH: ShannonEntropieProzedur.REGELPROTOKOLL,
    ShannonEntropieGeltung.GRUNDLEGEND_ENTROPISCH: ShannonEntropieProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[ShannonEntropieGeltung, float] = {
    ShannonEntropieGeltung.GESPERRT: 0.0,
    ShannonEntropieGeltung.ENTROPISCH: 0.04,
    ShannonEntropieGeltung.GRUNDLEGEND_ENTROPISCH: 0.08,
}

_TIER_DELTA: dict[ShannonEntropieGeltung, int] = {
    ShannonEntropieGeltung.GESPERRT: 0,
    ShannonEntropieGeltung.ENTROPISCH: 1,
    ShannonEntropieGeltung.GRUNDLEGEND_ENTROPISCH: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ShannonEntropieNorm:
    shannon_entropie_feld_id: str
    shannon_entropie_typ: ShannonEntropieTyp
    prozedur: ShannonEntropieProzedur
    geltung: ShannonEntropieGeltung
    shannon_entropie_weight: float
    shannon_entropie_tier: int
    canonical: bool
    shannon_entropie_ids: tuple[str, ...]
    shannon_entropie_tags: tuple[str, ...]


@dataclass(frozen=True)
class ShannonEntropieFeld:
    feld_id: str
    chaos_verfassung: ChaosVerfassung
    normen: tuple[ShannonEntropieNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.shannon_entropie_feld_id for n in self.normen if n.geltung is ShannonEntropieGeltung.GESPERRT)

    @property
    def entropisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.shannon_entropie_feld_id for n in self.normen if n.geltung is ShannonEntropieGeltung.ENTROPISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.shannon_entropie_feld_id for n in self.normen if n.geltung is ShannonEntropieGeltung.GRUNDLEGEND_ENTROPISCH)

    @property
    def feld_signal(self):
        if any(n.geltung is ShannonEntropieGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-gesperrt")
        elif any(n.geltung is ShannonEntropieGeltung.ENTROPISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-entropisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="feld-grundlegend-entropisch")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_shannon_entropie_feld(
    chaos_verfassung: ChaosVerfassung | None = None,
    *,
    feld_id: str = "shannon-entropie-feld",
) -> ShannonEntropieFeld:
    if chaos_verfassung is None:
        chaos_verfassung = build_chaos_verfassung(verfassung_id=f"{feld_id}-verfassung")

    normen: list[ShannonEntropieNorm] = []
    for parent_norm in chaos_verfassung.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{feld_id}-{parent_norm.chaos_verfassung_id.removeprefix(f'{chaos_verfassung.verfassung_id}-')}"
        raw_weight = min(1.0, parent_norm.chaos_verfassungs_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.chaos_verfassungs_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is ShannonEntropieGeltung.GRUNDLEGEND_ENTROPISCH)
        normen.append(
            ShannonEntropieNorm(
                shannon_entropie_feld_id=new_id,
                shannon_entropie_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                shannon_entropie_weight=new_weight,
                shannon_entropie_tier=new_tier,
                canonical=is_canonical,
                shannon_entropie_ids=parent_norm.chaos_verfassungs_ids + (new_id,),
                shannon_entropie_tags=parent_norm.chaos_verfassungs_tags + (f"shannon-entropie:{new_geltung.value}",),
            )
        )
    return ShannonEntropieFeld(
        feld_id=feld_id,
        chaos_verfassung=chaos_verfassung,
        normen=tuple(normen),
    )
