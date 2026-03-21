"""
#352 MagnetohydrodynamikRegister — MHD: Plasma als vollständig leitfähige
Governance-Flüssigkeit. Die gekoppelten Maxwell-Navier-Stokes-Gleichungen
regeln Fluss, Druck und Magnetfeld gleichzeitig — totale Kohärenz als Prinzip.
Geltungsstufen: GESPERRT / MAGNETOHYDRODYNAMISCH / GRUNDLEGEND_MAGNETOHYDRODYNAMISCH
Parent: PlasmaFeld (#351)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .plasma_feld import (
    PlasmaFeld,
    PlasmaGeltung,
    build_plasma_feld,
)

_GELTUNG_MAP: dict[PlasmaGeltung, "MagnetohydrodynamikGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[PlasmaGeltung.GESPERRT] = MagnetohydrodynamikGeltung.GESPERRT
    _GELTUNG_MAP[PlasmaGeltung.PLASMATISCH] = MagnetohydrodynamikGeltung.MAGNETOHYDRODYNAMISCH
    _GELTUNG_MAP[PlasmaGeltung.GRUNDLEGEND_PLASMATISCH] = MagnetohydrodynamikGeltung.GRUNDLEGEND_MAGNETOHYDRODYNAMISCH


class MagnetohydrodynamikTyp(Enum):
    SCHUTZ_MAGNETOHYDRODYNAMIK = "schutz-magnetohydrodynamik"
    ORDNUNGS_MAGNETOHYDRODYNAMIK = "ordnungs-magnetohydrodynamik"
    SOUVERAENITAETS_MAGNETOHYDRODYNAMIK = "souveraenitaets-magnetohydrodynamik"


class MagnetohydrodynamikProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class MagnetohydrodynamikGeltung(Enum):
    GESPERRT = "gesperrt"
    MAGNETOHYDRODYNAMISCH = "magnetohydrodynamisch"
    GRUNDLEGEND_MAGNETOHYDRODYNAMISCH = "grundlegend-magnetohydrodynamisch"


_init_map()

_TYP_MAP: dict[MagnetohydrodynamikGeltung, MagnetohydrodynamikTyp] = {
    MagnetohydrodynamikGeltung.GESPERRT: MagnetohydrodynamikTyp.SCHUTZ_MAGNETOHYDRODYNAMIK,
    MagnetohydrodynamikGeltung.MAGNETOHYDRODYNAMISCH: MagnetohydrodynamikTyp.ORDNUNGS_MAGNETOHYDRODYNAMIK,
    MagnetohydrodynamikGeltung.GRUNDLEGEND_MAGNETOHYDRODYNAMISCH: MagnetohydrodynamikTyp.SOUVERAENITAETS_MAGNETOHYDRODYNAMIK,
}

_PROZEDUR_MAP: dict[MagnetohydrodynamikGeltung, MagnetohydrodynamikProzedur] = {
    MagnetohydrodynamikGeltung.GESPERRT: MagnetohydrodynamikProzedur.NOTPROZEDUR,
    MagnetohydrodynamikGeltung.MAGNETOHYDRODYNAMISCH: MagnetohydrodynamikProzedur.REGELPROTOKOLL,
    MagnetohydrodynamikGeltung.GRUNDLEGEND_MAGNETOHYDRODYNAMISCH: MagnetohydrodynamikProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[MagnetohydrodynamikGeltung, float] = {
    MagnetohydrodynamikGeltung.GESPERRT: 0.0,
    MagnetohydrodynamikGeltung.MAGNETOHYDRODYNAMISCH: 0.04,
    MagnetohydrodynamikGeltung.GRUNDLEGEND_MAGNETOHYDRODYNAMISCH: 0.08,
}

_TIER_DELTA: dict[MagnetohydrodynamikGeltung, int] = {
    MagnetohydrodynamikGeltung.GESPERRT: 0,
    MagnetohydrodynamikGeltung.MAGNETOHYDRODYNAMISCH: 1,
    MagnetohydrodynamikGeltung.GRUNDLEGEND_MAGNETOHYDRODYNAMISCH: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MagnetohydrodynamikNorm:
    magnetohydrodynamik_register_id: str
    magnetohydrodynamik_typ: MagnetohydrodynamikTyp
    prozedur: MagnetohydrodynamikProzedur
    geltung: MagnetohydrodynamikGeltung
    magnetohydrodynamik_weight: float
    magnetohydrodynamik_tier: int
    canonical: bool
    magnetohydrodynamik_ids: tuple[str, ...]
    magnetohydrodynamik_tags: tuple[str, ...]


@dataclass(frozen=True)
class MagnetohydrodynamikRegister:
    register_id: str
    plasma_feld: PlasmaFeld
    normen: tuple[MagnetohydrodynamikNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.magnetohydrodynamik_register_id for n in self.normen if n.geltung is MagnetohydrodynamikGeltung.GESPERRT)

    @property
    def magnetohydrodynamisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.magnetohydrodynamik_register_id for n in self.normen if n.geltung is MagnetohydrodynamikGeltung.MAGNETOHYDRODYNAMISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.magnetohydrodynamik_register_id for n in self.normen if n.geltung is MagnetohydrodynamikGeltung.GRUNDLEGEND_MAGNETOHYDRODYNAMISCH)

    @property
    def register_signal(self):
        if any(n.geltung is MagnetohydrodynamikGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-gesperrt")
        elif any(n.geltung is MagnetohydrodynamikGeltung.MAGNETOHYDRODYNAMISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-magnetohydrodynamisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="register-grundlegend-magnetohydrodynamisch")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_magnetohydrodynamik_register(
    plasma_feld: PlasmaFeld | None = None,
    *,
    register_id: str = "magnetohydrodynamik-register",
) -> MagnetohydrodynamikRegister:
    if plasma_feld is None:
        plasma_feld = build_plasma_feld(feld_id=f"{register_id}-feld")

    normen: list[MagnetohydrodynamikNorm] = []
    for parent_norm in plasma_feld.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{register_id}-{parent_norm.plasma_feld_id.removeprefix(f'{plasma_feld.feld_id}-')}"
        raw_weight = min(1.0, parent_norm.plasma_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.plasma_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is MagnetohydrodynamikGeltung.GRUNDLEGEND_MAGNETOHYDRODYNAMISCH)
        normen.append(
            MagnetohydrodynamikNorm(
                magnetohydrodynamik_register_id=new_id,
                magnetohydrodynamik_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                magnetohydrodynamik_weight=new_weight,
                magnetohydrodynamik_tier=new_tier,
                canonical=is_canonical,
                magnetohydrodynamik_ids=parent_norm.plasma_ids + (new_id,),
                magnetohydrodynamik_tags=parent_norm.plasma_tags + (f"magnetohydrodynamik:{new_geltung.value}",),
            )
        )
    return MagnetohydrodynamikRegister(
        register_id=register_id,
        plasma_feld=plasma_feld,
        normen=tuple(normen),
    )
