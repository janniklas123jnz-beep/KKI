"""
#353 DebyeAbschirmungCharta — Die Debye-Länge λ_D = √(ε₀kT/ne²) bestimmt
den Schirmradius des Plasmas: Störungen werden lokal abgeschirmt, globale
Quasi-Neutralität bleibt erhalten. Leitsterns Governance-Architektur folgt
demselben Prinzip — lokale Kapseln schirmen, ohne globale Kohärenz zu brechen.
Geltungsstufen: GESPERRT / DEBYEABGESCHIRMT / GRUNDLEGEND_DEBYEABGESCHIRMT
Parent: MagnetohydrodynamikRegister (#352)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .magnetohydrodynamik_register import (
    MagnetohydrodynamikRegister,
    MagnetohydrodynamikGeltung,
    build_magnetohydrodynamik_register,
)

_GELTUNG_MAP: dict[MagnetohydrodynamikGeltung, "DebyeAbschirmungGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[MagnetohydrodynamikGeltung.GESPERRT] = DebyeAbschirmungGeltung.GESPERRT
    _GELTUNG_MAP[MagnetohydrodynamikGeltung.MAGNETOHYDRODYNAMISCH] = DebyeAbschirmungGeltung.DEBYEABGESCHIRMT
    _GELTUNG_MAP[MagnetohydrodynamikGeltung.GRUNDLEGEND_MAGNETOHYDRODYNAMISCH] = DebyeAbschirmungGeltung.GRUNDLEGEND_DEBYEABGESCHIRMT


class DebyeAbschirmungTyp(Enum):
    SCHUTZ_DEBYE_ABSCHIRMUNG = "schutz-debye-abschirmung"
    ORDNUNGS_DEBYE_ABSCHIRMUNG = "ordnungs-debye-abschirmung"
    SOUVERAENITAETS_DEBYE_ABSCHIRMUNG = "souveraenitaets-debye-abschirmung"


class DebyeAbschirmungProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class DebyeAbschirmungGeltung(Enum):
    GESPERRT = "gesperrt"
    DEBYEABGESCHIRMT = "debyeabgeschirmt"
    GRUNDLEGEND_DEBYEABGESCHIRMT = "grundlegend-debyeabgeschirmt"


_init_map()

_TYP_MAP: dict[DebyeAbschirmungGeltung, DebyeAbschirmungTyp] = {
    DebyeAbschirmungGeltung.GESPERRT: DebyeAbschirmungTyp.SCHUTZ_DEBYE_ABSCHIRMUNG,
    DebyeAbschirmungGeltung.DEBYEABGESCHIRMT: DebyeAbschirmungTyp.ORDNUNGS_DEBYE_ABSCHIRMUNG,
    DebyeAbschirmungGeltung.GRUNDLEGEND_DEBYEABGESCHIRMT: DebyeAbschirmungTyp.SOUVERAENITAETS_DEBYE_ABSCHIRMUNG,
}

_PROZEDUR_MAP: dict[DebyeAbschirmungGeltung, DebyeAbschirmungProzedur] = {
    DebyeAbschirmungGeltung.GESPERRT: DebyeAbschirmungProzedur.NOTPROZEDUR,
    DebyeAbschirmungGeltung.DEBYEABGESCHIRMT: DebyeAbschirmungProzedur.REGELPROTOKOLL,
    DebyeAbschirmungGeltung.GRUNDLEGEND_DEBYEABGESCHIRMT: DebyeAbschirmungProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[DebyeAbschirmungGeltung, float] = {
    DebyeAbschirmungGeltung.GESPERRT: 0.0,
    DebyeAbschirmungGeltung.DEBYEABGESCHIRMT: 0.04,
    DebyeAbschirmungGeltung.GRUNDLEGEND_DEBYEABGESCHIRMT: 0.08,
}

_TIER_DELTA: dict[DebyeAbschirmungGeltung, int] = {
    DebyeAbschirmungGeltung.GESPERRT: 0,
    DebyeAbschirmungGeltung.DEBYEABGESCHIRMT: 1,
    DebyeAbschirmungGeltung.GRUNDLEGEND_DEBYEABGESCHIRMT: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DebyeAbschirmungNorm:
    debye_abschirmung_charta_id: str
    debye_abschirmung_typ: DebyeAbschirmungTyp
    prozedur: DebyeAbschirmungProzedur
    geltung: DebyeAbschirmungGeltung
    debye_abschirmung_weight: float
    debye_abschirmung_tier: int
    canonical: bool
    debye_abschirmung_ids: tuple[str, ...]
    debye_abschirmung_tags: tuple[str, ...]


@dataclass(frozen=True)
class DebyeAbschirmungCharta:
    charta_id: str
    magnetohydrodynamik_register: MagnetohydrodynamikRegister
    normen: tuple[DebyeAbschirmungNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.debye_abschirmung_charta_id for n in self.normen if n.geltung is DebyeAbschirmungGeltung.GESPERRT)

    @property
    def debyeabgeschirmt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.debye_abschirmung_charta_id for n in self.normen if n.geltung is DebyeAbschirmungGeltung.DEBYEABGESCHIRMT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.debye_abschirmung_charta_id for n in self.normen if n.geltung is DebyeAbschirmungGeltung.GRUNDLEGEND_DEBYEABGESCHIRMT)

    @property
    def charta_signal(self):
        if any(n.geltung is DebyeAbschirmungGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is DebyeAbschirmungGeltung.DEBYEABGESCHIRMT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-debyeabgeschirmt")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-debyeabgeschirmt")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_debye_abschirmung_charta(
    magnetohydrodynamik_register: MagnetohydrodynamikRegister | None = None,
    *,
    charta_id: str = "debye-abschirmung-charta",
) -> DebyeAbschirmungCharta:
    if magnetohydrodynamik_register is None:
        magnetohydrodynamik_register = build_magnetohydrodynamik_register(register_id=f"{charta_id}-register")

    normen: list[DebyeAbschirmungNorm] = []
    for parent_norm in magnetohydrodynamik_register.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.magnetohydrodynamik_register_id.removeprefix(f'{magnetohydrodynamik_register.register_id}-')}"
        raw_weight = min(1.0, parent_norm.magnetohydrodynamik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.magnetohydrodynamik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is DebyeAbschirmungGeltung.GRUNDLEGEND_DEBYEABGESCHIRMT)
        normen.append(
            DebyeAbschirmungNorm(
                debye_abschirmung_charta_id=new_id,
                debye_abschirmung_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                debye_abschirmung_weight=new_weight,
                debye_abschirmung_tier=new_tier,
                canonical=is_canonical,
                debye_abschirmung_ids=parent_norm.magnetohydrodynamik_ids + (new_id,),
                debye_abschirmung_tags=parent_norm.magnetohydrodynamik_tags + (f"debye-abschirmung:{new_geltung.value}",),
            )
        )
    return DebyeAbschirmungCharta(
        charta_id=charta_id,
        magnetohydrodynamik_register=magnetohydrodynamik_register,
        normen=tuple(normen),
    )
