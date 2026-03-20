"""#299 – PhotoeffektCharta: Photoeffekt als Governance-Charta.

Parent: photon_norm (#298)
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .photon_norm import (
    PhotonNormGeltung,
    PhotonNormSatz,
    build_photon_norm,
)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class PhotoeffektTyp(Enum):
    SCHUTZ_PHOTOEFFEKT = "schutz-photoeffekt"
    ORDNUNGS_PHOTOEFFEKT = "ordnungs-photoeffekt"
    SOUVERAENITAETS_PHOTOEFFEKT = "souveraenitaets-photoeffekt"


class PhotoeffektProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class PhotoeffektGeltung(Enum):
    GESPERRT = "gesperrt"
    PHOTOEFFEKTIV = "photoeffektiv"
    GRUNDLEGEND_PHOTOEFFEKTIV = "grundlegend-photoeffektiv"


# ---------------------------------------------------------------------------
# Internal maps
# ---------------------------------------------------------------------------

_GELTUNG_MAP: dict[PhotonNormGeltung, PhotoeffektGeltung] = {
    PhotonNormGeltung.GESPERRT: PhotoeffektGeltung.GESPERRT,
    PhotonNormGeltung.PHOTONISCH: PhotoeffektGeltung.PHOTOEFFEKTIV,
    PhotonNormGeltung.GRUNDLEGEND_PHOTONISCH: PhotoeffektGeltung.GRUNDLEGEND_PHOTOEFFEKTIV,
}

_TYP_MAP: dict[PhotonNormGeltung, PhotoeffektTyp] = {
    PhotonNormGeltung.GESPERRT: PhotoeffektTyp.SCHUTZ_PHOTOEFFEKT,
    PhotonNormGeltung.PHOTONISCH: PhotoeffektTyp.ORDNUNGS_PHOTOEFFEKT,
    PhotonNormGeltung.GRUNDLEGEND_PHOTONISCH: PhotoeffektTyp.SOUVERAENITAETS_PHOTOEFFEKT,
}

_PROZEDUR_MAP: dict[PhotonNormGeltung, PhotoeffektProzedur] = {
    PhotonNormGeltung.GESPERRT: PhotoeffektProzedur.NOTPROZEDUR,
    PhotonNormGeltung.PHOTONISCH: PhotoeffektProzedur.REGELPROTOKOLL,
    PhotonNormGeltung.GRUNDLEGEND_PHOTONISCH: PhotoeffektProzedur.PLENARPROTOKOLL,
}

_WEIGHT_BONUS: dict[PhotonNormGeltung, float] = {
    PhotonNormGeltung.GESPERRT: 0.0,
    PhotonNormGeltung.PHOTONISCH: 0.04,
    PhotonNormGeltung.GRUNDLEGEND_PHOTONISCH: 0.08,
}

_TIER_BONUS: dict[PhotonNormGeltung, int] = {
    PhotonNormGeltung.GESPERRT: 0,
    PhotonNormGeltung.PHOTONISCH: 1,
    PhotonNormGeltung.GRUNDLEGEND_PHOTONISCH: 2,
}

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PhotoeffektNorm:
    photoeffekt_charta_id: str
    photoeffekt_typ: PhotoeffektTyp
    prozedur: PhotoeffektProzedur
    geltung: PhotoeffektGeltung
    photoeffekt_weight: float
    photoeffekt_tier: int
    canonical: bool
    photoeffekt_ids: tuple[str, ...]
    photoeffekt_tags: tuple[str, ...]


@dataclass(frozen=True)
class PhotoeffektCharta:
    charta_id: str
    photon_norm: PhotonNormSatz
    normen: tuple[PhotoeffektNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.photoeffekt_charta_id for n in self.normen if n.geltung is PhotoeffektGeltung.GESPERRT)

    @property
    def photoeffektiv_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.photoeffekt_charta_id for n in self.normen if n.geltung is PhotoeffektGeltung.PHOTOEFFEKTIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.photoeffekt_charta_id for n in self.normen if n.geltung is PhotoeffektGeltung.GRUNDLEGEND_PHOTOEFFEKTIV)

    @property
    def charta_signal(self):
        if any(n.geltung is PhotoeffektGeltung.GESPERRT for n in self.normen):
            status = "charta-gesperrt"
            severity = "critical"
        elif any(n.geltung is PhotoeffektGeltung.PHOTOEFFEKTIV for n in self.normen):
            status = "charta-photoeffektiv"
            severity = "warning"
        else:
            status = "charta-grundlegend-photoeffektiv"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def build_photoeffekt_charta(
    photon_norm: PhotonNormSatz | None = None,
    *,
    charta_id: str = "photoeffekt-charta",
) -> PhotoeffektCharta:
    if photon_norm is None:
        photon_norm = build_photon_norm(norm_id=f"{charta_id}-norm")

    normen: list[PhotoeffektNorm] = []
    for parent_norm in photon_norm.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{charta_id}-{parent_norm.photon_norm_id.removeprefix(f'{photon_norm.norm_id}-')}"
        raw_weight = min(1.0, round(parent_norm.photon_norm_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.photon_norm_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is PhotoeffektGeltung.GRUNDLEGEND_PHOTOEFFEKTIV)
        normen.append(
            PhotoeffektNorm(
                photoeffekt_charta_id=new_id,
                photoeffekt_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                photoeffekt_weight=raw_weight,
                photoeffekt_tier=new_tier,
                canonical=is_canonical,
                photoeffekt_ids=parent_norm.photon_norm_ids + (new_id,),
                photoeffekt_tags=parent_norm.photon_norm_tags + (f"photoeffekt-charta:{new_geltung.value}",),
            )
        )

    return PhotoeffektCharta(
        charta_id=charta_id,
        photon_norm=photon_norm,
        normen=tuple(normen),
    )
