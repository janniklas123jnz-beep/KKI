"""kooperations_manifest — Weltrecht & Kosmopolitik layer 5 (#235)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .allianz_vertrag import (
    AllianzGeltung,
    AllianzNorm,
    AllianzProzedur,
    AllianzTyp,
    AllianzVertrag,
    build_allianz_vertrag,
)

__all__ = [
    "KooperationsGrad",
    "KooperationsProzedur",
    "KooperationsGeltung",
    "KooperationsNorm",
    "KooperationsManifest",
    "build_kooperations_manifest",
]


class KooperationsGrad(str, Enum):
    SCHUTZ_KOOPERATION = "schutz-kooperation"
    ORDNUNGS_KOOPERATION = "ordnungs-kooperation"
    SOUVERAENITAETS_KOOPERATION = "souveraenitaets-kooperation"


class KooperationsProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KooperationsGeltung(str, Enum):
    GESPERRT = "gesperrt"
    KOOPERIERT = "kooperiert"
    GRUNDLEGEND_KOOPERIERT = "grundlegend-kooperiert"


_GRAD_MAP: dict[AllianzGeltung, KooperationsGrad] = {
    AllianzGeltung.GESPERRT: KooperationsGrad.SCHUTZ_KOOPERATION,
    AllianzGeltung.VERBUNDEN: KooperationsGrad.ORDNUNGS_KOOPERATION,
    AllianzGeltung.GRUNDLEGEND_VERBUNDEN: KooperationsGrad.SOUVERAENITAETS_KOOPERATION,
}
_PROZEDUR_MAP: dict[AllianzGeltung, KooperationsProzedur] = {
    AllianzGeltung.GESPERRT: KooperationsProzedur.NOTPROZEDUR,
    AllianzGeltung.VERBUNDEN: KooperationsProzedur.REGELPROTOKOLL,
    AllianzGeltung.GRUNDLEGEND_VERBUNDEN: KooperationsProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[AllianzGeltung, KooperationsGeltung] = {
    AllianzGeltung.GESPERRT: KooperationsGeltung.GESPERRT,
    AllianzGeltung.VERBUNDEN: KooperationsGeltung.KOOPERIERT,
    AllianzGeltung.GRUNDLEGEND_VERBUNDEN: KooperationsGeltung.GRUNDLEGEND_KOOPERIERT,
}
_WEIGHT_BONUS: dict[AllianzGeltung, float] = {
    AllianzGeltung.GESPERRT: 0.0,
    AllianzGeltung.VERBUNDEN: 0.04,
    AllianzGeltung.GRUNDLEGEND_VERBUNDEN: 0.08,
}
_TIER_BONUS: dict[AllianzGeltung, int] = {
    AllianzGeltung.GESPERRT: 0,
    AllianzGeltung.VERBUNDEN: 1,
    AllianzGeltung.GRUNDLEGEND_VERBUNDEN: 2,
}


@dataclass(frozen=True)
class KooperationsNorm:
    kooperations_manifest_id: str
    kooperations_grad: KooperationsGrad
    prozedur: KooperationsProzedur
    geltung: KooperationsGeltung
    kooperations_weight: float
    kooperations_tier: int
    canonical: bool
    kooperations_manifest_ids: tuple[str, ...]
    kooperations_manifest_tags: tuple[str, ...]


@dataclass(frozen=True)
class KooperationsManifest:
    manifest_id: str
    allianz_vertrag: AllianzVertrag
    normen: tuple[KooperationsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kooperations_manifest_id for n in self.normen if n.geltung is KooperationsGeltung.GESPERRT)

    @property
    def kooperiert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kooperations_manifest_id for n in self.normen if n.geltung is KooperationsGeltung.KOOPERIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kooperations_manifest_id for n in self.normen if n.geltung is KooperationsGeltung.GRUNDLEGEND_KOOPERIERT)

    @property
    def manifest_signal(self):
        if any(n.geltung is KooperationsGeltung.GESPERRT for n in self.normen):
            status = "manifest-gesperrt"
            severity = "critical"
        elif any(n.geltung is KooperationsGeltung.KOOPERIERT for n in self.normen):
            status = "manifest-kooperiert"
            severity = "warning"
        else:
            status = "manifest-grundlegend-kooperiert"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_kooperations_manifest(
    allianz_vertrag: AllianzVertrag | None = None,
    *,
    manifest_id: str = "kooperations-manifest",
) -> KooperationsManifest:
    if allianz_vertrag is None:
        allianz_vertrag = build_allianz_vertrag(vertrag_id=f"{manifest_id}-vertrag")

    normen: list[KooperationsNorm] = []
    for parent_norm in allianz_vertrag.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{manifest_id}-{parent_norm.allianz_vertrag_id.removeprefix(f'{allianz_vertrag.vertrag_id}-')}"
        raw_weight = min(1.0, round(parent_norm.allianz_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.allianz_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KooperationsGeltung.GRUNDLEGEND_KOOPERIERT)
        normen.append(
            KooperationsNorm(
                kooperations_manifest_id=new_id,
                kooperations_grad=_GRAD_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                kooperations_weight=raw_weight,
                kooperations_tier=new_tier,
                canonical=is_canonical,
                kooperations_manifest_ids=parent_norm.allianz_vertrag_ids + (new_id,),
                kooperations_manifest_tags=parent_norm.allianz_vertrag_tags + (f"kooperations-manifest:{new_geltung.value}",),
            )
        )

    return KooperationsManifest(
        manifest_id=manifest_id,
        allianz_vertrag=allianz_vertrag,
        normen=tuple(normen),
    )
