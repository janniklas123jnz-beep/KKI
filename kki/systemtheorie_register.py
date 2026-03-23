"""
#482 SystemtheorieRegister — Luhmann: Soziale Systeme als autopoietische Kommunikation.
Niklas Luhmann (1984): Soziale Systeme — Funktionssysteme operieren selbstreferenziell;
  strukturelle Kopplung verbindet Systeme ohne Verschmelzung; Kommunikation als Grundelement.
Talcott Parsons (1951): AGIL-Schema — Adaption, Goal Attainment, Integration, Latency;
  Funktionale Differenzierung als Merkmal moderner Gesellschaften.
Leitsterns Terra-Schwarm registriert Systemgrenzen: GESPERRT sichert Systemidentität,
SYSTEMTHEORETISCH ermöglicht funktionale Differenzierung, GRUNDLEGEND_SYSTEMTHEORETISCH
synthetisiert die Beobachtung zweiter Ordnung über alle Teilsysteme.
Parent: KybernetikFeld (#481)
Block #481–#490: Systemtheorie & Kybernetik
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kybernetik_feld import (
    KybernetikFeld,
    KybernetikFeldGeltung,
    build_kybernetik_feld,
)

_GELTUNG_MAP: dict[KybernetikFeldGeltung, "SystemtheorieRegisterGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[KybernetikFeldGeltung.GESPERRT] = SystemtheorieRegisterGeltung.GESPERRT
    _GELTUNG_MAP[KybernetikFeldGeltung.KYBERNETISCH] = SystemtheorieRegisterGeltung.SYSTEMTHEORETISCH
    _GELTUNG_MAP[KybernetikFeldGeltung.GRUNDLEGEND_KYBERNETISCH] = SystemtheorieRegisterGeltung.GRUNDLEGEND_SYSTEMTHEORETISCH


class SystemtheorieRegisterTyp(Enum):
    SCHUTZ_SYSTEMTHEORIE = "schutz-systemtheorie"
    ORDNUNGS_SYSTEMTHEORIE = "ordnungs-systemtheorie"
    SOUVERAENITAETS_SYSTEMTHEORIE = "souveraenitaets-systemtheorie"


class SystemtheorieRegisterProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class SystemtheorieRegisterGeltung(Enum):
    GESPERRT = "gesperrt"
    SYSTEMTHEORETISCH = "systemtheoretisch"
    GRUNDLEGEND_SYSTEMTHEORETISCH = "grundlegend-systemtheoretisch"


_init_map()

_TYP_MAP: dict[SystemtheorieRegisterGeltung, SystemtheorieRegisterTyp] = {
    SystemtheorieRegisterGeltung.GESPERRT: SystemtheorieRegisterTyp.SCHUTZ_SYSTEMTHEORIE,
    SystemtheorieRegisterGeltung.SYSTEMTHEORETISCH: SystemtheorieRegisterTyp.ORDNUNGS_SYSTEMTHEORIE,
    SystemtheorieRegisterGeltung.GRUNDLEGEND_SYSTEMTHEORETISCH: SystemtheorieRegisterTyp.SOUVERAENITAETS_SYSTEMTHEORIE,
}

_PROZEDUR_MAP: dict[SystemtheorieRegisterGeltung, SystemtheorieRegisterProzedur] = {
    SystemtheorieRegisterGeltung.GESPERRT: SystemtheorieRegisterProzedur.NOTPROZEDUR,
    SystemtheorieRegisterGeltung.SYSTEMTHEORETISCH: SystemtheorieRegisterProzedur.REGELPROTOKOLL,
    SystemtheorieRegisterGeltung.GRUNDLEGEND_SYSTEMTHEORETISCH: SystemtheorieRegisterProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[SystemtheorieRegisterGeltung, float] = {
    SystemtheorieRegisterGeltung.GESPERRT: 0.0,
    SystemtheorieRegisterGeltung.SYSTEMTHEORETISCH: 0.04,
    SystemtheorieRegisterGeltung.GRUNDLEGEND_SYSTEMTHEORETISCH: 0.08,
}

_TIER_DELTA: dict[SystemtheorieRegisterGeltung, int] = {
    SystemtheorieRegisterGeltung.GESPERRT: 0,
    SystemtheorieRegisterGeltung.SYSTEMTHEORETISCH: 1,
    SystemtheorieRegisterGeltung.GRUNDLEGEND_SYSTEMTHEORETISCH: 2,
}


@dataclass(frozen=True)
class SystemtheorieRegisterNorm:
    systemtheorie_register_id: str
    systemtheorie_typ: SystemtheorieRegisterTyp
    prozedur: SystemtheorieRegisterProzedur
    geltung: SystemtheorieRegisterGeltung
    systemtheorie_weight: float
    systemtheorie_tier: int
    canonical: bool
    systemtheorie_ids: tuple[str, ...]
    systemtheorie_tags: tuple[str, ...]


@dataclass(frozen=True)
class SystemtheorieRegister:
    register_id: str
    kybernetik_feld: KybernetikFeld
    normen: tuple[SystemtheorieRegisterNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.systemtheorie_register_id for n in self.normen if n.geltung is SystemtheorieRegisterGeltung.GESPERRT)

    @property
    def systemtheoretisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.systemtheorie_register_id for n in self.normen if n.geltung is SystemtheorieRegisterGeltung.SYSTEMTHEORETISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.systemtheorie_register_id for n in self.normen if n.geltung is SystemtheorieRegisterGeltung.GRUNDLEGEND_SYSTEMTHEORETISCH)

    @property
    def register_signal(self):
        if any(n.geltung is SystemtheorieRegisterGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-gesperrt")
        elif any(n.geltung is SystemtheorieRegisterGeltung.SYSTEMTHEORETISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-systemtheoretisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="register-grundlegend-systemtheoretisch")


def build_systemtheorie_register(
    kybernetik_feld: KybernetikFeld | None = None,
    *,
    register_id: str = "systemtheorie-register",
) -> SystemtheorieRegister:
    if kybernetik_feld is None:
        kybernetik_feld = build_kybernetik_feld(feld_id=f"{register_id}-feld")

    normen: list[SystemtheorieRegisterNorm] = []
    for parent_norm in kybernetik_feld.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{register_id}-{parent_norm.kybernetik_feld_id.removeprefix(f'{kybernetik_feld.feld_id}-')}"
        raw_weight = min(1.0, parent_norm.kybernetik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kybernetik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SystemtheorieRegisterGeltung.GRUNDLEGEND_SYSTEMTHEORETISCH)
        normen.append(
            SystemtheorieRegisterNorm(
                systemtheorie_register_id=new_id,
                systemtheorie_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                systemtheorie_weight=new_weight,
                systemtheorie_tier=new_tier,
                canonical=is_canonical,
                systemtheorie_ids=parent_norm.kybernetik_ids + (new_id,),
                systemtheorie_tags=parent_norm.kybernetik_tags + (f"systemtheorie-register:{new_geltung.value}",),
            )
        )
    return SystemtheorieRegister(
        register_id=register_id,
        kybernetik_feld=kybernetik_feld,
        normen=tuple(normen),
    )
