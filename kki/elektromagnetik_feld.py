"""#291 – ElektromagnetikFeld: Elektromagnetismus als Governance-Grundfeld.

Parent: thermodynamik_verfassung (#290)
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .thermodynamik_verfassung import (
    ThermoverfassungsGeltung,
    ThermodynamikVerfassung,
    build_thermodynamik_verfassung,
)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ElektromagnetikTyp(Enum):
    SCHUTZ_ELEKTROMAGNETIK = "schutz-elektromagnetik"
    ORDNUNGS_ELEKTROMAGNETIK = "ordnungs-elektromagnetik"
    SOUVERAENITAETS_ELEKTROMAGNETIK = "souveraenitaets-elektromagnetik"


class ElektromagnetikProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class ElektromagnetikGeltung(Enum):
    GESPERRT = "gesperrt"
    ELEKTROMAGNETISCH = "elektromagnetisch"
    GRUNDLEGEND_ELEKTROMAGNETISCH = "grundlegend-elektromagnetisch"


# ---------------------------------------------------------------------------
# Internal maps
# ---------------------------------------------------------------------------

_GELTUNG_MAP: dict[ThermoverfassungsGeltung, ElektromagnetikGeltung] = {
    ThermoverfassungsGeltung.GESPERRT: ElektromagnetikGeltung.GESPERRT,
    ThermoverfassungsGeltung.THERMOVERFASST: ElektromagnetikGeltung.ELEKTROMAGNETISCH,
    ThermoverfassungsGeltung.GRUNDLEGEND_THERMOVERFASST: ElektromagnetikGeltung.GRUNDLEGEND_ELEKTROMAGNETISCH,
}

_TYP_MAP: dict[ThermoverfassungsGeltung, ElektromagnetikTyp] = {
    ThermoverfassungsGeltung.GESPERRT: ElektromagnetikTyp.SCHUTZ_ELEKTROMAGNETIK,
    ThermoverfassungsGeltung.THERMOVERFASST: ElektromagnetikTyp.ORDNUNGS_ELEKTROMAGNETIK,
    ThermoverfassungsGeltung.GRUNDLEGEND_THERMOVERFASST: ElektromagnetikTyp.SOUVERAENITAETS_ELEKTROMAGNETIK,
}

_PROZEDUR_MAP: dict[ThermoverfassungsGeltung, ElektromagnetikProzedur] = {
    ThermoverfassungsGeltung.GESPERRT: ElektromagnetikProzedur.NOTPROZEDUR,
    ThermoverfassungsGeltung.THERMOVERFASST: ElektromagnetikProzedur.REGELPROTOKOLL,
    ThermoverfassungsGeltung.GRUNDLEGEND_THERMOVERFASST: ElektromagnetikProzedur.PLENARPROTOKOLL,
}

_WEIGHT_BONUS: dict[ThermoverfassungsGeltung, float] = {
    ThermoverfassungsGeltung.GESPERRT: 0.0,
    ThermoverfassungsGeltung.THERMOVERFASST: 0.04,
    ThermoverfassungsGeltung.GRUNDLEGEND_THERMOVERFASST: 0.08,
}

_TIER_BONUS: dict[ThermoverfassungsGeltung, int] = {
    ThermoverfassungsGeltung.GESPERRT: 0,
    ThermoverfassungsGeltung.THERMOVERFASST: 1,
    ThermoverfassungsGeltung.GRUNDLEGEND_THERMOVERFASST: 2,
}

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ElektromagnetikNorm:
    elektromagnetik_feld_id: str
    elektromagnetik_typ: ElektromagnetikTyp
    prozedur: ElektromagnetikProzedur
    geltung: ElektromagnetikGeltung
    elektromagnetik_weight: float
    elektromagnetik_tier: int
    canonical: bool
    elektromagnetik_ids: tuple[str, ...]
    elektromagnetik_tags: tuple[str, ...]


@dataclass(frozen=True)
class ElektromagnetikFeld:
    feld_id: str
    thermodynamik_verfassung: ThermodynamikVerfassung
    normen: tuple[ElektromagnetikNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.elektromagnetik_feld_id for n in self.normen if n.geltung is ElektromagnetikGeltung.GESPERRT)

    @property
    def elektromagnetisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.elektromagnetik_feld_id for n in self.normen if n.geltung is ElektromagnetikGeltung.ELEKTROMAGNETISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.elektromagnetik_feld_id for n in self.normen if n.geltung is ElektromagnetikGeltung.GRUNDLEGEND_ELEKTROMAGNETISCH)

    @property
    def feld_signal(self):
        if any(n.geltung is ElektromagnetikGeltung.GESPERRT for n in self.normen):
            status = "feld-gesperrt"
            severity = "critical"
        elif any(n.geltung is ElektromagnetikGeltung.ELEKTROMAGNETISCH for n in self.normen):
            status = "feld-elektromagnetisch"
            severity = "warning"
        else:
            status = "feld-grundlegend-elektromagnetisch"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def build_elektromagnetik_feld(
    thermodynamik_verfassung: ThermodynamikVerfassung | None = None,
    *,
    feld_id: str = "elektromagnetik-feld",
) -> ElektromagnetikFeld:
    if thermodynamik_verfassung is None:
        thermodynamik_verfassung = build_thermodynamik_verfassung(verfassung_id=f"{feld_id}-verfassung")

    normen: list[ElektromagnetikNorm] = []
    for parent_norm in thermodynamik_verfassung.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{feld_id}-{parent_norm.thermodynamik_verfassung_id.removeprefix(f'{thermodynamik_verfassung.verfassung_id}-')}"
        raw_weight = min(1.0, round(parent_norm.thermoverfassungs_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.thermoverfassungs_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is ElektromagnetikGeltung.GRUNDLEGEND_ELEKTROMAGNETISCH)
        normen.append(
            ElektromagnetikNorm(
                elektromagnetik_feld_id=new_id,
                elektromagnetik_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                elektromagnetik_weight=raw_weight,
                elektromagnetik_tier=new_tier,
                canonical=is_canonical,
                elektromagnetik_ids=parent_norm.thermoverfassungs_ids + (new_id,),
                elektromagnetik_tags=parent_norm.thermoverfassungs_tags + (f"elektromagnetik-feld:{new_geltung.value}",),
            )
        )

    return ElektromagnetikFeld(
        feld_id=feld_id,
        thermodynamik_verfassung=thermodynamik_verfassung,
        normen=tuple(normen),
    )
