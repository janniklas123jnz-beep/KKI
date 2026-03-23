"""
#471 ErkenntnisFeld — Kant: Kritik der reinen Vernunft, a priori / a posteriori.
Immanuel Kants Erkenntnistheorie unterscheidet apriorisches Wissen (unabhängig von
Erfahrung) von aposteriorischem Wissen (durch Erfahrung). Die Kategorien des Verstandes
strukturieren die Wahrnehmung: Raum und Zeit als Anschauungsformen, Kausalität als
reiner Verstandesbegriff. Leitsterns Terra-Schwarm filtert Informationen nach
Erkenntnisform — apriorische Strukturen bilden die Grundarchitektur, aposteriorische
Daten füllen sie mit Inhalt. GESPERRT sichert reine Vernunft, ERKENNTNISTHEORETISCH
ermöglicht erfahrungsbasiertes Lernen, GRUNDLEGEND_ERKENNTNISTHEORETISCH synthetisiert.
Parent: LinguistikVerfassung (#470)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .linguistik_verfassung import (
    LinguistikVerfassung,
    LinguistikVerfassungsGeltung,
    build_linguistik_verfassung,
)

_GELTUNG_MAP: dict[LinguistikVerfassungsGeltung, "ErkenntnisFeldGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[LinguistikVerfassungsGeltung.GESPERRT] = ErkenntnisFeldGeltung.GESPERRT
    _GELTUNG_MAP[LinguistikVerfassungsGeltung.LINGUISTISCH] = ErkenntnisFeldGeltung.ERKENNTNISTHEORETISCH
    _GELTUNG_MAP[LinguistikVerfassungsGeltung.GRUNDLEGEND_LINGUISTISCH] = ErkenntnisFeldGeltung.GRUNDLEGEND_ERKENNTNISTHEORETISCH


class ErkenntnisFeldTyp(Enum):
    SCHUTZ_ERKENNTNIS = "schutz-erkenntnis"
    ORDNUNGS_ERKENNTNIS = "ordnungs-erkenntnis"
    SOUVERAENITAETS_ERKENNTNIS = "souveraenitaets-erkenntnis"


class ErkenntnisFeldProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class ErkenntnisFeldGeltung(Enum):
    GESPERRT = "gesperrt"
    ERKENNTNISTHEORETISCH = "erkenntnistheoretisch"
    GRUNDLEGEND_ERKENNTNISTHEORETISCH = "grundlegend-erkenntnistheoretisch"


_init_map()

_TYP_MAP: dict[ErkenntnisFeldGeltung, ErkenntnisFeldTyp] = {
    ErkenntnisFeldGeltung.GESPERRT: ErkenntnisFeldTyp.SCHUTZ_ERKENNTNIS,
    ErkenntnisFeldGeltung.ERKENNTNISTHEORETISCH: ErkenntnisFeldTyp.ORDNUNGS_ERKENNTNIS,
    ErkenntnisFeldGeltung.GRUNDLEGEND_ERKENNTNISTHEORETISCH: ErkenntnisFeldTyp.SOUVERAENITAETS_ERKENNTNIS,
}

_PROZEDUR_MAP: dict[ErkenntnisFeldGeltung, ErkenntnisFeldProzedur] = {
    ErkenntnisFeldGeltung.GESPERRT: ErkenntnisFeldProzedur.NOTPROZEDUR,
    ErkenntnisFeldGeltung.ERKENNTNISTHEORETISCH: ErkenntnisFeldProzedur.REGELPROTOKOLL,
    ErkenntnisFeldGeltung.GRUNDLEGEND_ERKENNTNISTHEORETISCH: ErkenntnisFeldProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[ErkenntnisFeldGeltung, float] = {
    ErkenntnisFeldGeltung.GESPERRT: 0.0,
    ErkenntnisFeldGeltung.ERKENNTNISTHEORETISCH: 0.04,
    ErkenntnisFeldGeltung.GRUNDLEGEND_ERKENNTNISTHEORETISCH: 0.08,
}

_TIER_DELTA: dict[ErkenntnisFeldGeltung, int] = {
    ErkenntnisFeldGeltung.GESPERRT: 0,
    ErkenntnisFeldGeltung.ERKENNTNISTHEORETISCH: 1,
    ErkenntnisFeldGeltung.GRUNDLEGEND_ERKENNTNISTHEORETISCH: 2,
}


@dataclass(frozen=True)
class ErkenntnisFeldNorm:
    erkenntnis_feld_id: str
    erkenntnis_typ: ErkenntnisFeldTyp
    prozedur: ErkenntnisFeldProzedur
    geltung: ErkenntnisFeldGeltung
    erkenntnis_weight: float
    erkenntnis_tier: int
    canonical: bool
    erkenntnis_ids: tuple[str, ...]
    erkenntnis_tags: tuple[str, ...]


@dataclass(frozen=True)
class ErkenntnisFeld:
    feld_id: str
    linguistik_verfassung: LinguistikVerfassung
    normen: tuple[ErkenntnisFeldNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.erkenntnis_feld_id for n in self.normen if n.geltung is ErkenntnisFeldGeltung.GESPERRT)

    @property
    def erkenntnistheoretisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.erkenntnis_feld_id for n in self.normen if n.geltung is ErkenntnisFeldGeltung.ERKENNTNISTHEORETISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.erkenntnis_feld_id for n in self.normen if n.geltung is ErkenntnisFeldGeltung.GRUNDLEGEND_ERKENNTNISTHEORETISCH)

    @property
    def feld_signal(self):
        if any(n.geltung is ErkenntnisFeldGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-gesperrt")
        elif any(n.geltung is ErkenntnisFeldGeltung.ERKENNTNISTHEORETISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-erkenntnistheoretisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="feld-grundlegend-erkenntnistheoretisch")


def build_erkenntnis_feld(
    linguistik_verfassung: LinguistikVerfassung | None = None,
    *,
    feld_id: str = "erkenntnis-feld",
) -> ErkenntnisFeld:
    if linguistik_verfassung is None:
        linguistik_verfassung = build_linguistik_verfassung(verfassung_id=f"{feld_id}-verfassung")

    normen: list[ErkenntnisFeldNorm] = []
    for parent_norm in linguistik_verfassung.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{feld_id}-{parent_norm.linguistik_verfassung_id.removeprefix(f'{linguistik_verfassung.verfassung_id}-')}"
        raw_weight = min(1.0, parent_norm.linguistik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.linguistik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is ErkenntnisFeldGeltung.GRUNDLEGEND_ERKENNTNISTHEORETISCH)
        normen.append(
            ErkenntnisFeldNorm(
                erkenntnis_feld_id=new_id,
                erkenntnis_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                erkenntnis_weight=new_weight,
                erkenntnis_tier=new_tier,
                canonical=is_canonical,
                erkenntnis_ids=parent_norm.linguistik_ids + (new_id,),
                erkenntnis_tags=parent_norm.linguistik_tags + (f"erkenntnis-feld:{new_geltung.value}",),
            )
        )
    return ErkenntnisFeld(
        feld_id=feld_id,
        linguistik_verfassung=linguistik_verfassung,
        normen=tuple(normen),
    )
