"""gedaechtnis_senat — Zivilisation & Transzendenz layer 7 (#247)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .wissens_manifest import (
    WissensGeltung,
    WissensGrad,
    WissensManifest,
    WissensNorm,
    WissensProzedur,
    build_wissens_manifest,
)

__all__ = [
    "GedaechtnisRang",
    "GedaechtnisProzedur",
    "GedaechtnisGeltung",
    "GedaechtnisNorm",
    "GedaechtnisSenat",
    "build_gedaechtnis_senat",
]


class GedaechtnisRang(str, Enum):
    SCHUTZ_GEDAECHTNIS = "schutz-gedaechtnis"
    ORDNUNGS_GEDAECHTNIS = "ordnungs-gedaechtnis"
    SOUVERAENITAETS_GEDAECHTNIS = "souveraenitaets-gedaechtnis"


class GedaechtnisProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class GedaechtnisGeltung(str, Enum):
    GESPERRT = "gesperrt"
    ERINNERT = "erinnert"
    GRUNDLEGEND_ERINNERT = "grundlegend-erinnert"


_RANG_MAP: dict[WissensGeltung, GedaechtnisRang] = {
    WissensGeltung.GESPERRT: GedaechtnisRang.SCHUTZ_GEDAECHTNIS,
    WissensGeltung.VERBREITET: GedaechtnisRang.ORDNUNGS_GEDAECHTNIS,
    WissensGeltung.GRUNDLEGEND_VERBREITET: GedaechtnisRang.SOUVERAENITAETS_GEDAECHTNIS,
}
_PROZEDUR_MAP: dict[WissensGeltung, GedaechtnisProzedur] = {
    WissensGeltung.GESPERRT: GedaechtnisProzedur.NOTPROZEDUR,
    WissensGeltung.VERBREITET: GedaechtnisProzedur.REGELPROTOKOLL,
    WissensGeltung.GRUNDLEGEND_VERBREITET: GedaechtnisProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[WissensGeltung, GedaechtnisGeltung] = {
    WissensGeltung.GESPERRT: GedaechtnisGeltung.GESPERRT,
    WissensGeltung.VERBREITET: GedaechtnisGeltung.ERINNERT,
    WissensGeltung.GRUNDLEGEND_VERBREITET: GedaechtnisGeltung.GRUNDLEGEND_ERINNERT,
}
_WEIGHT_BONUS: dict[WissensGeltung, float] = {
    WissensGeltung.GESPERRT: 0.0,
    WissensGeltung.VERBREITET: 0.04,
    WissensGeltung.GRUNDLEGEND_VERBREITET: 0.08,
}
_TIER_BONUS: dict[WissensGeltung, int] = {
    WissensGeltung.GESPERRT: 0,
    WissensGeltung.VERBREITET: 1,
    WissensGeltung.GRUNDLEGEND_VERBREITET: 2,
}


@dataclass(frozen=True)
class GedaechtnisNorm:
    gedaechtnis_senat_id: str
    gedaechtnis_rang: GedaechtnisRang
    prozedur: GedaechtnisProzedur
    geltung: GedaechtnisGeltung
    gedaechtnis_weight: float
    gedaechtnis_tier: int
    canonical: bool
    gedaechtnis_senat_ids: tuple[str, ...]
    gedaechtnis_senat_tags: tuple[str, ...]


@dataclass(frozen=True)
class GedaechtnisSenat:
    senat_id: str
    wissens_manifest: WissensManifest
    normen: tuple[GedaechtnisNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.gedaechtnis_senat_id for n in self.normen if n.geltung is GedaechtnisGeltung.GESPERRT)

    @property
    def erinnert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.gedaechtnis_senat_id for n in self.normen if n.geltung is GedaechtnisGeltung.ERINNERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.gedaechtnis_senat_id for n in self.normen if n.geltung is GedaechtnisGeltung.GRUNDLEGEND_ERINNERT)

    @property
    def senat_signal(self):
        if any(n.geltung is GedaechtnisGeltung.GESPERRT for n in self.normen):
            status = "senat-gesperrt"
            severity = "critical"
        elif any(n.geltung is GedaechtnisGeltung.ERINNERT for n in self.normen):
            status = "senat-erinnert"
            severity = "warning"
        else:
            status = "senat-grundlegend-erinnert"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_gedaechtnis_senat(
    wissens_manifest: WissensManifest | None = None,
    *,
    senat_id: str = "gedaechtnis-senat",
) -> GedaechtnisSenat:
    if wissens_manifest is None:
        wissens_manifest = build_wissens_manifest(manifest_id=f"{senat_id}-manifest")

    normen: list[GedaechtnisNorm] = []
    for parent_norm in wissens_manifest.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{senat_id}-{parent_norm.wissens_manifest_id.removeprefix(f'{wissens_manifest.manifest_id}-')}"
        raw_weight = min(1.0, round(parent_norm.wissens_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.wissens_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is GedaechtnisGeltung.GRUNDLEGEND_ERINNERT)
        normen.append(
            GedaechtnisNorm(
                gedaechtnis_senat_id=new_id,
                gedaechtnis_rang=_RANG_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                gedaechtnis_weight=raw_weight,
                gedaechtnis_tier=new_tier,
                canonical=is_canonical,
                gedaechtnis_senat_ids=parent_norm.wissens_manifest_ids + (new_id,),
                gedaechtnis_senat_tags=parent_norm.wissens_manifest_tags + (f"gedaechtnis-senat:{new_geltung.value}",),
            )
        )

    return GedaechtnisSenat(
        senat_id=senat_id,
        wissens_manifest=wissens_manifest,
        normen=tuple(normen),
    )
