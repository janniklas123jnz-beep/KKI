"""
#401 MathematikFeld — Formale Systeme & Mathematik: Hilbert-Programm (1900):
Vollständigkeit, Konsistenz, Entscheidbarkeit als Ziele formaler Systeme.
Peano-Arithmetik (1889): 5 Axiome definieren die natürlichen Zahlen.
Gödels Vollständigkeitssatz (1930): jede wahre Aussage der Prädikatenlogik
1. Ordnung ist beweisbar. ZF-Mengenlehre (Zermelo 1908, Fraenkel 1922):
9 Axiome als universelles Gerüst. Kategorienlehre (Eilenberg/MacLane 1945):
Morphismen und Funktoren als strukturerhaltende Abbildungen.
Leitsterns Terra-Schwarm ist formal begründet: axiomatisch, konsistent,
beweisbar, strukturell.
Geltungsstufen: GESPERRT / MATHEMATISCH / GRUNDLEGEND_MATHEMATISCH
Parent: KognitionsVerfassung (#400)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kognitions_verfassung import (
    KognitionsVerfassung,
    KognitionsVerfassungsGeltung,
    build_kognitions_verfassung,
)

_GELTUNG_MAP: dict[KognitionsVerfassungsGeltung, "MathematikFeldGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[KognitionsVerfassungsGeltung.GESPERRT] = MathematikFeldGeltung.GESPERRT
    _GELTUNG_MAP[KognitionsVerfassungsGeltung.KOGNITIONSVERFASST] = MathematikFeldGeltung.MATHEMATISCH
    _GELTUNG_MAP[KognitionsVerfassungsGeltung.GRUNDLEGEND_KOGNITIONSVERFASST] = MathematikFeldGeltung.GRUNDLEGEND_MATHEMATISCH


class MathematikFeldTyp(Enum):
    SCHUTZ_MATHEMATIK = "schutz-mathematik"
    ORDNUNGS_MATHEMATIK = "ordnungs-mathematik"
    SOUVERAENITAETS_MATHEMATIK = "souveraenitaets-mathematik"


class MathematikFeldProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class MathematikFeldGeltung(Enum):
    GESPERRT = "gesperrt"
    MATHEMATISCH = "mathematisch"
    GRUNDLEGEND_MATHEMATISCH = "grundlegend-mathematisch"


_init_map()

_TYP_MAP: dict[MathematikFeldGeltung, MathematikFeldTyp] = {
    MathematikFeldGeltung.GESPERRT: MathematikFeldTyp.SCHUTZ_MATHEMATIK,
    MathematikFeldGeltung.MATHEMATISCH: MathematikFeldTyp.ORDNUNGS_MATHEMATIK,
    MathematikFeldGeltung.GRUNDLEGEND_MATHEMATISCH: MathematikFeldTyp.SOUVERAENITAETS_MATHEMATIK,
}

_PROZEDUR_MAP: dict[MathematikFeldGeltung, MathematikFeldProzedur] = {
    MathematikFeldGeltung.GESPERRT: MathematikFeldProzedur.NOTPROZEDUR,
    MathematikFeldGeltung.MATHEMATISCH: MathematikFeldProzedur.REGELPROTOKOLL,
    MathematikFeldGeltung.GRUNDLEGEND_MATHEMATISCH: MathematikFeldProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[MathematikFeldGeltung, float] = {
    MathematikFeldGeltung.GESPERRT: 0.0,
    MathematikFeldGeltung.MATHEMATISCH: 0.04,
    MathematikFeldGeltung.GRUNDLEGEND_MATHEMATISCH: 0.08,
}

_TIER_DELTA: dict[MathematikFeldGeltung, int] = {
    MathematikFeldGeltung.GESPERRT: 0,
    MathematikFeldGeltung.MATHEMATISCH: 1,
    MathematikFeldGeltung.GRUNDLEGEND_MATHEMATISCH: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MathematikFeldNorm:
    mathematik_feld_id: str
    mathematik_typ: MathematikFeldTyp
    prozedur: MathematikFeldProzedur
    geltung: MathematikFeldGeltung
    mathematik_weight: float
    mathematik_tier: int
    canonical: bool
    mathematik_ids: tuple[str, ...]
    mathematik_tags: tuple[str, ...]


@dataclass(frozen=True)
class MathematikFeld:
    feld_id: str
    kognitions_verfassung: KognitionsVerfassung
    normen: tuple[MathematikFeldNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.mathematik_feld_id for n in self.normen if n.geltung is MathematikFeldGeltung.GESPERRT)

    @property
    def mathematisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.mathematik_feld_id for n in self.normen if n.geltung is MathematikFeldGeltung.MATHEMATISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.mathematik_feld_id for n in self.normen if n.geltung is MathematikFeldGeltung.GRUNDLEGEND_MATHEMATISCH)

    @property
    def feld_signal(self):
        if any(n.geltung is MathematikFeldGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-gesperrt")
        elif any(n.geltung is MathematikFeldGeltung.MATHEMATISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-mathematisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="feld-grundlegend-mathematisch")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_mathematik_feld(
    kognitions_verfassung: KognitionsVerfassung | None = None,
    *,
    feld_id: str = "mathematik-feld",
) -> MathematikFeld:
    if kognitions_verfassung is None:
        kognitions_verfassung = build_kognitions_verfassung(verfassung_id=f"{feld_id}-verfassung")

    normen: list[MathematikFeldNorm] = []
    for parent_norm in kognitions_verfassung.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{feld_id}-{parent_norm.kognitions_verfassung_id.removeprefix(f'{kognitions_verfassung.verfassung_id}-')}"
        raw_weight = min(1.0, parent_norm.kognitions_verfassungs_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kognitions_verfassungs_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is MathematikFeldGeltung.GRUNDLEGEND_MATHEMATISCH)
        normen.append(
            MathematikFeldNorm(
                mathematik_feld_id=new_id,
                mathematik_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                mathematik_weight=new_weight,
                mathematik_tier=new_tier,
                canonical=is_canonical,
                mathematik_ids=parent_norm.kognitions_verfassungs_ids + (new_id,),
                mathematik_tags=parent_norm.kognitions_verfassungs_tags + (f"mathematik:{new_geltung.value}",),
            )
        )
    return MathematikFeld(
        feld_id=feld_id,
        kognitions_verfassung=kognitions_verfassung,
        normen=tuple(normen),
    )
