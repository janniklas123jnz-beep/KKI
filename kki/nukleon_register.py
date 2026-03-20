"""#302 – NukleonRegister: Nukleonen als Governance-Register.

Parent: kernphysik_feld (#301)
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kernphysik_feld import (
    KernphysikGeltung,
    KernphysikFeld,
    build_kernphysik_feld,
)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class NukleonTyp(Enum):
    SCHUTZ_NUKLEON = "schutz-nukleon"
    ORDNUNGS_NUKLEON = "ordnungs-nukleon"
    SOUVERAENITAETS_NUKLEON = "souveraenitaets-nukleon"


class NukleonProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class NukleonGeltung(Enum):
    GESPERRT = "gesperrt"
    NUKLEONISCH = "nukleonisch"
    GRUNDLEGEND_NUKLEONISCH = "grundlegend-nukleonisch"


# ---------------------------------------------------------------------------
# Internal maps
# ---------------------------------------------------------------------------

_GELTUNG_MAP: dict[KernphysikGeltung, NukleonGeltung] = {
    KernphysikGeltung.GESPERRT: NukleonGeltung.GESPERRT,
    KernphysikGeltung.KERNPHYSIKALISCH: NukleonGeltung.NUKLEONISCH,
    KernphysikGeltung.GRUNDLEGEND_KERNPHYSIKALISCH: NukleonGeltung.GRUNDLEGEND_NUKLEONISCH,
}

_TYP_MAP: dict[KernphysikGeltung, NukleonTyp] = {
    KernphysikGeltung.GESPERRT: NukleonTyp.SCHUTZ_NUKLEON,
    KernphysikGeltung.KERNPHYSIKALISCH: NukleonTyp.ORDNUNGS_NUKLEON,
    KernphysikGeltung.GRUNDLEGEND_KERNPHYSIKALISCH: NukleonTyp.SOUVERAENITAETS_NUKLEON,
}

_PROZEDUR_MAP: dict[KernphysikGeltung, NukleonProzedur] = {
    KernphysikGeltung.GESPERRT: NukleonProzedur.NOTPROZEDUR,
    KernphysikGeltung.KERNPHYSIKALISCH: NukleonProzedur.REGELPROTOKOLL,
    KernphysikGeltung.GRUNDLEGEND_KERNPHYSIKALISCH: NukleonProzedur.PLENARPROTOKOLL,
}

_WEIGHT_BONUS: dict[KernphysikGeltung, float] = {
    KernphysikGeltung.GESPERRT: 0.0,
    KernphysikGeltung.KERNPHYSIKALISCH: 0.04,
    KernphysikGeltung.GRUNDLEGEND_KERNPHYSIKALISCH: 0.08,
}

_TIER_BONUS: dict[KernphysikGeltung, int] = {
    KernphysikGeltung.GESPERRT: 0,
    KernphysikGeltung.KERNPHYSIKALISCH: 1,
    KernphysikGeltung.GRUNDLEGEND_KERNPHYSIKALISCH: 2,
}

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class NukleonNorm:
    nukleon_register_id: str
    nukleon_typ: NukleonTyp
    prozedur: NukleonProzedur
    geltung: NukleonGeltung
    nukleon_weight: float
    nukleon_tier: int
    canonical: bool
    nukleon_ids: tuple[str, ...]
    nukleon_tags: tuple[str, ...]


@dataclass(frozen=True)
class NukleonRegister:
    register_id: str
    kernphysik_feld: KernphysikFeld
    normen: tuple[NukleonNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.nukleon_register_id for n in self.normen if n.geltung is NukleonGeltung.GESPERRT)

    @property
    def nukleonisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.nukleon_register_id for n in self.normen if n.geltung is NukleonGeltung.NUKLEONISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.nukleon_register_id for n in self.normen if n.geltung is NukleonGeltung.GRUNDLEGEND_NUKLEONISCH)

    @property
    def register_signal(self):
        if any(n.geltung is NukleonGeltung.GESPERRT for n in self.normen):
            status = "register-gesperrt"
            severity = "critical"
        elif any(n.geltung is NukleonGeltung.NUKLEONISCH for n in self.normen):
            status = "register-nukleonisch"
            severity = "warning"
        else:
            status = "register-grundlegend-nukleonisch"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def build_nukleon_register(
    kernphysik_feld: KernphysikFeld | None = None,
    *,
    register_id: str = "nukleon-register",
) -> NukleonRegister:
    if kernphysik_feld is None:
        kernphysik_feld = build_kernphysik_feld(feld_id=f"{register_id}-feld")

    normen: list[NukleonNorm] = []
    for parent_norm in kernphysik_feld.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{register_id}-{parent_norm.kernphysik_feld_id.removeprefix(f'{kernphysik_feld.feld_id}-')}"
        raw_weight = min(1.0, round(parent_norm.kernphysik_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.kernphysik_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is NukleonGeltung.GRUNDLEGEND_NUKLEONISCH)
        normen.append(
            NukleonNorm(
                nukleon_register_id=new_id,
                nukleon_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                nukleon_weight=raw_weight,
                nukleon_tier=new_tier,
                canonical=is_canonical,
                nukleon_ids=parent_norm.kernphysik_ids + (new_id,),
                nukleon_tags=parent_norm.kernphysik_tags + (f"nukleon-register:{new_geltung.value}",),
            )
        )

    return NukleonRegister(
        register_id=register_id,
        kernphysik_feld=kernphysik_feld,
        normen=tuple(normen),
    )
