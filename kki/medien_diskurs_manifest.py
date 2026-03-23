"""
#565 DiskursManifest (Medienwissenschaft) — Foucault/Habermas/Derrida Diskurstheorie Manifest

Michel Foucault (1969): L'Archéologie du savoir — Diskurs als Gesamtheit der
  Aussagen in einem diskursiven Feld; Episteme als historisches Apriori; Macht/Wissen
  als untrennbares Gefüge; diskursive Formationen und ihre Regeln im Peta-Schwarm
  Leitstern.
Jürgen Habermas (1983): Moralbewusstsein und kommunikatives Handeln — Diskursethik
  als Verfahren zur Begründung von Normen; Universalisierungsprinzip U; ideale
  Kommunikationsgemeinschaft als regulative Idee im Peta-Schwarm Leitstern.
Jacques Derrida (1967): De la grammatologie — Dekonstruktion als Lektürestrategie;
  Schrift als Spur und Differenz; Différance als aufgeschobene Bedeutung;
  Logozentrismus-Kritik als Grundlage der Diskursanalyse im Peta-Schwarm Leitstern. 📜🗣️
Parent: InformationsKodex (#564)
Block #561–#570: Medienwissenschaft & Kommunikationstheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .informations_kodex import (
    InformationsKodex,
    InformationsKodexGeltung,
    build_informations_kodex,
)

_WEIGHT_DELTA: dict["DiskursManifestGeltung", float] = {}
_TIER_DELTA: dict["DiskursManifestGeltung", int] = {}
_TYP_MAP: dict["DiskursManifestGeltung", "DiskursManifestTyp"] = {}
_PROZEDUR_MAP: dict["DiskursManifestGeltung", "DiskursManifestProzedur"] = {}
_GELTUNG_MAP: dict[InformationsKodexGeltung, "DiskursManifestGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        DiskursManifestGeltung.GESPERRT: 0.0,
        DiskursManifestGeltung.DISKURSIV: 0.05,
        DiskursManifestGeltung.GRUNDLEGEND_DISKURSIV: 0.1,
    })
    _TIER_DELTA.update({
        DiskursManifestGeltung.GESPERRT: 0,
        DiskursManifestGeltung.DISKURSIV: 1,
        DiskursManifestGeltung.GRUNDLEGEND_DISKURSIV: 2,
    })
    _TYP_MAP.update({
        DiskursManifestGeltung.GESPERRT: DiskursManifestTyp.SCHUTZ_DISKURS,
        DiskursManifestGeltung.DISKURSIV: DiskursManifestTyp.ORDNUNGS_DISKURS,
        DiskursManifestGeltung.GRUNDLEGEND_DISKURSIV: DiskursManifestTyp.SOUVERAENITAETS_DISKURS,
    })
    _PROZEDUR_MAP.update({
        DiskursManifestGeltung.GESPERRT: DiskursManifestProzedur.NOTPROZEDUR,
        DiskursManifestGeltung.DISKURSIV: DiskursManifestProzedur.REGELPROTOKOLL,
        DiskursManifestGeltung.GRUNDLEGEND_DISKURSIV: DiskursManifestProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        InformationsKodexGeltung.GESPERRT: DiskursManifestGeltung.GESPERRT,
        InformationsKodexGeltung.INFORMATIONELL: DiskursManifestGeltung.DISKURSIV,
        InformationsKodexGeltung.GRUNDLEGEND_INFORMATIONELL: DiskursManifestGeltung.GRUNDLEGEND_DISKURSIV,
    })


class DiskursManifestGeltung(Enum):
    GESPERRT = "gesperrt"
    DISKURSIV = "diskursiv"
    GRUNDLEGEND_DISKURSIV = "grundlegend-diskursiv"


class DiskursManifestTyp(Enum):
    SCHUTZ_DISKURS = "schutz-diskurs"
    ORDNUNGS_DISKURS = "ordnungs-diskurs"
    SOUVERAENITAETS_DISKURS = "souveraenitaets-diskurs"


class DiskursManifestProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class DiskursManifestNorm:
    diskurs_manifest_id: str
    medien_typ: DiskursManifestTyp
    prozedur: DiskursManifestProzedur
    geltung: DiskursManifestGeltung
    medien_weight: float
    medien_tier: int
    canonical: bool
    medien_ids: tuple[str, ...]
    medien_tags: tuple[str, ...]


@dataclass(frozen=True)
class DiskursManifest:
    manifest_id: str
    informations_kodex: InformationsKodex
    normen: tuple[DiskursManifestNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.diskurs_manifest_id for n in self.normen
            if n.geltung is DiskursManifestGeltung.GESPERRT
        )

    @property
    def diskursiv_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.diskurs_manifest_id for n in self.normen
            if n.geltung is DiskursManifestGeltung.DISKURSIV
        )

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.diskurs_manifest_id for n in self.normen
            if n.geltung is DiskursManifestGeltung.GRUNDLEGEND_DISKURSIV
        )

    @property
    def manifest_signal(self):
        from types import SimpleNamespace
        if any(n.geltung is DiskursManifestGeltung.GESPERRT for n in self.normen):
            return SimpleNamespace(status="manifest-gesperrt")
        elif any(n.geltung is DiskursManifestGeltung.DISKURSIV for n in self.normen):
            return SimpleNamespace(status="manifest-diskursiv")
        return SimpleNamespace(status="manifest-grundlegend-diskursiv")


_init_map()


def build_diskurs_manifest(
    informations_kodex: InformationsKodex | None = None,
    *,
    manifest_id: str = "diskurs-manifest",
) -> DiskursManifest:
    if informations_kodex is None:
        informations_kodex = build_informations_kodex(
            kodex_id=f"{manifest_id}-kodex"
        )

    normen: list[DiskursManifestNorm] = []
    for parent_norm in informations_kodex.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{manifest_id}-{parent_norm.informations_kodex_id.removeprefix(f'{informations_kodex.kodex_id}-')}"
        raw_weight = min(1.0, parent_norm.medien_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.medien_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is DiskursManifestGeltung.GRUNDLEGEND_DISKURSIV)
        normen.append(
            DiskursManifestNorm(
                diskurs_manifest_id=new_id,
                medien_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                medien_weight=new_weight,
                medien_tier=new_tier,
                canonical=is_canonical,
                medien_ids=parent_norm.medien_ids + (new_id,),
                medien_tags=parent_norm.medien_tags + (f"diskurs-manifest:{new_geltung.value}",),
            )
        )
    return DiskursManifest(
        manifest_id=manifest_id,
        informations_kodex=informations_kodex,
        normen=tuple(normen),
    )
