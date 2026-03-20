"""
#317 SymmetriebrechungsSenat — Spontane Symmetriebrechung als Governance-Senat.
Geltungsstufen: GESPERRT / SYMMETRIEGEBROCHEN / GRUNDLEGEND_SYMMETRIEGEBROCHEN
Parent: HiggsManifest (#316)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .higgs_manifest import HiggsGeltung, HiggsManifest, build_higgs_manifest

_GELTUNG_MAP: dict[HiggsGeltung, "SymmetriebrechungsGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[HiggsGeltung.GESPERRT] = SymmetriebrechungsGeltung.GESPERRT
    _GELTUNG_MAP[HiggsGeltung.HIGGSGEKOPPELT] = SymmetriebrechungsGeltung.SYMMETRIEGEBROCHEN
    _GELTUNG_MAP[HiggsGeltung.GRUNDLEGEND_HIGGSGEKOPPELT] = SymmetriebrechungsGeltung.GRUNDLEGEND_SYMMETRIEGEBROCHEN


class SymmetriebrechungsTyp(Enum):
    SCHUTZ_SYMMETRIEBRECHUNG = "schutz-symmetriebrechung"
    ORDNUNGS_SYMMETRIEBRECHUNG = "ordnungs-symmetriebrechung"
    SOUVERAENITAETS_SYMMETRIEBRECHUNG = "souveraenitaets-symmetriebrechung"


class SymmetriebrechungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class SymmetriebrechungsGeltung(Enum):
    GESPERRT = "gesperrt"
    SYMMETRIEGEBROCHEN = "symmetriegebrochen"
    GRUNDLEGEND_SYMMETRIEGEBROCHEN = "grundlegend-symmetriegebrochen"


_init_map()

_TYP_MAP: dict[SymmetriebrechungsGeltung, SymmetriebrechungsTyp] = {
    SymmetriebrechungsGeltung.GESPERRT: SymmetriebrechungsTyp.SCHUTZ_SYMMETRIEBRECHUNG,
    SymmetriebrechungsGeltung.SYMMETRIEGEBROCHEN: SymmetriebrechungsTyp.ORDNUNGS_SYMMETRIEBRECHUNG,
    SymmetriebrechungsGeltung.GRUNDLEGEND_SYMMETRIEGEBROCHEN: SymmetriebrechungsTyp.SOUVERAENITAETS_SYMMETRIEBRECHUNG,
}

_PROZEDUR_MAP: dict[SymmetriebrechungsGeltung, SymmetriebrechungsProzedur] = {
    SymmetriebrechungsGeltung.GESPERRT: SymmetriebrechungsProzedur.NOTPROZEDUR,
    SymmetriebrechungsGeltung.SYMMETRIEGEBROCHEN: SymmetriebrechungsProzedur.REGELPROTOKOLL,
    SymmetriebrechungsGeltung.GRUNDLEGEND_SYMMETRIEGEBROCHEN: SymmetriebrechungsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[SymmetriebrechungsGeltung, float] = {
    SymmetriebrechungsGeltung.GESPERRT: 0.0,
    SymmetriebrechungsGeltung.SYMMETRIEGEBROCHEN: 0.04,
    SymmetriebrechungsGeltung.GRUNDLEGEND_SYMMETRIEGEBROCHEN: 0.08,
}

_TIER_DELTA: dict[SymmetriebrechungsGeltung, int] = {
    SymmetriebrechungsGeltung.GESPERRT: 0,
    SymmetriebrechungsGeltung.SYMMETRIEGEBROCHEN: 1,
    SymmetriebrechungsGeltung.GRUNDLEGEND_SYMMETRIEGEBROCHEN: 2,
}


@dataclass(frozen=True)
class SymmetriebrechungsNorm:
    symmetriebrechungs_senat_id: str
    symmetriebrechungs_typ: SymmetriebrechungsTyp
    prozedur: SymmetriebrechungsProzedur
    geltung: SymmetriebrechungsGeltung
    symmetriebrechungs_weight: float
    symmetriebrechungs_tier: int
    canonical: bool
    symmetriebrechungs_ids: tuple[str, ...]
    symmetriebrechungs_tags: tuple[str, ...]


@dataclass(frozen=True)
class SymmetriebrechungsSenat:
    senat_id: str
    higgs_manifest: HiggsManifest
    normen: tuple[SymmetriebrechungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.symmetriebrechungs_senat_id for n in self.normen if n.geltung is SymmetriebrechungsGeltung.GESPERRT)

    @property
    def symmetriegebrochen_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.symmetriebrechungs_senat_id for n in self.normen if n.geltung is SymmetriebrechungsGeltung.SYMMETRIEGEBROCHEN)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.symmetriebrechungs_senat_id for n in self.normen if n.geltung is SymmetriebrechungsGeltung.GRUNDLEGEND_SYMMETRIEGEBROCHEN)

    @property
    def senat_signal(self):
        if any(n.geltung is SymmetriebrechungsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-gesperrt")
        elif any(n.geltung is SymmetriebrechungsGeltung.SYMMETRIEGEBROCHEN for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-symmetriegebrochen")
        from types import SimpleNamespace
        return SimpleNamespace(status="senat-grundlegend-symmetriegebrochen")


def build_symmetriebrechungs_senat(
    higgs_manifest: HiggsManifest | None = None,
    *,
    senat_id: str = "symmetriebrechungs-senat",
) -> SymmetriebrechungsSenat:
    if higgs_manifest is None:
        higgs_manifest = build_higgs_manifest(manifest_id=f"{senat_id}-manifest")

    normen: list[SymmetriebrechungsNorm] = []
    for parent_norm in higgs_manifest.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{senat_id}-{parent_norm.higgs_manifest_id.removeprefix(f'{higgs_manifest.manifest_id}-')}"
        raw_weight = min(1.0, parent_norm.higgs_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.higgs_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SymmetriebrechungsGeltung.GRUNDLEGEND_SYMMETRIEGEBROCHEN)
        normen.append(
            SymmetriebrechungsNorm(
                symmetriebrechungs_senat_id=new_id,
                symmetriebrechungs_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                symmetriebrechungs_weight=new_weight,
                symmetriebrechungs_tier=new_tier,
                canonical=is_canonical,
                symmetriebrechungs_ids=parent_norm.higgs_ids + (new_id,),
                symmetriebrechungs_tags=parent_norm.higgs_tags + (f"symmetriebrechungs-senat:{new_geltung.value}",),
            )
        )
    return SymmetriebrechungsSenat(
        senat_id=senat_id,
        higgs_manifest=higgs_manifest,
        normen=tuple(normen),
    )
