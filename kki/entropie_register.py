"""#282 – EntropieRegister: Entropie als Ordnungsmaß im Governance-Register.

Parent: thermodynamik_feld (#281)
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .thermodynamik_feld import (
    ThermodynamikGeltung,
    ThermodynamikFeld,
    build_thermodynamik_feld,
)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class EntropieTyp(Enum):
    SCHUTZ_ENTROPIE = "schutz-entropie"
    ORDNUNGS_ENTROPIE = "ordnungs-entropie"
    SOUVERAENITAETS_ENTROPIE = "souveraenitaets-entropie"


class EntropieProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class EntropieGeltung(Enum):
    GESPERRT = "gesperrt"
    ENTROPISCH = "entropisch"
    GRUNDLEGEND_ENTROPISCH = "grundlegend-entropisch"


# ---------------------------------------------------------------------------
# Internal maps
# ---------------------------------------------------------------------------

_GELTUNG_MAP: dict[ThermodynamikGeltung, EntropieGeltung] = {
    ThermodynamikGeltung.GESPERRT: EntropieGeltung.GESPERRT,
    ThermodynamikGeltung.THERMISCH: EntropieGeltung.ENTROPISCH,
    ThermodynamikGeltung.GRUNDLEGEND_THERMISCH: EntropieGeltung.GRUNDLEGEND_ENTROPISCH,
}

_TYP_MAP: dict[ThermodynamikGeltung, EntropieTyp] = {
    ThermodynamikGeltung.GESPERRT: EntropieTyp.SCHUTZ_ENTROPIE,
    ThermodynamikGeltung.THERMISCH: EntropieTyp.ORDNUNGS_ENTROPIE,
    ThermodynamikGeltung.GRUNDLEGEND_THERMISCH: EntropieTyp.SOUVERAENITAETS_ENTROPIE,
}

_PROZEDUR_MAP: dict[ThermodynamikGeltung, EntropieProzedur] = {
    ThermodynamikGeltung.GESPERRT: EntropieProzedur.NOTPROZEDUR,
    ThermodynamikGeltung.THERMISCH: EntropieProzedur.REGELPROTOKOLL,
    ThermodynamikGeltung.GRUNDLEGEND_THERMISCH: EntropieProzedur.PLENARPROTOKOLL,
}

_WEIGHT_BONUS: dict[ThermodynamikGeltung, float] = {
    ThermodynamikGeltung.GESPERRT: 0.0,
    ThermodynamikGeltung.THERMISCH: 0.04,
    ThermodynamikGeltung.GRUNDLEGEND_THERMISCH: 0.08,
}

_TIER_BONUS: dict[ThermodynamikGeltung, int] = {
    ThermodynamikGeltung.GESPERRT: 0,
    ThermodynamikGeltung.THERMISCH: 1,
    ThermodynamikGeltung.GRUNDLEGEND_THERMISCH: 2,
}

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class EntropieNorm:
    entropie_register_id: str
    entropie_typ: EntropieTyp
    prozedur: EntropieProzedur
    geltung: EntropieGeltung
    entropie_weight: float
    entropie_tier: int
    canonical: bool
    entropie_ids: tuple[str, ...]
    entropie_tags: tuple[str, ...]


@dataclass(frozen=True)
class EntropieRegister:
    register_id: str
    thermodynamik_feld: ThermodynamikFeld
    normen: tuple[EntropieNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.entropie_register_id for n in self.normen if n.geltung is EntropieGeltung.GESPERRT)

    @property
    def entropisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.entropie_register_id for n in self.normen if n.geltung is EntropieGeltung.ENTROPISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.entropie_register_id for n in self.normen if n.geltung is EntropieGeltung.GRUNDLEGEND_ENTROPISCH)

    @property
    def register_signal(self):
        if any(n.geltung is EntropieGeltung.GESPERRT for n in self.normen):
            status = "register-gesperrt"
            severity = "critical"
        elif any(n.geltung is EntropieGeltung.ENTROPISCH for n in self.normen):
            status = "register-entropisch"
            severity = "warning"
        else:
            status = "register-grundlegend-entropisch"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def build_entropie_register(
    thermodynamik_feld: ThermodynamikFeld | None = None,
    *,
    register_id: str = "entropie-register",
) -> EntropieRegister:
    if thermodynamik_feld is None:
        thermodynamik_feld = build_thermodynamik_feld(feld_id=f"{register_id}-feld")

    normen: list[EntropieNorm] = []
    for parent_norm in thermodynamik_feld.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{register_id}-{parent_norm.thermodynamik_feld_id.removeprefix(f'{thermodynamik_feld.feld_id}-')}"
        raw_weight = min(1.0, round(parent_norm.thermodynamik_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.thermodynamik_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is EntropieGeltung.GRUNDLEGEND_ENTROPISCH)
        normen.append(
            EntropieNorm(
                entropie_register_id=new_id,
                entropie_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                entropie_weight=raw_weight,
                entropie_tier=new_tier,
                canonical=is_canonical,
                entropie_ids=parent_norm.thermodynamik_ids + (new_id,),
                entropie_tags=parent_norm.thermodynamik_tags + (f"entropie-register:{new_geltung.value}",),
            )
        )

    return EntropieRegister(
        register_id=register_id,
        thermodynamik_feld=thermodynamik_feld,
        normen=tuple(normen),
    )
