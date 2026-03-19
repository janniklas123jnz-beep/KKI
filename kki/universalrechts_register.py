"""universalrechts_register — Weltrecht & Kosmopolitik layer 7 (#237)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .solidaritaets_pakt import (
    SolidaritaetsGeltung,
    SolidaritaetsNorm,
    SolidaritaetsPakt,
    SolidaritaetsProzedur,
    SolidaritaetsTyp,
    build_solidaritaets_pakt,
)

__all__ = [
    "UniversalrechtsRang",
    "UniversalrechtsProzedur",
    "UniversalrechtsGeltung",
    "UniversalrechtsNorm",
    "UniversalrechtsRegister",
    "build_universalrechts_register",
]


class UniversalrechtsRang(str, Enum):
    SCHUTZ_RANG = "schutz-rang"
    ORDNUNGS_RANG = "ordnungs-rang"
    SOUVERAENITAETS_RANG = "souveraenitaets-rang"


class UniversalrechtsProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class UniversalrechtsGeltung(str, Enum):
    GESPERRT = "gesperrt"
    REGISTRIERT = "registriert"
    GRUNDLEGEND_REGISTRIERT = "grundlegend-registriert"


_RANG_MAP: dict[SolidaritaetsGeltung, UniversalrechtsRang] = {
    SolidaritaetsGeltung.GESPERRT: UniversalrechtsRang.SCHUTZ_RANG,
    SolidaritaetsGeltung.BESIEGELT: UniversalrechtsRang.ORDNUNGS_RANG,
    SolidaritaetsGeltung.GRUNDLEGEND_BESIEGELT: UniversalrechtsRang.SOUVERAENITAETS_RANG,
}
_PROZEDUR_MAP: dict[SolidaritaetsGeltung, UniversalrechtsProzedur] = {
    SolidaritaetsGeltung.GESPERRT: UniversalrechtsProzedur.NOTPROZEDUR,
    SolidaritaetsGeltung.BESIEGELT: UniversalrechtsProzedur.REGELPROTOKOLL,
    SolidaritaetsGeltung.GRUNDLEGEND_BESIEGELT: UniversalrechtsProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[SolidaritaetsGeltung, UniversalrechtsGeltung] = {
    SolidaritaetsGeltung.GESPERRT: UniversalrechtsGeltung.GESPERRT,
    SolidaritaetsGeltung.BESIEGELT: UniversalrechtsGeltung.REGISTRIERT,
    SolidaritaetsGeltung.GRUNDLEGEND_BESIEGELT: UniversalrechtsGeltung.GRUNDLEGEND_REGISTRIERT,
}
_WEIGHT_BONUS: dict[SolidaritaetsGeltung, float] = {
    SolidaritaetsGeltung.GESPERRT: 0.0,
    SolidaritaetsGeltung.BESIEGELT: 0.04,
    SolidaritaetsGeltung.GRUNDLEGEND_BESIEGELT: 0.08,
}
_TIER_BONUS: dict[SolidaritaetsGeltung, int] = {
    SolidaritaetsGeltung.GESPERRT: 0,
    SolidaritaetsGeltung.BESIEGELT: 1,
    SolidaritaetsGeltung.GRUNDLEGEND_BESIEGELT: 2,
}


@dataclass(frozen=True)
class UniversalrechtsNorm:
    universalrechts_register_id: str
    universalrechts_rang: UniversalrechtsRang
    prozedur: UniversalrechtsProzedur
    geltung: UniversalrechtsGeltung
    universalrechts_weight: float
    universalrechts_tier: int
    canonical: bool
    universalrechts_register_ids: tuple[str, ...]
    universalrechts_register_tags: tuple[str, ...]


@dataclass(frozen=True)
class UniversalrechtsRegister:
    register_id: str
    solidaritaets_pakt: SolidaritaetsPakt
    normen: tuple[UniversalrechtsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.universalrechts_register_id for n in self.normen if n.geltung is UniversalrechtsGeltung.GESPERRT)

    @property
    def registriert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.universalrechts_register_id for n in self.normen if n.geltung is UniversalrechtsGeltung.REGISTRIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.universalrechts_register_id for n in self.normen if n.geltung is UniversalrechtsGeltung.GRUNDLEGEND_REGISTRIERT)

    @property
    def register_signal(self):
        if any(n.geltung is UniversalrechtsGeltung.GESPERRT for n in self.normen):
            status = "register-gesperrt"
            severity = "critical"
        elif any(n.geltung is UniversalrechtsGeltung.REGISTRIERT for n in self.normen):
            status = "register-registriert"
            severity = "warning"
        else:
            status = "register-grundlegend-registriert"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_universalrechts_register(
    solidaritaets_pakt: SolidaritaetsPakt | None = None,
    *,
    register_id: str = "universalrechts-register",
) -> UniversalrechtsRegister:
    if solidaritaets_pakt is None:
        solidaritaets_pakt = build_solidaritaets_pakt(pakt_id=f"{register_id}-pakt")

    normen: list[UniversalrechtsNorm] = []
    for parent_norm in solidaritaets_pakt.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{register_id}-{parent_norm.solidaritaets_pakt_id.removeprefix(f'{solidaritaets_pakt.pakt_id}-')}"
        raw_weight = min(1.0, round(parent_norm.solidaritaets_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.solidaritaets_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is UniversalrechtsGeltung.GRUNDLEGEND_REGISTRIERT)
        normen.append(
            UniversalrechtsNorm(
                universalrechts_register_id=new_id,
                universalrechts_rang=_RANG_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                universalrechts_weight=raw_weight,
                universalrechts_tier=new_tier,
                canonical=is_canonical,
                universalrechts_register_ids=parent_norm.solidaritaets_pakt_ids + (new_id,),
                universalrechts_register_tags=parent_norm.solidaritaets_pakt_tags + (f"universalrechts-register:{new_geltung.value}",),
            )
        )

    return UniversalrechtsRegister(
        register_id=register_id,
        solidaritaets_pakt=solidaritaets_pakt,
        normen=tuple(normen),
    )
