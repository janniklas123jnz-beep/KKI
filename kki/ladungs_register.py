"""#292 – LadungsRegister: Elektrische Ladung als Governance-Register.

Parent: elektromagnetik_feld (#291)
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .elektromagnetik_feld import (
    ElektromagnetikGeltung,
    ElektromagnetikFeld,
    build_elektromagnetik_feld,
)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class LadungsTyp(Enum):
    SCHUTZ_LADUNG = "schutz-ladung"
    ORDNUNGS_LADUNG = "ordnungs-ladung"
    SOUVERAENITAETS_LADUNG = "souveraenitaets-ladung"


class LadungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class LadungsGeltung(Enum):
    GESPERRT = "gesperrt"
    GELADEN = "geladen"
    GRUNDLEGEND_GELADEN = "grundlegend-geladen"


# ---------------------------------------------------------------------------
# Internal maps
# ---------------------------------------------------------------------------

_GELTUNG_MAP: dict[ElektromagnetikGeltung, LadungsGeltung] = {
    ElektromagnetikGeltung.GESPERRT: LadungsGeltung.GESPERRT,
    ElektromagnetikGeltung.ELEKTROMAGNETISCH: LadungsGeltung.GELADEN,
    ElektromagnetikGeltung.GRUNDLEGEND_ELEKTROMAGNETISCH: LadungsGeltung.GRUNDLEGEND_GELADEN,
}

_TYP_MAP: dict[ElektromagnetikGeltung, LadungsTyp] = {
    ElektromagnetikGeltung.GESPERRT: LadungsTyp.SCHUTZ_LADUNG,
    ElektromagnetikGeltung.ELEKTROMAGNETISCH: LadungsTyp.ORDNUNGS_LADUNG,
    ElektromagnetikGeltung.GRUNDLEGEND_ELEKTROMAGNETISCH: LadungsTyp.SOUVERAENITAETS_LADUNG,
}

_PROZEDUR_MAP: dict[ElektromagnetikGeltung, LadungsProzedur] = {
    ElektromagnetikGeltung.GESPERRT: LadungsProzedur.NOTPROZEDUR,
    ElektromagnetikGeltung.ELEKTROMAGNETISCH: LadungsProzedur.REGELPROTOKOLL,
    ElektromagnetikGeltung.GRUNDLEGEND_ELEKTROMAGNETISCH: LadungsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_BONUS: dict[ElektromagnetikGeltung, float] = {
    ElektromagnetikGeltung.GESPERRT: 0.0,
    ElektromagnetikGeltung.ELEKTROMAGNETISCH: 0.04,
    ElektromagnetikGeltung.GRUNDLEGEND_ELEKTROMAGNETISCH: 0.08,
}

_TIER_BONUS: dict[ElektromagnetikGeltung, int] = {
    ElektromagnetikGeltung.GESPERRT: 0,
    ElektromagnetikGeltung.ELEKTROMAGNETISCH: 1,
    ElektromagnetikGeltung.GRUNDLEGEND_ELEKTROMAGNETISCH: 2,
}

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LadungsNorm:
    ladungs_register_id: str
    ladungs_typ: LadungsTyp
    prozedur: LadungsProzedur
    geltung: LadungsGeltung
    ladungs_weight: float
    ladungs_tier: int
    canonical: bool
    ladungs_ids: tuple[str, ...]
    ladungs_tags: tuple[str, ...]


@dataclass(frozen=True)
class LadungsRegister:
    register_id: str
    elektromagnetik_feld: ElektromagnetikFeld
    normen: tuple[LadungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.ladungs_register_id for n in self.normen if n.geltung is LadungsGeltung.GESPERRT)

    @property
    def geladen_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.ladungs_register_id for n in self.normen if n.geltung is LadungsGeltung.GELADEN)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.ladungs_register_id for n in self.normen if n.geltung is LadungsGeltung.GRUNDLEGEND_GELADEN)

    @property
    def register_signal(self):
        if any(n.geltung is LadungsGeltung.GESPERRT for n in self.normen):
            status = "register-gesperrt"
            severity = "critical"
        elif any(n.geltung is LadungsGeltung.GELADEN for n in self.normen):
            status = "register-geladen"
            severity = "warning"
        else:
            status = "register-grundlegend-geladen"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def build_ladungs_register(
    elektromagnetik_feld: ElektromagnetikFeld | None = None,
    *,
    register_id: str = "ladungs-register",
) -> LadungsRegister:
    if elektromagnetik_feld is None:
        elektromagnetik_feld = build_elektromagnetik_feld(feld_id=f"{register_id}-feld")

    normen: list[LadungsNorm] = []
    for parent_norm in elektromagnetik_feld.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{register_id}-{parent_norm.elektromagnetik_feld_id.removeprefix(f'{elektromagnetik_feld.feld_id}-')}"
        raw_weight = min(1.0, round(parent_norm.elektromagnetik_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.elektromagnetik_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is LadungsGeltung.GRUNDLEGEND_GELADEN)
        normen.append(
            LadungsNorm(
                ladungs_register_id=new_id,
                ladungs_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                ladungs_weight=raw_weight,
                ladungs_tier=new_tier,
                canonical=is_canonical,
                ladungs_ids=parent_norm.elektromagnetik_ids + (new_id,),
                ladungs_tags=parent_norm.elektromagnetik_tags + (f"ladungs-register:{new_geltung.value}",),
            )
        )

    return LadungsRegister(
        register_id=register_id,
        elektromagnetik_feld=elektromagnetik_feld,
        normen=tuple(normen),
    )
