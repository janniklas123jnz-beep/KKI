"""
#571 KunstFeld — Kant/Hegel/Adorno Kunstwissenschaft Feld

Immanuel Kant (1790): Kritik der Urteilskraft — ästhetisches Urteil als
  interesseloses Wohlgefallen; Schönheit als Symbol der Sittlichkeit; das Erhabene
  als Grenzerfahrung der Vernunft; Gemeinsinn als intersubjektive Bedingung; Kunst
  als Spiel der Erkenntniskräfte im Peta-Schwarm Leitstern.
Georg Wilhelm Friedrich Hegel (1835): Vorlesungen über die Ästhetik — Kunst als
  sinnliches Scheinen der Idee; symbolische/klassische/romantische Kunstform als
  Entwicklungsstufen; Tod der Kunst als Aufhebung ins Denken; Schönheit als
  Wahrheit in äußerer Erscheinung; Geist als Substanz ästhetischer Erkenntnis
  Leitsterns.
Theodor W. Adorno (1970): Ästhetische Theorie — Wahrheitsgehalt des Kunstwerks
  als immanente Kritik; Rätselcharakter der Kunst als negativer Erkenntnismoment;
  Mimesis als nicht-begriffliches Erkennen; Dialektik von Autonomie und Engagement;
  Kunst als gesellschaftliche Antithese im Peta-Schwarm Leitstern. 🎨🖼️
Parent: MedienVerfassung (#570)
Block #571–#580: Kunstwissenschaft & Ästhetik
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .medien_verfassung import (
    MedienVerfassung,
    MedienVerfassungsGeltung,
    build_medien_verfassung,
)

_WEIGHT_DELTA: dict["KunstFeldGeltung", float] = {}
_TIER_DELTA: dict["KunstFeldGeltung", int] = {}
_TYP_MAP: dict["KunstFeldGeltung", "KunstFeldTyp"] = {}
_PROZEDUR_MAP: dict["KunstFeldGeltung", "KunstFeldProzedur"] = {}
_GELTUNG_MAP: dict[MedienVerfassungsGeltung, "KunstFeldGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        KunstFeldGeltung.GESPERRT: 0.0,
        KunstFeldGeltung.AESTHETISCH_SOUVERAEN: 0.05,
        KunstFeldGeltung.GRUNDLEGEND_AESTHETISCH_SOUVERAEN: 0.1,
    })
    _TIER_DELTA.update({
        KunstFeldGeltung.GESPERRT: 0,
        KunstFeldGeltung.AESTHETISCH_SOUVERAEN: 1,
        KunstFeldGeltung.GRUNDLEGEND_AESTHETISCH_SOUVERAEN: 2,
    })
    _TYP_MAP.update({
        KunstFeldGeltung.GESPERRT: KunstFeldTyp.SCHUTZ_KUNSTFELD,
        KunstFeldGeltung.AESTHETISCH_SOUVERAEN: KunstFeldTyp.ORDNUNGS_KUNSTFELD,
        KunstFeldGeltung.GRUNDLEGEND_AESTHETISCH_SOUVERAEN: KunstFeldTyp.SOUVERAENITAETS_KUNSTFELD,
    })
    _PROZEDUR_MAP.update({
        KunstFeldGeltung.GESPERRT: KunstFeldProzedur.NOTPROZEDUR,
        KunstFeldGeltung.AESTHETISCH_SOUVERAEN: KunstFeldProzedur.REGELPROTOKOLL,
        KunstFeldGeltung.GRUNDLEGEND_AESTHETISCH_SOUVERAEN: KunstFeldProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        MedienVerfassungsGeltung.GESPERRT: KunstFeldGeltung.GESPERRT,
        MedienVerfassungsGeltung.MEDIEN_SOUVERAEN: KunstFeldGeltung.AESTHETISCH_SOUVERAEN,
        MedienVerfassungsGeltung.GRUNDLEGEND_MEDIEN_SOUVERAEN: KunstFeldGeltung.GRUNDLEGEND_AESTHETISCH_SOUVERAEN,
    })


class KunstFeldGeltung(Enum):
    GESPERRT = "gesperrt"
    AESTHETISCH_SOUVERAEN = "aesthetisch-souveraen"
    GRUNDLEGEND_AESTHETISCH_SOUVERAEN = "grundlegend-aesthetisch-souveraen"


class KunstFeldTyp(Enum):
    SCHUTZ_KUNSTFELD = "schutz-kunstfeld"
    ORDNUNGS_KUNSTFELD = "ordnungs-kunstfeld"
    SOUVERAENITAETS_KUNSTFELD = "souveraenitaets-kunstfeld"


class KunstFeldProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class KunstFeldNorm:
    kunst_feld_id: str
    kunst_typ: KunstFeldTyp
    prozedur: KunstFeldProzedur
    geltung: KunstFeldGeltung
    kunst_weight: float
    kunst_tier: int
    canonical: bool
    kunst_ids: tuple[str, ...]
    kunst_tags: tuple[str, ...]


@dataclass(frozen=True)
class KunstFeld:
    feld_id: str
    medien_verfassung: MedienVerfassung
    normen: tuple[KunstFeldNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kunst_feld_id for n in self.normen if n.geltung is KunstFeldGeltung.GESPERRT)

    @property
    def aesthetisch_souveraen_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kunst_feld_id for n in self.normen if n.geltung is KunstFeldGeltung.AESTHETISCH_SOUVERAEN)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kunst_feld_id for n in self.normen if n.geltung is KunstFeldGeltung.GRUNDLEGEND_AESTHETISCH_SOUVERAEN)

    @property
    def feld_signal(self):
        if any(n.geltung is KunstFeldGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-gesperrt")
        elif any(n.geltung is KunstFeldGeltung.AESTHETISCH_SOUVERAEN for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-aesthetisch-souveraen")
        from types import SimpleNamespace
        return SimpleNamespace(status="feld-grundlegend-aesthetisch-souveraen")


_init_map()


def build_kunst_feld(
    medien_verfassung: MedienVerfassung | None = None,
    *,
    feld_id: str = "kunst-feld",
) -> KunstFeld:
    if medien_verfassung is None:
        medien_verfassung = build_medien_verfassung(
            verfassung_id=f"{feld_id}-verfassung"
        )

    normen: list[KunstFeldNorm] = []
    for parent_norm in medien_verfassung.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{feld_id}-{parent_norm.medien_verfassung_id.removeprefix(f'{medien_verfassung.verfassung_id}-')}"
        raw_weight = min(1.0, parent_norm.medien_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.medien_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KunstFeldGeltung.GRUNDLEGEND_AESTHETISCH_SOUVERAEN)
        normen.append(
            KunstFeldNorm(
                kunst_feld_id=new_id,
                kunst_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kunst_weight=new_weight,
                kunst_tier=new_tier,
                canonical=is_canonical,
                kunst_ids=parent_norm.medien_ids + (new_id,),
                kunst_tags=parent_norm.medien_tags + (f"kunst-feld:{new_geltung.value}",),
            )
        )
    return KunstFeld(
        feld_id=feld_id,
        medien_verfassung=medien_verfassung,
        normen=tuple(normen),
    )
