"""raumzeit_register — Relativität & Raumzeit layer 2 (#272)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .relativitaets_feld import (
    RelativitaetsFeld,
    RelativitaetsGeltung,
    RelativitaetsNorm,
    RelativitaetsProzedur,
    RelativitaetsTyp,
    build_relativitaets_feld,
)

__all__ = [
    "RaumzeitRang",
    "RaumzeitProzedur",
    "RaumzeitGeltung",
    "RaumzeitNorm",
    "RaumzeitRegister",
    "build_raumzeit_register",
]


class RaumzeitRang(str, Enum):
    SCHUTZ_RAUMZEIT = "schutz-raumzeit"
    ORDNUNGS_RAUMZEIT = "ordnungs-raumzeit"
    SOUVERAENITAETS_RAUMZEIT = "souveraenitaets-raumzeit"


class RaumzeitProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class RaumzeitGeltung(str, Enum):
    GESPERRT = "gesperrt"
    RAUMZEITLICH = "raumzeitlich"
    GRUNDLEGEND_RAUMZEITLICH = "grundlegend-raumzeitlich"


_RANG_MAP: dict[RelativitaetsGeltung, RaumzeitRang] = {
    RelativitaetsGeltung.GESPERRT: RaumzeitRang.SCHUTZ_RAUMZEIT,
    RelativitaetsGeltung.RELATIV: RaumzeitRang.ORDNUNGS_RAUMZEIT,
    RelativitaetsGeltung.GRUNDLEGEND_RELATIV: RaumzeitRang.SOUVERAENITAETS_RAUMZEIT,
}
_PROZEDUR_MAP: dict[RelativitaetsGeltung, RaumzeitProzedur] = {
    RelativitaetsGeltung.GESPERRT: RaumzeitProzedur.NOTPROZEDUR,
    RelativitaetsGeltung.RELATIV: RaumzeitProzedur.REGELPROTOKOLL,
    RelativitaetsGeltung.GRUNDLEGEND_RELATIV: RaumzeitProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[RelativitaetsGeltung, RaumzeitGeltung] = {
    RelativitaetsGeltung.GESPERRT: RaumzeitGeltung.GESPERRT,
    RelativitaetsGeltung.RELATIV: RaumzeitGeltung.RAUMZEITLICH,
    RelativitaetsGeltung.GRUNDLEGEND_RELATIV: RaumzeitGeltung.GRUNDLEGEND_RAUMZEITLICH,
}
_WEIGHT_BONUS: dict[RelativitaetsGeltung, float] = {
    RelativitaetsGeltung.GESPERRT: 0.0,
    RelativitaetsGeltung.RELATIV: 0.04,
    RelativitaetsGeltung.GRUNDLEGEND_RELATIV: 0.08,
}
_TIER_BONUS: dict[RelativitaetsGeltung, int] = {
    RelativitaetsGeltung.GESPERRT: 0,
    RelativitaetsGeltung.RELATIV: 1,
    RelativitaetsGeltung.GRUNDLEGEND_RELATIV: 2,
}


@dataclass(frozen=True)
class RaumzeitNorm:
    raumzeit_register_id: str
    raumzeit_rang: RaumzeitRang
    prozedur: RaumzeitProzedur
    geltung: RaumzeitGeltung
    raumzeit_weight: float
    raumzeit_tier: int
    canonical: bool
    raumzeit_register_ids: tuple[str, ...]
    raumzeit_register_tags: tuple[str, ...]


@dataclass(frozen=True)
class RaumzeitRegister:
    register_id: str
    relativitaets_feld: RelativitaetsFeld
    normen: tuple[RaumzeitNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.raumzeit_register_id for n in self.normen if n.geltung is RaumzeitGeltung.GESPERRT)

    @property
    def raumzeitlich_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.raumzeit_register_id for n in self.normen if n.geltung is RaumzeitGeltung.RAUMZEITLICH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.raumzeit_register_id for n in self.normen if n.geltung is RaumzeitGeltung.GRUNDLEGEND_RAUMZEITLICH)

    @property
    def register_signal(self):
        if any(n.geltung is RaumzeitGeltung.GESPERRT for n in self.normen):
            status = "register-gesperrt"
            severity = "critical"
        elif any(n.geltung is RaumzeitGeltung.RAUMZEITLICH for n in self.normen):
            status = "register-raumzeitlich"
            severity = "warning"
        else:
            status = "register-grundlegend-raumzeitlich"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_raumzeit_register(
    relativitaets_feld: RelativitaetsFeld | None = None,
    *,
    register_id: str = "raumzeit-register",
) -> RaumzeitRegister:
    if relativitaets_feld is None:
        relativitaets_feld = build_relativitaets_feld(feld_id=f"{register_id}-feld")

    normen: list[RaumzeitNorm] = []
    for parent_norm in relativitaets_feld.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{register_id}-{parent_norm.relativitaets_feld_id.removeprefix(f'{relativitaets_feld.feld_id}-')}"
        raw_weight = min(1.0, round(parent_norm.relativitaets_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.relativitaets_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is RaumzeitGeltung.GRUNDLEGEND_RAUMZEITLICH)
        normen.append(
            RaumzeitNorm(
                raumzeit_register_id=new_id,
                raumzeit_rang=_RANG_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                raumzeit_weight=raw_weight,
                raumzeit_tier=new_tier,
                canonical=is_canonical,
                raumzeit_register_ids=parent_norm.relativitaets_feld_ids + (new_id,),
                raumzeit_register_tags=parent_norm.relativitaets_feld_tags + (f"raumzeit-register:{new_geltung.value}",),
            )
        )

    return RaumzeitRegister(
        register_id=register_id,
        relativitaets_feld=relativitaets_feld,
        normen=tuple(normen),
    )
