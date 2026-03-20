"""#284 – EnergieerhaltungsKodex: 1. Hauptsatz der Thermodynamik als Governance-Kodex.

Parent: waerme_charta (#283)
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .waerme_charta import (
    WaermeGeltung,
    WaermeCharta,
    build_waerme_charta,
)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class EnergieerhaltungsTyp(Enum):
    SCHUTZ_ENERGIEERHALTUNG = "schutz-energieerhaltung"
    ORDNUNGS_ENERGIEERHALTUNG = "ordnungs-energieerhaltung"
    SOUVERAENITAETS_ENERGIEERHALTUNG = "souveraenitaets-energieerhaltung"


class EnergieerhaltungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class EnergieerhaltungsGeltung(Enum):
    GESPERRT = "gesperrt"
    ENERGIEERHALTEND = "energieerhaltend"
    GRUNDLEGEND_ENERGIEERHALTEND = "grundlegend-energieerhaltend"


# ---------------------------------------------------------------------------
# Internal maps
# ---------------------------------------------------------------------------

_GELTUNG_MAP: dict[WaermeGeltung, EnergieerhaltungsGeltung] = {
    WaermeGeltung.GESPERRT: EnergieerhaltungsGeltung.GESPERRT,
    WaermeGeltung.WAERMEUEBERTRAGEN: EnergieerhaltungsGeltung.ENERGIEERHALTEND,
    WaermeGeltung.GRUNDLEGEND_WAERMEUEBERTRAGEN: EnergieerhaltungsGeltung.GRUNDLEGEND_ENERGIEERHALTEND,
}

_TYP_MAP: dict[WaermeGeltung, EnergieerhaltungsTyp] = {
    WaermeGeltung.GESPERRT: EnergieerhaltungsTyp.SCHUTZ_ENERGIEERHALTUNG,
    WaermeGeltung.WAERMEUEBERTRAGEN: EnergieerhaltungsTyp.ORDNUNGS_ENERGIEERHALTUNG,
    WaermeGeltung.GRUNDLEGEND_WAERMEUEBERTRAGEN: EnergieerhaltungsTyp.SOUVERAENITAETS_ENERGIEERHALTUNG,
}

_PROZEDUR_MAP: dict[WaermeGeltung, EnergieerhaltungsProzedur] = {
    WaermeGeltung.GESPERRT: EnergieerhaltungsProzedur.NOTPROZEDUR,
    WaermeGeltung.WAERMEUEBERTRAGEN: EnergieerhaltungsProzedur.REGELPROTOKOLL,
    WaermeGeltung.GRUNDLEGEND_WAERMEUEBERTRAGEN: EnergieerhaltungsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_BONUS: dict[WaermeGeltung, float] = {
    WaermeGeltung.GESPERRT: 0.0,
    WaermeGeltung.WAERMEUEBERTRAGEN: 0.04,
    WaermeGeltung.GRUNDLEGEND_WAERMEUEBERTRAGEN: 0.08,
}

_TIER_BONUS: dict[WaermeGeltung, int] = {
    WaermeGeltung.GESPERRT: 0,
    WaermeGeltung.WAERMEUEBERTRAGEN: 1,
    WaermeGeltung.GRUNDLEGEND_WAERMEUEBERTRAGEN: 2,
}

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class EnergieerhaltungsNorm:
    energieerhaltungs_kodex_id: str
    energieerhaltungs_typ: EnergieerhaltungsTyp
    prozedur: EnergieerhaltungsProzedur
    geltung: EnergieerhaltungsGeltung
    energieerhaltungs_weight: float
    energieerhaltungs_tier: int
    canonical: bool
    energieerhaltungs_ids: tuple[str, ...]
    energieerhaltungs_tags: tuple[str, ...]


@dataclass(frozen=True)
class EnergieerhaltungsKodex:
    kodex_id: str
    waerme_charta: WaermeCharta
    normen: tuple[EnergieerhaltungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.energieerhaltungs_kodex_id for n in self.normen if n.geltung is EnergieerhaltungsGeltung.GESPERRT)

    @property
    def energieerhaltend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.energieerhaltungs_kodex_id for n in self.normen if n.geltung is EnergieerhaltungsGeltung.ENERGIEERHALTEND)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.energieerhaltungs_kodex_id for n in self.normen if n.geltung is EnergieerhaltungsGeltung.GRUNDLEGEND_ENERGIEERHALTEND)

    @property
    def kodex_signal(self):
        if any(n.geltung is EnergieerhaltungsGeltung.GESPERRT for n in self.normen):
            status = "kodex-gesperrt"
            severity = "critical"
        elif any(n.geltung is EnergieerhaltungsGeltung.ENERGIEERHALTEND for n in self.normen):
            status = "kodex-energieerhaltend"
            severity = "warning"
        else:
            status = "kodex-grundlegend-energieerhaltend"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def build_energieerhaltungs_kodex(
    waerme_charta: WaermeCharta | None = None,
    *,
    kodex_id: str = "energieerhaltungs-kodex",
) -> EnergieerhaltungsKodex:
    if waerme_charta is None:
        waerme_charta = build_waerme_charta(charta_id=f"{kodex_id}-charta")

    normen: list[EnergieerhaltungsNorm] = []
    for parent_norm in waerme_charta.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{kodex_id}-{parent_norm.waerme_charta_id.removeprefix(f'{waerme_charta.charta_id}-')}"
        raw_weight = min(1.0, round(parent_norm.waerme_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.waerme_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is EnergieerhaltungsGeltung.GRUNDLEGEND_ENERGIEERHALTEND)
        normen.append(
            EnergieerhaltungsNorm(
                energieerhaltungs_kodex_id=new_id,
                energieerhaltungs_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                energieerhaltungs_weight=raw_weight,
                energieerhaltungs_tier=new_tier,
                canonical=is_canonical,
                energieerhaltungs_ids=parent_norm.waerme_ids + (new_id,),
                energieerhaltungs_tags=parent_norm.waerme_tags + (f"energieerhaltungs-kodex:{new_geltung.value}",),
            )
        )

    return EnergieerhaltungsKodex(
        kodex_id=kodex_id,
        waerme_charta=waerme_charta,
        normen=tuple(normen),
    )
