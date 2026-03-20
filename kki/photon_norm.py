"""#298 – PhotonNorm (*_norm-Muster): Photon-Normierung als Governance-Satzung.

Parent: spektral_senat (#297)
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .spektral_senat import (
    SpektralGeltung,
    SpektralSenat,
    build_spektral_senat,
)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class PhotonNormTyp(Enum):
    SCHUTZ_PHOTONNORM = "schutz-photonnorm"
    ORDNUNGS_PHOTONNORM = "ordnungs-photonnorm"
    SOUVERAENITAETS_PHOTONNORM = "souveraenitaets-photonnorm"


class PhotonNormProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class PhotonNormGeltung(Enum):
    GESPERRT = "gesperrt"
    PHOTONISCH = "photonisch"
    GRUNDLEGEND_PHOTONISCH = "grundlegend-photonisch"


# ---------------------------------------------------------------------------
# Internal maps
# ---------------------------------------------------------------------------

_GELTUNG_MAP: dict[SpektralGeltung, PhotonNormGeltung] = {
    SpektralGeltung.GESPERRT: PhotonNormGeltung.GESPERRT,
    SpektralGeltung.SPEKTRAL: PhotonNormGeltung.PHOTONISCH,
    SpektralGeltung.GRUNDLEGEND_SPEKTRAL: PhotonNormGeltung.GRUNDLEGEND_PHOTONISCH,
}

_TYP_MAP: dict[SpektralGeltung, PhotonNormTyp] = {
    SpektralGeltung.GESPERRT: PhotonNormTyp.SCHUTZ_PHOTONNORM,
    SpektralGeltung.SPEKTRAL: PhotonNormTyp.ORDNUNGS_PHOTONNORM,
    SpektralGeltung.GRUNDLEGEND_SPEKTRAL: PhotonNormTyp.SOUVERAENITAETS_PHOTONNORM,
}

_PROZEDUR_MAP: dict[SpektralGeltung, PhotonNormProzedur] = {
    SpektralGeltung.GESPERRT: PhotonNormProzedur.NOTPROZEDUR,
    SpektralGeltung.SPEKTRAL: PhotonNormProzedur.REGELPROTOKOLL,
    SpektralGeltung.GRUNDLEGEND_SPEKTRAL: PhotonNormProzedur.PLENARPROTOKOLL,
}

_WEIGHT_BONUS: dict[SpektralGeltung, float] = {
    SpektralGeltung.GESPERRT: 0.0,
    SpektralGeltung.SPEKTRAL: 0.04,
    SpektralGeltung.GRUNDLEGEND_SPEKTRAL: 0.08,
}

_TIER_BONUS: dict[SpektralGeltung, int] = {
    SpektralGeltung.GESPERRT: 0,
    SpektralGeltung.SPEKTRAL: 1,
    SpektralGeltung.GRUNDLEGEND_SPEKTRAL: 2,
}

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PhotonNormEintrag:
    photon_norm_id: str
    photon_norm_typ: PhotonNormTyp
    prozedur: PhotonNormProzedur
    geltung: PhotonNormGeltung
    photon_norm_weight: float
    photon_norm_tier: int
    canonical: bool
    photon_norm_ids: tuple[str, ...]
    photon_norm_tags: tuple[str, ...]


@dataclass(frozen=True)
class PhotonNormSatz:
    norm_id: str
    spektral_senat: SpektralSenat
    normen: tuple[PhotonNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.photon_norm_id for n in self.normen if n.geltung is PhotonNormGeltung.GESPERRT)

    @property
    def photonisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.photon_norm_id for n in self.normen if n.geltung is PhotonNormGeltung.PHOTONISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.photon_norm_id for n in self.normen if n.geltung is PhotonNormGeltung.GRUNDLEGEND_PHOTONISCH)

    @property
    def norm_signal(self):
        if any(n.geltung is PhotonNormGeltung.GESPERRT for n in self.normen):
            status = "norm-gesperrt"
            severity = "critical"
        elif any(n.geltung is PhotonNormGeltung.PHOTONISCH for n in self.normen):
            status = "norm-photonisch"
            severity = "warning"
        else:
            status = "norm-grundlegend-photonisch"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def build_photon_norm(
    spektral_senat: SpektralSenat | None = None,
    *,
    norm_id: str = "photon-norm",
) -> PhotonNormSatz:
    if spektral_senat is None:
        spektral_senat = build_spektral_senat(senat_id=f"{norm_id}-senat")

    normen: list[PhotonNormEintrag] = []
    for parent_norm in spektral_senat.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{norm_id}-{parent_norm.spektral_senat_id.removeprefix(f'{spektral_senat.senat_id}-')}"
        raw_weight = min(1.0, round(parent_norm.spektral_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.spektral_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is PhotonNormGeltung.GRUNDLEGEND_PHOTONISCH)
        normen.append(
            PhotonNormEintrag(
                photon_norm_id=new_id,
                photon_norm_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                photon_norm_weight=raw_weight,
                photon_norm_tier=new_tier,
                canonical=is_canonical,
                photon_norm_ids=parent_norm.spektral_ids + (new_id,),
                photon_norm_tags=parent_norm.spektral_tags + (f"photon-norm:{new_geltung.value}",),
            )
        )

    return PhotonNormSatz(
        norm_id=norm_id,
        spektral_senat=spektral_senat,
        normen=tuple(normen),
    )
