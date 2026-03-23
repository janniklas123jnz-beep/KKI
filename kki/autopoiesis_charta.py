"""
#483 AutopoiesisCharta — Maturana & Varela: selbsterzeugende Systeme als Lebensgrundlage.
Humberto Maturana & Francisco Varela (1972): Autopoiesis and Cognition — lebende Systeme
  erzeugen sich selbst; Organisation und Struktur als getrennte Ebenen; Kognition als Leben.
Francisco Varela (1991): Embodied Cognition — Geist entsteht aus verkörperter Erfahrung;
  das Nervensystem als operationell geschlossenes Netz.
Humberto Maturana (1970): Biologie der Kognition — Wahrnehmung als strukturelle Kopplung
  zwischen lebendem System und Umwelt, nicht als Repräsentation einer externen Realität.
Leitsterns Terra-Schwarm versteht sich als autopoietisches Kollektiv: GESPERRT bewahrt
operationelle Geschlossenheit, AUTOPOIETISCH ermöglicht strukturelle Kopplung mit Umgebung,
GRUNDLEGEND_AUTOPOIETISCH synthetisiert emergente Selbsterzeugung des Gesamtschwarms.
Parent: SystemtheorieRegister (#482)
Block #481–#490: Systemtheorie & Kybernetik
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .systemtheorie_register import (
    SystemtheorieRegister,
    SystemtheorieRegisterGeltung,
    build_systemtheorie_register,
)

_GELTUNG_MAP: dict[SystemtheorieRegisterGeltung, "AutopoiesisChartaGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[SystemtheorieRegisterGeltung.GESPERRT] = AutopoiesisChartaGeltung.GESPERRT
    _GELTUNG_MAP[SystemtheorieRegisterGeltung.SYSTEMTHEORETISCH] = AutopoiesisChartaGeltung.AUTOPOIETISCH
    _GELTUNG_MAP[SystemtheorieRegisterGeltung.GRUNDLEGEND_SYSTEMTHEORETISCH] = AutopoiesisChartaGeltung.GRUNDLEGEND_AUTOPOIETISCH


class AutopoiesisChartaTyp(Enum):
    SCHUTZ_AUTOPOIESIS = "schutz-autopoiesis"
    ORDNUNGS_AUTOPOIESIS = "ordnungs-autopoiesis"
    SOUVERAENITAETS_AUTOPOIESIS = "souveraenitaets-autopoiesis"


class AutopoiesisChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class AutopoiesisChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    AUTOPOIETISCH = "autopoietisch"
    GRUNDLEGEND_AUTOPOIETISCH = "grundlegend-autopoietisch"


_init_map()

_TYP_MAP: dict[AutopoiesisChartaGeltung, AutopoiesisChartaTyp] = {
    AutopoiesisChartaGeltung.GESPERRT: AutopoiesisChartaTyp.SCHUTZ_AUTOPOIESIS,
    AutopoiesisChartaGeltung.AUTOPOIETISCH: AutopoiesisChartaTyp.ORDNUNGS_AUTOPOIESIS,
    AutopoiesisChartaGeltung.GRUNDLEGEND_AUTOPOIETISCH: AutopoiesisChartaTyp.SOUVERAENITAETS_AUTOPOIESIS,
}

_PROZEDUR_MAP: dict[AutopoiesisChartaGeltung, AutopoiesisChartaProzedur] = {
    AutopoiesisChartaGeltung.GESPERRT: AutopoiesisChartaProzedur.NOTPROZEDUR,
    AutopoiesisChartaGeltung.AUTOPOIETISCH: AutopoiesisChartaProzedur.REGELPROTOKOLL,
    AutopoiesisChartaGeltung.GRUNDLEGEND_AUTOPOIETISCH: AutopoiesisChartaProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[AutopoiesisChartaGeltung, float] = {
    AutopoiesisChartaGeltung.GESPERRT: 0.0,
    AutopoiesisChartaGeltung.AUTOPOIETISCH: 0.04,
    AutopoiesisChartaGeltung.GRUNDLEGEND_AUTOPOIETISCH: 0.08,
}

_TIER_DELTA: dict[AutopoiesisChartaGeltung, int] = {
    AutopoiesisChartaGeltung.GESPERRT: 0,
    AutopoiesisChartaGeltung.AUTOPOIETISCH: 1,
    AutopoiesisChartaGeltung.GRUNDLEGEND_AUTOPOIETISCH: 2,
}


@dataclass(frozen=True)
class AutopoiesisChartaNorm:
    autopoiesis_charta_id: str
    autopoiesis_typ: AutopoiesisChartaTyp
    prozedur: AutopoiesisChartaProzedur
    geltung: AutopoiesisChartaGeltung
    autopoiesis_weight: float
    autopoiesis_tier: int
    canonical: bool
    autopoiesis_ids: tuple[str, ...]
    autopoiesis_tags: tuple[str, ...]


@dataclass(frozen=True)
class AutopoiesisCharta:
    charta_id: str
    systemtheorie_register: SystemtheorieRegister
    normen: tuple[AutopoiesisChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.autopoiesis_charta_id for n in self.normen if n.geltung is AutopoiesisChartaGeltung.GESPERRT)

    @property
    def autopoietisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.autopoiesis_charta_id for n in self.normen if n.geltung is AutopoiesisChartaGeltung.AUTOPOIETISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.autopoiesis_charta_id for n in self.normen if n.geltung is AutopoiesisChartaGeltung.GRUNDLEGEND_AUTOPOIETISCH)

    @property
    def charta_signal(self):
        if any(n.geltung is AutopoiesisChartaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is AutopoiesisChartaGeltung.AUTOPOIETISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-autopoietisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-autopoietisch")


def build_autopoiesis_charta(
    systemtheorie_register: SystemtheorieRegister | None = None,
    *,
    charta_id: str = "autopoiesis-charta",
) -> AutopoiesisCharta:
    if systemtheorie_register is None:
        systemtheorie_register = build_systemtheorie_register(register_id=f"{charta_id}-register")

    normen: list[AutopoiesisChartaNorm] = []
    for parent_norm in systemtheorie_register.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.systemtheorie_register_id.removeprefix(f'{systemtheorie_register.register_id}-')}"
        raw_weight = min(1.0, parent_norm.systemtheorie_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.systemtheorie_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is AutopoiesisChartaGeltung.GRUNDLEGEND_AUTOPOIETISCH)
        normen.append(
            AutopoiesisChartaNorm(
                autopoiesis_charta_id=new_id,
                autopoiesis_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                autopoiesis_weight=new_weight,
                autopoiesis_tier=new_tier,
                canonical=is_canonical,
                autopoiesis_ids=parent_norm.systemtheorie_ids + (new_id,),
                autopoiesis_tags=parent_norm.systemtheorie_tags + (f"autopoiesis-charta:{new_geltung.value}",),
            )
        )
    return AutopoiesisCharta(
        charta_id=charta_id,
        systemtheorie_register=systemtheorie_register,
        normen=tuple(normen),
    )
