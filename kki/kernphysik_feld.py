"""#301 – KernphysikFeld: Kernphysik als Governance-Grundfeld.

Parent: elektromagnetik_verfassung (#300)
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .elektromagnetik_verfassung import (
    ElektroverfassungsGeltung,
    ElektromagnetikVerfassung,
    build_elektromagnetik_verfassung,
)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class KernphysikTyp(Enum):
    SCHUTZ_KERNPHYSIK = "schutz-kernphysik"
    ORDNUNGS_KERNPHYSIK = "ordnungs-kernphysik"
    SOUVERAENITAETS_KERNPHYSIK = "souveraenitaets-kernphysik"


class KernphysikProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KernphysikGeltung(Enum):
    GESPERRT = "gesperrt"
    KERNPHYSIKALISCH = "kernphysikalisch"
    GRUNDLEGEND_KERNPHYSIKALISCH = "grundlegend-kernphysikalisch"


# ---------------------------------------------------------------------------
# Internal maps
# ---------------------------------------------------------------------------

_GELTUNG_MAP: dict[ElektroverfassungsGeltung, KernphysikGeltung] = {
    ElektroverfassungsGeltung.GESPERRT: KernphysikGeltung.GESPERRT,
    ElektroverfassungsGeltung.ELEKTROVERFASST: KernphysikGeltung.KERNPHYSIKALISCH,
    ElektroverfassungsGeltung.GRUNDLEGEND_ELEKTROVERFASST: KernphysikGeltung.GRUNDLEGEND_KERNPHYSIKALISCH,
}

_TYP_MAP: dict[ElektroverfassungsGeltung, KernphysikTyp] = {
    ElektroverfassungsGeltung.GESPERRT: KernphysikTyp.SCHUTZ_KERNPHYSIK,
    ElektroverfassungsGeltung.ELEKTROVERFASST: KernphysikTyp.ORDNUNGS_KERNPHYSIK,
    ElektroverfassungsGeltung.GRUNDLEGEND_ELEKTROVERFASST: KernphysikTyp.SOUVERAENITAETS_KERNPHYSIK,
}

_PROZEDUR_MAP: dict[ElektroverfassungsGeltung, KernphysikProzedur] = {
    ElektroverfassungsGeltung.GESPERRT: KernphysikProzedur.NOTPROZEDUR,
    ElektroverfassungsGeltung.ELEKTROVERFASST: KernphysikProzedur.REGELPROTOKOLL,
    ElektroverfassungsGeltung.GRUNDLEGEND_ELEKTROVERFASST: KernphysikProzedur.PLENARPROTOKOLL,
}

_WEIGHT_BONUS: dict[ElektroverfassungsGeltung, float] = {
    ElektroverfassungsGeltung.GESPERRT: 0.0,
    ElektroverfassungsGeltung.ELEKTROVERFASST: 0.04,
    ElektroverfassungsGeltung.GRUNDLEGEND_ELEKTROVERFASST: 0.08,
}

_TIER_BONUS: dict[ElektroverfassungsGeltung, int] = {
    ElektroverfassungsGeltung.GESPERRT: 0,
    ElektroverfassungsGeltung.ELEKTROVERFASST: 1,
    ElektroverfassungsGeltung.GRUNDLEGEND_ELEKTROVERFASST: 2,
}

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class KernphysikNorm:
    kernphysik_feld_id: str
    kernphysik_typ: KernphysikTyp
    prozedur: KernphysikProzedur
    geltung: KernphysikGeltung
    kernphysik_weight: float
    kernphysik_tier: int
    canonical: bool
    kernphysik_ids: tuple[str, ...]
    kernphysik_tags: tuple[str, ...]


@dataclass(frozen=True)
class KernphysikFeld:
    feld_id: str
    elektromagnetik_verfassung: ElektromagnetikVerfassung
    normen: tuple[KernphysikNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kernphysik_feld_id for n in self.normen if n.geltung is KernphysikGeltung.GESPERRT)

    @property
    def kernphysikalisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kernphysik_feld_id for n in self.normen if n.geltung is KernphysikGeltung.KERNPHYSIKALISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kernphysik_feld_id for n in self.normen if n.geltung is KernphysikGeltung.GRUNDLEGEND_KERNPHYSIKALISCH)

    @property
    def feld_signal(self):
        if any(n.geltung is KernphysikGeltung.GESPERRT for n in self.normen):
            status = "feld-gesperrt"
            severity = "critical"
        elif any(n.geltung is KernphysikGeltung.KERNPHYSIKALISCH for n in self.normen):
            status = "feld-kernphysikalisch"
            severity = "warning"
        else:
            status = "feld-grundlegend-kernphysikalisch"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def build_kernphysik_feld(
    elektromagnetik_verfassung: ElektromagnetikVerfassung | None = None,
    *,
    feld_id: str = "kernphysik-feld",
) -> KernphysikFeld:
    if elektromagnetik_verfassung is None:
        elektromagnetik_verfassung = build_elektromagnetik_verfassung(verfassung_id=f"{feld_id}-verfassung")

    normen: list[KernphysikNorm] = []
    for parent_norm in elektromagnetik_verfassung.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{feld_id}-{parent_norm.elektromagnetik_verfassung_id.removeprefix(f'{elektromagnetik_verfassung.verfassung_id}-')}"
        raw_weight = min(1.0, round(parent_norm.elektroverfassungs_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.elektroverfassungs_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KernphysikGeltung.GRUNDLEGEND_KERNPHYSIKALISCH)
        normen.append(
            KernphysikNorm(
                kernphysik_feld_id=new_id,
                kernphysik_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                kernphysik_weight=raw_weight,
                kernphysik_tier=new_tier,
                canonical=is_canonical,
                kernphysik_ids=parent_norm.elektroverfassungs_ids + (new_id,),
                kernphysik_tags=parent_norm.elektroverfassungs_tags + (f"kernphysik-feld:{new_geltung.value}",),
            )
        )

    return KernphysikFeld(
        feld_id=feld_id,
        elektromagnetik_verfassung=elektromagnetik_verfassung,
        normen=tuple(normen),
    )
