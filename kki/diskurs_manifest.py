"""
#505 DiskursManifest — Habermas/Apel/Benhabib Grundlagen der Diskursethik

Jürgen Habermas (1983): Moralbewusstsein und kommunikatives Handeln — Diskursethik: moralische
  Normen sind nur dann gültig, wenn alle Betroffenen ihnen in einem herrschaftsfreien Diskurs
  zustimmen könnten; ideale Sprechsituation als regulative Idee; kommunikatives Handeln vs.
  strategisches Handeln; Verfahren der Argumentation als Quelle moralischer Verbindlichkeit.
Karl-Otto Apel (1973): Transformation der Philosophie — Transzendentalpragmatik: die ideale
  Kommunikationsgemeinschaft ist unhintergehbare Voraussetzung jeden Argumentierens; reale und
  ideale Kommunikationsgemeinschaft als Orientierungsgröße ethischen Handelns.
Seyla Benhabib (1992): Situating the Self — konkrete vs. verallgemeinerte Andere: Diskursethik
  muss die Partikularität konkreter Personen einbeziehen; feministische Kritik an abstrakten
  Universalisierungen; interaktiver Universalismus als Synthese.
Leitsterns Peta-Schwarm verankert Diskurs als demokratisches Legitimationsprinzip: GESPERRT
sichert diskursive Kernnormen, DISKURSIV ermöglicht adaptive Kommunikationskoordination
über Millionen Agenten, GRUNDLEGEND_DISKURSIV synthetisiert das vollständige diskursethische
Fundament für souveräne Peta-Schwarm-Deliberation. 🗣️
Parent: TugendKodex (#504)
Block #501–#510: Ethik & Moralphilosophie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .tugend_kodex import (
    TugendKodex,
    TugendKodexGeltung,
    build_tugend_kodex,
)

_GELTUNG_MAP: dict[TugendKodexGeltung, "DiskursManifestGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[TugendKodexGeltung.GESPERRT] = DiskursManifestGeltung.GESPERRT
    _GELTUNG_MAP[TugendKodexGeltung.TUGENDHAFT] = DiskursManifestGeltung.DISKURSIV
    _GELTUNG_MAP[TugendKodexGeltung.GRUNDLEGEND_TUGENDHAFT] = DiskursManifestGeltung.GRUNDLEGEND_DISKURSIV


class DiskursManifestTyp(Enum):
    SCHUTZ_DISKURS = "schutz-diskurs"
    ORDNUNGS_DISKURS = "ordnungs-diskurs"
    SOUVERAENITAETS_DISKURS = "souveraenitaets-diskurs"


class DiskursManifestProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class DiskursManifestGeltung(Enum):
    GESPERRT = "gesperrt"
    DISKURSIV = "diskursiv"
    GRUNDLEGEND_DISKURSIV = "grundlegend-diskursiv"


_init_map()

_TYP_MAP: dict[DiskursManifestGeltung, DiskursManifestTyp] = {
    DiskursManifestGeltung.GESPERRT: DiskursManifestTyp.SCHUTZ_DISKURS,
    DiskursManifestGeltung.DISKURSIV: DiskursManifestTyp.ORDNUNGS_DISKURS,
    DiskursManifestGeltung.GRUNDLEGEND_DISKURSIV: DiskursManifestTyp.SOUVERAENITAETS_DISKURS,
}

_PROZEDUR_MAP: dict[DiskursManifestGeltung, DiskursManifestProzedur] = {
    DiskursManifestGeltung.GESPERRT: DiskursManifestProzedur.NOTPROZEDUR,
    DiskursManifestGeltung.DISKURSIV: DiskursManifestProzedur.REGELPROTOKOLL,
    DiskursManifestGeltung.GRUNDLEGEND_DISKURSIV: DiskursManifestProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[DiskursManifestGeltung, float] = {
    DiskursManifestGeltung.GESPERRT: 0.0,
    DiskursManifestGeltung.DISKURSIV: 0.04,
    DiskursManifestGeltung.GRUNDLEGEND_DISKURSIV: 0.08,
}

_TIER_DELTA: dict[DiskursManifestGeltung, int] = {
    DiskursManifestGeltung.GESPERRT: 0,
    DiskursManifestGeltung.DISKURSIV: 1,
    DiskursManifestGeltung.GRUNDLEGEND_DISKURSIV: 2,
}


@dataclass(frozen=True)
class DiskursManifestNorm:
    diskurs_manifest_id: str
    diskurs_typ: DiskursManifestTyp
    prozedur: DiskursManifestProzedur
    geltung: DiskursManifestGeltung
    diskurs_weight: float
    diskurs_tier: int
    canonical: bool
    diskurs_ids: tuple[str, ...]
    diskurs_tags: tuple[str, ...]


@dataclass(frozen=True)
class DiskursManifest:
    manifest_id: str
    tugend_kodex: TugendKodex
    normen: tuple[DiskursManifestNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.diskurs_manifest_id for n in self.normen if n.geltung is DiskursManifestGeltung.GESPERRT)

    @property
    def diskursiv_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.diskurs_manifest_id for n in self.normen if n.geltung is DiskursManifestGeltung.DISKURSIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.diskurs_manifest_id for n in self.normen if n.geltung is DiskursManifestGeltung.GRUNDLEGEND_DISKURSIV)

    @property
    def manifest_signal(self):
        if any(n.geltung is DiskursManifestGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-gesperrt")
        elif any(n.geltung is DiskursManifestGeltung.DISKURSIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-diskursiv")
        from types import SimpleNamespace
        return SimpleNamespace(status="manifest-grundlegend-diskursiv")


def build_diskurs_manifest(
    tugend_kodex: TugendKodex | None = None,
    *,
    manifest_id: str = "diskurs-manifest",
) -> DiskursManifest:
    if tugend_kodex is None:
        tugend_kodex = build_tugend_kodex(kodex_id=f"{manifest_id}-kodex")

    normen: list[DiskursManifestNorm] = []
    for parent_norm in tugend_kodex.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{manifest_id}-{parent_norm.tugend_kodex_id.removeprefix(f'{tugend_kodex.kodex_id}-')}"
        raw_weight = min(1.0, parent_norm.tugend_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.tugend_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is DiskursManifestGeltung.GRUNDLEGEND_DISKURSIV)
        normen.append(
            DiskursManifestNorm(
                diskurs_manifest_id=new_id,
                diskurs_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                diskurs_weight=new_weight,
                diskurs_tier=new_tier,
                canonical=is_canonical,
                diskurs_ids=parent_norm.tugend_ids + (new_id,),
                diskurs_tags=parent_norm.tugend_tags + (f"diskurs-manifest:{new_geltung.value}",),
            )
        )
    return DiskursManifest(
        manifest_id=manifest_id,
        tugend_kodex=tugend_kodex,
        normen=tuple(normen),
    )
