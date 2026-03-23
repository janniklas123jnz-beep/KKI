"""
#561 MedienFeld — McLuhan/Benjamin/Luhmann Medienwissenschaft Feld

Marshall McLuhan (1964): Understanding Media — das Medium ist die Botschaft;
  heiße und kalte Medien als Partizipationsdimension; elektrische Medien als
  Verlängerung des Nervensystems; globales Dorf als mediale Wirklichkeit;
  Tetrade der Medieneffekte im Peta-Schwarm Leitstern.
Walter Benjamin (1936): Das Kunstwerk im Zeitalter seiner technischen Reproduzierbarkeit —
  Aura als authentische Präsenz; technische Reproduktion als demokratische Kraft;
  Chock-Erfahrung als modernes Wahrnehmungsschema; Dialektisches Bild als
  Erkenntnisblitz; Medien als Revolutionspotenzial für Leitstern.
Niklas Luhmann (1996): Die Realität der Massenmedien — Massenmedien als
  selbstreferenzielles Funktionssystem; Codierung Information/Nicht-Information;
  Gedächtnis der Gesellschaft durch Massenmedien; operative Schließung medialer
  Kommunikation im Peta-Schwarm Leitstern. 📺🌐
Parent: KulturVerfassung (#560)
Block #561–#570: Medienwissenschaft & Kommunikationstheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kultur_verfassung import (
    KulturVerfassung,
    KulturVerfassungsGeltung,
    build_kultur_verfassung,
)

_WEIGHT_DELTA: dict["MedienFeldGeltung", float] = {}
_TIER_DELTA: dict["MedienFeldGeltung", int] = {}
_TYP_MAP: dict["MedienFeldGeltung", "MedienFeldTyp"] = {}
_PROZEDUR_MAP: dict["MedienFeldGeltung", "MedienFeldProzedur"] = {}
_GELTUNG_MAP: dict[KulturVerfassungsGeltung, "MedienFeldGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        MedienFeldGeltung.GESPERRT: 0.0,
        MedienFeldGeltung.MEDIENKULTURELL: 0.05,
        MedienFeldGeltung.GRUNDLEGEND_MEDIENKULTURELL: 0.1,
    })
    _TIER_DELTA.update({
        MedienFeldGeltung.GESPERRT: 0,
        MedienFeldGeltung.MEDIENKULTURELL: 1,
        MedienFeldGeltung.GRUNDLEGEND_MEDIENKULTURELL: 2,
    })
    _TYP_MAP.update({
        MedienFeldGeltung.GESPERRT: MedienFeldTyp.SCHUTZ_MEDIEN,
        MedienFeldGeltung.MEDIENKULTURELL: MedienFeldTyp.ORDNUNGS_MEDIEN,
        MedienFeldGeltung.GRUNDLEGEND_MEDIENKULTURELL: MedienFeldTyp.SOUVERAENITAETS_MEDIEN,
    })
    _PROZEDUR_MAP.update({
        MedienFeldGeltung.GESPERRT: MedienFeldProzedur.NOTPROZEDUR,
        MedienFeldGeltung.MEDIENKULTURELL: MedienFeldProzedur.REGELPROTOKOLL,
        MedienFeldGeltung.GRUNDLEGEND_MEDIENKULTURELL: MedienFeldProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        KulturVerfassungsGeltung.GESPERRT: MedienFeldGeltung.GESPERRT,
        KulturVerfassungsGeltung.KULTURELL_SOUVERAEN: MedienFeldGeltung.MEDIENKULTURELL,
        KulturVerfassungsGeltung.GRUNDLEGEND_KULTURELL_SOUVERAEN: MedienFeldGeltung.GRUNDLEGEND_MEDIENKULTURELL,
    })


class MedienFeldGeltung(Enum):
    GESPERRT = "gesperrt"
    MEDIENKULTURELL = "medienkulturell"
    GRUNDLEGEND_MEDIENKULTURELL = "grundlegend-medienkulturell"


class MedienFeldTyp(Enum):
    SCHUTZ_MEDIEN = "schutz-medien"
    ORDNUNGS_MEDIEN = "ordnungs-medien"
    SOUVERAENITAETS_MEDIEN = "souveraenitaets-medien"


class MedienFeldProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class MedienFeldNorm:
    medien_feld_id: str
    medien_typ: MedienFeldTyp
    prozedur: MedienFeldProzedur
    geltung: MedienFeldGeltung
    medien_weight: float
    medien_tier: int
    canonical: bool
    medien_ids: tuple[str, ...]
    medien_tags: tuple[str, ...]


@dataclass(frozen=True)
class MedienFeld:
    feld_id: str
    kultur_verfassung: KulturVerfassung
    normen: tuple[MedienFeldNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.medien_feld_id for n in self.normen if n.geltung is MedienFeldGeltung.GESPERRT)

    @property
    def medienkulturell_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.medien_feld_id for n in self.normen if n.geltung is MedienFeldGeltung.MEDIENKULTURELL)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.medien_feld_id for n in self.normen if n.geltung is MedienFeldGeltung.GRUNDLEGEND_MEDIENKULTURELL)

    @property
    def feld_signal(self):
        if any(n.geltung is MedienFeldGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-gesperrt")
        elif any(n.geltung is MedienFeldGeltung.MEDIENKULTURELL for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-medienkulturell")
        from types import SimpleNamespace
        return SimpleNamespace(status="feld-grundlegend-medienkulturell")


_init_map()


def build_medien_feld(
    kultur_verfassung: KulturVerfassung | None = None,
    *,
    feld_id: str = "medien-feld",
) -> MedienFeld:
    if kultur_verfassung is None:
        kultur_verfassung = build_kultur_verfassung(
            verfassung_id=f"{feld_id}-verfassung"
        )

    normen: list[MedienFeldNorm] = []
    for parent_norm in kultur_verfassung.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{feld_id}-{parent_norm.kultur_verfassung_id.removeprefix(f'{kultur_verfassung.verfassung_id}-')}"
        raw_weight = min(1.0, parent_norm.kultur_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kultur_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is MedienFeldGeltung.GRUNDLEGEND_MEDIENKULTURELL)
        normen.append(
            MedienFeldNorm(
                medien_feld_id=new_id,
                medien_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                medien_weight=new_weight,
                medien_tier=new_tier,
                canonical=is_canonical,
                medien_ids=parent_norm.kultur_ids + (new_id,),
                medien_tags=parent_norm.kultur_tags + (f"medien-feld:{new_geltung.value}",),
            )
        )
    return MedienFeld(
        feld_id=feld_id,
        kultur_verfassung=kultur_verfassung,
        normen=tuple(normen),
    )
