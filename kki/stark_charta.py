"""#303 – StarkCharta: Starke Kernkraft als Governance-Charta.

Parent: nukleon_register (#302)
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .nukleon_register import (
    NukleonGeltung,
    NukleonRegister,
    build_nukleon_register,
)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class StarkTyp(Enum):
    SCHUTZ_STARKRAFT = "schutz-starkraft"
    ORDNUNGS_STARKRAFT = "ordnungs-starkraft"
    SOUVERAENITAETS_STARKRAFT = "souveraenitaets-starkraft"


class StarkProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class StarkGeltung(Enum):
    GESPERRT = "gesperrt"
    STARK = "stark"
    GRUNDLEGEND_STARK = "grundlegend-stark"


# ---------------------------------------------------------------------------
# Internal maps
# ---------------------------------------------------------------------------

_GELTUNG_MAP: dict[NukleonGeltung, StarkGeltung] = {
    NukleonGeltung.GESPERRT: StarkGeltung.GESPERRT,
    NukleonGeltung.NUKLEONISCH: StarkGeltung.STARK,
    NukleonGeltung.GRUNDLEGEND_NUKLEONISCH: StarkGeltung.GRUNDLEGEND_STARK,
}

_TYP_MAP: dict[NukleonGeltung, StarkTyp] = {
    NukleonGeltung.GESPERRT: StarkTyp.SCHUTZ_STARKRAFT,
    NukleonGeltung.NUKLEONISCH: StarkTyp.ORDNUNGS_STARKRAFT,
    NukleonGeltung.GRUNDLEGEND_NUKLEONISCH: StarkTyp.SOUVERAENITAETS_STARKRAFT,
}

_PROZEDUR_MAP: dict[NukleonGeltung, StarkProzedur] = {
    NukleonGeltung.GESPERRT: StarkProzedur.NOTPROZEDUR,
    NukleonGeltung.NUKLEONISCH: StarkProzedur.REGELPROTOKOLL,
    NukleonGeltung.GRUNDLEGEND_NUKLEONISCH: StarkProzedur.PLENARPROTOKOLL,
}

_WEIGHT_BONUS: dict[NukleonGeltung, float] = {
    NukleonGeltung.GESPERRT: 0.0,
    NukleonGeltung.NUKLEONISCH: 0.04,
    NukleonGeltung.GRUNDLEGEND_NUKLEONISCH: 0.08,
}

_TIER_BONUS: dict[NukleonGeltung, int] = {
    NukleonGeltung.GESPERRT: 0,
    NukleonGeltung.NUKLEONISCH: 1,
    NukleonGeltung.GRUNDLEGEND_NUKLEONISCH: 2,
}

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class StarkNorm:
    stark_charta_id: str
    stark_typ: StarkTyp
    prozedur: StarkProzedur
    geltung: StarkGeltung
    stark_weight: float
    stark_tier: int
    canonical: bool
    stark_ids: tuple[str, ...]
    stark_tags: tuple[str, ...]


@dataclass(frozen=True)
class StarkCharta:
    charta_id: str
    nukleon_register: NukleonRegister
    normen: tuple[StarkNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.stark_charta_id for n in self.normen if n.geltung is StarkGeltung.GESPERRT)

    @property
    def stark_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.stark_charta_id for n in self.normen if n.geltung is StarkGeltung.STARK)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.stark_charta_id for n in self.normen if n.geltung is StarkGeltung.GRUNDLEGEND_STARK)

    @property
    def charta_signal(self):
        if any(n.geltung is StarkGeltung.GESPERRT for n in self.normen):
            status = "charta-gesperrt"
            severity = "critical"
        elif any(n.geltung is StarkGeltung.STARK for n in self.normen):
            status = "charta-stark"
            severity = "warning"
        else:
            status = "charta-grundlegend-stark"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def build_stark_charta(
    nukleon_register: NukleonRegister | None = None,
    *,
    charta_id: str = "stark-charta",
) -> StarkCharta:
    if nukleon_register is None:
        nukleon_register = build_nukleon_register(register_id=f"{charta_id}-register")

    normen: list[StarkNorm] = []
    for parent_norm in nukleon_register.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{charta_id}-{parent_norm.nukleon_register_id.removeprefix(f'{nukleon_register.register_id}-')}"
        raw_weight = min(1.0, round(parent_norm.nukleon_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.nukleon_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is StarkGeltung.GRUNDLEGEND_STARK)
        normen.append(
            StarkNorm(
                stark_charta_id=new_id,
                stark_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                stark_weight=raw_weight,
                stark_tier=new_tier,
                canonical=is_canonical,
                stark_ids=parent_norm.nukleon_ids + (new_id,),
                stark_tags=parent_norm.nukleon_tags + (f"stark-charta:{new_geltung.value}",),
            )
        )

    return StarkCharta(
        charta_id=charta_id,
        nukleon_register=nukleon_register,
        normen=tuple(normen),
    )
