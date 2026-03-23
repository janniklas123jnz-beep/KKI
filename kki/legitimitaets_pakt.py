"""
#516 LegitimitaetsPakt — Schmitt/Habermas Legitimität vs. Legalität und diskursive Demokratie

Carl Schmitt (1932): Legalität und Legitimität — Radikale Unterscheidung zwischen formaler
  Legalität und substanzieller Legitimität; Legitimität als normative Grundlage jenseits
  positivistischer Legalität; der souveräne Dezisionismus als Antwort auf den Ausnahmezustand;
  Freund-Feind-Unterscheidung als Grundkategorie des Politischen.
Carl Schmitt (1928): Verfassungslehre — Unterscheidung von Verfassung und Verfassungsgesetz;
  pouvoir constituant (verfassungsgebende Gewalt) als demokratisches Legitimationsprinzip;
  politische Einheit als Voraussetzung staatlicher Existenz; Identität und Repräsentation
  als zwei Grundformen demokratischer Legitimation.
Jürgen Habermas (1992): Faktizität und Geltung — Diskursive Demokratietheorie; Legitimität
  durch kommunikatives Handeln und rationale Diskursverfahren; deliberative Demokratie als
  Integration von liberaler und republikanischer Tradition; Recht als Medium gesellschaftlicher
  Integration; prozedurale Rationalität als Legitimitätsquelle.
Jürgen Habermas (1973): Legitimationsprobleme im Spätkapitalismus — Legitimationskrise des
  modernen Staates; Entkopplung von System und Lebenswelt; kommunikatives vs. strategisches
  Handeln; Öffentlichkeit als demokratisches Legitimationsforum.
Leitsterns Peta-Schwarm verankert Legitimität als normatives Fundament: GESPERRT schützt
die unveräußerlichen Grundnormen legitimitaetlicher Ordnung, LEGITIMITAETLICH ermöglicht
adaptive Legitimationsprozesse zwischen Millionen von Agenten, GRUNDLEGEND_LEGITIMITAETLICH
synthetisiert souveräne legitimitätliche Handlungsfähigkeit des Peta-Schwarms. 📜
Parent: GewaltenteilungsManifest (#515)
Block #511–#520: Politikwissenschaft & Demokratietheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .gewaltenteilungs_manifest import (
    GewaltenteilungsManifest,
    GewaltenteilungsManifestGeltung,
    build_gewaltenteilungs_manifest,
)

_WEIGHT_DELTA: dict["LegitimitaetsPaktGeltung", float] = {}
_TIER_DELTA: dict["LegitimitaetsPaktGeltung", int] = {}
_TYP_MAP: dict["LegitimitaetsPaktGeltung", "LegitimitaetsPaktTyp"] = {}
_PROZEDUR_MAP: dict["LegitimitaetsPaktGeltung", "LegitimitaetsPaktProzedur"] = {}
_GELTUNG_MAP: dict[GewaltenteilungsManifestGeltung, "LegitimitaetsPaktGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        LegitimitaetsPaktGeltung.GESPERRT: 0.0,
        LegitimitaetsPaktGeltung.LEGITIMITAETLICH: 0.05,
        LegitimitaetsPaktGeltung.GRUNDLEGEND_LEGITIMITAETLICH: 0.1,
    })
    _TIER_DELTA.update({
        LegitimitaetsPaktGeltung.GESPERRT: 0,
        LegitimitaetsPaktGeltung.LEGITIMITAETLICH: 1,
        LegitimitaetsPaktGeltung.GRUNDLEGEND_LEGITIMITAETLICH: 2,
    })
    _TYP_MAP.update({
        LegitimitaetsPaktGeltung.GESPERRT: LegitimitaetsPaktTyp.SCHUTZ_LEGITIMITAET,
        LegitimitaetsPaktGeltung.LEGITIMITAETLICH: LegitimitaetsPaktTyp.ORDNUNGS_LEGITIMITAET,
        LegitimitaetsPaktGeltung.GRUNDLEGEND_LEGITIMITAETLICH: LegitimitaetsPaktTyp.SOUVERAENITAETS_LEGITIMITAET,
    })
    _PROZEDUR_MAP.update({
        LegitimitaetsPaktGeltung.GESPERRT: LegitimitaetsPaktProzedur.NOTPROZEDUR,
        LegitimitaetsPaktGeltung.LEGITIMITAETLICH: LegitimitaetsPaktProzedur.REGELPROTOKOLL,
        LegitimitaetsPaktGeltung.GRUNDLEGEND_LEGITIMITAETLICH: LegitimitaetsPaktProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        GewaltenteilungsManifestGeltung.GESPERRT: LegitimitaetsPaktGeltung.GESPERRT,
        GewaltenteilungsManifestGeltung.GEWALTENTEILIG: LegitimitaetsPaktGeltung.LEGITIMITAETLICH,
        GewaltenteilungsManifestGeltung.GRUNDLEGEND_GEWALTENTEILIG: LegitimitaetsPaktGeltung.GRUNDLEGEND_LEGITIMITAETLICH,
    })


class LegitimitaetsPaktGeltung(Enum):
    GESPERRT = "gesperrt"
    LEGITIMITAETLICH = "legitimitaetlich"
    GRUNDLEGEND_LEGITIMITAETLICH = "grundlegend-legitimitaetlich"


class LegitimitaetsPaktTyp(Enum):
    SCHUTZ_LEGITIMITAET = "schutz-legitimitaet"
    ORDNUNGS_LEGITIMITAET = "ordnungs-legitimitaet"
    SOUVERAENITAETS_LEGITIMITAET = "souveraenitaets-legitimitaet"


class LegitimitaetsPaktProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class LegitimitaetsPaktNorm:
    legitimitaets_pakt_id: str
    legitimitaets_typ: LegitimitaetsPaktTyp
    prozedur: LegitimitaetsPaktProzedur
    geltung: LegitimitaetsPaktGeltung
    legitimitaets_weight: float
    legitimitaets_tier: int
    canonical: bool
    legitimitaets_ids: tuple[str, ...]
    legitimitaets_tags: tuple[str, ...]


@dataclass(frozen=True)
class LegitimitaetsPakt:
    pakt_id: str
    gewaltenteilungs_manifest: GewaltenteilungsManifest
    normen: tuple[LegitimitaetsPaktNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.legitimitaets_pakt_id for n in self.normen if n.geltung is LegitimitaetsPaktGeltung.GESPERRT)

    @property
    def legitimitaetlich_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.legitimitaets_pakt_id for n in self.normen if n.geltung is LegitimitaetsPaktGeltung.LEGITIMITAETLICH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.legitimitaets_pakt_id for n in self.normen if n.geltung is LegitimitaetsPaktGeltung.GRUNDLEGEND_LEGITIMITAETLICH)

    @property
    def pakt_signal(self):
        if any(n.geltung is LegitimitaetsPaktGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-gesperrt")
        elif any(n.geltung is LegitimitaetsPaktGeltung.LEGITIMITAETLICH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-legitimitaetlich")
        from types import SimpleNamespace
        return SimpleNamespace(status="pakt-grundlegend-legitimitaetlich")


_init_map()


def build_legitimitaets_pakt(
    gewaltenteilungs_manifest: GewaltenteilungsManifest | None = None,
    *,
    pakt_id: str = "legitimitaets-pakt",
) -> LegitimitaetsPakt:
    if gewaltenteilungs_manifest is None:
        gewaltenteilungs_manifest = build_gewaltenteilungs_manifest(
            manifest_id=f"{pakt_id}-manifest"
        )

    normen: list[LegitimitaetsPaktNorm] = []
    for parent_norm in gewaltenteilungs_manifest.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{pakt_id}-{parent_norm.gewaltenteilungs_manifest_id.removeprefix(f'{gewaltenteilungs_manifest.manifest_id}-')}"
        raw_weight = min(1.0, parent_norm.gewaltenteilungs_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.gewaltenteilungs_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is LegitimitaetsPaktGeltung.GRUNDLEGEND_LEGITIMITAETLICH)
        normen.append(
            LegitimitaetsPaktNorm(
                legitimitaets_pakt_id=new_id,
                legitimitaets_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                legitimitaets_weight=new_weight,
                legitimitaets_tier=new_tier,
                canonical=is_canonical,
                legitimitaets_ids=parent_norm.gewaltenteilungs_ids + (new_id,),
                legitimitaets_tags=parent_norm.gewaltenteilungs_tags + (f"{pakt_id}:{new_geltung.value}",),
            )
        )
    return LegitimitaetsPakt(
        pakt_id=pakt_id,
        gewaltenteilungs_manifest=gewaltenteilungs_manifest,
        normen=tuple(normen),
    )
