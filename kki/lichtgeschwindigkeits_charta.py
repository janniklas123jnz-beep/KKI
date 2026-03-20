"""lichtgeschwindigkeits_charta — Relativität & Raumzeit layer 3 (#273)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .raumzeit_register import (
    RaumzeitGeltung,
    RaumzeitNorm,
    RaumzeitProzedur,
    RaumzeitRang,
    RaumzeitRegister,
    build_raumzeit_register,
)

__all__ = [
    "LichtgeschwindigkeitsTyp",
    "LichtgeschwindigkeitsProzedur",
    "LichtgeschwindigkeitsGeltung",
    "LichtgeschwindigkeitsNorm",
    "LichtgeschwindigkeitsCharta",
    "build_lichtgeschwindigkeits_charta",
]


class LichtgeschwindigkeitsTyp(str, Enum):
    SCHUTZ_LICHT = "schutz-licht"
    ORDNUNGS_LICHT = "ordnungs-licht"
    SOUVERAENITAETS_LICHT = "souveraenitaets-licht"


class LichtgeschwindigkeitsProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class LichtgeschwindigkeitsGeltung(str, Enum):
    GESPERRT = "gesperrt"
    LICHTSCHNELL = "lichtschnell"
    GRUNDLEGEND_LICHTSCHNELL = "grundlegend-lichtschnell"


_TYP_MAP: dict[RaumzeitGeltung, LichtgeschwindigkeitsTyp] = {
    RaumzeitGeltung.GESPERRT: LichtgeschwindigkeitsTyp.SCHUTZ_LICHT,
    RaumzeitGeltung.RAUMZEITLICH: LichtgeschwindigkeitsTyp.ORDNUNGS_LICHT,
    RaumzeitGeltung.GRUNDLEGEND_RAUMZEITLICH: LichtgeschwindigkeitsTyp.SOUVERAENITAETS_LICHT,
}
_PROZEDUR_MAP: dict[RaumzeitGeltung, LichtgeschwindigkeitsProzedur] = {
    RaumzeitGeltung.GESPERRT: LichtgeschwindigkeitsProzedur.NOTPROZEDUR,
    RaumzeitGeltung.RAUMZEITLICH: LichtgeschwindigkeitsProzedur.REGELPROTOKOLL,
    RaumzeitGeltung.GRUNDLEGEND_RAUMZEITLICH: LichtgeschwindigkeitsProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[RaumzeitGeltung, LichtgeschwindigkeitsGeltung] = {
    RaumzeitGeltung.GESPERRT: LichtgeschwindigkeitsGeltung.GESPERRT,
    RaumzeitGeltung.RAUMZEITLICH: LichtgeschwindigkeitsGeltung.LICHTSCHNELL,
    RaumzeitGeltung.GRUNDLEGEND_RAUMZEITLICH: LichtgeschwindigkeitsGeltung.GRUNDLEGEND_LICHTSCHNELL,
}
_WEIGHT_BONUS: dict[RaumzeitGeltung, float] = {
    RaumzeitGeltung.GESPERRT: 0.0,
    RaumzeitGeltung.RAUMZEITLICH: 0.04,
    RaumzeitGeltung.GRUNDLEGEND_RAUMZEITLICH: 0.08,
}
_TIER_BONUS: dict[RaumzeitGeltung, int] = {
    RaumzeitGeltung.GESPERRT: 0,
    RaumzeitGeltung.RAUMZEITLICH: 1,
    RaumzeitGeltung.GRUNDLEGEND_RAUMZEITLICH: 2,
}


@dataclass(frozen=True)
class LichtgeschwindigkeitsNorm:
    lichtgeschwindigkeits_charta_id: str
    lichtgeschwindigkeits_typ: LichtgeschwindigkeitsTyp
    prozedur: LichtgeschwindigkeitsProzedur
    geltung: LichtgeschwindigkeitsGeltung
    lichtgeschwindigkeits_weight: float
    lichtgeschwindigkeits_tier: int
    canonical: bool
    lichtgeschwindigkeits_charta_ids: tuple[str, ...]
    lichtgeschwindigkeits_charta_tags: tuple[str, ...]


@dataclass(frozen=True)
class LichtgeschwindigkeitsCharta:
    charta_id: str
    raumzeit_register: RaumzeitRegister
    normen: tuple[LichtgeschwindigkeitsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.lichtgeschwindigkeits_charta_id for n in self.normen if n.geltung is LichtgeschwindigkeitsGeltung.GESPERRT)

    @property
    def lichtschnell_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.lichtgeschwindigkeits_charta_id for n in self.normen if n.geltung is LichtgeschwindigkeitsGeltung.LICHTSCHNELL)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.lichtgeschwindigkeits_charta_id for n in self.normen if n.geltung is LichtgeschwindigkeitsGeltung.GRUNDLEGEND_LICHTSCHNELL)

    @property
    def charta_signal(self):
        if any(n.geltung is LichtgeschwindigkeitsGeltung.GESPERRT for n in self.normen):
            status = "charta-gesperrt"
            severity = "critical"
        elif any(n.geltung is LichtgeschwindigkeitsGeltung.LICHTSCHNELL for n in self.normen):
            status = "charta-lichtschnell"
            severity = "warning"
        else:
            status = "charta-grundlegend-lichtschnell"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_lichtgeschwindigkeits_charta(
    raumzeit_register: RaumzeitRegister | None = None,
    *,
    charta_id: str = "lichtgeschwindigkeits-charta",
) -> LichtgeschwindigkeitsCharta:
    if raumzeit_register is None:
        raumzeit_register = build_raumzeit_register(register_id=f"{charta_id}-register")

    normen: list[LichtgeschwindigkeitsNorm] = []
    for parent_norm in raumzeit_register.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{charta_id}-{parent_norm.raumzeit_register_id.removeprefix(f'{raumzeit_register.register_id}-')}"
        raw_weight = min(1.0, round(parent_norm.raumzeit_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.raumzeit_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is LichtgeschwindigkeitsGeltung.GRUNDLEGEND_LICHTSCHNELL)
        normen.append(
            LichtgeschwindigkeitsNorm(
                lichtgeschwindigkeits_charta_id=new_id,
                lichtgeschwindigkeits_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                lichtgeschwindigkeits_weight=raw_weight,
                lichtgeschwindigkeits_tier=new_tier,
                canonical=is_canonical,
                lichtgeschwindigkeits_charta_ids=parent_norm.raumzeit_register_ids + (new_id,),
                lichtgeschwindigkeits_charta_tags=parent_norm.raumzeit_register_tags + (f"lichtgeschwindigkeits-charta:{new_geltung.value}",),
            )
        )

    return LichtgeschwindigkeitsCharta(
        charta_id=charta_id,
        raumzeit_register=raumzeit_register,
        normen=tuple(normen),
    )
