"""
#331 AstrophysikFeld — Astrophysik als Governance-Wurzelfeld: Sterne als Energiequellen
des Terra-Schwarms Leitstern.
Geltungsstufen: GESPERRT / ASTROPHYSIKALISCH / GRUNDLEGEND_ASTROPHYSIKALISCH
Parent: KosmologieVerfassung (#330)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kosmologie_verfassung import (
    KosmologieVerfassung,
    KosmologieVerfassungsGeltung,
    build_kosmologie_verfassung,
)

_GELTUNG_MAP: dict[KosmologieVerfassungsGeltung, "AstrophysikGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[KosmologieVerfassungsGeltung.GESPERRT] = AstrophysikGeltung.GESPERRT
    _GELTUNG_MAP[KosmologieVerfassungsGeltung.KOSMOLOGIEVERFASST] = AstrophysikGeltung.ASTROPHYSIKALISCH
    _GELTUNG_MAP[KosmologieVerfassungsGeltung.GRUNDLEGEND_KOSMOLOGIEVERFASST] = AstrophysikGeltung.GRUNDLEGEND_ASTROPHYSIKALISCH


class AstrophysikTyp(Enum):
    SCHUTZ_ASTROPHYSIK = "schutz-astrophysik"
    ORDNUNGS_ASTROPHYSIK = "ordnungs-astrophysik"
    SOUVERAENITAETS_ASTROPHYSIK = "souveraenitaets-astrophysik"


class AstrophysikProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class AstrophysikGeltung(Enum):
    GESPERRT = "gesperrt"
    ASTROPHYSIKALISCH = "astrophysikalisch"
    GRUNDLEGEND_ASTROPHYSIKALISCH = "grundlegend-astrophysikalisch"


_init_map()

_TYP_MAP: dict[AstrophysikGeltung, AstrophysikTyp] = {
    AstrophysikGeltung.GESPERRT: AstrophysikTyp.SCHUTZ_ASTROPHYSIK,
    AstrophysikGeltung.ASTROPHYSIKALISCH: AstrophysikTyp.ORDNUNGS_ASTROPHYSIK,
    AstrophysikGeltung.GRUNDLEGEND_ASTROPHYSIKALISCH: AstrophysikTyp.SOUVERAENITAETS_ASTROPHYSIK,
}

_PROZEDUR_MAP: dict[AstrophysikGeltung, AstrophysikProzedur] = {
    AstrophysikGeltung.GESPERRT: AstrophysikProzedur.NOTPROZEDUR,
    AstrophysikGeltung.ASTROPHYSIKALISCH: AstrophysikProzedur.REGELPROTOKOLL,
    AstrophysikGeltung.GRUNDLEGEND_ASTROPHYSIKALISCH: AstrophysikProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[AstrophysikGeltung, float] = {
    AstrophysikGeltung.GESPERRT: 0.0,
    AstrophysikGeltung.ASTROPHYSIKALISCH: 0.04,
    AstrophysikGeltung.GRUNDLEGEND_ASTROPHYSIKALISCH: 0.08,
}

_TIER_DELTA: dict[AstrophysikGeltung, int] = {
    AstrophysikGeltung.GESPERRT: 0,
    AstrophysikGeltung.ASTROPHYSIKALISCH: 1,
    AstrophysikGeltung.GRUNDLEGEND_ASTROPHYSIKALISCH: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AstrophysikNorm:
    astrophysik_feld_id: str
    astrophysik_typ: AstrophysikTyp
    prozedur: AstrophysikProzedur
    geltung: AstrophysikGeltung
    astrophysik_weight: float
    astrophysik_tier: int
    canonical: bool
    astrophysik_ids: tuple[str, ...]
    astrophysik_tags: tuple[str, ...]


@dataclass(frozen=True)
class AstrophysikFeld:
    feld_id: str
    kosmologie_verfassung: KosmologieVerfassung
    normen: tuple[AstrophysikNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.astrophysik_feld_id for n in self.normen if n.geltung is AstrophysikGeltung.GESPERRT)

    @property
    def astrophysikalisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.astrophysik_feld_id for n in self.normen if n.geltung is AstrophysikGeltung.ASTROPHYSIKALISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.astrophysik_feld_id for n in self.normen if n.geltung is AstrophysikGeltung.GRUNDLEGEND_ASTROPHYSIKALISCH)

    @property
    def feld_signal(self):
        if any(n.geltung is AstrophysikGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-gesperrt")
        elif any(n.geltung is AstrophysikGeltung.ASTROPHYSIKALISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-astrophysikalisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="feld-grundlegend-astrophysikalisch")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_astrophysik_feld(
    kosmologie_verfassung: KosmologieVerfassung | None = None,
    *,
    feld_id: str = "astrophysik-feld",
) -> AstrophysikFeld:
    if kosmologie_verfassung is None:
        kosmologie_verfassung = build_kosmologie_verfassung(verfassung_id=f"{feld_id}-verfassung")

    normen: list[AstrophysikNorm] = []
    for parent_norm in kosmologie_verfassung.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{feld_id}-{parent_norm.kosmologie_verfassung_id.removeprefix(f'{kosmologie_verfassung.verfassung_id}-')}"
        raw_weight = min(1.0, parent_norm.kosmologie_verfassungs_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kosmologie_verfassungs_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is AstrophysikGeltung.GRUNDLEGEND_ASTROPHYSIKALISCH)
        normen.append(
            AstrophysikNorm(
                astrophysik_feld_id=new_id,
                astrophysik_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                astrophysik_weight=new_weight,
                astrophysik_tier=new_tier,
                canonical=is_canonical,
                astrophysik_ids=parent_norm.kosmologie_verfassungs_ids + (new_id,),
                astrophysik_tags=parent_norm.kosmologie_verfassungs_tags + (f"astrophysik:{new_geltung.value}",),
            )
        )
    return AstrophysikFeld(
        feld_id=feld_id,
        kosmologie_verfassung=kosmologie_verfassung,
        normen=tuple(normen),
    )
