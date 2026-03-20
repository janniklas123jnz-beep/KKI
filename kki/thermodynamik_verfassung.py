"""#290 – ThermodynamikVerfassung: Block-Krone Thermodynamik & Entropie.

Parent: waermestrahlung_charta (#289)
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .waermestrahlung_charta import (
    WaermestrahlungsGeltung,
    WaermestrahlungsCharta,
    build_waermestrahlung_charta,
)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ThermoverfassungsTyp(Enum):
    SCHUTZ_THERMOVERFASSUNG = "schutz-thermoverfassung"
    ORDNUNGS_THERMOVERFASSUNG = "ordnungs-thermoverfassung"
    SOUVERAENITAETS_THERMOVERFASSUNG = "souveraenitaets-thermoverfassung"


class ThermoverfassungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class ThermoverfassungsGeltung(Enum):
    GESPERRT = "gesperrt"
    THERMOVERFASST = "thermoverfasst"
    GRUNDLEGEND_THERMOVERFASST = "grundlegend-thermoverfasst"


# ---------------------------------------------------------------------------
# Internal maps
# ---------------------------------------------------------------------------

_GELTUNG_MAP: dict[WaermestrahlungsGeltung, ThermoverfassungsGeltung] = {
    WaermestrahlungsGeltung.GESPERRT: ThermoverfassungsGeltung.GESPERRT,
    WaermestrahlungsGeltung.STRAHLEND: ThermoverfassungsGeltung.THERMOVERFASST,
    WaermestrahlungsGeltung.GRUNDLEGEND_STRAHLEND: ThermoverfassungsGeltung.GRUNDLEGEND_THERMOVERFASST,
}

_TYP_MAP: dict[WaermestrahlungsGeltung, ThermoverfassungsTyp] = {
    WaermestrahlungsGeltung.GESPERRT: ThermoverfassungsTyp.SCHUTZ_THERMOVERFASSUNG,
    WaermestrahlungsGeltung.STRAHLEND: ThermoverfassungsTyp.ORDNUNGS_THERMOVERFASSUNG,
    WaermestrahlungsGeltung.GRUNDLEGEND_STRAHLEND: ThermoverfassungsTyp.SOUVERAENITAETS_THERMOVERFASSUNG,
}

_PROZEDUR_MAP: dict[WaermestrahlungsGeltung, ThermoverfassungsProzedur] = {
    WaermestrahlungsGeltung.GESPERRT: ThermoverfassungsProzedur.NOTPROZEDUR,
    WaermestrahlungsGeltung.STRAHLEND: ThermoverfassungsProzedur.REGELPROTOKOLL,
    WaermestrahlungsGeltung.GRUNDLEGEND_STRAHLEND: ThermoverfassungsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_BONUS: dict[WaermestrahlungsGeltung, float] = {
    WaermestrahlungsGeltung.GESPERRT: 0.0,
    WaermestrahlungsGeltung.STRAHLEND: 0.04,
    WaermestrahlungsGeltung.GRUNDLEGEND_STRAHLEND: 0.08,
}

_TIER_BONUS: dict[WaermestrahlungsGeltung, int] = {
    WaermestrahlungsGeltung.GESPERRT: 0,
    WaermestrahlungsGeltung.STRAHLEND: 1,
    WaermestrahlungsGeltung.GRUNDLEGEND_STRAHLEND: 2,
}

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ThermoverfassungsNorm:
    thermodynamik_verfassung_id: str
    thermoverfassungs_typ: ThermoverfassungsTyp
    prozedur: ThermoverfassungsProzedur
    geltung: ThermoverfassungsGeltung
    thermoverfassungs_weight: float
    thermoverfassungs_tier: int
    canonical: bool
    thermoverfassungs_ids: tuple[str, ...]
    thermoverfassungs_tags: tuple[str, ...]


@dataclass(frozen=True)
class ThermodynamikVerfassung:
    verfassung_id: str
    waermestrahlung_charta: WaermestrahlungsCharta
    normen: tuple[ThermoverfassungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.thermodynamik_verfassung_id for n in self.normen if n.geltung is ThermoverfassungsGeltung.GESPERRT)

    @property
    def thermoverfasst_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.thermodynamik_verfassung_id for n in self.normen if n.geltung is ThermoverfassungsGeltung.THERMOVERFASST)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.thermodynamik_verfassung_id for n in self.normen if n.geltung is ThermoverfassungsGeltung.GRUNDLEGEND_THERMOVERFASST)

    @property
    def verfassung_signal(self):
        if any(n.geltung is ThermoverfassungsGeltung.GESPERRT for n in self.normen):
            status = "verfassung-gesperrt"
            severity = "critical"
        elif any(n.geltung is ThermoverfassungsGeltung.THERMOVERFASST for n in self.normen):
            status = "verfassung-thermoverfasst"
            severity = "warning"
        else:
            status = "verfassung-grundlegend-thermoverfasst"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def build_thermodynamik_verfassung(
    waermestrahlung_charta: WaermestrahlungsCharta | None = None,
    *,
    verfassung_id: str = "thermodynamik-verfassung",
) -> ThermodynamikVerfassung:
    if waermestrahlung_charta is None:
        waermestrahlung_charta = build_waermestrahlung_charta(charta_id=f"{verfassung_id}-charta")

    normen: list[ThermoverfassungsNorm] = []
    for parent_norm in waermestrahlung_charta.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{verfassung_id}-{parent_norm.waermestrahlung_charta_id.removeprefix(f'{waermestrahlung_charta.charta_id}-')}"
        raw_weight = min(1.0, round(parent_norm.waermestrahlung_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.waermestrahlung_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is ThermoverfassungsGeltung.GRUNDLEGEND_THERMOVERFASST)
        normen.append(
            ThermoverfassungsNorm(
                thermodynamik_verfassung_id=new_id,
                thermoverfassungs_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                thermoverfassungs_weight=raw_weight,
                thermoverfassungs_tier=new_tier,
                canonical=is_canonical,
                thermoverfassungs_ids=parent_norm.waermestrahlung_ids + (new_id,),
                thermoverfassungs_tags=parent_norm.waermestrahlung_tags + (f"thermodynamik-verfassung:{new_geltung.value}",),
            )
        )

    return ThermodynamikVerfassung(
        verfassung_id=verfassung_id,
        waermestrahlung_charta=waermestrahlung_charta,
        normen=tuple(normen),
    )
