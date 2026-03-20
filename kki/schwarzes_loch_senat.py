"""schwarzes_loch_senat — Relativität & Raumzeit layer 7 (#277)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .singularitaets_manifest import (
    SingularitaetsGeltung,
    SingularitaetsManifest,
    SingularitaetsNorm,
    SingularitaetsProzedur,
    SingularitaetsTyp,
    build_singularitaets_manifest,
)

__all__ = [
    "SchwarzsLochTyp",
    "SchwarzsLochProzedur",
    "SchwarzsLochGeltung",
    "SchwarzsLochNorm",
    "SchwarzeLoechSenat",
    "build_schwarzes_loch_senat",
]


class SchwarzsLochTyp(str, Enum):
    SCHUTZ_SCHWARZES_LOCH = "schutz-schwarzes-loch"
    ORDNUNGS_SCHWARZES_LOCH = "ordnungs-schwarzes-loch"
    SOUVERAENITAETS_SCHWARZES_LOCH = "souveraenitaets-schwarzes-loch"


class SchwarzsLochProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class SchwarzsLochGeltung(str, Enum):
    GESPERRT = "gesperrt"
    ABSORBIERT = "absorbiert"
    GRUNDLEGEND_ABSORBIERT = "grundlegend-absorbiert"


_TYP_MAP: dict[SingularitaetsGeltung, SchwarzsLochTyp] = {
    SingularitaetsGeltung.GESPERRT: SchwarzsLochTyp.SCHUTZ_SCHWARZES_LOCH,
    SingularitaetsGeltung.SINGULAER: SchwarzsLochTyp.ORDNUNGS_SCHWARZES_LOCH,
    SingularitaetsGeltung.GRUNDLEGEND_SINGULAER: SchwarzsLochTyp.SOUVERAENITAETS_SCHWARZES_LOCH,
}
_PROZEDUR_MAP: dict[SingularitaetsGeltung, SchwarzsLochProzedur] = {
    SingularitaetsGeltung.GESPERRT: SchwarzsLochProzedur.NOTPROZEDUR,
    SingularitaetsGeltung.SINGULAER: SchwarzsLochProzedur.REGELPROTOKOLL,
    SingularitaetsGeltung.GRUNDLEGEND_SINGULAER: SchwarzsLochProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[SingularitaetsGeltung, SchwarzsLochGeltung] = {
    SingularitaetsGeltung.GESPERRT: SchwarzsLochGeltung.GESPERRT,
    SingularitaetsGeltung.SINGULAER: SchwarzsLochGeltung.ABSORBIERT,
    SingularitaetsGeltung.GRUNDLEGEND_SINGULAER: SchwarzsLochGeltung.GRUNDLEGEND_ABSORBIERT,
}
_WEIGHT_BONUS: dict[SingularitaetsGeltung, float] = {
    SingularitaetsGeltung.GESPERRT: 0.0,
    SingularitaetsGeltung.SINGULAER: 0.04,
    SingularitaetsGeltung.GRUNDLEGEND_SINGULAER: 0.08,
}
_TIER_BONUS: dict[SingularitaetsGeltung, int] = {
    SingularitaetsGeltung.GESPERRT: 0,
    SingularitaetsGeltung.SINGULAER: 1,
    SingularitaetsGeltung.GRUNDLEGEND_SINGULAER: 2,
}


@dataclass(frozen=True)
class SchwarzsLochNorm:
    schwarzes_loch_senat_id: str
    schwarzes_loch_typ: SchwarzsLochTyp
    prozedur: SchwarzsLochProzedur
    geltung: SchwarzsLochGeltung
    schwarzes_loch_weight: float
    schwarzes_loch_tier: int
    canonical: bool
    schwarzes_loch_senat_ids: tuple[str, ...]
    schwarzes_loch_senat_tags: tuple[str, ...]


@dataclass(frozen=True)
class SchwarzeLoechSenat:
    senat_id: str
    singularitaets_manifest: SingularitaetsManifest
    normen: tuple[SchwarzsLochNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.schwarzes_loch_senat_id for n in self.normen if n.geltung is SchwarzsLochGeltung.GESPERRT)

    @property
    def absorbiert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.schwarzes_loch_senat_id for n in self.normen if n.geltung is SchwarzsLochGeltung.ABSORBIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.schwarzes_loch_senat_id for n in self.normen if n.geltung is SchwarzsLochGeltung.GRUNDLEGEND_ABSORBIERT)

    @property
    def senat_signal(self):
        if any(n.geltung is SchwarzsLochGeltung.GESPERRT for n in self.normen):
            status = "senat-gesperrt"
            severity = "critical"
        elif any(n.geltung is SchwarzsLochGeltung.ABSORBIERT for n in self.normen):
            status = "senat-absorbiert"
            severity = "warning"
        else:
            status = "senat-grundlegend-absorbiert"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_schwarzes_loch_senat(
    singularitaets_manifest: SingularitaetsManifest | None = None,
    *,
    senat_id: str = "schwarzes-loch-senat",
) -> SchwarzeLoechSenat:
    if singularitaets_manifest is None:
        singularitaets_manifest = build_singularitaets_manifest(manifest_id=f"{senat_id}-manifest")

    normen: list[SchwarzsLochNorm] = []
    for parent_norm in singularitaets_manifest.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{senat_id}-{parent_norm.singularitaets_manifest_id.removeprefix(f'{singularitaets_manifest.manifest_id}-')}"
        raw_weight = min(1.0, round(parent_norm.singularitaets_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.singularitaets_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SchwarzsLochGeltung.GRUNDLEGEND_ABSORBIERT)
        normen.append(
            SchwarzsLochNorm(
                schwarzes_loch_senat_id=new_id,
                schwarzes_loch_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                schwarzes_loch_weight=raw_weight,
                schwarzes_loch_tier=new_tier,
                canonical=is_canonical,
                schwarzes_loch_senat_ids=parent_norm.singularitaets_manifest_ids + (new_id,),
                schwarzes_loch_senat_tags=parent_norm.singularitaets_manifest_tags + (f"schwarzes-loch-senat:{new_geltung.value}",),
            )
        )

    return SchwarzeLoechSenat(
        senat_id=senat_id,
        singularitaets_manifest=singularitaets_manifest,
        normen=tuple(normen),
    )
