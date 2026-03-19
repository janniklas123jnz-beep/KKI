"""diplomatie_charta — Weltrecht & Kosmopolitik layer 3 (#233)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .voelkerrechts_kodex import (
    VoelkerrechtsGeltung,
    VoelkerrechtsKlasse,
    VoelkerrechtsKodex,
    VoelkerrechtsNorm,
    VoelkerrechtsProzedur,
    build_voelkerrechts_kodex,
)

__all__ = [
    "DiplomatieRang",
    "DiplomatieProzedur",
    "DiplomatieGeltung",
    "DiplomatieNorm",
    "DiplomatieCharta",
    "build_diplomatie_charta",
]


class DiplomatieRang(str, Enum):
    SCHUTZ_RANG = "schutz-rang"
    ORDNUNGS_RANG = "ordnungs-rang"
    SOUVERAENITAETS_RANG = "souveraenitaets-rang"


class DiplomatieProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class DiplomatieGeltung(str, Enum):
    GESPERRT = "gesperrt"
    AKKREDITIERT = "akkreditiert"
    GRUNDLEGEND_AKKREDITIERT = "grundlegend-akkreditiert"


_RANG_MAP: dict[VoelkerrechtsGeltung, DiplomatieRang] = {
    VoelkerrechtsGeltung.GESPERRT: DiplomatieRang.SCHUTZ_RANG,
    VoelkerrechtsGeltung.KODIFIZIERT: DiplomatieRang.ORDNUNGS_RANG,
    VoelkerrechtsGeltung.GRUNDLEGEND_KODIFIZIERT: DiplomatieRang.SOUVERAENITAETS_RANG,
}
_PROZEDUR_MAP: dict[VoelkerrechtsGeltung, DiplomatieProzedur] = {
    VoelkerrechtsGeltung.GESPERRT: DiplomatieProzedur.NOTPROZEDUR,
    VoelkerrechtsGeltung.KODIFIZIERT: DiplomatieProzedur.REGELPROTOKOLL,
    VoelkerrechtsGeltung.GRUNDLEGEND_KODIFIZIERT: DiplomatieProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[VoelkerrechtsGeltung, DiplomatieGeltung] = {
    VoelkerrechtsGeltung.GESPERRT: DiplomatieGeltung.GESPERRT,
    VoelkerrechtsGeltung.KODIFIZIERT: DiplomatieGeltung.AKKREDITIERT,
    VoelkerrechtsGeltung.GRUNDLEGEND_KODIFIZIERT: DiplomatieGeltung.GRUNDLEGEND_AKKREDITIERT,
}
_WEIGHT_BONUS: dict[VoelkerrechtsGeltung, float] = {
    VoelkerrechtsGeltung.GESPERRT: 0.0,
    VoelkerrechtsGeltung.KODIFIZIERT: 0.04,
    VoelkerrechtsGeltung.GRUNDLEGEND_KODIFIZIERT: 0.08,
}
_TIER_BONUS: dict[VoelkerrechtsGeltung, int] = {
    VoelkerrechtsGeltung.GESPERRT: 0,
    VoelkerrechtsGeltung.KODIFIZIERT: 1,
    VoelkerrechtsGeltung.GRUNDLEGEND_KODIFIZIERT: 2,
}


@dataclass(frozen=True)
class DiplomatieNorm:
    diplomatie_charta_id: str
    diplomatie_rang: DiplomatieRang
    prozedur: DiplomatieProzedur
    geltung: DiplomatieGeltung
    diplomatie_weight: float
    diplomatie_tier: int
    canonical: bool
    diplomatie_charta_ids: tuple[str, ...]
    diplomatie_charta_tags: tuple[str, ...]


@dataclass(frozen=True)
class DiplomatieCharta:
    charta_id: str
    voelkerrechts_kodex: VoelkerrechtsKodex
    normen: tuple[DiplomatieNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.diplomatie_charta_id for n in self.normen if n.geltung is DiplomatieGeltung.GESPERRT)

    @property
    def akkreditiert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.diplomatie_charta_id for n in self.normen if n.geltung is DiplomatieGeltung.AKKREDITIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.diplomatie_charta_id for n in self.normen if n.geltung is DiplomatieGeltung.GRUNDLEGEND_AKKREDITIERT)

    @property
    def charta_signal(self):
        if any(n.geltung is DiplomatieGeltung.GESPERRT for n in self.normen):
            status = "charta-gesperrt"
            severity = "critical"
        elif any(n.geltung is DiplomatieGeltung.AKKREDITIERT for n in self.normen):
            status = "charta-akkreditiert"
            severity = "warning"
        else:
            status = "charta-grundlegend-akkreditiert"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_diplomatie_charta(
    voelkerrechts_kodex: VoelkerrechtsKodex | None = None,
    *,
    charta_id: str = "diplomatie-charta",
) -> DiplomatieCharta:
    if voelkerrechts_kodex is None:
        voelkerrechts_kodex = build_voelkerrechts_kodex(
            kodex_id=f"{charta_id}-kodex"
        )

    normen: list[DiplomatieNorm] = []
    for parent_norm in voelkerrechts_kodex.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{charta_id}-{parent_norm.voelkerrechts_kodex_id.removeprefix(f'{voelkerrechts_kodex.kodex_id}-')}"
        raw_weight = min(1.0, round(parent_norm.voelkerrechts_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.voelkerrechts_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is DiplomatieGeltung.GRUNDLEGEND_AKKREDITIERT)
        normen.append(
            DiplomatieNorm(
                diplomatie_charta_id=new_id,
                diplomatie_rang=_RANG_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                diplomatie_weight=raw_weight,
                diplomatie_tier=new_tier,
                canonical=is_canonical,
                diplomatie_charta_ids=parent_norm.voelkerrechts_kodex_ids + (new_id,),
                diplomatie_charta_tags=parent_norm.voelkerrechts_kodex_tags + (f"diplomatie-charta:{new_geltung.value}",),
            )
        )

    return DiplomatieCharta(
        charta_id=charta_id,
        voelkerrechts_kodex=voelkerrechts_kodex,
        normen=tuple(normen),
    )
