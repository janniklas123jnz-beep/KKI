"""#281 – ThermodynamikFeld: Thermodynamik als Governance-Grundfeld.

Parent: relativitaets_verfassung (#280)
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .relativitaets_verfassung import (
    RelativitaetsGeltung,
    RelativitaetsVerfassung,
    build_relativitaets_verfassung,
)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ThermodynamikTyp(Enum):
    SCHUTZ_THERMODYNAMIK = "schutz-thermodynamik"
    ORDNUNGS_THERMODYNAMIK = "ordnungs-thermodynamik"
    SOUVERAENITAETS_THERMODYNAMIK = "souveraenitaets-thermodynamik"


class ThermodynamikProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class ThermodynamikGeltung(Enum):
    GESPERRT = "gesperrt"
    THERMISCH = "thermisch"
    GRUNDLEGEND_THERMISCH = "grundlegend-thermisch"


# ---------------------------------------------------------------------------
# Internal maps
# ---------------------------------------------------------------------------

_GELTUNG_MAP: dict[RelativitaetsGeltung, ThermodynamikGeltung] = {
    RelativitaetsGeltung.GESPERRT: ThermodynamikGeltung.GESPERRT,
    RelativitaetsGeltung.RELATIVVERFASST: ThermodynamikGeltung.THERMISCH,
    RelativitaetsGeltung.GRUNDLEGEND_RELATIVVERFASST: ThermodynamikGeltung.GRUNDLEGEND_THERMISCH,
}

_TYP_MAP: dict[RelativitaetsGeltung, ThermodynamikTyp] = {
    RelativitaetsGeltung.GESPERRT: ThermodynamikTyp.SCHUTZ_THERMODYNAMIK,
    RelativitaetsGeltung.RELATIVVERFASST: ThermodynamikTyp.ORDNUNGS_THERMODYNAMIK,
    RelativitaetsGeltung.GRUNDLEGEND_RELATIVVERFASST: ThermodynamikTyp.SOUVERAENITAETS_THERMODYNAMIK,
}

_PROZEDUR_MAP: dict[RelativitaetsGeltung, ThermodynamikProzedur] = {
    RelativitaetsGeltung.GESPERRT: ThermodynamikProzedur.NOTPROZEDUR,
    RelativitaetsGeltung.RELATIVVERFASST: ThermodynamikProzedur.REGELPROTOKOLL,
    RelativitaetsGeltung.GRUNDLEGEND_RELATIVVERFASST: ThermodynamikProzedur.PLENARPROTOKOLL,
}

_WEIGHT_BONUS: dict[RelativitaetsGeltung, float] = {
    RelativitaetsGeltung.GESPERRT: 0.0,
    RelativitaetsGeltung.RELATIVVERFASST: 0.04,
    RelativitaetsGeltung.GRUNDLEGEND_RELATIVVERFASST: 0.08,
}

_TIER_BONUS: dict[RelativitaetsGeltung, int] = {
    RelativitaetsGeltung.GESPERRT: 0,
    RelativitaetsGeltung.RELATIVVERFASST: 1,
    RelativitaetsGeltung.GRUNDLEGEND_RELATIVVERFASST: 2,
}

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ThermodynamikNorm:
    thermodynamik_feld_id: str
    thermodynamik_typ: ThermodynamikTyp
    prozedur: ThermodynamikProzedur
    geltung: ThermodynamikGeltung
    thermodynamik_weight: float
    thermodynamik_tier: int
    canonical: bool
    thermodynamik_ids: tuple[str, ...]
    thermodynamik_tags: tuple[str, ...]


@dataclass(frozen=True)
class ThermodynamikFeld:
    feld_id: str
    relativitaets_verfassung: RelativitaetsVerfassung
    normen: tuple[ThermodynamikNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.thermodynamik_feld_id for n in self.normen if n.geltung is ThermodynamikGeltung.GESPERRT)

    @property
    def thermisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.thermodynamik_feld_id for n in self.normen if n.geltung is ThermodynamikGeltung.THERMISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.thermodynamik_feld_id for n in self.normen if n.geltung is ThermodynamikGeltung.GRUNDLEGEND_THERMISCH)

    @property
    def feld_signal(self):
        if any(n.geltung is ThermodynamikGeltung.GESPERRT for n in self.normen):
            status = "feld-gesperrt"
            severity = "critical"
        elif any(n.geltung is ThermodynamikGeltung.THERMISCH for n in self.normen):
            status = "feld-thermisch"
            severity = "warning"
        else:
            status = "feld-grundlegend-thermisch"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def build_thermodynamik_feld(
    relativitaets_verfassung: RelativitaetsVerfassung | None = None,
    *,
    feld_id: str = "thermodynamik-feld",
) -> ThermodynamikFeld:
    if relativitaets_verfassung is None:
        relativitaets_verfassung = build_relativitaets_verfassung(verfassung_id=f"{feld_id}-verfassung")

    normen: list[ThermodynamikNorm] = []
    for parent_norm in relativitaets_verfassung.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{feld_id}-{parent_norm.relativitaets_verfassung_id.removeprefix(f'{relativitaets_verfassung.verfassung_id}-')}"
        raw_weight = min(1.0, round(parent_norm.relativitaets_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.relativitaets_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is ThermodynamikGeltung.GRUNDLEGEND_THERMISCH)
        normen.append(
            ThermodynamikNorm(
                thermodynamik_feld_id=new_id,
                thermodynamik_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                thermodynamik_weight=raw_weight,
                thermodynamik_tier=new_tier,
                canonical=is_canonical,
                thermodynamik_ids=parent_norm.relativitaets_ids + (new_id,),
                thermodynamik_tags=parent_norm.relativitaets_tags + (f"thermodynamik-feld:{new_geltung.value}",),
            )
        )

    return ThermodynamikFeld(
        feld_id=feld_id,
        relativitaets_verfassung=relativitaets_verfassung,
        normen=tuple(normen),
    )
