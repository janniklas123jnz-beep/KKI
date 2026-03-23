"""
#556 KulturgedaechnisPakt — Kulturelles Gedächtnis & kollektive Erinnerung

Jan Assmann (1992): Das kulturelle Gedächtnis — kulturelles Gedächtnis als Fundament:
  Unterscheidung von kommunikativem (ca. 80 Jahre) und kulturellem Gedächtnis (Jahrtausende);
  Erinnerungsfiguren als kodierte und institutionalisierte Vergangenheitsbezüge; Kanon und
  Archiv; kulturelle Identität als Produkt selektiver Erinnerung und Vergessen.
Maurice Halbwachs (1925): Les cadres sociaux de la mémoire — kollektives Gedächtnis:
  Erinnerung als soziales Konstrukt; das Individuum erinnert stets als Mitglied sozialer
  Gruppen; cadres sociaux (soziale Rahmen) als Strukturen kollektiver Gedächtnisbildung;
  jede Gruppe konstituiert sich durch ihre spezifische Erinnerungsgemeinschaft.
Aleida Assmann (1999): Erinnerungsräume — Formen und Wandlungen des kulturellen Gedächtnisses:
  Funktions- und Speichergedächtnis als komplementäre Modi; Erinnerungsräume (Körper, Ort,
  Bild, Schrift); Trauma und Tabu im kulturellen Gedächtnis; nationale Erinnerungskulturen
  im Spannungsfeld von Kanonisierung, Verdrängung und Rehabilitierung.

Leitsterns KulturgedaechnisPakt: GESPERRT schützt gedächtniskulturelle Grundstrukturen,
KULTURGEDAECHTNISHAFT kodiert adaptive Erinnerungspraxis, GRUNDLEGEND_KULTURGEDAECHTNISHAFT
synthetisiert den vollen kulturgedächtnistheoretischen Erkenntnisanspruch des Peta-Schwarms Leitstern. 📜
Parent: KultursystemeManifest (#555)
Block #551–#560: Kulturwissenschaften & Kulturanthropologie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import SimpleNamespace

from .kultursysteme_manifest import (
    KultursystemeManifest,
    KultursystemeManifestGeltung,
    build_kultursysteme_manifest,
)

_WEIGHT_DELTA: dict["KulturgedaechnisPaktGeltung", float] = {}
_TIER_DELTA: dict["KulturgedaechnisPaktGeltung", int] = {}
_TYP_MAP: dict["KulturgedaechnisPaktGeltung", "KulturgedaechnisPaktTyp"] = {}
_PROZEDUR_MAP: dict["KulturgedaechnisPaktGeltung", "KulturgedaechnisPaktProzedur"] = {}
_GELTUNG_MAP: dict[KultursystemeManifestGeltung, "KulturgedaechnisPaktGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        KulturgedaechnisPaktGeltung.GESPERRT: 0.0,
        KulturgedaechnisPaktGeltung.KULTURGEDAECHTNISHAFT: 0.05,
        KulturgedaechnisPaktGeltung.GRUNDLEGEND_KULTURGEDAECHTNISHAFT: 0.1,
    })
    _TIER_DELTA.update({
        KulturgedaechnisPaktGeltung.GESPERRT: 0,
        KulturgedaechnisPaktGeltung.KULTURGEDAECHTNISHAFT: 1,
        KulturgedaechnisPaktGeltung.GRUNDLEGEND_KULTURGEDAECHTNISHAFT: 2,
    })
    _TYP_MAP.update({
        KulturgedaechnisPaktGeltung.GESPERRT: KulturgedaechnisPaktTyp.SCHUTZ_KULTURGEDAECHTNIS,
        KulturgedaechnisPaktGeltung.KULTURGEDAECHTNISHAFT: KulturgedaechnisPaktTyp.ORDNUNGS_KULTURGEDAECHTNIS,
        KulturgedaechnisPaktGeltung.GRUNDLEGEND_KULTURGEDAECHTNISHAFT: KulturgedaechnisPaktTyp.SOUVERAENITAETS_KULTURGEDAECHTNIS,
    })
    _PROZEDUR_MAP.update({
        KulturgedaechnisPaktGeltung.GESPERRT: KulturgedaechnisPaktProzedur.NOTPROZEDUR,
        KulturgedaechnisPaktGeltung.KULTURGEDAECHTNISHAFT: KulturgedaechnisPaktProzedur.REGELPROTOKOLL,
        KulturgedaechnisPaktGeltung.GRUNDLEGEND_KULTURGEDAECHTNISHAFT: KulturgedaechnisPaktProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        KultursystemeManifestGeltung.GESPERRT: KulturgedaechnisPaktGeltung.GESPERRT,
        KultursystemeManifestGeltung.KULTURSYSTEMISCH: KulturgedaechnisPaktGeltung.KULTURGEDAECHTNISHAFT,
        KultursystemeManifestGeltung.GRUNDLEGEND_KULTURSYSTEMISCH: KulturgedaechnisPaktGeltung.GRUNDLEGEND_KULTURGEDAECHTNISHAFT,
    })


class KulturgedaechnisPaktGeltung(Enum):
    GESPERRT = "gesperrt"
    KULTURGEDAECHTNISHAFT = "kulturgedaechtnishaft"
    GRUNDLEGEND_KULTURGEDAECHTNISHAFT = "grundlegend-kulturgedaechtnishaft"


class KulturgedaechnisPaktTyp(Enum):
    SCHUTZ_KULTURGEDAECHTNIS = "schutz-kulturgedaechtnis"
    ORDNUNGS_KULTURGEDAECHTNIS = "ordnungs-kulturgedaechtnis"
    SOUVERAENITAETS_KULTURGEDAECHTNIS = "souveraenitaets-kulturgedaechtnis"


class KulturgedaechnisPaktProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class KulturgedaechnisPaktNorm:
    kulturgedaechtnis_pakt_id: str
    kultur_typ: KulturgedaechnisPaktTyp
    prozedur: KulturgedaechnisPaktProzedur
    geltung: KulturgedaechnisPaktGeltung
    kultur_weight: float
    kultur_tier: int
    canonical: bool
    kultur_ids: tuple[str, ...]
    kultur_tags: tuple[str, ...]


@dataclass(frozen=True)
class KulturgedaechnisPakt:
    pakt_id: str
    kultursysteme_manifest: KultursystemeManifest
    normen: tuple[KulturgedaechnisPaktNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.kulturgedaechtnis_pakt_id
            for n in self.normen
            if n.geltung is KulturgedaechnisPaktGeltung.GESPERRT
        )

    @property
    def kulturgedaechtnishaft_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.kulturgedaechtnis_pakt_id
            for n in self.normen
            if n.geltung is KulturgedaechnisPaktGeltung.KULTURGEDAECHTNISHAFT
        )

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.kulturgedaechtnis_pakt_id
            for n in self.normen
            if n.geltung is KulturgedaechnisPaktGeltung.GRUNDLEGEND_KULTURGEDAECHTNISHAFT
        )

    @property
    def pakt_signal(self) -> SimpleNamespace:
        if any(n.geltung is KulturgedaechnisPaktGeltung.GESPERRT for n in self.normen):
            return SimpleNamespace(status="pakt-gesperrt")
        elif any(n.geltung is KulturgedaechnisPaktGeltung.KULTURGEDAECHTNISHAFT for n in self.normen):
            return SimpleNamespace(status="pakt-kulturgedaechtnishaft")
        return SimpleNamespace(status="pakt-grundlegend-kulturgedaechtnishaft")


_init_map()


def build_kulturgedaechtnis_pakt(
    kultursysteme_manifest: KultursystemeManifest | None = None,
    *,
    pakt_id: str = "kulturgedaechtnis-pakt",
) -> KulturgedaechnisPakt:
    if kultursysteme_manifest is None:
        kultursysteme_manifest = build_kultursysteme_manifest(manifest_id=f"{pakt_id}-manifest")

    normen: list[KulturgedaechnisPaktNorm] = []
    for parent_norm in kultursysteme_manifest.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{pakt_id}-{parent_norm.kultursysteme_manifest_id.removeprefix(f'{kultursysteme_manifest.manifest_id}-')}"
        raw_weight = min(1.0, parent_norm.kultur_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kultur_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (
            new_geltung is KulturgedaechnisPaktGeltung.GRUNDLEGEND_KULTURGEDAECHTNISHAFT
        )
        normen.append(
            KulturgedaechnisPaktNorm(
                kulturgedaechtnis_pakt_id=new_id,
                kultur_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kultur_weight=new_weight,
                kultur_tier=new_tier,
                canonical=is_canonical,
                kultur_ids=parent_norm.kultur_ids + (new_id,),
                kultur_tags=parent_norm.kultur_tags + (f"kulturgedaechtnis-pakt:{new_geltung.value}",),
            )
        )
    return KulturgedaechnisPakt(
        pakt_id=pakt_id,
        kultursysteme_manifest=kultursysteme_manifest,
        normen=tuple(normen),
    )
