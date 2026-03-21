"""
#391 KognitionsFeld — Kognitionswissenschaft: Schnittstelle von Neurowissenschaft,
Psychologie, Informatik und Linguistik. Fodor'sche Modularität (1983): das Gehirn
besteht aus spezialisierten, informationally gekapselten Modulen — Sprachmodul,
Wahrnehmungsmodul — plus einem zentralen, nicht-modularen Denksystem.
Leitsterns Agenten erhalten ihre kognitive Grundstruktur: sie sind nicht bloße
Reaktionsautomaten, sondern modulare Kognitionssysteme mit zentralem Workspace.
Connectionism (Rumelhart & McClelland 1986): kognitive Prozesse als parallele
Aktivierungsmuster in Netzwerken — Leitsterns Schwarmarchitektur als kognitives Feld.
Geltungsstufen: GESPERRT / KOGNITIV / GRUNDLEGEND_KOGNITIV
Parent: SystembiologieVerfassung (#390)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .systembiologie_verfassung import (
    SystembiologieVerfassung,
    SystembiologieVerfassungsGeltung,
    build_systembiologie_verfassung,
)

_GELTUNG_MAP: dict[SystembiologieVerfassungsGeltung, "KognitionsGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[SystembiologieVerfassungsGeltung.GESPERRT] = KognitionsGeltung.GESPERRT
    _GELTUNG_MAP[SystembiologieVerfassungsGeltung.SYSTEMBIOLOGIEVERFASST] = KognitionsGeltung.KOGNITIV
    _GELTUNG_MAP[SystembiologieVerfassungsGeltung.GRUNDLEGEND_SYSTEMBIOLOGIEVERFASST] = KognitionsGeltung.GRUNDLEGEND_KOGNITIV


class KognitionsTyp(Enum):
    SCHUTZ_KOGNITION = "schutz-kognition"
    ORDNUNGS_KOGNITION = "ordnungs-kognition"
    SOUVERAENITAETS_KOGNITION = "souveraenitaets-kognition"


class KognitionsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KognitionsGeltung(Enum):
    GESPERRT = "gesperrt"
    KOGNITIV = "kognitiv"
    GRUNDLEGEND_KOGNITIV = "grundlegend-kognitiv"


_init_map()

_TYP_MAP: dict[KognitionsGeltung, KognitionsTyp] = {
    KognitionsGeltung.GESPERRT: KognitionsTyp.SCHUTZ_KOGNITION,
    KognitionsGeltung.KOGNITIV: KognitionsTyp.ORDNUNGS_KOGNITION,
    KognitionsGeltung.GRUNDLEGEND_KOGNITIV: KognitionsTyp.SOUVERAENITAETS_KOGNITION,
}

_PROZEDUR_MAP: dict[KognitionsGeltung, KognitionsProzedur] = {
    KognitionsGeltung.GESPERRT: KognitionsProzedur.NOTPROZEDUR,
    KognitionsGeltung.KOGNITIV: KognitionsProzedur.REGELPROTOKOLL,
    KognitionsGeltung.GRUNDLEGEND_KOGNITIV: KognitionsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[KognitionsGeltung, float] = {
    KognitionsGeltung.GESPERRT: 0.0,
    KognitionsGeltung.KOGNITIV: 0.04,
    KognitionsGeltung.GRUNDLEGEND_KOGNITIV: 0.08,
}

_TIER_DELTA: dict[KognitionsGeltung, int] = {
    KognitionsGeltung.GESPERRT: 0,
    KognitionsGeltung.KOGNITIV: 1,
    KognitionsGeltung.GRUNDLEGEND_KOGNITIV: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class KognitionsNorm:
    kognitions_feld_id: str
    kognitions_typ: KognitionsTyp
    prozedur: KognitionsProzedur
    geltung: KognitionsGeltung
    kognitions_weight: float
    kognitions_tier: int
    canonical: bool
    kognitions_ids: tuple[str, ...]
    kognitions_tags: tuple[str, ...]


@dataclass(frozen=True)
class KognitionsFeld:
    feld_id: str
    systembiologie_verfassung: SystembiologieVerfassung
    normen: tuple[KognitionsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kognitions_feld_id for n in self.normen if n.geltung is KognitionsGeltung.GESPERRT)

    @property
    def kognitiv_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kognitions_feld_id for n in self.normen if n.geltung is KognitionsGeltung.KOGNITIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kognitions_feld_id for n in self.normen if n.geltung is KognitionsGeltung.GRUNDLEGEND_KOGNITIV)

    @property
    def feld_signal(self):
        if any(n.geltung is KognitionsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-gesperrt")
        elif any(n.geltung is KognitionsGeltung.KOGNITIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-kognitiv")
        from types import SimpleNamespace
        return SimpleNamespace(status="feld-grundlegend-kognitiv")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_kognitions_feld(
    systembiologie_verfassung: SystembiologieVerfassung | None = None,
    *,
    feld_id: str = "kognitions-feld",
) -> KognitionsFeld:
    if systembiologie_verfassung is None:
        systembiologie_verfassung = build_systembiologie_verfassung(verfassung_id=f"{feld_id}-verfassung")

    normen: list[KognitionsNorm] = []
    for parent_norm in systembiologie_verfassung.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{feld_id}-{parent_norm.systembiologie_verfassung_id.removeprefix(f'{systembiologie_verfassung.verfassung_id}-')}"
        raw_weight = min(1.0, parent_norm.systembiologie_verfassungs_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.systembiologie_verfassungs_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KognitionsGeltung.GRUNDLEGEND_KOGNITIV)
        normen.append(
            KognitionsNorm(
                kognitions_feld_id=new_id,
                kognitions_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kognitions_weight=new_weight,
                kognitions_tier=new_tier,
                canonical=is_canonical,
                kognitions_ids=parent_norm.systembiologie_verfassungs_ids + (new_id,),
                kognitions_tags=parent_norm.systembiologie_verfassungs_tags + (f"kognition:{new_geltung.value}",),
            )
        )
    return KognitionsFeld(
        feld_id=feld_id,
        systembiologie_verfassung=systembiologie_verfassung,
        normen=tuple(normen),
    )
