"""
#581 PaedagogikFeld — Dewey/Freire/Vygotsky Pädagogik Feld

John Dewey (1916): Democracy and Education — Lernen als Erfahrungsprozess;
  Schule als demokratische Gemeinschaft; Problemlösen als pädagogisches Prinzip;
  Verbindung von Theorie und Praxis als Bildungsideal; reflexives Denken als
  Ziel der Erziehung im Peta-Schwarm Leitstern.
Paulo Freire (1968): Pädagogik der Unterdrückten — Bankiers-Konzept als
  Kritik der passiven Wissensübertragung; Dialog als Grundprinzip der Bildung;
  Bewusstseinsbildung (Conscientização) als Befreiungsprozess; Lernen als
  gemeinsame Welterschließung; Praxis als Einheit von Reflexion und Aktion
  im Peta-Schwarm Leitstern.
Lev Vygotsky (1934): Denken und Sprechen — Zone der nächsten Entwicklung als
  pädagogisches Grundkonzept; Scaffolding als Lernunterstützung; soziale
  Konstruktion von Wissen; Sprache als Werkzeug des Denkens; interpsychische
  Prozesse als Basis intrapsychischer Entwicklung im Peta-Schwarm Leitstern. 🎓📚
Parent: KunstVerfassung (#580)
Block #581–#590: Pädagogik & Bildungswissenschaft
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kunst_verfassung import (
    KunstVerfassung,
    KunstVerfassungsGeltung,
    build_kunst_verfassung,
)

_WEIGHT_DELTA: dict["PaedagogikFeldGeltung", float] = {}
_TIER_DELTA: dict["PaedagogikFeldGeltung", int] = {}
_TYP_MAP: dict["PaedagogikFeldGeltung", "PaedagogikFeldTyp"] = {}
_PROZEDUR_MAP: dict["PaedagogikFeldGeltung", "PaedagogikFeldProzedur"] = {}
_GELTUNG_MAP: dict[KunstVerfassungsGeltung, "PaedagogikFeldGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        PaedagogikFeldGeltung.GESPERRT: 0.0,
        PaedagogikFeldGeltung.PAEDAGOGISCH_SOUVERAEN: 0.05,
        PaedagogikFeldGeltung.GRUNDLEGEND_PAEDAGOGISCH_SOUVERAEN: 0.1,
    })
    _TIER_DELTA.update({
        PaedagogikFeldGeltung.GESPERRT: 0,
        PaedagogikFeldGeltung.PAEDAGOGISCH_SOUVERAEN: 1,
        PaedagogikFeldGeltung.GRUNDLEGEND_PAEDAGOGISCH_SOUVERAEN: 2,
    })
    _TYP_MAP.update({
        PaedagogikFeldGeltung.GESPERRT: PaedagogikFeldTyp.SCHUTZ_PAEDAGOGIKFELD,
        PaedagogikFeldGeltung.PAEDAGOGISCH_SOUVERAEN: PaedagogikFeldTyp.ORDNUNGS_PAEDAGOGIKFELD,
        PaedagogikFeldGeltung.GRUNDLEGEND_PAEDAGOGISCH_SOUVERAEN: PaedagogikFeldTyp.SOUVERAENITAETS_PAEDAGOGIKFELD,
    })
    _PROZEDUR_MAP.update({
        PaedagogikFeldGeltung.GESPERRT: PaedagogikFeldProzedur.NOTPROZEDUR,
        PaedagogikFeldGeltung.PAEDAGOGISCH_SOUVERAEN: PaedagogikFeldProzedur.REGELPROTOKOLL,
        PaedagogikFeldGeltung.GRUNDLEGEND_PAEDAGOGISCH_SOUVERAEN: PaedagogikFeldProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        KunstVerfassungsGeltung.GESPERRT: PaedagogikFeldGeltung.GESPERRT,
        KunstVerfassungsGeltung.KUNST_SOUVERAEN: PaedagogikFeldGeltung.PAEDAGOGISCH_SOUVERAEN,
        KunstVerfassungsGeltung.GRUNDLEGEND_KUNST_SOUVERAEN: PaedagogikFeldGeltung.GRUNDLEGEND_PAEDAGOGISCH_SOUVERAEN,
    })


class PaedagogikFeldGeltung(Enum):
    GESPERRT = "gesperrt"
    PAEDAGOGISCH_SOUVERAEN = "paedagogisch-souveraen"
    GRUNDLEGEND_PAEDAGOGISCH_SOUVERAEN = "grundlegend-paedagogisch-souveraen"


class PaedagogikFeldTyp(Enum):
    SCHUTZ_PAEDAGOGIKFELD = "schutz-paedagogikfeld"
    ORDNUNGS_PAEDAGOGIKFELD = "ordnungs-paedagogikfeld"
    SOUVERAENITAETS_PAEDAGOGIKFELD = "souveraenitaets-paedagogikfeld"


class PaedagogikFeldProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class PaedagogikFeldNorm:
    paedagogik_feld_id: str
    paedagogik_typ: PaedagogikFeldTyp
    prozedur: PaedagogikFeldProzedur
    geltung: PaedagogikFeldGeltung
    paedagogik_weight: float
    paedagogik_tier: int
    canonical: bool
    paedagogik_ids: tuple[str, ...]
    paedagogik_tags: tuple[str, ...]


@dataclass(frozen=True)
class PaedagogikFeld:
    feld_id: str
    kunst_verfassung: KunstVerfassung
    normen: tuple[PaedagogikFeldNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.paedagogik_feld_id for n in self.normen if n.geltung is PaedagogikFeldGeltung.GESPERRT)

    @property
    def paedagogisch_souveraen_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.paedagogik_feld_id for n in self.normen if n.geltung is PaedagogikFeldGeltung.PAEDAGOGISCH_SOUVERAEN)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.paedagogik_feld_id for n in self.normen if n.geltung is PaedagogikFeldGeltung.GRUNDLEGEND_PAEDAGOGISCH_SOUVERAEN)

    @property
    def feld_signal(self):
        if any(n.geltung is PaedagogikFeldGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-gesperrt")
        elif any(n.geltung is PaedagogikFeldGeltung.PAEDAGOGISCH_SOUVERAEN for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-paedagogisch-souveraen")
        from types import SimpleNamespace
        return SimpleNamespace(status="feld-grundlegend-paedagogisch-souveraen")


_init_map()


def build_paedagogik_feld(
    kunst_verfassung: KunstVerfassung | None = None,
    *,
    feld_id: str = "paedagogik-feld",
) -> PaedagogikFeld:
    if kunst_verfassung is None:
        kunst_verfassung = build_kunst_verfassung(
            verfassung_id=f"{feld_id}-verfassung"
        )

    normen: list[PaedagogikFeldNorm] = []
    for parent_norm in kunst_verfassung.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{feld_id}-{parent_norm.kunst_verfassung_id.removeprefix(f'{kunst_verfassung.verfassung_id}-')}"
        raw_weight = min(1.0, parent_norm.kunst_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kunst_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is PaedagogikFeldGeltung.GRUNDLEGEND_PAEDAGOGISCH_SOUVERAEN)
        normen.append(
            PaedagogikFeldNorm(
                paedagogik_feld_id=new_id,
                paedagogik_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                paedagogik_weight=new_weight,
                paedagogik_tier=new_tier,
                canonical=is_canonical,
                paedagogik_ids=parent_norm.kunst_ids + (new_id,),
                paedagogik_tags=parent_norm.kunst_tags + (f"paedagogik-feld:{new_geltung.value}",),
            )
        )
    return PaedagogikFeld(
        feld_id=feld_id,
        kunst_verfassung=kunst_verfassung,
        normen=tuple(normen),
    )
