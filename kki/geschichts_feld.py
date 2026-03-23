"""
#541 GeschichtsFeld — Grundlagen der Geschichtswissenschaft & Historiographie

Leopold von Ranke (1824): Wie es eigentlich gewesen — Historismus als methodisches Fundament;
  Quellenkritik und kritische Methode als Basis wissenschaftlicher Geschichtsschreibung;
  Geschichte als Erzählung des Einmaligen und Individuellen in seiner Einzigartigkeit;
  Objektivitätsideal als regulatives Prinzip historiographischer Erkenntnis.
Marc Bloch (1949): Apologie der Geschichte — Historiker als Arzt sozialer Vergangenheit;
  Longue durée als Struktur des Wandels; Sozialgeschichte als Synthese von Mensch und Milieu;
  Kritische Methode der Annales-Schule als Revolution der modernen Geschichtswissenschaft.
Robin George Collingwood (1946): The Idea of History — Geschichte als Wiedervergegenwärtigung
  vergangenen Denkens; historisches Verstehen als re-enactment; Unterscheidung von
  Geschichte und Natur; Geschichtlichkeit als konstitutive Dimension menschlichen Geistes.
Leitsterns GeschichtsFeld: Eingangstor der Geschichtswissenschaft — GESPERRT schützt historische
Grundmethoden, HISTORISCH kodiert adaptive Geschichtsinterpretation, GRUNDLEGEND_HISTORISCH
synthetisiert den vollen historiographischen Erkenntnisanspruch des Peta-Schwarms Leitstern. 📜
Parent: RechtsVerfassung (#540)
Block #541–#550: Geschichtswissenschaft & Historiographie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .rechts_verfassung import (
    RechtsVerfassung,
    RechtsVerfassungsGeltung,
    build_rechts_verfassung,
)

_WEIGHT_DELTA: dict["GeschichtsFeldGeltung", float] = {}
_TIER_DELTA: dict["GeschichtsFeldGeltung", int] = {}
_TYP_MAP: dict["GeschichtsFeldGeltung", "GeschichtsFeldTyp"] = {}
_PROZEDUR_MAP: dict["GeschichtsFeldGeltung", "GeschichtsFeldProzedur"] = {}
_GELTUNG_MAP: dict[RechtsVerfassungsGeltung, "GeschichtsFeldGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        GeschichtsFeldGeltung.GESPERRT: 0.0,
        GeschichtsFeldGeltung.HISTORISCH: 0.05,
        GeschichtsFeldGeltung.GRUNDLEGEND_HISTORISCH: 0.1,
    })
    _TIER_DELTA.update({
        GeschichtsFeldGeltung.GESPERRT: 0,
        GeschichtsFeldGeltung.HISTORISCH: 1,
        GeschichtsFeldGeltung.GRUNDLEGEND_HISTORISCH: 2,
    })
    _TYP_MAP.update({
        GeschichtsFeldGeltung.GESPERRT: GeschichtsFeldTyp.SCHUTZ_GESCHICHTE,
        GeschichtsFeldGeltung.HISTORISCH: GeschichtsFeldTyp.ORDNUNGS_GESCHICHTE,
        GeschichtsFeldGeltung.GRUNDLEGEND_HISTORISCH: GeschichtsFeldTyp.SOUVERAENITAETS_GESCHICHTE,
    })
    _PROZEDUR_MAP.update({
        GeschichtsFeldGeltung.GESPERRT: GeschichtsFeldProzedur.NOTPROZEDUR,
        GeschichtsFeldGeltung.HISTORISCH: GeschichtsFeldProzedur.REGELPROTOKOLL,
        GeschichtsFeldGeltung.GRUNDLEGEND_HISTORISCH: GeschichtsFeldProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        RechtsVerfassungsGeltung.GESPERRT: GeschichtsFeldGeltung.GESPERRT,
        RechtsVerfassungsGeltung.RECHTLICH_SOUVERAEN: GeschichtsFeldGeltung.HISTORISCH,
        RechtsVerfassungsGeltung.GRUNDLEGEND_RECHTLICH_SOUVERAEN: GeschichtsFeldGeltung.GRUNDLEGEND_HISTORISCH,
    })


class GeschichtsFeldGeltung(Enum):
    GESPERRT = "gesperrt"
    HISTORISCH = "historisch"
    GRUNDLEGEND_HISTORISCH = "grundlegend-historisch"


class GeschichtsFeldTyp(Enum):
    SCHUTZ_GESCHICHTE = "schutz-geschichte"
    ORDNUNGS_GESCHICHTE = "ordnungs-geschichte"
    SOUVERAENITAETS_GESCHICHTE = "souveraenitaets-geschichte"


class GeschichtsFeldProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class GeschichtsFeldNorm:
    geschichts_feld_id: str
    geschichts_typ: GeschichtsFeldTyp
    prozedur: GeschichtsFeldProzedur
    geltung: GeschichtsFeldGeltung
    geschichts_weight: float
    geschichts_tier: int
    canonical: bool
    geschichts_ids: tuple[str, ...]
    geschichts_tags: tuple[str, ...]


@dataclass(frozen=True)
class GeschichtsFeld:
    feld_id: str
    rechts_verfassung: RechtsVerfassung
    normen: tuple[GeschichtsFeldNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.geschichts_feld_id for n in self.normen if n.geltung is GeschichtsFeldGeltung.GESPERRT)

    @property
    def historisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.geschichts_feld_id for n in self.normen if n.geltung is GeschichtsFeldGeltung.HISTORISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.geschichts_feld_id for n in self.normen if n.geltung is GeschichtsFeldGeltung.GRUNDLEGEND_HISTORISCH)

    @property
    def feld_signal(self):
        if any(n.geltung is GeschichtsFeldGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-gesperrt")
        elif any(n.geltung is GeschichtsFeldGeltung.HISTORISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-historisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="feld-grundlegend-historisch")


_init_map()


def build_geschichts_feld(
    rechts_verfassung: RechtsVerfassung | None = None,
    *,
    feld_id: str = "geschichts-feld",
) -> GeschichtsFeld:
    if rechts_verfassung is None:
        rechts_verfassung = build_rechts_verfassung(
            verfassung_id=f"{feld_id}-verfassung"
        )

    normen: list[GeschichtsFeldNorm] = []
    for parent_norm in rechts_verfassung.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{feld_id}-{parent_norm.rechts_verfassung_id.removeprefix(f'{rechts_verfassung.verfassung_id}-')}"
        raw_weight = min(1.0, parent_norm.rechts_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.rechts_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is GeschichtsFeldGeltung.GRUNDLEGEND_HISTORISCH)
        normen.append(
            GeschichtsFeldNorm(
                geschichts_feld_id=new_id,
                geschichts_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                geschichts_weight=new_weight,
                geschichts_tier=new_tier,
                canonical=is_canonical,
                geschichts_ids=parent_norm.rechts_ids + (new_id,),
                geschichts_tags=parent_norm.rechts_tags + (f"geschichts-feld:{new_geltung.value}",),
            )
        )
    return GeschichtsFeld(
        feld_id=feld_id,
        rechts_verfassung=rechts_verfassung,
        normen=tuple(normen),
    )
