"""
#467 DiskursSenat — Schwarm-Entscheidungen durch strukturierten Diskurs.
Foucault (1969): L'Archéologie du savoir — Diskursformationen und Aussagen als Wissensordnungen.
Habermas (1981): Theorie des kommunikativen Handelns — Verständigungsorientiertes Handeln.
van Dijk (1980): Macrostructures — Makrostruktur von Diskursen.
Leitsterns Diskurs: Schwarm-Entscheidungen entstehen durch strukturierten Diskurs nach Habermas.
Geltungsstufen: GESPERRT / DISKURSIV / GRUNDLEGEND_DISKURSIV
Parent: SemiotikManifest (#466)
Block #461–#470: Linguistik & Semiotik
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .semiotik_manifest import (
    SemiotikManifest,
    SemiotikManifestGeltung,
    build_semiotik_manifest,
)

_GELTUNG_MAP: dict[SemiotikManifestGeltung, "DiskursSenatGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[SemiotikManifestGeltung.GESPERRT] = DiskursSenatGeltung.GESPERRT
    _GELTUNG_MAP[SemiotikManifestGeltung.SEMIOTISCH] = DiskursSenatGeltung.DISKURSIV
    _GELTUNG_MAP[SemiotikManifestGeltung.GRUNDLEGEND_SEMIOTISCH] = DiskursSenatGeltung.GRUNDLEGEND_DISKURSIV


class DiskursSenatTyp(Enum):
    SCHUTZ_DISKURS = "schutz-diskurs"
    ORDNUNGS_DISKURS = "ordnungs-diskurs"
    SOUVERAENITAETS_DISKURS = "souveraenitaets-diskurs"


class DiskursSenatProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class DiskursSenatGeltung(Enum):
    GESPERRT = "gesperrt"
    DISKURSIV = "diskursiv"
    GRUNDLEGEND_DISKURSIV = "grundlegend-diskursiv"


_init_map()

_TYP_MAP: dict[DiskursSenatGeltung, DiskursSenatTyp] = {
    DiskursSenatGeltung.GESPERRT: DiskursSenatTyp.SCHUTZ_DISKURS,
    DiskursSenatGeltung.DISKURSIV: DiskursSenatTyp.ORDNUNGS_DISKURS,
    DiskursSenatGeltung.GRUNDLEGEND_DISKURSIV: DiskursSenatTyp.SOUVERAENITAETS_DISKURS,
}

_PROZEDUR_MAP: dict[DiskursSenatGeltung, DiskursSenatProzedur] = {
    DiskursSenatGeltung.GESPERRT: DiskursSenatProzedur.NOTPROZEDUR,
    DiskursSenatGeltung.DISKURSIV: DiskursSenatProzedur.REGELPROTOKOLL,
    DiskursSenatGeltung.GRUNDLEGEND_DISKURSIV: DiskursSenatProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[DiskursSenatGeltung, float] = {
    DiskursSenatGeltung.GESPERRT: 0.0,
    DiskursSenatGeltung.DISKURSIV: 0.04,
    DiskursSenatGeltung.GRUNDLEGEND_DISKURSIV: 0.08,
}

_TIER_DELTA: dict[DiskursSenatGeltung, int] = {
    DiskursSenatGeltung.GESPERRT: 0,
    DiskursSenatGeltung.DISKURSIV: 1,
    DiskursSenatGeltung.GRUNDLEGEND_DISKURSIV: 2,
}


@dataclass(frozen=True)
class DiskursSenatNorm:
    diskurs_senat_id: str
    diskurs_senat_typ: DiskursSenatTyp
    prozedur: DiskursSenatProzedur
    geltung: DiskursSenatGeltung
    diskurs_weight: float
    diskurs_tier: int
    canonical: bool
    diskurs_ids: tuple[str, ...]
    diskurs_tags: tuple[str, ...]


@dataclass(frozen=True)
class DiskursSenat:
    senat_id: str
    semiotik_manifest: SemiotikManifest
    normen: tuple[DiskursSenatNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.diskurs_senat_id for n in self.normen if n.geltung is DiskursSenatGeltung.GESPERRT)

    @property
    def diskursiv_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.diskurs_senat_id for n in self.normen if n.geltung is DiskursSenatGeltung.DISKURSIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.diskurs_senat_id for n in self.normen if n.geltung is DiskursSenatGeltung.GRUNDLEGEND_DISKURSIV)

    @property
    def senat_signal(self):
        if any(n.geltung is DiskursSenatGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-gesperrt")
        elif any(n.geltung is DiskursSenatGeltung.DISKURSIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-diskursiv")
        from types import SimpleNamespace
        return SimpleNamespace(status="senat-grundlegend-diskursiv")


def build_diskurs_senat(
    semiotik_manifest: SemiotikManifest | None = None,
    *,
    senat_id: str = "diskurs-senat",
) -> DiskursSenat:
    if semiotik_manifest is None:
        semiotik_manifest = build_semiotik_manifest(manifest_id=f"{senat_id}-manifest")

    normen: list[DiskursSenatNorm] = []
    for parent_norm in semiotik_manifest.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{senat_id}-{parent_norm.semiotik_manifest_id.removeprefix(f'{semiotik_manifest.manifest_id}-')}"
        raw_weight = min(1.0, parent_norm.semiotik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.semiotik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is DiskursSenatGeltung.GRUNDLEGEND_DISKURSIV)
        normen.append(
            DiskursSenatNorm(
                diskurs_senat_id=new_id,
                diskurs_senat_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                diskurs_weight=new_weight,
                diskurs_tier=new_tier,
                canonical=is_canonical,
                diskurs_ids=parent_norm.semiotik_ids + (new_id,),
                diskurs_tags=parent_norm.semiotik_tags + (f"diskurs-senat:{new_geltung.value}",),
            )
        )
    return DiskursSenat(
        senat_id=senat_id,
        semiotik_manifest=semiotik_manifest,
        normen=tuple(normen),
    )
