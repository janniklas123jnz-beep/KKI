"""
#533 VerfassungsrechtsCharta — Verfassungsrecht & Grundrechtsdogmatik

Hans Kelsen (1934): Reine Rechtslehre — Stufenbau der Rechtsordnung; Grundnorm als
  hypothetische Letztbegründung; Verfassung als oberste positive Rechtsnorm; Trennung
  von Sein und Sollen; Normativismus als Fundament der Verfassungsrechtswissenschaft.
Carl Schmitt (1928): Verfassungslehre — Unterscheidung von Verfassung und Verfassungsgesetz;
  Pouvoir constituant als vorjuridische Entscheidung; Ausnahmezustand als Souveränitätstest;
  Freund-Feind-Unterscheidung als politisches Grundprinzip; Demokratie und Liberalismus.
Ronald Dworkin (1986): Law's Empire — Constitution as integrity; Rechte als Trümpfe gegen
  Mehrheitsentscheidungen; Prinzipien vs. Regeln; Herkules-Richter als Ideal verfassungs-
  rechtlicher Interpretation; Verfassung als moralisch lesbare Grundordnung.
Leitsterns VerfassungsrechtsCharta: Verfassungsrechtliche Normenhierarchie — GESPERRT sichert
konstitutionelle Grundnormen, VERFASSUNGSRECHTLICH kodiert adaptive Grundrechtsanwendung,
GRUNDLEGEND_VERFASSUNGSRECHTLICH synthetisiert souveräne Verfassungsordnung. ⚖️
Parent: RechtssystemRegister (#532)
Block #531–#540: Rechtswissenschaft & Jurisprudenz
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .rechts_system_register import (
    RechtssystemRegister,
    RechtssystemRegisterGeltung,
    build_rechts_system_register,
)

_WEIGHT_DELTA: dict["VerfassungsrechtsChartaGeltung", float] = {}
_TIER_DELTA: dict["VerfassungsrechtsChartaGeltung", int] = {}
_TYP_MAP: dict["VerfassungsrechtsChartaGeltung", "VerfassungsrechtsChartaTyp"] = {}
_PROZEDUR_MAP: dict["VerfassungsrechtsChartaGeltung", "VerfassungsrechtsChartaProzedur"] = {}
_GELTUNG_MAP: dict[RechtssystemRegisterGeltung, "VerfassungsrechtsChartaGeltung"] = {}


def _init_map() -> None:
    _WEIGHT_DELTA.update({
        VerfassungsrechtsChartaGeltung.GESPERRT: 0.0,
        VerfassungsrechtsChartaGeltung.VERFASSUNGSRECHTLICH: 0.05,
        VerfassungsrechtsChartaGeltung.GRUNDLEGEND_VERFASSUNGSRECHTLICH: 0.1,
    })
    _TIER_DELTA.update({
        VerfassungsrechtsChartaGeltung.GESPERRT: 0,
        VerfassungsrechtsChartaGeltung.VERFASSUNGSRECHTLICH: 1,
        VerfassungsrechtsChartaGeltung.GRUNDLEGEND_VERFASSUNGSRECHTLICH: 2,
    })
    _TYP_MAP.update({
        VerfassungsrechtsChartaGeltung.GESPERRT: VerfassungsrechtsChartaTyp.SCHUTZ_VERFASSUNGSRECHT,
        VerfassungsrechtsChartaGeltung.VERFASSUNGSRECHTLICH: VerfassungsrechtsChartaTyp.ORDNUNGS_VERFASSUNGSRECHT,
        VerfassungsrechtsChartaGeltung.GRUNDLEGEND_VERFASSUNGSRECHTLICH: VerfassungsrechtsChartaTyp.SOUVERAENITAETS_VERFASSUNGSRECHT,
    })
    _PROZEDUR_MAP.update({
        VerfassungsrechtsChartaGeltung.GESPERRT: VerfassungsrechtsChartaProzedur.NOTPROZEDUR,
        VerfassungsrechtsChartaGeltung.VERFASSUNGSRECHTLICH: VerfassungsrechtsChartaProzedur.REGELPROTOKOLL,
        VerfassungsrechtsChartaGeltung.GRUNDLEGEND_VERFASSUNGSRECHTLICH: VerfassungsrechtsChartaProzedur.PLENARPROTOKOLL,
    })
    _GELTUNG_MAP.update({
        RechtssystemRegisterGeltung.GESPERRT: VerfassungsrechtsChartaGeltung.GESPERRT,
        RechtssystemRegisterGeltung.RECHTSSYSTEMISCH: VerfassungsrechtsChartaGeltung.VERFASSUNGSRECHTLICH,
        RechtssystemRegisterGeltung.GRUNDLEGEND_RECHTSSYSTEMISCH: VerfassungsrechtsChartaGeltung.GRUNDLEGEND_VERFASSUNGSRECHTLICH,
    })


class VerfassungsrechtsChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    VERFASSUNGSRECHTLICH = "verfassungsrechtlich"
    GRUNDLEGEND_VERFASSUNGSRECHTLICH = "grundlegend-verfassungsrechtlich"


class VerfassungsrechtsChartaTyp(Enum):
    SCHUTZ_VERFASSUNGSRECHT = "schutz-verfassungsrecht"
    ORDNUNGS_VERFASSUNGSRECHT = "ordnungs-verfassungsrecht"
    SOUVERAENITAETS_VERFASSUNGSRECHT = "souveraenitaets-verfassungsrecht"


class VerfassungsrechtsChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


@dataclass(frozen=True)
class VerfassungsrechtsChartaNorm:
    verfassungsrechts_charta_id: str
    verfassungsrechts_typ: VerfassungsrechtsChartaTyp
    prozedur: VerfassungsrechtsChartaProzedur
    geltung: VerfassungsrechtsChartaGeltung
    verfassungsrechts_weight: float
    verfassungsrechts_tier: int
    canonical: bool
    verfassungsrechts_ids: tuple[str, ...]
    verfassungsrechts_tags: tuple[str, ...]


@dataclass(frozen=True)
class VerfassungsrechtsCharta:
    charta_id: str
    rechts_system_register: RechtssystemRegister
    normen: tuple[VerfassungsrechtsChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.verfassungsrechts_charta_id for n in self.normen if n.geltung is VerfassungsrechtsChartaGeltung.GESPERRT)

    @property
    def verfassungsrechtlich_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.verfassungsrechts_charta_id for n in self.normen if n.geltung is VerfassungsrechtsChartaGeltung.VERFASSUNGSRECHTLICH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.verfassungsrechts_charta_id for n in self.normen if n.geltung is VerfassungsrechtsChartaGeltung.GRUNDLEGEND_VERFASSUNGSRECHTLICH)

    @property
    def charta_signal(self):
        if any(n.geltung is VerfassungsrechtsChartaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is VerfassungsrechtsChartaGeltung.VERFASSUNGSRECHTLICH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-verfassungsrechtlich")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-verfassungsrechtlich")


_init_map()


def build_verfassungsrechts_charta(
    rechts_system_register: RechtssystemRegister | None = None,
    *,
    charta_id: str = "verfassungsrechts-charta",
) -> VerfassungsrechtsCharta:
    if rechts_system_register is None:
        rechts_system_register = build_rechts_system_register(
            register_id=f"{charta_id}-register"
        )

    normen: list[VerfassungsrechtsChartaNorm] = []
    for parent_norm in rechts_system_register.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.rechts_system_register_id.removeprefix(f'{rechts_system_register.register_id}-')}"
        raw_weight = min(1.0, parent_norm.rechts_system_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.rechts_system_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is VerfassungsrechtsChartaGeltung.GRUNDLEGEND_VERFASSUNGSRECHTLICH)
        normen.append(
            VerfassungsrechtsChartaNorm(
                verfassungsrechts_charta_id=new_id,
                verfassungsrechts_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                verfassungsrechts_weight=new_weight,
                verfassungsrechts_tier=new_tier,
                canonical=is_canonical,
                verfassungsrechts_ids=parent_norm.rechts_system_ids + (new_id,),
                verfassungsrechts_tags=parent_norm.rechts_system_tags + (f"verfassungsrechts-charta:{new_geltung.value}",),
            )
        )
    return VerfassungsrechtsCharta(
        charta_id=charta_id,
        rechts_system_register=rechts_system_register,
        normen=tuple(normen),
    )
