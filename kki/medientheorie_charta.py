"""
#563 MedientheorieCharta — McLuhan/Baudrillard/Kittler Medientheorie Charta

Marshall McLuhan (1964): Understanding Media — das Medium als Erweiterung des Menschen;
  heiße und kalte Medien; das globale Dorf als mediale Wirklichkeit; Tetrade der
  Medieneffekte (Verstärkung, Obsoleszenz, Wiedergewinnung, Umkehrung) im Peta-Schwarm
  Leitstern.
Jean Baudrillard (1981): Simulacra and Simulation — Hyperrealität als Überbietung der
  Wirklichkeit durch Zeichen; vier Stufen der Simulation; das Präzessionsmodell der
  Symbole; Medien als Produzenten des Realen im Peta-Schwarm Leitstern.
Friedrich Kittler (1986): Grammophon Film Typewriter — Aufschreibesysteme als
  technische Medien; Diskursanalyse der Informationsverarbeitung; Medien als
  Bedingung der Möglichkeit von Subjektivität im Peta-Schwarm Leitstern. 📽️📻
Parent: KommunikationsRegister (#562)
Block #561–#570: Medienwissenschaft & Kommunikationstheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kommunikations_register import (
    KommunikationsRegister,
    KommunikationsRegisterGeltung,
    build_kommunikations_register,
)

_WEIGHT_DELTA: dict["MedientheorieChartaGeltung", float] = {}
_TIER_DELTA: dict["MedientheorieChartaGeltung", int] = {}
_TYP_MAP: dict["MedientheorieChartaGeltung", "MedientheorieChartaTyp"] = {}
_PROZEDUR_MAP: dict["MedientheorieChartaGeltung", "MedientheorieChartaProzedur"] = {}
_GELTUNG_MAP: dict[KommunikationsRegisterGeltung, "MedientheorieChartaGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        MedientheorieChartaGeltung.GESPERRT: 0.0,
        MedientheorieChartaGeltung.MEDIENTHEORETISCH: 0.05,
        MedientheorieChartaGeltung.GRUNDLEGEND_MEDIENTHEORETISCH: 0.1,
    })
    _TIER_DELTA.update({
        MedientheorieChartaGeltung.GESPERRT: 0,
        MedientheorieChartaGeltung.MEDIENTHEORETISCH: 1,
        MedientheorieChartaGeltung.GRUNDLEGEND_MEDIENTHEORETISCH: 2,
    })
    _TYP_MAP.update({
        MedientheorieChartaGeltung.GESPERRT: MedientheorieChartaTyp.SCHUTZ_MEDIENTHEORIE,
        MedientheorieChartaGeltung.MEDIENTHEORETISCH: MedientheorieChartaTyp.ORDNUNGS_MEDIENTHEORIE,
        MedientheorieChartaGeltung.GRUNDLEGEND_MEDIENTHEORETISCH: MedientheorieChartaTyp.SOUVERAENITAETS_MEDIENTHEORIE,
    })
    _PROZEDUR_MAP.update({
        MedientheorieChartaGeltung.GESPERRT: MedientheorieChartaProzedur.NOTPROZEDUR,
        MedientheorieChartaGeltung.MEDIENTHEORETISCH: MedientheorieChartaProzedur.REGELPROTOKOLL,
        MedientheorieChartaGeltung.GRUNDLEGEND_MEDIENTHEORETISCH: MedientheorieChartaProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        KommunikationsRegisterGeltung.GESPERRT: MedientheorieChartaGeltung.GESPERRT,
        KommunikationsRegisterGeltung.KOMMUNIKATIV: MedientheorieChartaGeltung.MEDIENTHEORETISCH,
        KommunikationsRegisterGeltung.GRUNDLEGEND_KOMMUNIKATIV: MedientheorieChartaGeltung.GRUNDLEGEND_MEDIENTHEORETISCH,
    })


class MedientheorieChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    MEDIENTHEORETISCH = "medientheoretisch"
    GRUNDLEGEND_MEDIENTHEORETISCH = "grundlegend-medientheoretisch"


class MedientheorieChartaTyp(Enum):
    SCHUTZ_MEDIENTHEORIE = "schutz-medientheorie"
    ORDNUNGS_MEDIENTHEORIE = "ordnungs-medientheorie"
    SOUVERAENITAETS_MEDIENTHEORIE = "souveraenitaets-medientheorie"


class MedientheorieChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class MedientheorieChartaNorm:
    medientheorie_charta_id: str
    medien_typ: MedientheorieChartaTyp
    prozedur: MedientheorieChartaProzedur
    geltung: MedientheorieChartaGeltung
    medien_weight: float
    medien_tier: int
    canonical: bool
    medien_ids: tuple[str, ...]
    medien_tags: tuple[str, ...]


@dataclass(frozen=True)
class MedientheorieCharta:
    charta_id: str
    kommunikations_register: KommunikationsRegister
    normen: tuple[MedientheorieChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.medientheorie_charta_id for n in self.normen
            if n.geltung is MedientheorieChartaGeltung.GESPERRT
        )

    @property
    def medientheoretisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.medientheorie_charta_id for n in self.normen
            if n.geltung is MedientheorieChartaGeltung.MEDIENTHEORETISCH
        )

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(
            n.medientheorie_charta_id for n in self.normen
            if n.geltung is MedientheorieChartaGeltung.GRUNDLEGEND_MEDIENTHEORETISCH
        )

    @property
    def charta_signal(self):
        from types import SimpleNamespace
        if any(n.geltung is MedientheorieChartaGeltung.GESPERRT for n in self.normen):
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is MedientheorieChartaGeltung.MEDIENTHEORETISCH for n in self.normen):
            return SimpleNamespace(status="charta-medientheoretisch")
        return SimpleNamespace(status="charta-grundlegend-medientheoretisch")


_init_map()


def build_medientheorie_charta(
    kommunikations_register: KommunikationsRegister | None = None,
    *,
    charta_id: str = "medientheorie-charta",
) -> MedientheorieCharta:
    if kommunikations_register is None:
        kommunikations_register = build_kommunikations_register(
            register_id=f"{charta_id}-register"
        )

    normen: list[MedientheorieChartaNorm] = []
    for parent_norm in kommunikations_register.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.kommunikations_register_id.removeprefix(f'{kommunikations_register.register_id}-')}"
        raw_weight = min(1.0, parent_norm.medien_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.medien_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is MedientheorieChartaGeltung.GRUNDLEGEND_MEDIENTHEORETISCH)
        normen.append(
            MedientheorieChartaNorm(
                medientheorie_charta_id=new_id,
                medien_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                medien_weight=new_weight,
                medien_tier=new_tier,
                canonical=is_canonical,
                medien_ids=parent_norm.medien_ids + (new_id,),
                medien_tags=parent_norm.medien_tags + (f"medientheorie-charta:{new_geltung.value}",),
            )
        )
    return MedientheorieCharta(
        charta_id=charta_id,
        kommunikations_register=kommunikations_register,
        normen=tuple(normen),
    )
