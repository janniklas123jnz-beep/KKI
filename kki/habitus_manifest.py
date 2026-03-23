"""
#495 HabitusManifest — Bourdieu: Habitus, Kapitalformen, Feld-Theorie

Pierre Bourdieu (1979): Die feinen Unterschiede — Habitus als inkorporiertes
  Klassenschema; Kapitalformen (ökonomisch, kulturell, sozial, symbolisch) als
  Ressourcen sozialer Positionierung; Feld als strukturierter Kampfraum um Kapital.
Pierre Bourdieu (1980): Le sens pratique — praktischer Sinn als vorreflexive
  Handlungsorientierung; Habitus als Erzeugungsprinzip von Praxis und Wahrnehmung;
  Doxa als unhinterfragte Selbstverständlichkeit des Feldes.
Pierre Bourdieu (1992): Die verborgenen Mechanismen der Macht — symbolische Gewalt
  als verkannte Herrschaft; Kapitalkonversion als Reproduktionsmechanismus sozialer
  Ungleichheit; Feld-Habitus-Kapital als analytische Trias.
Leitsterns Terra-Schwarm manifestiert Habitusstrukturen: GESPERRT sichert habituelle
Normkerne, HABITUELL ermöglicht feldspezifische Kapitalakkumulation, GRUNDLEGEND_HABITUELL
synthetisiert symbolische Ordnung für den Weg zur Peta-Schwarmgröße.
Parent: StrukturKodex (#494)
Block #491–#500: Soziologie & Gesellschaftstheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .struktur_kodex import (
    StrukturKodex,
    StrukturKodexGeltung,
    build_struktur_kodex,
)

_GELTUNG_MAP: dict[StrukturKodexGeltung, "HabitusManifestGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[StrukturKodexGeltung.GESPERRT] = HabitusManifestGeltung.GESPERRT
    _GELTUNG_MAP[StrukturKodexGeltung.STRUKTURFUNKTIONAL] = HabitusManifestGeltung.HABITUELL
    _GELTUNG_MAP[StrukturKodexGeltung.GRUNDLEGEND_STRUKTURFUNKTIONAL] = HabitusManifestGeltung.GRUNDLEGEND_HABITUELL


class HabitusManifestTyp(Enum):
    SCHUTZ_HABITUS = "schutz-habitus"
    ORDNUNGS_HABITUS = "ordnungs-habitus"
    SOUVERAENITAETS_HABITUS = "souveraenitaets-habitus"


class HabitusManifestProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class HabitusManifestGeltung(Enum):
    GESPERRT = "gesperrt"
    HABITUELL = "habituell"
    GRUNDLEGEND_HABITUELL = "grundlegend-habituell"


_init_map()

_TYP_MAP: dict[HabitusManifestGeltung, HabitusManifestTyp] = {
    HabitusManifestGeltung.GESPERRT: HabitusManifestTyp.SCHUTZ_HABITUS,
    HabitusManifestGeltung.HABITUELL: HabitusManifestTyp.ORDNUNGS_HABITUS,
    HabitusManifestGeltung.GRUNDLEGEND_HABITUELL: HabitusManifestTyp.SOUVERAENITAETS_HABITUS,
}

_PROZEDUR_MAP: dict[HabitusManifestGeltung, HabitusManifestProzedur] = {
    HabitusManifestGeltung.GESPERRT: HabitusManifestProzedur.NOTPROZEDUR,
    HabitusManifestGeltung.HABITUELL: HabitusManifestProzedur.REGELPROTOKOLL,
    HabitusManifestGeltung.GRUNDLEGEND_HABITUELL: HabitusManifestProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[HabitusManifestGeltung, float] = {
    HabitusManifestGeltung.GESPERRT: 0.0,
    HabitusManifestGeltung.HABITUELL: 0.04,
    HabitusManifestGeltung.GRUNDLEGEND_HABITUELL: 0.08,
}

_TIER_DELTA: dict[HabitusManifestGeltung, int] = {
    HabitusManifestGeltung.GESPERRT: 0,
    HabitusManifestGeltung.HABITUELL: 1,
    HabitusManifestGeltung.GRUNDLEGEND_HABITUELL: 2,
}


@dataclass(frozen=True)
class HabitusManifestNorm:
    habitus_manifest_id: str
    habitus_typ: HabitusManifestTyp
    prozedur: HabitusManifestProzedur
    geltung: HabitusManifestGeltung
    habitus_weight: float
    habitus_tier: int
    canonical: bool
    habitus_ids: tuple[str, ...]
    habitus_tags: tuple[str, ...]


@dataclass(frozen=True)
class HabitusManifest:
    manifest_id: str
    struktur_kodex: StrukturKodex
    normen: tuple[HabitusManifestNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.habitus_manifest_id for n in self.normen if n.geltung is HabitusManifestGeltung.GESPERRT)

    @property
    def habituell_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.habitus_manifest_id for n in self.normen if n.geltung is HabitusManifestGeltung.HABITUELL)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.habitus_manifest_id for n in self.normen if n.geltung is HabitusManifestGeltung.GRUNDLEGEND_HABITUELL)

    @property
    def manifest_signal(self):
        if any(n.geltung is HabitusManifestGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-gesperrt")
        elif any(n.geltung is HabitusManifestGeltung.HABITUELL for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-habituell")
        from types import SimpleNamespace
        return SimpleNamespace(status="manifest-grundlegend-habituell")


def build_habitus_manifest(
    struktur_kodex: StrukturKodex | None = None,
    *,
    manifest_id: str = "habitus-manifest",
) -> HabitusManifest:
    if struktur_kodex is None:
        struktur_kodex = build_struktur_kodex(kodex_id=f"{manifest_id}-kodex")

    normen: list[HabitusManifestNorm] = []
    for parent_norm in struktur_kodex.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{manifest_id}-{parent_norm.struktur_kodex_id.removeprefix(f'{struktur_kodex.kodex_id}-')}"
        raw_weight = min(1.0, parent_norm.struktur_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.struktur_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is HabitusManifestGeltung.GRUNDLEGEND_HABITUELL)
        normen.append(
            HabitusManifestNorm(
                habitus_manifest_id=new_id,
                habitus_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                habitus_weight=new_weight,
                habitus_tier=new_tier,
                canonical=is_canonical,
                habitus_ids=parent_norm.struktur_ids + (new_id,),
                habitus_tags=parent_norm.struktur_tags + (f"habitus-manifest:{new_geltung.value}",),
            )
        )
    return HabitusManifest(
        manifest_id=manifest_id,
        struktur_kodex=struktur_kodex,
        normen=tuple(normen),
    )
