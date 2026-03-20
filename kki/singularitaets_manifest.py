"""singularitaets_manifest — Relativität & Raumzeit layer 6 (#276)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kruemmungs_pakt import (
    KruemmungsGeltung,
    KruemmungsNorm,
    KruemmungsPakt,
    KruemmungsProzedur,
    KruemmungsTyp,
    build_kruemmungs_pakt,
)

__all__ = [
    "SingularitaetsTyp",
    "SingularitaetsProzedur",
    "SingularitaetsGeltung",
    "SingularitaetsNorm",
    "SingularitaetsManifest",
    "build_singularitaets_manifest",
]


class SingularitaetsTyp(str, Enum):
    SCHUTZ_SINGULARITAET = "schutz-singularitaet"
    ORDNUNGS_SINGULARITAET = "ordnungs-singularitaet"
    SOUVERAENITAETS_SINGULARITAET = "souveraenitaets-singularitaet"


class SingularitaetsProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class SingularitaetsGeltung(str, Enum):
    GESPERRT = "gesperrt"
    SINGULAER = "singulaer"
    GRUNDLEGEND_SINGULAER = "grundlegend-singulaer"


_TYP_MAP: dict[KruemmungsGeltung, SingularitaetsTyp] = {
    KruemmungsGeltung.GESPERRT: SingularitaetsTyp.SCHUTZ_SINGULARITAET,
    KruemmungsGeltung.GEKRUEMMT: SingularitaetsTyp.ORDNUNGS_SINGULARITAET,
    KruemmungsGeltung.GRUNDLEGEND_GEKRUEMMT: SingularitaetsTyp.SOUVERAENITAETS_SINGULARITAET,
}
_PROZEDUR_MAP: dict[KruemmungsGeltung, SingularitaetsProzedur] = {
    KruemmungsGeltung.GESPERRT: SingularitaetsProzedur.NOTPROZEDUR,
    KruemmungsGeltung.GEKRUEMMT: SingularitaetsProzedur.REGELPROTOKOLL,
    KruemmungsGeltung.GRUNDLEGEND_GEKRUEMMT: SingularitaetsProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[KruemmungsGeltung, SingularitaetsGeltung] = {
    KruemmungsGeltung.GESPERRT: SingularitaetsGeltung.GESPERRT,
    KruemmungsGeltung.GEKRUEMMT: SingularitaetsGeltung.SINGULAER,
    KruemmungsGeltung.GRUNDLEGEND_GEKRUEMMT: SingularitaetsGeltung.GRUNDLEGEND_SINGULAER,
}
_WEIGHT_BONUS: dict[KruemmungsGeltung, float] = {
    KruemmungsGeltung.GESPERRT: 0.0,
    KruemmungsGeltung.GEKRUEMMT: 0.04,
    KruemmungsGeltung.GRUNDLEGEND_GEKRUEMMT: 0.08,
}
_TIER_BONUS: dict[KruemmungsGeltung, int] = {
    KruemmungsGeltung.GESPERRT: 0,
    KruemmungsGeltung.GEKRUEMMT: 1,
    KruemmungsGeltung.GRUNDLEGEND_GEKRUEMMT: 2,
}


@dataclass(frozen=True)
class SingularitaetsNorm:
    singularitaets_manifest_id: str
    singularitaets_typ: SingularitaetsTyp
    prozedur: SingularitaetsProzedur
    geltung: SingularitaetsGeltung
    singularitaets_weight: float
    singularitaets_tier: int
    canonical: bool
    singularitaets_manifest_ids: tuple[str, ...]
    singularitaets_manifest_tags: tuple[str, ...]


@dataclass(frozen=True)
class SingularitaetsManifest:
    manifest_id: str
    kruemmungs_pakt: KruemmungsPakt
    normen: tuple[SingularitaetsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.singularitaets_manifest_id for n in self.normen if n.geltung is SingularitaetsGeltung.GESPERRT)

    @property
    def singulaer_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.singularitaets_manifest_id for n in self.normen if n.geltung is SingularitaetsGeltung.SINGULAER)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.singularitaets_manifest_id for n in self.normen if n.geltung is SingularitaetsGeltung.GRUNDLEGEND_SINGULAER)

    @property
    def manifest_signal(self):
        if any(n.geltung is SingularitaetsGeltung.GESPERRT for n in self.normen):
            status = "manifest-gesperrt"
            severity = "critical"
        elif any(n.geltung is SingularitaetsGeltung.SINGULAER for n in self.normen):
            status = "manifest-singulaer"
            severity = "warning"
        else:
            status = "manifest-grundlegend-singulaer"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_singularitaets_manifest(
    kruemmungs_pakt: KruemmungsPakt | None = None,
    *,
    manifest_id: str = "singularitaets-manifest",
) -> SingularitaetsManifest:
    if kruemmungs_pakt is None:
        kruemmungs_pakt = build_kruemmungs_pakt(pakt_id=f"{manifest_id}-pakt")

    normen: list[SingularitaetsNorm] = []
    for parent_norm in kruemmungs_pakt.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{manifest_id}-{parent_norm.kruemmungs_pakt_id.removeprefix(f'{kruemmungs_pakt.pakt_id}-')}"
        raw_weight = min(1.0, round(parent_norm.kruemmungs_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.kruemmungs_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SingularitaetsGeltung.GRUNDLEGEND_SINGULAER)
        normen.append(
            SingularitaetsNorm(
                singularitaets_manifest_id=new_id,
                singularitaets_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                singularitaets_weight=raw_weight,
                singularitaets_tier=new_tier,
                canonical=is_canonical,
                singularitaets_manifest_ids=parent_norm.kruemmungs_pakt_ids + (new_id,),
                singularitaets_manifest_tags=parent_norm.kruemmungs_pakt_tags + (f"singularitaets-manifest:{new_geltung.value}",),
            )
        )

    return SingularitaetsManifest(
        manifest_id=manifest_id,
        kruemmungs_pakt=kruemmungs_pakt,
        normen=tuple(normen),
    )
