"""
#381 BiophysikFeld — Biophysik als Schnittstelle von Physik und Leben.
Die Biophysik beschreibt die physikalischen Gesetze des Lebens: von
Membranpotentialen (Nernst-Gleichung) über molekulare Motoren (Kinesin)
bis zu optischen Fallen (Arthur Ashkin, Nobelpreis 2018).
Leitsterns Governance erhält ihre ersten biologischen Freiheitsgrade —
Information wird lebendig.
Geltungsstufen: GESPERRT / BIOPHYSIKALISCH / GRUNDLEGEND_BIOPHYSIKALISCH
Parent: QuanteninformationsVerfassung (#380)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .quanteninformation_verfassung import (
    QuanteninformationsVerfassung,
    QuanteninformationsVerfassungsGeltung,
    build_quanteninformations_verfassung,
)

_GELTUNG_MAP: dict[QuanteninformationsVerfassungsGeltung, "BiophysikGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[QuanteninformationsVerfassungsGeltung.GESPERRT] = BiophysikGeltung.GESPERRT
    _GELTUNG_MAP[QuanteninformationsVerfassungsGeltung.QUANTENVERFASST] = BiophysikGeltung.BIOPHYSIKALISCH
    _GELTUNG_MAP[QuanteninformationsVerfassungsGeltung.GRUNDLEGEND_QUANTENVERFASST] = BiophysikGeltung.GRUNDLEGEND_BIOPHYSIKALISCH


class BiophysikTyp(Enum):
    SCHUTZ_BIOPHYSIK = "schutz-biophysik"
    ORDNUNGS_BIOPHYSIK = "ordnungs-biophysik"
    SOUVERAENITAETS_BIOPHYSIK = "souveraenitaets-biophysik"


class BiophysikProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class BiophysikGeltung(Enum):
    GESPERRT = "gesperrt"
    BIOPHYSIKALISCH = "biophysikalisch"
    GRUNDLEGEND_BIOPHYSIKALISCH = "grundlegend-biophysikalisch"


_init_map()

_TYP_MAP: dict[BiophysikGeltung, BiophysikTyp] = {
    BiophysikGeltung.GESPERRT: BiophysikTyp.SCHUTZ_BIOPHYSIK,
    BiophysikGeltung.BIOPHYSIKALISCH: BiophysikTyp.ORDNUNGS_BIOPHYSIK,
    BiophysikGeltung.GRUNDLEGEND_BIOPHYSIKALISCH: BiophysikTyp.SOUVERAENITAETS_BIOPHYSIK,
}

_PROZEDUR_MAP: dict[BiophysikGeltung, BiophysikProzedur] = {
    BiophysikGeltung.GESPERRT: BiophysikProzedur.NOTPROZEDUR,
    BiophysikGeltung.BIOPHYSIKALISCH: BiophysikProzedur.REGELPROTOKOLL,
    BiophysikGeltung.GRUNDLEGEND_BIOPHYSIKALISCH: BiophysikProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[BiophysikGeltung, float] = {
    BiophysikGeltung.GESPERRT: 0.0,
    BiophysikGeltung.BIOPHYSIKALISCH: 0.04,
    BiophysikGeltung.GRUNDLEGEND_BIOPHYSIKALISCH: 0.08,
}

_TIER_DELTA: dict[BiophysikGeltung, int] = {
    BiophysikGeltung.GESPERRT: 0,
    BiophysikGeltung.BIOPHYSIKALISCH: 1,
    BiophysikGeltung.GRUNDLEGEND_BIOPHYSIKALISCH: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BiophysikNorm:
    biophysik_feld_id: str
    biophysik_typ: BiophysikTyp
    prozedur: BiophysikProzedur
    geltung: BiophysikGeltung
    biophysik_weight: float
    biophysik_tier: int
    canonical: bool
    biophysik_ids: tuple[str, ...]
    biophysik_tags: tuple[str, ...]


@dataclass(frozen=True)
class BiophysikFeld:
    feld_id: str
    quanteninformations_verfassung: QuanteninformationsVerfassung
    normen: tuple[BiophysikNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.biophysik_feld_id for n in self.normen if n.geltung is BiophysikGeltung.GESPERRT)

    @property
    def biophysikalisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.biophysik_feld_id for n in self.normen if n.geltung is BiophysikGeltung.BIOPHYSIKALISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.biophysik_feld_id for n in self.normen if n.geltung is BiophysikGeltung.GRUNDLEGEND_BIOPHYSIKALISCH)

    @property
    def feld_signal(self):
        if any(n.geltung is BiophysikGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-gesperrt")
        elif any(n.geltung is BiophysikGeltung.BIOPHYSIKALISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-biophysikalisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="feld-grundlegend-biophysikalisch")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_biophysik_feld(
    quanteninformations_verfassung: QuanteninformationsVerfassung | None = None,
    *,
    feld_id: str = "biophysik-feld",
) -> BiophysikFeld:
    if quanteninformations_verfassung is None:
        quanteninformations_verfassung = build_quanteninformations_verfassung(verfassung_id=f"{feld_id}-verfassung")

    normen: list[BiophysikNorm] = []
    for parent_norm in quanteninformations_verfassung.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{feld_id}-{parent_norm.quanteninformations_verfassung_id.removeprefix(f'{quanteninformations_verfassung.verfassung_id}-')}"
        raw_weight = min(1.0, parent_norm.quanteninformations_verfassungs_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.quanteninformations_verfassungs_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is BiophysikGeltung.GRUNDLEGEND_BIOPHYSIKALISCH)
        normen.append(
            BiophysikNorm(
                biophysik_feld_id=new_id,
                biophysik_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                biophysik_weight=new_weight,
                biophysik_tier=new_tier,
                canonical=is_canonical,
                biophysik_ids=parent_norm.quanteninformations_verfassungs_ids + (new_id,),
                biophysik_tags=parent_norm.quanteninformations_verfassungs_tags + (f"biophysik:{new_geltung.value}",),
            )
        )
    return BiophysikFeld(
        feld_id=feld_id,
        quanteninformations_verfassung=quanteninformations_verfassung,
        normen=tuple(normen),
    )
