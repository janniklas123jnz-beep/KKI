"""
#496 StrukturierungsPakt — Giddens: Strukturationstheorie; Beck: Risikogesellschaft

Anthony Giddens (1984): Die Konstitution der Gesellschaft — Strukturationstheorie als
  Überwindung des Dualismus von Struktur und Handeln; Dualität der Struktur (Struktur
  als Medium und Ergebnis sozialer Praxis); Rekursivität als Grundmerkmal sozialer
  Reproduktion; Zeitgeographie und Routinisierung als Stabilisatoren.
Anthony Giddens (1990): Konsequenzen der Moderne — Reflexive Modernisierung als
  Selbstkonfrontation der Moderne mit ihren eigenen Folgen; Enttraditionalisierung
  und Globalisierung als Signaturen der Spätmoderne.
Ulrich Beck (1986): Risikogesellschaft — reflexive Modernisierung als Risikoproduktion;
  Subpolitik als neue Form politischer Partizipation jenseits institutioneller Kanäle;
  Individualisierung als struktureller Zwang zur Selbstbiographie.
Leitsterns Terra-Schwarm paktiert Strukturierungsdynamiken: GESPERRT sichert
strukturierende Normkerne, STRUKTURIEREND ermöglicht reflexive Handlungs-Struktur-
Vermittlung, GRUNDLEGEND_STRUKTURIEREND synthetisiert rekursive Reproduktionslogik
für den Weg zur Peta-Schwarmgröße.
Parent: HabitusManifest (#495)
Block #491–#500: Soziologie & Gesellschaftstheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .habitus_manifest import (
    HabitusManifest,
    HabitusManifestGeltung,
    build_habitus_manifest,
)

_GELTUNG_MAP: dict[HabitusManifestGeltung, "StrukturierungsPaktGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[HabitusManifestGeltung.GESPERRT] = StrukturierungsPaktGeltung.GESPERRT
    _GELTUNG_MAP[HabitusManifestGeltung.HABITUELL] = StrukturierungsPaktGeltung.STRUKTURIEREND
    _GELTUNG_MAP[HabitusManifestGeltung.GRUNDLEGEND_HABITUELL] = StrukturierungsPaktGeltung.GRUNDLEGEND_STRUKTURIEREND


class StrukturierungsPaktTyp(Enum):
    SCHUTZ_STRUKTURIERUNG = "schutz-strukturierung"
    ORDNUNGS_STRUKTURIERUNG = "ordnungs-strukturierung"
    SOUVERAENITAETS_STRUKTURIERUNG = "souveraenitaets-strukturierung"


class StrukturierungsPaktProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class StrukturierungsPaktGeltung(Enum):
    GESPERRT = "gesperrt"
    STRUKTURIEREND = "strukturierend"
    GRUNDLEGEND_STRUKTURIEREND = "grundlegend-strukturierend"


_init_map()

_TYP_MAP: dict[StrukturierungsPaktGeltung, StrukturierungsPaktTyp] = {
    StrukturierungsPaktGeltung.GESPERRT: StrukturierungsPaktTyp.SCHUTZ_STRUKTURIERUNG,
    StrukturierungsPaktGeltung.STRUKTURIEREND: StrukturierungsPaktTyp.ORDNUNGS_STRUKTURIERUNG,
    StrukturierungsPaktGeltung.GRUNDLEGEND_STRUKTURIEREND: StrukturierungsPaktTyp.SOUVERAENITAETS_STRUKTURIERUNG,
}

_PROZEDUR_MAP: dict[StrukturierungsPaktGeltung, StrukturierungsPaktProzedur] = {
    StrukturierungsPaktGeltung.GESPERRT: StrukturierungsPaktProzedur.NOTPROZEDUR,
    StrukturierungsPaktGeltung.STRUKTURIEREND: StrukturierungsPaktProzedur.REGELPROTOKOLL,
    StrukturierungsPaktGeltung.GRUNDLEGEND_STRUKTURIEREND: StrukturierungsPaktProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[StrukturierungsPaktGeltung, float] = {
    StrukturierungsPaktGeltung.GESPERRT: 0.0,
    StrukturierungsPaktGeltung.STRUKTURIEREND: 0.04,
    StrukturierungsPaktGeltung.GRUNDLEGEND_STRUKTURIEREND: 0.08,
}

_TIER_DELTA: dict[StrukturierungsPaktGeltung, int] = {
    StrukturierungsPaktGeltung.GESPERRT: 0,
    StrukturierungsPaktGeltung.STRUKTURIEREND: 1,
    StrukturierungsPaktGeltung.GRUNDLEGEND_STRUKTURIEREND: 2,
}


@dataclass(frozen=True)
class StrukturierungsPaktNorm:
    strukturierungs_pakt_id: str
    strukturierungs_typ: StrukturierungsPaktTyp
    prozedur: StrukturierungsPaktProzedur
    geltung: StrukturierungsPaktGeltung
    strukturierungs_weight: float
    strukturierungs_tier: int
    canonical: bool
    strukturierungs_ids: tuple[str, ...]
    strukturierungs_tags: tuple[str, ...]


@dataclass(frozen=True)
class StrukturierungsPakt:
    pakt_id: str
    habitus_manifest: HabitusManifest
    normen: tuple[StrukturierungsPaktNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.strukturierungs_pakt_id for n in self.normen if n.geltung is StrukturierungsPaktGeltung.GESPERRT)

    @property
    def strukturierend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.strukturierungs_pakt_id for n in self.normen if n.geltung is StrukturierungsPaktGeltung.STRUKTURIEREND)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.strukturierungs_pakt_id for n in self.normen if n.geltung is StrukturierungsPaktGeltung.GRUNDLEGEND_STRUKTURIEREND)

    @property
    def pakt_signal(self):
        if any(n.geltung is StrukturierungsPaktGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-gesperrt")
        elif any(n.geltung is StrukturierungsPaktGeltung.STRUKTURIEREND for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-strukturierend")
        from types import SimpleNamespace
        return SimpleNamespace(status="pakt-grundlegend-strukturierend")


def build_strukturierungs_pakt(
    habitus_manifest: HabitusManifest | None = None,
    *,
    pakt_id: str = "strukturierungs-pakt",
) -> StrukturierungsPakt:
    if habitus_manifest is None:
        habitus_manifest = build_habitus_manifest(manifest_id=f"{pakt_id}-manifest")

    normen: list[StrukturierungsPaktNorm] = []
    for parent_norm in habitus_manifest.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{pakt_id}-{parent_norm.habitus_manifest_id.removeprefix(f'{habitus_manifest.manifest_id}-')}"
        raw_weight = min(1.0, parent_norm.habitus_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.habitus_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is StrukturierungsPaktGeltung.GRUNDLEGEND_STRUKTURIEREND)
        normen.append(
            StrukturierungsPaktNorm(
                strukturierungs_pakt_id=new_id,
                strukturierungs_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                strukturierungs_weight=new_weight,
                strukturierungs_tier=new_tier,
                canonical=is_canonical,
                strukturierungs_ids=parent_norm.habitus_ids + (new_id,),
                strukturierungs_tags=parent_norm.habitus_tags + (f"strukturierungs-pakt:{new_geltung.value}",),
            )
        )
    return StrukturierungsPakt(
        pakt_id=pakt_id,
        habitus_manifest=habitus_manifest,
        normen=tuple(normen),
    )
