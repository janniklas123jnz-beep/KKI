"""#293 – MaxwellCharta: Maxwell-Gleichungen als Governance-Charta.

Parent: ladungs_register (#292)
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .ladungs_register import (
    LadungsGeltung,
    LadungsRegister,
    build_ladungs_register,
)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class MaxwellTyp(Enum):
    SCHUTZ_MAXWELL = "schutz-maxwell"
    ORDNUNGS_MAXWELL = "ordnungs-maxwell"
    SOUVERAENITAETS_MAXWELL = "souveraenitaets-maxwell"


class MaxwellProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class MaxwellGeltung(Enum):
    GESPERRT = "gesperrt"
    MAXWELLISCH = "maxwellisch"
    GRUNDLEGEND_MAXWELLISCH = "grundlegend-maxwellisch"


# ---------------------------------------------------------------------------
# Internal maps
# ---------------------------------------------------------------------------

_GELTUNG_MAP: dict[LadungsGeltung, MaxwellGeltung] = {
    LadungsGeltung.GESPERRT: MaxwellGeltung.GESPERRT,
    LadungsGeltung.GELADEN: MaxwellGeltung.MAXWELLISCH,
    LadungsGeltung.GRUNDLEGEND_GELADEN: MaxwellGeltung.GRUNDLEGEND_MAXWELLISCH,
}

_TYP_MAP: dict[LadungsGeltung, MaxwellTyp] = {
    LadungsGeltung.GESPERRT: MaxwellTyp.SCHUTZ_MAXWELL,
    LadungsGeltung.GELADEN: MaxwellTyp.ORDNUNGS_MAXWELL,
    LadungsGeltung.GRUNDLEGEND_GELADEN: MaxwellTyp.SOUVERAENITAETS_MAXWELL,
}

_PROZEDUR_MAP: dict[LadungsGeltung, MaxwellProzedur] = {
    LadungsGeltung.GESPERRT: MaxwellProzedur.NOTPROZEDUR,
    LadungsGeltung.GELADEN: MaxwellProzedur.REGELPROTOKOLL,
    LadungsGeltung.GRUNDLEGEND_GELADEN: MaxwellProzedur.PLENARPROTOKOLL,
}

_WEIGHT_BONUS: dict[LadungsGeltung, float] = {
    LadungsGeltung.GESPERRT: 0.0,
    LadungsGeltung.GELADEN: 0.04,
    LadungsGeltung.GRUNDLEGEND_GELADEN: 0.08,
}

_TIER_BONUS: dict[LadungsGeltung, int] = {
    LadungsGeltung.GESPERRT: 0,
    LadungsGeltung.GELADEN: 1,
    LadungsGeltung.GRUNDLEGEND_GELADEN: 2,
}

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MaxwellNorm:
    maxwell_charta_id: str
    maxwell_typ: MaxwellTyp
    prozedur: MaxwellProzedur
    geltung: MaxwellGeltung
    maxwell_weight: float
    maxwell_tier: int
    canonical: bool
    maxwell_ids: tuple[str, ...]
    maxwell_tags: tuple[str, ...]


@dataclass(frozen=True)
class MaxwellCharta:
    charta_id: str
    ladungs_register: LadungsRegister
    normen: tuple[MaxwellNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.maxwell_charta_id for n in self.normen if n.geltung is MaxwellGeltung.GESPERRT)

    @property
    def maxwellisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.maxwell_charta_id for n in self.normen if n.geltung is MaxwellGeltung.MAXWELLISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.maxwell_charta_id for n in self.normen if n.geltung is MaxwellGeltung.GRUNDLEGEND_MAXWELLISCH)

    @property
    def charta_signal(self):
        if any(n.geltung is MaxwellGeltung.GESPERRT for n in self.normen):
            status = "charta-gesperrt"
            severity = "critical"
        elif any(n.geltung is MaxwellGeltung.MAXWELLISCH for n in self.normen):
            status = "charta-maxwellisch"
            severity = "warning"
        else:
            status = "charta-grundlegend-maxwellisch"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def build_maxwell_charta(
    ladungs_register: LadungsRegister | None = None,
    *,
    charta_id: str = "maxwell-charta",
) -> MaxwellCharta:
    if ladungs_register is None:
        ladungs_register = build_ladungs_register(register_id=f"{charta_id}-register")

    normen: list[MaxwellNorm] = []
    for parent_norm in ladungs_register.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{charta_id}-{parent_norm.ladungs_register_id.removeprefix(f'{ladungs_register.register_id}-')}"
        raw_weight = min(1.0, round(parent_norm.ladungs_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.ladungs_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is MaxwellGeltung.GRUNDLEGEND_MAXWELLISCH)
        normen.append(
            MaxwellNorm(
                maxwell_charta_id=new_id,
                maxwell_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                maxwell_weight=raw_weight,
                maxwell_tier=new_tier,
                canonical=is_canonical,
                maxwell_ids=parent_norm.ladungs_ids + (new_id,),
                maxwell_tags=parent_norm.ladungs_tags + (f"maxwell-charta:{new_geltung.value}",),
            )
        )

    return MaxwellCharta(
        charta_id=charta_id,
        ladungs_register=ladungs_register,
        normen=tuple(normen),
    )
