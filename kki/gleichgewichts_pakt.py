"""#285 – GleichgewichtsPakt: Thermodynamisches Gleichgewicht als Governance-Pakt.

Parent: energieerhaltungs_kodex (#284)
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .energieerhaltungs_kodex import (
    EnergieerhaltungsGeltung,
    EnergieerhaltungsKodex,
    build_energieerhaltungs_kodex,
)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class GleichgewichtsTyp(Enum):
    SCHUTZ_GLEICHGEWICHT = "schutz-gleichgewicht"
    ORDNUNGS_GLEICHGEWICHT = "ordnungs-gleichgewicht"
    SOUVERAENITAETS_GLEICHGEWICHT = "souveraenitaets-gleichgewicht"


class GleichgewichtsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class GleichgewichtsGeltung(Enum):
    GESPERRT = "gesperrt"
    EQUILIBRIERT = "equilibriert"
    GRUNDLEGEND_EQUILIBRIERT = "grundlegend-equilibriert"


# ---------------------------------------------------------------------------
# Internal maps
# ---------------------------------------------------------------------------

_GELTUNG_MAP: dict[EnergieerhaltungsGeltung, GleichgewichtsGeltung] = {
    EnergieerhaltungsGeltung.GESPERRT: GleichgewichtsGeltung.GESPERRT,
    EnergieerhaltungsGeltung.ENERGIEERHALTEND: GleichgewichtsGeltung.EQUILIBRIERT,
    EnergieerhaltungsGeltung.GRUNDLEGEND_ENERGIEERHALTEND: GleichgewichtsGeltung.GRUNDLEGEND_EQUILIBRIERT,
}

_TYP_MAP: dict[EnergieerhaltungsGeltung, GleichgewichtsTyp] = {
    EnergieerhaltungsGeltung.GESPERRT: GleichgewichtsTyp.SCHUTZ_GLEICHGEWICHT,
    EnergieerhaltungsGeltung.ENERGIEERHALTEND: GleichgewichtsTyp.ORDNUNGS_GLEICHGEWICHT,
    EnergieerhaltungsGeltung.GRUNDLEGEND_ENERGIEERHALTEND: GleichgewichtsTyp.SOUVERAENITAETS_GLEICHGEWICHT,
}

_PROZEDUR_MAP: dict[EnergieerhaltungsGeltung, GleichgewichtsProzedur] = {
    EnergieerhaltungsGeltung.GESPERRT: GleichgewichtsProzedur.NOTPROZEDUR,
    EnergieerhaltungsGeltung.ENERGIEERHALTEND: GleichgewichtsProzedur.REGELPROTOKOLL,
    EnergieerhaltungsGeltung.GRUNDLEGEND_ENERGIEERHALTEND: GleichgewichtsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_BONUS: dict[EnergieerhaltungsGeltung, float] = {
    EnergieerhaltungsGeltung.GESPERRT: 0.0,
    EnergieerhaltungsGeltung.ENERGIEERHALTEND: 0.04,
    EnergieerhaltungsGeltung.GRUNDLEGEND_ENERGIEERHALTEND: 0.08,
}

_TIER_BONUS: dict[EnergieerhaltungsGeltung, int] = {
    EnergieerhaltungsGeltung.GESPERRT: 0,
    EnergieerhaltungsGeltung.ENERGIEERHALTEND: 1,
    EnergieerhaltungsGeltung.GRUNDLEGEND_ENERGIEERHALTEND: 2,
}

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class GleichgewichtsNorm:
    gleichgewichts_pakt_id: str
    gleichgewichts_typ: GleichgewichtsTyp
    prozedur: GleichgewichtsProzedur
    geltung: GleichgewichtsGeltung
    gleichgewichts_weight: float
    gleichgewichts_tier: int
    canonical: bool
    gleichgewichts_ids: tuple[str, ...]
    gleichgewichts_tags: tuple[str, ...]


@dataclass(frozen=True)
class GleichgewichtsPakt:
    pakt_id: str
    energieerhaltungs_kodex: EnergieerhaltungsKodex
    normen: tuple[GleichgewichtsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.gleichgewichts_pakt_id for n in self.normen if n.geltung is GleichgewichtsGeltung.GESPERRT)

    @property
    def equilibriert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.gleichgewichts_pakt_id for n in self.normen if n.geltung is GleichgewichtsGeltung.EQUILIBRIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.gleichgewichts_pakt_id for n in self.normen if n.geltung is GleichgewichtsGeltung.GRUNDLEGEND_EQUILIBRIERT)

    @property
    def pakt_signal(self):
        if any(n.geltung is GleichgewichtsGeltung.GESPERRT for n in self.normen):
            status = "pakt-gesperrt"
            severity = "critical"
        elif any(n.geltung is GleichgewichtsGeltung.EQUILIBRIERT for n in self.normen):
            status = "pakt-equilibriert"
            severity = "warning"
        else:
            status = "pakt-grundlegend-equilibriert"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def build_gleichgewichts_pakt(
    energieerhaltungs_kodex: EnergieerhaltungsKodex | None = None,
    *,
    pakt_id: str = "gleichgewichts-pakt",
) -> GleichgewichtsPakt:
    if energieerhaltungs_kodex is None:
        energieerhaltungs_kodex = build_energieerhaltungs_kodex(kodex_id=f"{pakt_id}-kodex")

    normen: list[GleichgewichtsNorm] = []
    for parent_norm in energieerhaltungs_kodex.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{pakt_id}-{parent_norm.energieerhaltungs_kodex_id.removeprefix(f'{energieerhaltungs_kodex.kodex_id}-')}"
        raw_weight = min(1.0, round(parent_norm.energieerhaltungs_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.energieerhaltungs_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is GleichgewichtsGeltung.GRUNDLEGEND_EQUILIBRIERT)
        normen.append(
            GleichgewichtsNorm(
                gleichgewichts_pakt_id=new_id,
                gleichgewichts_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                gleichgewichts_weight=raw_weight,
                gleichgewichts_tier=new_tier,
                canonical=is_canonical,
                gleichgewichts_ids=parent_norm.energieerhaltungs_ids + (new_id,),
                gleichgewichts_tags=parent_norm.energieerhaltungs_tags + (f"gleichgewichts-pakt:{new_geltung.value}",),
            )
        )

    return GleichgewichtsPakt(
        pakt_id=pakt_id,
        energieerhaltungs_kodex=energieerhaltungs_kodex,
        normen=tuple(normen),
    )
