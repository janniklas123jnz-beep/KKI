"""#286 – CarnotManifest: Carnot-Effizienzprinzip als Governance-Manifest.

Parent: gleichgewichts_pakt (#285)
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .gleichgewichts_pakt import (
    GleichgewichtsGeltung,
    GleichgewichtsPakt,
    build_gleichgewichts_pakt,
)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class CarnotTyp(Enum):
    SCHUTZ_CARNOT = "schutz-carnot"
    ORDNUNGS_CARNOT = "ordnungs-carnot"
    SOUVERAENITAETS_CARNOT = "souveraenitaets-carnot"


class CarnotProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class CarnotGeltung(Enum):
    GESPERRT = "gesperrt"
    CARNOTISCH = "carnotisch"
    GRUNDLEGEND_CARNOTISCH = "grundlegend-carnotisch"


# ---------------------------------------------------------------------------
# Internal maps
# ---------------------------------------------------------------------------

_GELTUNG_MAP: dict[GleichgewichtsGeltung, CarnotGeltung] = {
    GleichgewichtsGeltung.GESPERRT: CarnotGeltung.GESPERRT,
    GleichgewichtsGeltung.EQUILIBRIERT: CarnotGeltung.CARNOTISCH,
    GleichgewichtsGeltung.GRUNDLEGEND_EQUILIBRIERT: CarnotGeltung.GRUNDLEGEND_CARNOTISCH,
}

_TYP_MAP: dict[GleichgewichtsGeltung, CarnotTyp] = {
    GleichgewichtsGeltung.GESPERRT: CarnotTyp.SCHUTZ_CARNOT,
    GleichgewichtsGeltung.EQUILIBRIERT: CarnotTyp.ORDNUNGS_CARNOT,
    GleichgewichtsGeltung.GRUNDLEGEND_EQUILIBRIERT: CarnotTyp.SOUVERAENITAETS_CARNOT,
}

_PROZEDUR_MAP: dict[GleichgewichtsGeltung, CarnotProzedur] = {
    GleichgewichtsGeltung.GESPERRT: CarnotProzedur.NOTPROZEDUR,
    GleichgewichtsGeltung.EQUILIBRIERT: CarnotProzedur.REGELPROTOKOLL,
    GleichgewichtsGeltung.GRUNDLEGEND_EQUILIBRIERT: CarnotProzedur.PLENARPROTOKOLL,
}

_WEIGHT_BONUS: dict[GleichgewichtsGeltung, float] = {
    GleichgewichtsGeltung.GESPERRT: 0.0,
    GleichgewichtsGeltung.EQUILIBRIERT: 0.04,
    GleichgewichtsGeltung.GRUNDLEGEND_EQUILIBRIERT: 0.08,
}

_TIER_BONUS: dict[GleichgewichtsGeltung, int] = {
    GleichgewichtsGeltung.GESPERRT: 0,
    GleichgewichtsGeltung.EQUILIBRIERT: 1,
    GleichgewichtsGeltung.GRUNDLEGEND_EQUILIBRIERT: 2,
}

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CarnotNorm:
    carnot_manifest_id: str
    carnot_typ: CarnotTyp
    prozedur: CarnotProzedur
    geltung: CarnotGeltung
    carnot_weight: float
    carnot_tier: int
    canonical: bool
    carnot_ids: tuple[str, ...]
    carnot_tags: tuple[str, ...]


@dataclass(frozen=True)
class CarnotManifest:
    manifest_id: str
    gleichgewichts_pakt: GleichgewichtsPakt
    normen: tuple[CarnotNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.carnot_manifest_id for n in self.normen if n.geltung is CarnotGeltung.GESPERRT)

    @property
    def carnotisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.carnot_manifest_id for n in self.normen if n.geltung is CarnotGeltung.CARNOTISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.carnot_manifest_id for n in self.normen if n.geltung is CarnotGeltung.GRUNDLEGEND_CARNOTISCH)

    @property
    def manifest_signal(self):
        if any(n.geltung is CarnotGeltung.GESPERRT for n in self.normen):
            status = "manifest-gesperrt"
            severity = "critical"
        elif any(n.geltung is CarnotGeltung.CARNOTISCH for n in self.normen):
            status = "manifest-carnotisch"
            severity = "warning"
        else:
            status = "manifest-grundlegend-carnotisch"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def build_carnot_manifest(
    gleichgewichts_pakt: GleichgewichtsPakt | None = None,
    *,
    manifest_id: str = "carnot-manifest",
) -> CarnotManifest:
    if gleichgewichts_pakt is None:
        gleichgewichts_pakt = build_gleichgewichts_pakt(pakt_id=f"{manifest_id}-pakt")

    normen: list[CarnotNorm] = []
    for parent_norm in gleichgewichts_pakt.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{manifest_id}-{parent_norm.gleichgewichts_pakt_id.removeprefix(f'{gleichgewichts_pakt.pakt_id}-')}"
        raw_weight = min(1.0, round(parent_norm.gleichgewichts_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.gleichgewichts_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is CarnotGeltung.GRUNDLEGEND_CARNOTISCH)
        normen.append(
            CarnotNorm(
                carnot_manifest_id=new_id,
                carnot_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                carnot_weight=raw_weight,
                carnot_tier=new_tier,
                canonical=is_canonical,
                carnot_ids=parent_norm.gleichgewichts_ids + (new_id,),
                carnot_tags=parent_norm.gleichgewichts_tags + (f"carnot-manifest:{new_geltung.value}",),
            )
        )

    return CarnotManifest(
        manifest_id=manifest_id,
        gleichgewichts_pakt=gleichgewichts_pakt,
        normen=tuple(normen),
    )
