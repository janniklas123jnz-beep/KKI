"""
#546 ZeitgeschichtsPakt — Pakt der Zeitgeschichtsforschung

Hans Rothfels (1953): Zeitgeschichte als Aufgabe — Epoche der Mitlebenden als Gegenstand;
  Zeitgeschichte als Geschichte der noch Lebenden und ihrer unmittelbaren Vorgeschichte;
  methodische Herausforderungen der Nähe: Quellenknappheit, Zeugenschaft, politische Sensibilität.
Martin Broszat (1969): Der Staat Hitlers — Alltagsgeschichte und Strukturgeschichte des NS-Regimes;
  Historisierung des Nationalsozialismus als methodisch-ethische Kontroverse;
  Alltagsgeschichte als Ergänzung zur politischen Geschichte des 20. Jahrhunderts.
Reinhart Koselleck (1979): Vergangene Zukunft — Begriffsgeschichte als Methode;
  Sattelzeit als Epochenbegriff für den semantischen Wandel 1750–1850;
  Erfahrungsraum und Erwartungshorizont als Grundkategorien historischer Zeit.
Parent: AnnalesManifest (#545)
Block #541–#550: Geschichtswissenschaft & Historiographie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .annales_manifest import (
    AnnalesManifest,
    AnnalesManifestGeltung,
    build_annales_manifest,
)

_WEIGHT_DELTA: dict["ZeitgeschichtsPaktGeltung", float] = {}
_TIER_DELTA: dict["ZeitgeschichtsPaktGeltung", int] = {}
_TYP_MAP: dict["ZeitgeschichtsPaktGeltung", "ZeitgeschichtsPaktTyp"] = {}
_PROZEDUR_MAP: dict["ZeitgeschichtsPaktGeltung", "ZeitgeschichtsPaktProzedur"] = {}
_GELTUNG_MAP: dict[AnnalesManifestGeltung, "ZeitgeschichtsPaktGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        ZeitgeschichtsPaktGeltung.GESPERRT: 0.0,
        ZeitgeschichtsPaktGeltung.ZEITGESCHICHTLICH: 0.05,
        ZeitgeschichtsPaktGeltung.GRUNDLEGEND_ZEITGESCHICHTLICH: 0.1,
    })
    _TIER_DELTA.update({
        ZeitgeschichtsPaktGeltung.GESPERRT: 0,
        ZeitgeschichtsPaktGeltung.ZEITGESCHICHTLICH: 1,
        ZeitgeschichtsPaktGeltung.GRUNDLEGEND_ZEITGESCHICHTLICH: 2,
    })
    _TYP_MAP.update({
        ZeitgeschichtsPaktGeltung.GESPERRT: ZeitgeschichtsPaktTyp.SCHUTZ_ZEITGESCHICHTE,
        ZeitgeschichtsPaktGeltung.ZEITGESCHICHTLICH: ZeitgeschichtsPaktTyp.ORDNUNGS_ZEITGESCHICHTE,
        ZeitgeschichtsPaktGeltung.GRUNDLEGEND_ZEITGESCHICHTLICH: ZeitgeschichtsPaktTyp.SOUVERAENITAETS_ZEITGESCHICHTE,
    })
    _PROZEDUR_MAP.update({
        ZeitgeschichtsPaktGeltung.GESPERRT: ZeitgeschichtsPaktProzedur.NOTPROZEDUR,
        ZeitgeschichtsPaktGeltung.ZEITGESCHICHTLICH: ZeitgeschichtsPaktProzedur.REGELPROTOKOLL,
        ZeitgeschichtsPaktGeltung.GRUNDLEGEND_ZEITGESCHICHTLICH: ZeitgeschichtsPaktProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        AnnalesManifestGeltung.GESPERRT: ZeitgeschichtsPaktGeltung.GESPERRT,
        AnnalesManifestGeltung.STRUKTURGESCHICHTLICH: ZeitgeschichtsPaktGeltung.ZEITGESCHICHTLICH,
        AnnalesManifestGeltung.GRUNDLEGEND_STRUKTURGESCHICHTLICH: ZeitgeschichtsPaktGeltung.GRUNDLEGEND_ZEITGESCHICHTLICH,
    })


class ZeitgeschichtsPaktGeltung(Enum):
    GESPERRT = "gesperrt"
    ZEITGESCHICHTLICH = "zeitgeschichtlich"
    GRUNDLEGEND_ZEITGESCHICHTLICH = "grundlegend-zeitgeschichtlich"


class ZeitgeschichtsPaktTyp(Enum):
    SCHUTZ_ZEITGESCHICHTE = "schutz-zeitgeschichte"
    ORDNUNGS_ZEITGESCHICHTE = "ordnungs-zeitgeschichte"
    SOUVERAENITAETS_ZEITGESCHICHTE = "souveraenitaets-zeitgeschichte"


class ZeitgeschichtsPaktProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class ZeitgeschichtsPaktNorm:
    zeitgeschichts_pakt_id: str
    geschichts_typ: ZeitgeschichtsPaktTyp
    prozedur: ZeitgeschichtsPaktProzedur
    geltung: ZeitgeschichtsPaktGeltung
    geschichts_weight: float
    geschichts_tier: int
    canonical: bool
    geschichts_ids: tuple[str, ...]
    geschichts_tags: tuple[str, ...]


@dataclass(frozen=True)
class ZeitgeschichtsPakt:
    pakt_id: str
    annales_manifest: AnnalesManifest
    normen: tuple[ZeitgeschichtsPaktNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.zeitgeschichts_pakt_id for n in self.normen
            if n.geltung is ZeitgeschichtsPaktGeltung.GESPERRT
        )

    @property
    def zeitgeschichtlich_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.zeitgeschichts_pakt_id for n in self.normen
            if n.geltung is ZeitgeschichtsPaktGeltung.ZEITGESCHICHTLICH
        )

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.zeitgeschichts_pakt_id for n in self.normen
            if n.geltung is ZeitgeschichtsPaktGeltung.GRUNDLEGEND_ZEITGESCHICHTLICH
        )

    @property
    def pakt_signal(self):
        from types import SimpleNamespace
        if any(n.geltung is ZeitgeschichtsPaktGeltung.GESPERRT for n in self.normen):
            return SimpleNamespace(status="pakt-gesperrt")
        elif any(n.geltung is ZeitgeschichtsPaktGeltung.ZEITGESCHICHTLICH for n in self.normen):
            return SimpleNamespace(status="pakt-zeitgeschichtlich")
        return SimpleNamespace(status="pakt-grundlegend-zeitgeschichtlich")


_init_map()


def build_zeitgeschichts_pakt(
    annales_manifest: AnnalesManifest | None = None,
    *,
    pakt_id: str = "zeitgeschichts-pakt",
) -> ZeitgeschichtsPakt:
    if annales_manifest is None:
        annales_manifest = build_annales_manifest(manifest_id=f"{pakt_id}-manifest")
    normen: list[ZeitgeschichtsPaktNorm] = []
    for parent_norm in annales_manifest.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{pakt_id}-{parent_norm.annales_manifest_id.removeprefix(f'{annales_manifest.manifest_id}-')}"
        raw_weight = min(1.0, parent_norm.geschichts_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.geschichts_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is ZeitgeschichtsPaktGeltung.GRUNDLEGEND_ZEITGESCHICHTLICH)
        normen.append(ZeitgeschichtsPaktNorm(
            zeitgeschichts_pakt_id=new_id,
            geschichts_typ=_TYP_MAP[new_geltung],
            prozedur=_PROZEDUR_MAP[new_geltung],
            geltung=new_geltung,
            geschichts_weight=new_weight,
            geschichts_tier=new_tier,
            canonical=is_canonical,
            geschichts_ids=parent_norm.geschichts_ids + (new_id,),
            geschichts_tags=parent_norm.geschichts_tags + (f"zeitgeschichts-pakt:{new_geltung.value}",),
        ))
    return ZeitgeschichtsPakt(
        pakt_id=pakt_id,
        annales_manifest=annales_manifest,
        normen=tuple(normen),
    )
