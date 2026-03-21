"""
#378 LandauerManifest — Landauer-Prinzip: Löschen eines Bits kostet mindestens
kT·ln(2) ≈ 2,87·10⁻²¹ J Energie bei Raumtemperatur (Rolf Landauer 1961).
Information ist physikalisch — keine Entscheidung verschwindet rückstandslos.
Leitsterns Manifest: Jede Governance-Aktion hinterlässt thermodynamische Spuren.
Verantwortung ist nicht philosophisch, sondern physikalisch garantiert.
Geltungsstufen: GESPERRT / LANDAUERGEBUNDEN / GRUNDLEGEND_LANDAUERGEBUNDEN
Parent: HolographischesPrinzipNorm (#377, *_norm)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .holographisches_prinzip_norm import (
    HolographischesPrinzipNormGeltung,
    HolographischesPrinzipNormSatz,
    build_holographisches_prinzip_norm,
)

_GELTUNG_MAP: dict[HolographischesPrinzipNormGeltung, "LandauerGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[HolographischesPrinzipNormGeltung.GESPERRT] = LandauerGeltung.GESPERRT
    _GELTUNG_MAP[HolographischesPrinzipNormGeltung.HOLOGRAPHISCH] = LandauerGeltung.LANDAUERGEBUNDEN
    _GELTUNG_MAP[HolographischesPrinzipNormGeltung.GRUNDLEGEND_HOLOGRAPHISCH] = LandauerGeltung.GRUNDLEGEND_LANDAUERGEBUNDEN


class LandauerTyp(Enum):
    SCHUTZ_LANDAUER = "schutz-landauer"
    ORDNUNGS_LANDAUER = "ordnungs-landauer"
    SOUVERAENITAETS_LANDAUER = "souveraenitaets-landauer"


class LandauerProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class LandauerGeltung(Enum):
    GESPERRT = "gesperrt"
    LANDAUERGEBUNDEN = "landauergebunden"
    GRUNDLEGEND_LANDAUERGEBUNDEN = "grundlegend-landauergebunden"


_init_map()

_TYP_MAP: dict[LandauerGeltung, LandauerTyp] = {
    LandauerGeltung.GESPERRT: LandauerTyp.SCHUTZ_LANDAUER,
    LandauerGeltung.LANDAUERGEBUNDEN: LandauerTyp.ORDNUNGS_LANDAUER,
    LandauerGeltung.GRUNDLEGEND_LANDAUERGEBUNDEN: LandauerTyp.SOUVERAENITAETS_LANDAUER,
}

_PROZEDUR_MAP: dict[LandauerGeltung, LandauerProzedur] = {
    LandauerGeltung.GESPERRT: LandauerProzedur.NOTPROZEDUR,
    LandauerGeltung.LANDAUERGEBUNDEN: LandauerProzedur.REGELPROTOKOLL,
    LandauerGeltung.GRUNDLEGEND_LANDAUERGEBUNDEN: LandauerProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[LandauerGeltung, float] = {
    LandauerGeltung.GESPERRT: 0.0,
    LandauerGeltung.LANDAUERGEBUNDEN: 0.04,
    LandauerGeltung.GRUNDLEGEND_LANDAUERGEBUNDEN: 0.08,
}

_TIER_DELTA: dict[LandauerGeltung, int] = {
    LandauerGeltung.GESPERRT: 0,
    LandauerGeltung.LANDAUERGEBUNDEN: 1,
    LandauerGeltung.GRUNDLEGEND_LANDAUERGEBUNDEN: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LandauerNorm:
    landauer_manifest_id: str
    landauer_typ: LandauerTyp
    prozedur: LandauerProzedur
    geltung: LandauerGeltung
    landauer_weight: float
    landauer_tier: int
    canonical: bool
    landauer_ids: tuple[str, ...]
    landauer_tags: tuple[str, ...]


@dataclass(frozen=True)
class LandauerManifest:
    manifest_id: str
    holographisches_prinzip_norm: HolographischesPrinzipNormSatz
    normen: tuple[LandauerNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.landauer_manifest_id for n in self.normen if n.geltung is LandauerGeltung.GESPERRT)

    @property
    def landauergebunden_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.landauer_manifest_id for n in self.normen if n.geltung is LandauerGeltung.LANDAUERGEBUNDEN)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.landauer_manifest_id for n in self.normen if n.geltung is LandauerGeltung.GRUNDLEGEND_LANDAUERGEBUNDEN)

    @property
    def manifest_signal(self):
        if any(n.geltung is LandauerGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-gesperrt")
        elif any(n.geltung is LandauerGeltung.LANDAUERGEBUNDEN for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-landauergebunden")
        from types import SimpleNamespace
        return SimpleNamespace(status="manifest-grundlegend-landauergebunden")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_landauer_manifest(
    holographisches_prinzip_norm: HolographischesPrinzipNormSatz | None = None,
    *,
    manifest_id: str = "landauer-manifest",
) -> LandauerManifest:
    if holographisches_prinzip_norm is None:
        holographisches_prinzip_norm = build_holographisches_prinzip_norm(norm_id=f"{manifest_id}-norm")

    normen: list[LandauerNorm] = []
    for parent_norm in holographisches_prinzip_norm.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{manifest_id}-{parent_norm.norm_id.removeprefix(f'{holographisches_prinzip_norm.norm_id}-')}"
        raw_weight = min(1.0, parent_norm.holographisches_prinzip_norm_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.holographisches_prinzip_norm_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is LandauerGeltung.GRUNDLEGEND_LANDAUERGEBUNDEN)
        normen.append(
            LandauerNorm(
                landauer_manifest_id=new_id,
                landauer_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                landauer_weight=new_weight,
                landauer_tier=new_tier,
                canonical=is_canonical,
                landauer_ids=parent_norm.holographisches_prinzip_norm_ids + (new_id,),
                landauer_tags=parent_norm.holographisches_prinzip_norm_tags + (f"landauer:{new_geltung.value}",),
            )
        )
    return LandauerManifest(
        manifest_id=manifest_id,
        holographisches_prinzip_norm=holographisches_prinzip_norm,
        normen=tuple(normen),
    )
