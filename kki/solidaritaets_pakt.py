"""solidaritaets_pakt — Weltrecht & Kosmopolitik layer 6 (#236)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kooperations_manifest import (
    KooperationsGeltung,
    KooperationsGrad,
    KooperationsManifest,
    KooperationsNorm,
    KooperationsProzedur,
    build_kooperations_manifest,
)

__all__ = [
    "SolidaritaetsTyp",
    "SolidaritaetsProzedur",
    "SolidaritaetsGeltung",
    "SolidaritaetsNorm",
    "SolidaritaetsPakt",
    "build_solidaritaets_pakt",
]


class SolidaritaetsTyp(str, Enum):
    SCHUTZ_SOLIDARITAET = "schutz-solidaritaet"
    ORDNUNGS_SOLIDARITAET = "ordnungs-solidaritaet"
    SOUVERAENITAETS_SOLIDARITAET = "souveraenitaets-solidaritaet"


class SolidaritaetsProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class SolidaritaetsGeltung(str, Enum):
    GESPERRT = "gesperrt"
    BESIEGELT = "besiegelt"
    GRUNDLEGEND_BESIEGELT = "grundlegend-besiegelt"


_TYP_MAP: dict[KooperationsGeltung, SolidaritaetsTyp] = {
    KooperationsGeltung.GESPERRT: SolidaritaetsTyp.SCHUTZ_SOLIDARITAET,
    KooperationsGeltung.KOOPERIERT: SolidaritaetsTyp.ORDNUNGS_SOLIDARITAET,
    KooperationsGeltung.GRUNDLEGEND_KOOPERIERT: SolidaritaetsTyp.SOUVERAENITAETS_SOLIDARITAET,
}
_PROZEDUR_MAP: dict[KooperationsGeltung, SolidaritaetsProzedur] = {
    KooperationsGeltung.GESPERRT: SolidaritaetsProzedur.NOTPROZEDUR,
    KooperationsGeltung.KOOPERIERT: SolidaritaetsProzedur.REGELPROTOKOLL,
    KooperationsGeltung.GRUNDLEGEND_KOOPERIERT: SolidaritaetsProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[KooperationsGeltung, SolidaritaetsGeltung] = {
    KooperationsGeltung.GESPERRT: SolidaritaetsGeltung.GESPERRT,
    KooperationsGeltung.KOOPERIERT: SolidaritaetsGeltung.BESIEGELT,
    KooperationsGeltung.GRUNDLEGEND_KOOPERIERT: SolidaritaetsGeltung.GRUNDLEGEND_BESIEGELT,
}
_WEIGHT_BONUS: dict[KooperationsGeltung, float] = {
    KooperationsGeltung.GESPERRT: 0.0,
    KooperationsGeltung.KOOPERIERT: 0.04,
    KooperationsGeltung.GRUNDLEGEND_KOOPERIERT: 0.08,
}
_TIER_BONUS: dict[KooperationsGeltung, int] = {
    KooperationsGeltung.GESPERRT: 0,
    KooperationsGeltung.KOOPERIERT: 1,
    KooperationsGeltung.GRUNDLEGEND_KOOPERIERT: 2,
}


@dataclass(frozen=True)
class SolidaritaetsNorm:
    solidaritaets_pakt_id: str
    solidaritaets_typ: SolidaritaetsTyp
    prozedur: SolidaritaetsProzedur
    geltung: SolidaritaetsGeltung
    solidaritaets_weight: float
    solidaritaets_tier: int
    canonical: bool
    solidaritaets_pakt_ids: tuple[str, ...]
    solidaritaets_pakt_tags: tuple[str, ...]


@dataclass(frozen=True)
class SolidaritaetsPakt:
    pakt_id: str
    kooperations_manifest: KooperationsManifest
    normen: tuple[SolidaritaetsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.solidaritaets_pakt_id for n in self.normen if n.geltung is SolidaritaetsGeltung.GESPERRT)

    @property
    def besiegelt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.solidaritaets_pakt_id for n in self.normen if n.geltung is SolidaritaetsGeltung.BESIEGELT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.solidaritaets_pakt_id for n in self.normen if n.geltung is SolidaritaetsGeltung.GRUNDLEGEND_BESIEGELT)

    @property
    def pakt_signal(self):
        if any(n.geltung is SolidaritaetsGeltung.GESPERRT for n in self.normen):
            status = "pakt-gesperrt"
            severity = "critical"
        elif any(n.geltung is SolidaritaetsGeltung.BESIEGELT for n in self.normen):
            status = "pakt-besiegelt"
            severity = "warning"
        else:
            status = "pakt-grundlegend-besiegelt"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_solidaritaets_pakt(
    kooperations_manifest: KooperationsManifest | None = None,
    *,
    pakt_id: str = "solidaritaets-pakt",
) -> SolidaritaetsPakt:
    if kooperations_manifest is None:
        kooperations_manifest = build_kooperations_manifest(manifest_id=f"{pakt_id}-manifest")

    normen: list[SolidaritaetsNorm] = []
    for parent_norm in kooperations_manifest.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{pakt_id}-{parent_norm.kooperations_manifest_id.removeprefix(f'{kooperations_manifest.manifest_id}-')}"
        raw_weight = min(1.0, round(parent_norm.kooperations_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.kooperations_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SolidaritaetsGeltung.GRUNDLEGEND_BESIEGELT)
        normen.append(
            SolidaritaetsNorm(
                solidaritaets_pakt_id=new_id,
                solidaritaets_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                solidaritaets_weight=raw_weight,
                solidaritaets_tier=new_tier,
                canonical=is_canonical,
                solidaritaets_pakt_ids=parent_norm.kooperations_manifest_ids + (new_id,),
                solidaritaets_pakt_tags=parent_norm.kooperations_manifest_tags + (f"solidaritaets-pakt:{new_geltung.value}",),
            )
        )

    return SolidaritaetsPakt(
        pakt_id=pakt_id,
        kooperations_manifest=kooperations_manifest,
        normen=tuple(normen),
    )
