"""#304 – SchwachKodex: Schwache Kernkraft als Governance-Kodex.

Parent: stark_charta (#303)
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .stark_charta import (
    StarkGeltung,
    StarkCharta,
    build_stark_charta,
)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class SchwachTyp(Enum):
    SCHUTZ_SCHWACHKRAFT = "schutz-schwachkraft"
    ORDNUNGS_SCHWACHKRAFT = "ordnungs-schwachkraft"
    SOUVERAENITAETS_SCHWACHKRAFT = "souveraenitaets-schwachkraft"


class SchwachProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class SchwachGeltung(Enum):
    GESPERRT = "gesperrt"
    SCHWACH = "schwach"
    GRUNDLEGEND_SCHWACH = "grundlegend-schwach"


# ---------------------------------------------------------------------------
# Internal maps
# ---------------------------------------------------------------------------

_GELTUNG_MAP: dict[StarkGeltung, SchwachGeltung] = {
    StarkGeltung.GESPERRT: SchwachGeltung.GESPERRT,
    StarkGeltung.STARK: SchwachGeltung.SCHWACH,
    StarkGeltung.GRUNDLEGEND_STARK: SchwachGeltung.GRUNDLEGEND_SCHWACH,
}

_TYP_MAP: dict[StarkGeltung, SchwachTyp] = {
    StarkGeltung.GESPERRT: SchwachTyp.SCHUTZ_SCHWACHKRAFT,
    StarkGeltung.STARK: SchwachTyp.ORDNUNGS_SCHWACHKRAFT,
    StarkGeltung.GRUNDLEGEND_STARK: SchwachTyp.SOUVERAENITAETS_SCHWACHKRAFT,
}

_PROZEDUR_MAP: dict[StarkGeltung, SchwachProzedur] = {
    StarkGeltung.GESPERRT: SchwachProzedur.NOTPROZEDUR,
    StarkGeltung.STARK: SchwachProzedur.REGELPROTOKOLL,
    StarkGeltung.GRUNDLEGEND_STARK: SchwachProzedur.PLENARPROTOKOLL,
}

_WEIGHT_BONUS: dict[StarkGeltung, float] = {
    StarkGeltung.GESPERRT: 0.0,
    StarkGeltung.STARK: 0.04,
    StarkGeltung.GRUNDLEGEND_STARK: 0.08,
}

_TIER_BONUS: dict[StarkGeltung, int] = {
    StarkGeltung.GESPERRT: 0,
    StarkGeltung.STARK: 1,
    StarkGeltung.GRUNDLEGEND_STARK: 2,
}

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SchwachNorm:
    schwach_kodex_id: str
    schwach_typ: SchwachTyp
    prozedur: SchwachProzedur
    geltung: SchwachGeltung
    schwach_weight: float
    schwach_tier: int
    canonical: bool
    schwach_ids: tuple[str, ...]
    schwach_tags: tuple[str, ...]


@dataclass(frozen=True)
class SchwachKodex:
    kodex_id: str
    stark_charta: StarkCharta
    normen: tuple[SchwachNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.schwach_kodex_id for n in self.normen if n.geltung is SchwachGeltung.GESPERRT)

    @property
    def schwach_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.schwach_kodex_id for n in self.normen if n.geltung is SchwachGeltung.SCHWACH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.schwach_kodex_id for n in self.normen if n.geltung is SchwachGeltung.GRUNDLEGEND_SCHWACH)

    @property
    def kodex_signal(self):
        if any(n.geltung is SchwachGeltung.GESPERRT for n in self.normen):
            status = "kodex-gesperrt"
            severity = "critical"
        elif any(n.geltung is SchwachGeltung.SCHWACH for n in self.normen):
            status = "kodex-schwach"
            severity = "warning"
        else:
            status = "kodex-grundlegend-schwach"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def build_schwach_kodex(
    stark_charta: StarkCharta | None = None,
    *,
    kodex_id: str = "schwach-kodex",
) -> SchwachKodex:
    if stark_charta is None:
        stark_charta = build_stark_charta(charta_id=f"{kodex_id}-charta")

    normen: list[SchwachNorm] = []
    for parent_norm in stark_charta.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{kodex_id}-{parent_norm.stark_charta_id.removeprefix(f'{stark_charta.charta_id}-')}"
        raw_weight = min(1.0, round(parent_norm.stark_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.stark_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SchwachGeltung.GRUNDLEGEND_SCHWACH)
        normen.append(
            SchwachNorm(
                schwach_kodex_id=new_id,
                schwach_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                schwach_weight=raw_weight,
                schwach_tier=new_tier,
                canonical=is_canonical,
                schwach_ids=parent_norm.stark_ids + (new_id,),
                schwach_tags=parent_norm.stark_tags + (f"schwach-kodex:{new_geltung.value}",),
            )
        )

    return SchwachKodex(
        kodex_id=kodex_id,
        stark_charta=stark_charta,
        normen=tuple(normen),
    )
