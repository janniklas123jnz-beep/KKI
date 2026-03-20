"""quanten_senat — Quantenfelder & Dimensionen layer 7 (#267)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kollaps_manifest import (
    KollapsGeltung,
    KollapsManifest,
    KollapsNorm,
    KollapsProzedur,
    KollapsTyp,
    build_kollaps_manifest,
)

__all__ = [
    "QuantenSenatTyp",
    "QuantenSenatProzedur",
    "QuantenSenatGeltung",
    "QuantenSenatNorm",
    "QuantenSenat",
    "build_quanten_senat",
]


class QuantenSenatTyp(str, Enum):
    SCHUTZ_SENAT = "schutz-senat"
    ORDNUNGS_SENAT = "ordnungs-senat"
    SOUVERAENITAETS_SENAT = "souveraenitaets-senat"


class QuantenSenatProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class QuantenSenatGeltung(str, Enum):
    GESPERRT = "gesperrt"
    SENATSREIF = "senatsreif"
    GRUNDLEGEND_SENATSREIF = "grundlegend-senatsreif"


_TYP_MAP: dict[KollapsGeltung, QuantenSenatTyp] = {
    KollapsGeltung.GESPERRT: QuantenSenatTyp.SCHUTZ_SENAT,
    KollapsGeltung.KOLLABIERT: QuantenSenatTyp.ORDNUNGS_SENAT,
    KollapsGeltung.GRUNDLEGEND_KOLLABIERT: QuantenSenatTyp.SOUVERAENITAETS_SENAT,
}
_PROZEDUR_MAP: dict[KollapsGeltung, QuantenSenatProzedur] = {
    KollapsGeltung.GESPERRT: QuantenSenatProzedur.NOTPROZEDUR,
    KollapsGeltung.KOLLABIERT: QuantenSenatProzedur.REGELPROTOKOLL,
    KollapsGeltung.GRUNDLEGEND_KOLLABIERT: QuantenSenatProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[KollapsGeltung, QuantenSenatGeltung] = {
    KollapsGeltung.GESPERRT: QuantenSenatGeltung.GESPERRT,
    KollapsGeltung.KOLLABIERT: QuantenSenatGeltung.SENATSREIF,
    KollapsGeltung.GRUNDLEGEND_KOLLABIERT: QuantenSenatGeltung.GRUNDLEGEND_SENATSREIF,
}
_WEIGHT_BONUS: dict[KollapsGeltung, float] = {
    KollapsGeltung.GESPERRT: 0.0,
    KollapsGeltung.KOLLABIERT: 0.04,
    KollapsGeltung.GRUNDLEGEND_KOLLABIERT: 0.08,
}
_TIER_BONUS: dict[KollapsGeltung, int] = {
    KollapsGeltung.GESPERRT: 0,
    KollapsGeltung.KOLLABIERT: 1,
    KollapsGeltung.GRUNDLEGEND_KOLLABIERT: 2,
}


@dataclass(frozen=True)
class QuantenSenatNorm:
    quanten_senat_id: str
    quanten_senat_typ: QuantenSenatTyp
    prozedur: QuantenSenatProzedur
    geltung: QuantenSenatGeltung
    quanten_senat_weight: float
    quanten_senat_tier: int
    canonical: bool
    quanten_senat_ids: tuple[str, ...]
    quanten_senat_tags: tuple[str, ...]


@dataclass(frozen=True)
class QuantenSenat:
    senat_id: str
    kollaps_manifest: KollapsManifest
    normen: tuple[QuantenSenatNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.quanten_senat_id for n in self.normen if n.geltung is QuantenSenatGeltung.GESPERRT)

    @property
    def senatsreif_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.quanten_senat_id for n in self.normen if n.geltung is QuantenSenatGeltung.SENATSREIF)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.quanten_senat_id for n in self.normen if n.geltung is QuantenSenatGeltung.GRUNDLEGEND_SENATSREIF)

    @property
    def senat_signal(self):
        if any(n.geltung is QuantenSenatGeltung.GESPERRT for n in self.normen):
            status = "senat-gesperrt"
            severity = "critical"
        elif any(n.geltung is QuantenSenatGeltung.SENATSREIF for n in self.normen):
            status = "senat-senatsreif"
            severity = "warning"
        else:
            status = "senat-grundlegend-senatsreif"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_quanten_senat(
    kollaps_manifest: KollapsManifest | None = None,
    *,
    senat_id: str = "quanten-senat",
) -> QuantenSenat:
    if kollaps_manifest is None:
        kollaps_manifest = build_kollaps_manifest(manifest_id=f"{senat_id}-manifest")

    normen: list[QuantenSenatNorm] = []
    for parent_norm in kollaps_manifest.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{senat_id}-{parent_norm.kollaps_manifest_id.removeprefix(f'{kollaps_manifest.manifest_id}-')}"
        raw_weight = min(1.0, round(parent_norm.kollaps_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.kollaps_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is QuantenSenatGeltung.GRUNDLEGEND_SENATSREIF)
        normen.append(
            QuantenSenatNorm(
                quanten_senat_id=new_id,
                quanten_senat_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                quanten_senat_weight=raw_weight,
                quanten_senat_tier=new_tier,
                canonical=is_canonical,
                quanten_senat_ids=parent_norm.kollaps_manifest_ids + (new_id,),
                quanten_senat_tags=parent_norm.kollaps_manifest_tags + (f"quanten-senat:{new_geltung.value}",),
            )
        )

    return QuantenSenat(
        senat_id=senat_id,
        kollaps_manifest=kollaps_manifest,
        normen=tuple(normen),
    )
