"""
#542 HistoriographieRegister — Register der historiographischen Normen

Leopold von Ranke (1824): Wie es eigentlich gewesen — Quellenkritik als Fundament;
  strenge Quellenkritik und das Objektivitätsideal als regulative Prinzipien;
  Unterscheidung zwischen primären und sekundären Quellen als methodische Grundlage.
Johann Gustav Droysen (1868): Historik — Systematik der geschichtswissenschaftlichen Methode;
  Verstehen als hermeneutisches Grundprinzip der Geschichtswissenschaft;
  Historismus als Lehre von der Einzigartigkeit historischer Ereignisse und Personen.
Karl Lamprecht (1891): Deutsche Geschichte — Kulturgeschichte als Ergänzung zur Politikgeschichte;
  kollektive Triebkräfte und soziale Determinanten als Motor historischen Wandels;
  Methodenstreit als Impuls zur Erweiterung des historiographischen Methodenrepertoires.
Parent: GeschichtsFeld (#541)
Block #541–#550: Geschichtswissenschaft & Historiographie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .geschichts_feld import (
    GeschichtsFeld,
    GeschichtsFeldGeltung,
    build_geschichts_feld,
)

_WEIGHT_DELTA: dict["HistoriographieRegisterGeltung", float] = {}
_TIER_DELTA: dict["HistoriographieRegisterGeltung", int] = {}
_TYP_MAP: dict["HistoriographieRegisterGeltung", "HistoriographieRegisterTyp"] = {}
_PROZEDUR_MAP: dict["HistoriographieRegisterGeltung", "HistoriographieRegisterProzedur"] = {}
_GELTUNG_MAP: dict[GeschichtsFeldGeltung, "HistoriographieRegisterGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        HistoriographieRegisterGeltung.GESPERRT: 0.0,
        HistoriographieRegisterGeltung.HISTORIOGRAPHISCH: 0.05,
        HistoriographieRegisterGeltung.GRUNDLEGEND_HISTORIOGRAPHISCH: 0.1,
    })
    _TIER_DELTA.update({
        HistoriographieRegisterGeltung.GESPERRT: 0,
        HistoriographieRegisterGeltung.HISTORIOGRAPHISCH: 1,
        HistoriographieRegisterGeltung.GRUNDLEGEND_HISTORIOGRAPHISCH: 2,
    })
    _TYP_MAP.update({
        HistoriographieRegisterGeltung.GESPERRT: HistoriographieRegisterTyp.SCHUTZ_HISTORIOGRAPHIE,
        HistoriographieRegisterGeltung.HISTORIOGRAPHISCH: HistoriographieRegisterTyp.ORDNUNGS_HISTORIOGRAPHIE,
        HistoriographieRegisterGeltung.GRUNDLEGEND_HISTORIOGRAPHISCH: HistoriographieRegisterTyp.SOUVERAENITAETS_HISTORIOGRAPHIE,
    })
    _PROZEDUR_MAP.update({
        HistoriographieRegisterGeltung.GESPERRT: HistoriographieRegisterProzedur.NOTPROZEDUR,
        HistoriographieRegisterGeltung.HISTORIOGRAPHISCH: HistoriographieRegisterProzedur.REGELPROTOKOLL,
        HistoriographieRegisterGeltung.GRUNDLEGEND_HISTORIOGRAPHISCH: HistoriographieRegisterProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        GeschichtsFeldGeltung.GESPERRT: HistoriographieRegisterGeltung.GESPERRT,
        GeschichtsFeldGeltung.HISTORISCH: HistoriographieRegisterGeltung.HISTORIOGRAPHISCH,
        GeschichtsFeldGeltung.GRUNDLEGEND_HISTORISCH: HistoriographieRegisterGeltung.GRUNDLEGEND_HISTORIOGRAPHISCH,
    })


class HistoriographieRegisterGeltung(Enum):
    GESPERRT = "gesperrt"
    HISTORIOGRAPHISCH = "historiographisch"
    GRUNDLEGEND_HISTORIOGRAPHISCH = "grundlegend-historiographisch"


class HistoriographieRegisterTyp(Enum):
    SCHUTZ_HISTORIOGRAPHIE = "schutz-historiographie"
    ORDNUNGS_HISTORIOGRAPHIE = "ordnungs-historiographie"
    SOUVERAENITAETS_HISTORIOGRAPHIE = "souveraenitaets-historiographie"


class HistoriographieRegisterProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class HistoriographieRegisterNorm:
    historiographie_register_id: str
    geschichts_typ: HistoriographieRegisterTyp
    prozedur: HistoriographieRegisterProzedur
    geltung: HistoriographieRegisterGeltung
    geschichts_weight: float
    geschichts_tier: int
    canonical: bool
    geschichts_ids: tuple[str, ...]
    geschichts_tags: tuple[str, ...]


@dataclass(frozen=True)
class HistoriographieRegister:
    register_id: str
    geschichts_feld: GeschichtsFeld
    normen: tuple[HistoriographieRegisterNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.historiographie_register_id for n in self.normen
            if n.geltung is HistoriographieRegisterGeltung.GESPERRT
        )

    @property
    def historiographisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.historiographie_register_id for n in self.normen
            if n.geltung is HistoriographieRegisterGeltung.HISTORIOGRAPHISCH
        )

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.historiographie_register_id for n in self.normen
            if n.geltung is HistoriographieRegisterGeltung.GRUNDLEGEND_HISTORIOGRAPHISCH
        )

    @property
    def register_signal(self):
        from types import SimpleNamespace
        if any(n.geltung is HistoriographieRegisterGeltung.GESPERRT for n in self.normen):
            return SimpleNamespace(status="register-gesperrt")
        elif any(n.geltung is HistoriographieRegisterGeltung.HISTORIOGRAPHISCH for n in self.normen):
            return SimpleNamespace(status="register-historiographisch")
        return SimpleNamespace(status="register-grundlegend-historiographisch")


_init_map()


def build_historiographie_register(
    geschichts_feld: GeschichtsFeld | None = None,
    *,
    register_id: str = "historiographie-register",
) -> HistoriographieRegister:
    if geschichts_feld is None:
        geschichts_feld = build_geschichts_feld(feld_id=f"{register_id}-feld")
    normen: list[HistoriographieRegisterNorm] = []
    for parent_norm in geschichts_feld.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{register_id}-{parent_norm.geschichts_feld_id.removeprefix(f'{geschichts_feld.feld_id}-')}"
        raw_weight = min(1.0, parent_norm.geschichts_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.geschichts_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is HistoriographieRegisterGeltung.GRUNDLEGEND_HISTORIOGRAPHISCH)
        normen.append(HistoriographieRegisterNorm(
            historiographie_register_id=new_id,
            geschichts_typ=_TYP_MAP[new_geltung],
            prozedur=_PROZEDUR_MAP[new_geltung],
            geltung=new_geltung,
            geschichts_weight=new_weight,
            geschichts_tier=new_tier,
            canonical=is_canonical,
            geschichts_ids=parent_norm.geschichts_ids + (new_id,),
            geschichts_tags=parent_norm.geschichts_tags + (f"historiographie-register:{new_geltung.value}",),
        ))
    return HistoriographieRegister(
        register_id=register_id,
        geschichts_feld=geschichts_feld,
        normen=tuple(normen),
    )
