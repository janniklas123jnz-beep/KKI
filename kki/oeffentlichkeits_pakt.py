"""
#566 OeffentlichkeitsPakt — Habermas/Arendt/Dewey Öffentlichkeitstheorie Pakt

Jürgen Habermas (1962): Strukturwandel der Öffentlichkeit — bürgerliche Öffentlichkeit
  als Sphäre zwischen Staat und Privatheit; räsonnierende Öffentlichkeit als demokratisches
  Prinzip; Verfall der Öffentlichkeit durch Medienkommerzialisierung; deliberative
  Demokratie als normatives Modell im Peta-Schwarm Leitstern.
Hannah Arendt (1958): The Human Condition — öffentlicher Raum als Ort des Erscheinens;
  Handeln als politische Praxis in der Pluralität; Macht als kollektives Handeln;
  öffentliche Freiheit als Teilhabe am gemeinsamen Welt-Raum im Peta-Schwarm Leitstern.
John Dewey (1927): The Public and Its Problems — Öffentlichkeit als kommunikative
  Gemeinschaft; demokratische Kommunikation als soziale Intelligenz; partizipative
  Demokratie als lernende Gesellschaft im Peta-Schwarm Leitstern. 🏛️🌐
Parent: DiskursManifest (#565)
Block #561–#570: Medienwissenschaft & Kommunikationstheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .medien_diskurs_manifest import (
    DiskursManifest,
    DiskursManifestGeltung,
    build_diskurs_manifest,
)

_WEIGHT_DELTA: dict["OeffentlichkeitsPaktGeltung", float] = {}
_TIER_DELTA: dict["OeffentlichkeitsPaktGeltung", int] = {}
_TYP_MAP: dict["OeffentlichkeitsPaktGeltung", "OeffentlichkeitsPaktTyp"] = {}
_PROZEDUR_MAP: dict["OeffentlichkeitsPaktGeltung", "OeffentlichkeitsPaktProzedur"] = {}
_GELTUNG_MAP: dict[DiskursManifestGeltung, "OeffentlichkeitsPaktGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        OeffentlichkeitsPaktGeltung.GESPERRT: 0.0,
        OeffentlichkeitsPaktGeltung.OEFFENTLICH: 0.05,
        OeffentlichkeitsPaktGeltung.GRUNDLEGEND_OEFFENTLICH: 0.1,
    })
    _TIER_DELTA.update({
        OeffentlichkeitsPaktGeltung.GESPERRT: 0,
        OeffentlichkeitsPaktGeltung.OEFFENTLICH: 1,
        OeffentlichkeitsPaktGeltung.GRUNDLEGEND_OEFFENTLICH: 2,
    })
    _TYP_MAP.update({
        OeffentlichkeitsPaktGeltung.GESPERRT: OeffentlichkeitsPaktTyp.SCHUTZ_OEFFENTLICHKEIT,
        OeffentlichkeitsPaktGeltung.OEFFENTLICH: OeffentlichkeitsPaktTyp.ORDNUNGS_OEFFENTLICHKEIT,
        OeffentlichkeitsPaktGeltung.GRUNDLEGEND_OEFFENTLICH: OeffentlichkeitsPaktTyp.SOUVERAENITAETS_OEFFENTLICHKEIT,
    })
    _PROZEDUR_MAP.update({
        OeffentlichkeitsPaktGeltung.GESPERRT: OeffentlichkeitsPaktProzedur.NOTPROZEDUR,
        OeffentlichkeitsPaktGeltung.OEFFENTLICH: OeffentlichkeitsPaktProzedur.REGELPROTOKOLL,
        OeffentlichkeitsPaktGeltung.GRUNDLEGEND_OEFFENTLICH: OeffentlichkeitsPaktProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        DiskursManifestGeltung.GESPERRT: OeffentlichkeitsPaktGeltung.GESPERRT,
        DiskursManifestGeltung.DISKURSIV: OeffentlichkeitsPaktGeltung.OEFFENTLICH,
        DiskursManifestGeltung.GRUNDLEGEND_DISKURSIV: OeffentlichkeitsPaktGeltung.GRUNDLEGEND_OEFFENTLICH,
    })


class OeffentlichkeitsPaktGeltung(Enum):
    GESPERRT = "gesperrt"
    OEFFENTLICH = "oeffentlich"
    GRUNDLEGEND_OEFFENTLICH = "grundlegend-oeffentlich"


class OeffentlichkeitsPaktTyp(Enum):
    SCHUTZ_OEFFENTLICHKEIT = "schutz-oeffentlichkeit"
    ORDNUNGS_OEFFENTLICHKEIT = "ordnungs-oeffentlichkeit"
    SOUVERAENITAETS_OEFFENTLICHKEIT = "souveraenitaets-oeffentlichkeit"


class OeffentlichkeitsPaktProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class OeffentlichkeitsPaktNorm:
    oeffentlichkeits_pakt_id: str
    medien_typ: OeffentlichkeitsPaktTyp
    prozedur: OeffentlichkeitsPaktProzedur
    geltung: OeffentlichkeitsPaktGeltung
    medien_weight: float
    medien_tier: int
    canonical: bool
    medien_ids: tuple[str, ...]
    medien_tags: tuple[str, ...]


@dataclass(frozen=True)
class OeffentlichkeitsPakt:
    pakt_id: str
    diskurs_manifest: DiskursManifest
    normen: tuple[OeffentlichkeitsPaktNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.oeffentlichkeits_pakt_id for n in self.normen
            if n.geltung is OeffentlichkeitsPaktGeltung.GESPERRT
        )

    @property
    def oeffentlich_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.oeffentlichkeits_pakt_id for n in self.normen
            if n.geltung is OeffentlichkeitsPaktGeltung.OEFFENTLICH
        )

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.oeffentlichkeits_pakt_id for n in self.normen
            if n.geltung is OeffentlichkeitsPaktGeltung.GRUNDLEGEND_OEFFENTLICH
        )

    @property
    def pakt_signal(self):
        from types import SimpleNamespace
        if any(n.geltung is OeffentlichkeitsPaktGeltung.GESPERRT for n in self.normen):
            return SimpleNamespace(status="pakt-gesperrt")
        elif any(n.geltung is OeffentlichkeitsPaktGeltung.OEFFENTLICH for n in self.normen):
            return SimpleNamespace(status="pakt-oeffentlich")
        return SimpleNamespace(status="pakt-grundlegend-oeffentlich")


_init_map()


def build_oeffentlichkeits_pakt(
    diskurs_manifest: DiskursManifest | None = None,
    *,
    pakt_id: str = "oeffentlichkeits-pakt",
) -> OeffentlichkeitsPakt:
    if diskurs_manifest is None:
        diskurs_manifest = build_diskurs_manifest(
            manifest_id=f"{pakt_id}-manifest"
        )

    normen: list[OeffentlichkeitsPaktNorm] = []
    for parent_norm in diskurs_manifest.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{pakt_id}-{parent_norm.diskurs_manifest_id.removeprefix(f'{diskurs_manifest.manifest_id}-')}"
        raw_weight = min(1.0, parent_norm.medien_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.medien_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is OeffentlichkeitsPaktGeltung.GRUNDLEGEND_OEFFENTLICH)
        normen.append(
            OeffentlichkeitsPaktNorm(
                oeffentlichkeits_pakt_id=new_id,
                medien_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                medien_weight=new_weight,
                medien_tier=new_tier,
                canonical=is_canonical,
                medien_ids=parent_norm.medien_ids + (new_id,),
                medien_tags=parent_norm.medien_tags + (f"oeffentlichkeits-pakt:{new_geltung.value}",),
            )
        )
    return OeffentlichkeitsPakt(
        pakt_id=pakt_id,
        diskurs_manifest=diskurs_manifest,
        normen=tuple(normen),
    )
