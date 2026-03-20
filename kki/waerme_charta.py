"""#283 – WaermeCharta: Wärmeübertragung als Governance-Charta.

Parent: entropie_register (#282)
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .entropie_register import (
    EntropieGeltung,
    EntropieRegister,
    build_entropie_register,
)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class WaermeTyp(Enum):
    SCHUTZ_WAERME = "schutz-waerme"
    ORDNUNGS_WAERME = "ordnungs-waerme"
    SOUVERAENITAETS_WAERME = "souveraenitaets-waerme"


class WaermeProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class WaermeGeltung(Enum):
    GESPERRT = "gesperrt"
    WAERMEUEBERTRAGEN = "waermeuebertragen"
    GRUNDLEGEND_WAERMEUEBERTRAGEN = "grundlegend-waermeuebertragen"


# ---------------------------------------------------------------------------
# Internal maps
# ---------------------------------------------------------------------------

_GELTUNG_MAP: dict[EntropieGeltung, WaermeGeltung] = {
    EntropieGeltung.GESPERRT: WaermeGeltung.GESPERRT,
    EntropieGeltung.ENTROPISCH: WaermeGeltung.WAERMEUEBERTRAGEN,
    EntropieGeltung.GRUNDLEGEND_ENTROPISCH: WaermeGeltung.GRUNDLEGEND_WAERMEUEBERTRAGEN,
}

_TYP_MAP: dict[EntropieGeltung, WaermeTyp] = {
    EntropieGeltung.GESPERRT: WaermeTyp.SCHUTZ_WAERME,
    EntropieGeltung.ENTROPISCH: WaermeTyp.ORDNUNGS_WAERME,
    EntropieGeltung.GRUNDLEGEND_ENTROPISCH: WaermeTyp.SOUVERAENITAETS_WAERME,
}

_PROZEDUR_MAP: dict[EntropieGeltung, WaermeProzedur] = {
    EntropieGeltung.GESPERRT: WaermeProzedur.NOTPROZEDUR,
    EntropieGeltung.ENTROPISCH: WaermeProzedur.REGELPROTOKOLL,
    EntropieGeltung.GRUNDLEGEND_ENTROPISCH: WaermeProzedur.PLENARPROTOKOLL,
}

_WEIGHT_BONUS: dict[EntropieGeltung, float] = {
    EntropieGeltung.GESPERRT: 0.0,
    EntropieGeltung.ENTROPISCH: 0.04,
    EntropieGeltung.GRUNDLEGEND_ENTROPISCH: 0.08,
}

_TIER_BONUS: dict[EntropieGeltung, int] = {
    EntropieGeltung.GESPERRT: 0,
    EntropieGeltung.ENTROPISCH: 1,
    EntropieGeltung.GRUNDLEGEND_ENTROPISCH: 2,
}

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class WaermeNorm:
    waerme_charta_id: str
    waerme_typ: WaermeTyp
    prozedur: WaermeProzedur
    geltung: WaermeGeltung
    waerme_weight: float
    waerme_tier: int
    canonical: bool
    waerme_ids: tuple[str, ...]
    waerme_tags: tuple[str, ...]


@dataclass(frozen=True)
class WaermeCharta:
    charta_id: str
    entropie_register: EntropieRegister
    normen: tuple[WaermeNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.waerme_charta_id for n in self.normen if n.geltung is WaermeGeltung.GESPERRT)

    @property
    def waermeuebertragen_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.waerme_charta_id for n in self.normen if n.geltung is WaermeGeltung.WAERMEUEBERTRAGEN)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.waerme_charta_id for n in self.normen if n.geltung is WaermeGeltung.GRUNDLEGEND_WAERMEUEBERTRAGEN)

    @property
    def charta_signal(self):
        if any(n.geltung is WaermeGeltung.GESPERRT for n in self.normen):
            status = "charta-gesperrt"
            severity = "critical"
        elif any(n.geltung is WaermeGeltung.WAERMEUEBERTRAGEN for n in self.normen):
            status = "charta-waermeuebertragen"
            severity = "warning"
        else:
            status = "charta-grundlegend-waermeuebertragen"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def build_waerme_charta(
    entropie_register: EntropieRegister | None = None,
    *,
    charta_id: str = "waerme-charta",
) -> WaermeCharta:
    if entropie_register is None:
        entropie_register = build_entropie_register(register_id=f"{charta_id}-register")

    normen: list[WaermeNorm] = []
    for parent_norm in entropie_register.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{charta_id}-{parent_norm.entropie_register_id.removeprefix(f'{entropie_register.register_id}-')}"
        raw_weight = min(1.0, round(parent_norm.entropie_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.entropie_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is WaermeGeltung.GRUNDLEGEND_WAERMEUEBERTRAGEN)
        normen.append(
            WaermeNorm(
                waerme_charta_id=new_id,
                waerme_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                waerme_weight=raw_weight,
                waerme_tier=new_tier,
                canonical=is_canonical,
                waerme_ids=parent_norm.entropie_ids + (new_id,),
                waerme_tags=parent_norm.entropie_tags + (f"waerme-charta:{new_geltung.value}",),
            )
        )

    return WaermeCharta(
        charta_id=charta_id,
        entropie_register=entropie_register,
        normen=tuple(normen),
    )
