"""
#333 HauptreihenchartaCharta — Hauptreihensterne als stabile Governance-Instanz:
Gleichgewicht zwischen Gravitation und Strahlungsdruck als Governance-Charta.
Geltungsstufen: GESPERRT / HAUPTREIHENSTABIL / GRUNDLEGEND_HAUPTREIHENSTABIL
Parent: ProtostellarRegister (#332)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .protostellar_register import (
    ProtostellarGeltung,
    ProtostellarRegister,
    build_protostellar_register,
)

_GELTUNG_MAP: dict[ProtostellarGeltung, "HauptreihenchartaGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[ProtostellarGeltung.GESPERRT] = HauptreihenchartaGeltung.GESPERRT
    _GELTUNG_MAP[ProtostellarGeltung.PROTOSTELLAR] = HauptreihenchartaGeltung.HAUPTREIHENSTABIL
    _GELTUNG_MAP[ProtostellarGeltung.GRUNDLEGEND_PROTOSTELLAR] = HauptreihenchartaGeltung.GRUNDLEGEND_HAUPTREIHENSTABIL


class HauptreihenchartaTyp(Enum):
    SCHUTZ_HAUPTREIHE = "schutz-hauptreihe"
    ORDNUNGS_HAUPTREIHE = "ordnungs-hauptreihe"
    SOUVERAENITAETS_HAUPTREIHE = "souveraenitaets-hauptreihe"


class HauptreihenchartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class HauptreihenchartaGeltung(Enum):
    GESPERRT = "gesperrt"
    HAUPTREIHENSTABIL = "hauptreihenstabil"
    GRUNDLEGEND_HAUPTREIHENSTABIL = "grundlegend-hauptreihenstabil"


_init_map()

_TYP_MAP: dict[HauptreihenchartaGeltung, HauptreihenchartaTyp] = {
    HauptreihenchartaGeltung.GESPERRT: HauptreihenchartaTyp.SCHUTZ_HAUPTREIHE,
    HauptreihenchartaGeltung.HAUPTREIHENSTABIL: HauptreihenchartaTyp.ORDNUNGS_HAUPTREIHE,
    HauptreihenchartaGeltung.GRUNDLEGEND_HAUPTREIHENSTABIL: HauptreihenchartaTyp.SOUVERAENITAETS_HAUPTREIHE,
}

_PROZEDUR_MAP: dict[HauptreihenchartaGeltung, HauptreihenchartaProzedur] = {
    HauptreihenchartaGeltung.GESPERRT: HauptreihenchartaProzedur.NOTPROZEDUR,
    HauptreihenchartaGeltung.HAUPTREIHENSTABIL: HauptreihenchartaProzedur.REGELPROTOKOLL,
    HauptreihenchartaGeltung.GRUNDLEGEND_HAUPTREIHENSTABIL: HauptreihenchartaProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[HauptreihenchartaGeltung, float] = {
    HauptreihenchartaGeltung.GESPERRT: 0.0,
    HauptreihenchartaGeltung.HAUPTREIHENSTABIL: 0.04,
    HauptreihenchartaGeltung.GRUNDLEGEND_HAUPTREIHENSTABIL: 0.08,
}

_TIER_DELTA: dict[HauptreihenchartaGeltung, int] = {
    HauptreihenchartaGeltung.GESPERRT: 0,
    HauptreihenchartaGeltung.HAUPTREIHENSTABIL: 1,
    HauptreihenchartaGeltung.GRUNDLEGEND_HAUPTREIHENSTABIL: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class HauptreihenchartaNorm:
    hauptreihen_charta_id: str
    hauptreihen_typ: HauptreihenchartaTyp
    prozedur: HauptreihenchartaProzedur
    geltung: HauptreihenchartaGeltung
    hauptreihen_weight: float
    hauptreihen_tier: int
    canonical: bool
    hauptreihen_ids: tuple[str, ...]
    hauptreihen_tags: tuple[str, ...]


@dataclass(frozen=True)
class HauptreihenchartaCharta:
    charta_id: str
    protostellar_register: ProtostellarRegister
    normen: tuple[HauptreihenchartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.hauptreihen_charta_id for n in self.normen if n.geltung is HauptreihenchartaGeltung.GESPERRT)

    @property
    def hauptreihenstabil_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.hauptreihen_charta_id for n in self.normen if n.geltung is HauptreihenchartaGeltung.HAUPTREIHENSTABIL)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.hauptreihen_charta_id for n in self.normen if n.geltung is HauptreihenchartaGeltung.GRUNDLEGEND_HAUPTREIHENSTABIL)

    @property
    def charta_signal(self):
        if any(n.geltung is HauptreihenchartaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is HauptreihenchartaGeltung.HAUPTREIHENSTABIL for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-hauptreihenstabil")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-hauptreihenstabil")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_hauptreihen_charta(
    protostellar_register: ProtostellarRegister | None = None,
    *,
    charta_id: str = "hauptreihen-charta",
) -> HauptreihenchartaCharta:
    if protostellar_register is None:
        protostellar_register = build_protostellar_register(register_id=f"{charta_id}-register")

    normen: list[HauptreihenchartaNorm] = []
    for parent_norm in protostellar_register.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.protostellar_register_id.removeprefix(f'{protostellar_register.register_id}-')}"
        raw_weight = min(1.0, parent_norm.protostellar_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.protostellar_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is HauptreihenchartaGeltung.GRUNDLEGEND_HAUPTREIHENSTABIL)
        normen.append(
            HauptreihenchartaNorm(
                hauptreihen_charta_id=new_id,
                hauptreihen_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                hauptreihen_weight=new_weight,
                hauptreihen_tier=new_tier,
                canonical=is_canonical,
                hauptreihen_ids=parent_norm.protostellar_ids + (new_id,),
                hauptreihen_tags=parent_norm.protostellar_tags + (f"hauptreihe:{new_geltung.value}",),
            )
        )
    return HauptreihenchartaCharta(
        charta_id=charta_id,
        protostellar_register=protostellar_register,
        normen=tuple(normen),
    )
