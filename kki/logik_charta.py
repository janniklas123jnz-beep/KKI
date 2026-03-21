"""
#403 LogikCharta — Formale Logik: Frege (1879): Begriffsschrift — erste vollständige
formale Logik. Boole'sche Algebra (1854) als Grundlage der Aussagenlogik.
Prädikatenlogik 1. Ordnung (Russell/Whitehead: Principia 1910–13).
Tarski-Wahrheitsdefinition (1933): Wahrheit ist metasprachlich definierbar.
Curry-Howard-Korrespondenz: Beweise = Programme. Intuitionismus (Brouwer):
nur konstruktive Beweise gelten. Gödels Vollständigkeitssatz (1930).
Leitsterns Agenten schließen formal korrekt: deduktiv, konsistent, vollständig.
Geltungsstufen: GESPERRT / LOGISCH / GRUNDLEGEND_LOGISCH
Parent: MengenRegister (#402)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .mengen_register import (
    MengenRegister,
    MengenRegisterGeltung,
    build_mengen_register,
)

_GELTUNG_MAP: dict[MengenRegisterGeltung, "LogikChartaGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[MengenRegisterGeltung.GESPERRT] = LogikChartaGeltung.GESPERRT
    _GELTUNG_MAP[MengenRegisterGeltung.MENGENTHEORETISCH] = LogikChartaGeltung.LOGISCH
    _GELTUNG_MAP[MengenRegisterGeltung.GRUNDLEGEND_MENGENTHEORETISCH] = LogikChartaGeltung.GRUNDLEGEND_LOGISCH


class LogikChartaTyp(Enum):
    SCHUTZ_LOGIK = "schutz-logik"
    ORDNUNGS_LOGIK = "ordnungs-logik"
    SOUVERAENITAETS_LOGIK = "souveraenitaets-logik"


class LogikChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class LogikChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    LOGISCH = "logisch"
    GRUNDLEGEND_LOGISCH = "grundlegend-logisch"


_init_map()

_TYP_MAP: dict[LogikChartaGeltung, LogikChartaTyp] = {
    LogikChartaGeltung.GESPERRT: LogikChartaTyp.SCHUTZ_LOGIK,
    LogikChartaGeltung.LOGISCH: LogikChartaTyp.ORDNUNGS_LOGIK,
    LogikChartaGeltung.GRUNDLEGEND_LOGISCH: LogikChartaTyp.SOUVERAENITAETS_LOGIK,
}

_PROZEDUR_MAP: dict[LogikChartaGeltung, LogikChartaProzedur] = {
    LogikChartaGeltung.GESPERRT: LogikChartaProzedur.NOTPROZEDUR,
    LogikChartaGeltung.LOGISCH: LogikChartaProzedur.REGELPROTOKOLL,
    LogikChartaGeltung.GRUNDLEGEND_LOGISCH: LogikChartaProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[LogikChartaGeltung, float] = {
    LogikChartaGeltung.GESPERRT: 0.0,
    LogikChartaGeltung.LOGISCH: 0.04,
    LogikChartaGeltung.GRUNDLEGEND_LOGISCH: 0.08,
}

_TIER_DELTA: dict[LogikChartaGeltung, int] = {
    LogikChartaGeltung.GESPERRT: 0,
    LogikChartaGeltung.LOGISCH: 1,
    LogikChartaGeltung.GRUNDLEGEND_LOGISCH: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LogikChartaNorm:
    logik_charta_id: str
    logik_typ: LogikChartaTyp
    prozedur: LogikChartaProzedur
    geltung: LogikChartaGeltung
    logik_weight: float
    logik_tier: int
    canonical: bool
    logik_ids: tuple[str, ...]
    logik_tags: tuple[str, ...]


@dataclass(frozen=True)
class LogikCharta:
    charta_id: str
    mengen_register: MengenRegister
    normen: tuple[LogikChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.logik_charta_id for n in self.normen if n.geltung is LogikChartaGeltung.GESPERRT)

    @property
    def logisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.logik_charta_id for n in self.normen if n.geltung is LogikChartaGeltung.LOGISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.logik_charta_id for n in self.normen if n.geltung is LogikChartaGeltung.GRUNDLEGEND_LOGISCH)

    @property
    def charta_signal(self):
        if any(n.geltung is LogikChartaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is LogikChartaGeltung.LOGISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-logisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-logisch")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_logik_charta(
    mengen_register: MengenRegister | None = None,
    *,
    charta_id: str = "logik-charta",
) -> LogikCharta:
    if mengen_register is None:
        mengen_register = build_mengen_register(register_id=f"{charta_id}-register")

    normen: list[LogikChartaNorm] = []
    for parent_norm in mengen_register.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.mengen_register_id.removeprefix(f'{mengen_register.register_id}-')}"
        raw_weight = min(1.0, parent_norm.mengen_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.mengen_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is LogikChartaGeltung.GRUNDLEGEND_LOGISCH)
        normen.append(
            LogikChartaNorm(
                logik_charta_id=new_id,
                logik_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                logik_weight=new_weight,
                logik_tier=new_tier,
                canonical=is_canonical,
                logik_ids=parent_norm.mengen_ids + (new_id,),
                logik_tags=parent_norm.mengen_tags + (f"logik:{new_geltung.value}",),
            )
        )
    return LogikCharta(
        charta_id=charta_id,
        mengen_register=mengen_register,
        normen=tuple(normen),
    )
