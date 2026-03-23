"""
#536 RechtssoziologiePakt — Rechtssoziologie & Recht als soziales System

Max Weber (1922): Wirtschaft und Gesellschaft — Rechtssoziologie; Formales und materiales
  Recht; Legitimität durch Legalität; Rationalisierung des Rechts als Merkmal der Moderne;
  Bürokratie und Rechtsordnung als Herrschaftsformen; Wertrationalität vs. Zweckrationalität.
Niklas Luhmann (1993): Das Recht der Gesellschaft — Recht als autopoietisches soziales System;
  Selbstreferenz und operative Geschlossenheit; Recht/Unrecht als binärer Code; Positivierung
  des Rechts; Rechtssystem und Gesellschaftssystem als strukturell gekoppelte Systeme.
Pierre Bourdieu (1987): The Force of Law / Das juristische Feld — Recht als soziales Feld
  mit eigenem Kapital; juridisches Feld als Kampf um Deutungshoheit; Habitus der Juristen;
  symbolische Gewalt des Rechts; Recht als Instrument sozialer Reproduktion.
Leitsterns RechtssoziologiePakt: Soziale Einbettung des Rechts — GESPERRT sichert
rechtssoziologische Grundstrukturen, RECHTSSOZIOLOGISCH kodiert adaptive Systemreflexion,
GRUNDLEGEND_RECHTSSOZIOLOGISCH synthetisiert souveräne Rechtssoziologie. ⚖️
Parent: RechtsphilosophieManifest (#535)
Block #531–#540: Rechtswissenschaft & Jurisprudenz
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .rechtsphilosophie_manifest import (
    RechtsphilosophieManifest,
    RechtsphilosophieManifestGeltung,
    build_rechtsphilosophie_manifest,
)

_WEIGHT_DELTA: dict["RechtssoziologiePaktGeltung", float] = {}
_TIER_DELTA: dict["RechtssoziologiePaktGeltung", int] = {}
_TYP_MAP: dict["RechtssoziologiePaktGeltung", "RechtssoziologiePaktTyp"] = {}
_PROZEDUR_MAP: dict["RechtssoziologiePaktGeltung", "RechtssoziologiePaktProzedur"] = {}
_GELTUNG_MAP: dict[RechtsphilosophieManifestGeltung, "RechtssoziologiePaktGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        RechtssoziologiePaktGeltung.GESPERRT: 0.0,
        RechtssoziologiePaktGeltung.RECHTSSOZIOLOGISCH: 0.05,
        RechtssoziologiePaktGeltung.GRUNDLEGEND_RECHTSSOZIOLOGISCH: 0.1,
    })
    _TIER_DELTA.update({
        RechtssoziologiePaktGeltung.GESPERRT: 0,
        RechtssoziologiePaktGeltung.RECHTSSOZIOLOGISCH: 1,
        RechtssoziologiePaktGeltung.GRUNDLEGEND_RECHTSSOZIOLOGISCH: 2,
    })
    _TYP_MAP.update({
        RechtssoziologiePaktGeltung.GESPERRT: RechtssoziologiePaktTyp.SCHUTZ_RECHTSSOZIOLOGIE,
        RechtssoziologiePaktGeltung.RECHTSSOZIOLOGISCH: RechtssoziologiePaktTyp.ORDNUNGS_RECHTSSOZIOLOGIE,
        RechtssoziologiePaktGeltung.GRUNDLEGEND_RECHTSSOZIOLOGISCH: RechtssoziologiePaktTyp.SOUVERAENITAETS_RECHTSSOZIOLOGIE,
    })
    _PROZEDUR_MAP.update({
        RechtssoziologiePaktGeltung.GESPERRT: RechtssoziologiePaktProzedur.NOTPROZEDUR,
        RechtssoziologiePaktGeltung.RECHTSSOZIOLOGISCH: RechtssoziologiePaktProzedur.REGELPROTOKOLL,
        RechtssoziologiePaktGeltung.GRUNDLEGEND_RECHTSSOZIOLOGISCH: RechtssoziologiePaktProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        RechtsphilosophieManifestGeltung.GESPERRT: RechtssoziologiePaktGeltung.GESPERRT,
        RechtsphilosophieManifestGeltung.RECHTSPHILOSOPHISCH: RechtssoziologiePaktGeltung.RECHTSSOZIOLOGISCH,
        RechtsphilosophieManifestGeltung.GRUNDLEGEND_RECHTSPHILOSOPHISCH: RechtssoziologiePaktGeltung.GRUNDLEGEND_RECHTSSOZIOLOGISCH,
    })


class RechtssoziologiePaktGeltung(Enum):
    GESPERRT = "gesperrt"
    RECHTSSOZIOLOGISCH = "rechtssoziologisch"
    GRUNDLEGEND_RECHTSSOZIOLOGISCH = "grundlegend-rechtssoziologisch"


class RechtssoziologiePaktTyp(Enum):
    SCHUTZ_RECHTSSOZIOLOGIE = "schutz-rechtssoziologie"
    ORDNUNGS_RECHTSSOZIOLOGIE = "ordnungs-rechtssoziologie"
    SOUVERAENITAETS_RECHTSSOZIOLOGIE = "souveraenitaets-rechtssoziologie"


class RechtssoziologiePaktProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class RechtssoziologiePaktNorm:
    rechtssoziologie_pakt_id: str
    rechtssoziologie_typ: RechtssoziologiePaktTyp
    prozedur: RechtssoziologiePaktProzedur
    geltung: RechtssoziologiePaktGeltung
    rechtssoziologie_weight: float
    rechtssoziologie_tier: int
    canonical: bool
    rechtssoziologie_ids: tuple[str, ...]
    rechtssoziologie_tags: tuple[str, ...]


@dataclass(frozen=True)
class RechtssoziologiePakt:
    pakt_id: str
    rechtsphilosophie_manifest: RechtsphilosophieManifest
    normen: tuple[RechtssoziologiePaktNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.rechtssoziologie_pakt_id for n in self.normen if n.geltung is RechtssoziologiePaktGeltung.GESPERRT)

    @property
    def rechtssoziologisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.rechtssoziologie_pakt_id for n in self.normen if n.geltung is RechtssoziologiePaktGeltung.RECHTSSOZIOLOGISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.rechtssoziologie_pakt_id for n in self.normen if n.geltung is RechtssoziologiePaktGeltung.GRUNDLEGEND_RECHTSSOZIOLOGISCH)

    @property
    def pakt_signal(self):
        if any(n.geltung is RechtssoziologiePaktGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-gesperrt")
        elif any(n.geltung is RechtssoziologiePaktGeltung.RECHTSSOZIOLOGISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-rechtssoziologisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="pakt-grundlegend-rechtssoziologisch")


_init_map()


def build_rechtssoziologie_pakt(
    rechtsphilosophie_manifest: RechtsphilosophieManifest | None = None,
    *,
    pakt_id: str = "rechtssoziologie-pakt",
) -> RechtssoziologiePakt:
    if rechtsphilosophie_manifest is None:
        rechtsphilosophie_manifest = build_rechtsphilosophie_manifest(
            manifest_id=f"{pakt_id}-manifest"
        )

    normen: list[RechtssoziologiePaktNorm] = []
    for parent_norm in rechtsphilosophie_manifest.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{pakt_id}-{parent_norm.rechtsphilosophie_manifest_id.removeprefix(f'{rechtsphilosophie_manifest.manifest_id}-')}"
        raw_weight = min(1.0, parent_norm.rechtsphilosophie_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.rechtsphilosophie_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is RechtssoziologiePaktGeltung.GRUNDLEGEND_RECHTSSOZIOLOGISCH)
        normen.append(
            RechtssoziologiePaktNorm(
                rechtssoziologie_pakt_id=new_id,
                rechtssoziologie_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                rechtssoziologie_weight=new_weight,
                rechtssoziologie_tier=new_tier,
                canonical=is_canonical,
                rechtssoziologie_ids=parent_norm.rechtsphilosophie_ids + (new_id,),
                rechtssoziologie_tags=parent_norm.rechtsphilosophie_tags + (f"rechtssoziologie-pakt:{new_geltung.value}",),
            )
        )
    return RechtssoziologiePakt(
        pakt_id=pakt_id,
        rechtsphilosophie_manifest=rechtsphilosophie_manifest,
        normen=tuple(normen),
    )
