"""kollaps_manifest — Quantenfelder & Dimensionen layer 6 (#266)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .verschraenkungs_pakt import (
    VerschraenkunsGeltung,
    VerschraenkunsNorm,
    VerschraenkunsPakt,
    VerschraenkunsProzedur,
    VerschraenkunsTyp,
    build_verschraenkungs_pakt,
)

__all__ = [
    "KollapsTyp",
    "KollapsProzedur",
    "KollapsGeltung",
    "KollapsNorm",
    "KollapsManifest",
    "build_kollaps_manifest",
]


class KollapsTyp(str, Enum):
    SCHUTZ_KOLLAPS = "schutz-kollaps"
    ORDNUNGS_KOLLAPS = "ordnungs-kollaps"
    SOUVERAENITAETS_KOLLAPS = "souveraenitaets-kollaps"


class KollapsProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KollapsGeltung(str, Enum):
    GESPERRT = "gesperrt"
    KOLLABIERT = "kollabiert"
    GRUNDLEGEND_KOLLABIERT = "grundlegend-kollabiert"


_TYP_MAP: dict[VerschraenkunsGeltung, KollapsTyp] = {
    VerschraenkunsGeltung.GESPERRT: KollapsTyp.SCHUTZ_KOLLAPS,
    VerschraenkunsGeltung.VERSCHRAENKT: KollapsTyp.ORDNUNGS_KOLLAPS,
    VerschraenkunsGeltung.GRUNDLEGEND_VERSCHRAENKT: KollapsTyp.SOUVERAENITAETS_KOLLAPS,
}
_PROZEDUR_MAP: dict[VerschraenkunsGeltung, KollapsProzedur] = {
    VerschraenkunsGeltung.GESPERRT: KollapsProzedur.NOTPROZEDUR,
    VerschraenkunsGeltung.VERSCHRAENKT: KollapsProzedur.REGELPROTOKOLL,
    VerschraenkunsGeltung.GRUNDLEGEND_VERSCHRAENKT: KollapsProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[VerschraenkunsGeltung, KollapsGeltung] = {
    VerschraenkunsGeltung.GESPERRT: KollapsGeltung.GESPERRT,
    VerschraenkunsGeltung.VERSCHRAENKT: KollapsGeltung.KOLLABIERT,
    VerschraenkunsGeltung.GRUNDLEGEND_VERSCHRAENKT: KollapsGeltung.GRUNDLEGEND_KOLLABIERT,
}
_WEIGHT_BONUS: dict[VerschraenkunsGeltung, float] = {
    VerschraenkunsGeltung.GESPERRT: 0.0,
    VerschraenkunsGeltung.VERSCHRAENKT: 0.04,
    VerschraenkunsGeltung.GRUNDLEGEND_VERSCHRAENKT: 0.08,
}
_TIER_BONUS: dict[VerschraenkunsGeltung, int] = {
    VerschraenkunsGeltung.GESPERRT: 0,
    VerschraenkunsGeltung.VERSCHRAENKT: 1,
    VerschraenkunsGeltung.GRUNDLEGEND_VERSCHRAENKT: 2,
}


@dataclass(frozen=True)
class KollapsNorm:
    kollaps_manifest_id: str
    kollaps_typ: KollapsTyp
    prozedur: KollapsProzedur
    geltung: KollapsGeltung
    kollaps_weight: float
    kollaps_tier: int
    canonical: bool
    kollaps_manifest_ids: tuple[str, ...]
    kollaps_manifest_tags: tuple[str, ...]


@dataclass(frozen=True)
class KollapsManifest:
    manifest_id: str
    verschraenkungs_pakt: VerschraenkunsPakt
    normen: tuple[KollapsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kollaps_manifest_id for n in self.normen if n.geltung is KollapsGeltung.GESPERRT)

    @property
    def kollabiert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kollaps_manifest_id for n in self.normen if n.geltung is KollapsGeltung.KOLLABIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kollaps_manifest_id for n in self.normen if n.geltung is KollapsGeltung.GRUNDLEGEND_KOLLABIERT)

    @property
    def manifest_signal(self):
        if any(n.geltung is KollapsGeltung.GESPERRT for n in self.normen):
            status = "manifest-gesperrt"
            severity = "critical"
        elif any(n.geltung is KollapsGeltung.KOLLABIERT for n in self.normen):
            status = "manifest-kollabiert"
            severity = "warning"
        else:
            status = "manifest-grundlegend-kollabiert"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_kollaps_manifest(
    verschraenkungs_pakt: VerschraenkunsPakt | None = None,
    *,
    manifest_id: str = "kollaps-manifest",
) -> KollapsManifest:
    if verschraenkungs_pakt is None:
        verschraenkungs_pakt = build_verschraenkungs_pakt(pakt_id=f"{manifest_id}-pakt")

    normen: list[KollapsNorm] = []
    for parent_norm in verschraenkungs_pakt.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{manifest_id}-{parent_norm.verschraenkungs_pakt_id.removeprefix(f'{verschraenkungs_pakt.pakt_id}-')}"
        raw_weight = min(1.0, round(parent_norm.verschraenkungs_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.verschraenkungs_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KollapsGeltung.GRUNDLEGEND_KOLLABIERT)
        normen.append(
            KollapsNorm(
                kollaps_manifest_id=new_id,
                kollaps_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                kollaps_weight=raw_weight,
                kollaps_tier=new_tier,
                canonical=is_canonical,
                kollaps_manifest_ids=parent_norm.verschraenkungs_pakt_ids + (new_id,),
                kollaps_manifest_tags=parent_norm.verschraenkungs_pakt_tags + (f"kollaps-manifest:{new_geltung.value}",),
            )
        )

    return KollapsManifest(
        manifest_id=manifest_id,
        verschraenkungs_pakt=verschraenkungs_pakt,
        normen=tuple(normen),
    )
