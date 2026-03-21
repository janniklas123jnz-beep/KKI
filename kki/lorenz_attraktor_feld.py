"""
#361 LorenzAttraktorFeld — Der Lorenz-Attraktor (1963): das Schmetterlingsexperiment.
Sensitive Abhängigkeit von Anfangsbedingungen: dx/dt = σ(y-x), dy/dt = x(ρ-z)-y,
dz/dt = xy-βz. Leitsterns Agenten erwerben Sensitivitätsbewusstsein — kleine
Entscheidungen können große Systemveränderungen auslösen.
Geltungsstufen: GESPERRT / LORENZATTRAHIERT / GRUNDLEGEND_LORENZATTRAHIERT
Parent: PlasmaVerfassung (#360)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .plasma_verfassung import (
    PlasmaVerfassung,
    PlasmaVerfassungsGeltung,
    build_plasma_verfassung,
)

_GELTUNG_MAP: dict[PlasmaVerfassungsGeltung, "LorenzAttraktorGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[PlasmaVerfassungsGeltung.GESPERRT] = LorenzAttraktorGeltung.GESPERRT
    _GELTUNG_MAP[PlasmaVerfassungsGeltung.PLASMAVERFASST] = LorenzAttraktorGeltung.LORENZATTRAHIERT
    _GELTUNG_MAP[PlasmaVerfassungsGeltung.GRUNDLEGEND_PLASMAVERFASST] = LorenzAttraktorGeltung.GRUNDLEGEND_LORENZATTRAHIERT


class LorenzAttraktorTyp(Enum):
    SCHUTZ_LORENZ_ATTRAKTOR = "schutz-lorenz-attraktor"
    ORDNUNGS_LORENZ_ATTRAKTOR = "ordnungs-lorenz-attraktor"
    SOUVERAENITAETS_LORENZ_ATTRAKTOR = "souveraenitaets-lorenz-attraktor"


class LorenzAttraktorProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class LorenzAttraktorGeltung(Enum):
    GESPERRT = "gesperrt"
    LORENZATTRAHIERT = "lorenzattrahiert"
    GRUNDLEGEND_LORENZATTRAHIERT = "grundlegend-lorenzattrahiert"


_init_map()

_TYP_MAP: dict[LorenzAttraktorGeltung, LorenzAttraktorTyp] = {
    LorenzAttraktorGeltung.GESPERRT: LorenzAttraktorTyp.SCHUTZ_LORENZ_ATTRAKTOR,
    LorenzAttraktorGeltung.LORENZATTRAHIERT: LorenzAttraktorTyp.ORDNUNGS_LORENZ_ATTRAKTOR,
    LorenzAttraktorGeltung.GRUNDLEGEND_LORENZATTRAHIERT: LorenzAttraktorTyp.SOUVERAENITAETS_LORENZ_ATTRAKTOR,
}

_PROZEDUR_MAP: dict[LorenzAttraktorGeltung, LorenzAttraktorProzedur] = {
    LorenzAttraktorGeltung.GESPERRT: LorenzAttraktorProzedur.NOTPROZEDUR,
    LorenzAttraktorGeltung.LORENZATTRAHIERT: LorenzAttraktorProzedur.REGELPROTOKOLL,
    LorenzAttraktorGeltung.GRUNDLEGEND_LORENZATTRAHIERT: LorenzAttraktorProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[LorenzAttraktorGeltung, float] = {
    LorenzAttraktorGeltung.GESPERRT: 0.0,
    LorenzAttraktorGeltung.LORENZATTRAHIERT: 0.04,
    LorenzAttraktorGeltung.GRUNDLEGEND_LORENZATTRAHIERT: 0.08,
}

_TIER_DELTA: dict[LorenzAttraktorGeltung, int] = {
    LorenzAttraktorGeltung.GESPERRT: 0,
    LorenzAttraktorGeltung.LORENZATTRAHIERT: 1,
    LorenzAttraktorGeltung.GRUNDLEGEND_LORENZATTRAHIERT: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LorenzAttraktorNorm:
    lorenz_attraktor_feld_id: str
    lorenz_attraktor_typ: LorenzAttraktorTyp
    prozedur: LorenzAttraktorProzedur
    geltung: LorenzAttraktorGeltung
    lorenz_attraktor_weight: float
    lorenz_attraktor_tier: int
    canonical: bool
    lorenz_attraktor_ids: tuple[str, ...]
    lorenz_attraktor_tags: tuple[str, ...]


@dataclass(frozen=True)
class LorenzAttraktorFeld:
    feld_id: str
    plasma_verfassung: PlasmaVerfassung
    normen: tuple[LorenzAttraktorNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.lorenz_attraktor_feld_id for n in self.normen if n.geltung is LorenzAttraktorGeltung.GESPERRT)

    @property
    def lorenzattrahiert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.lorenz_attraktor_feld_id for n in self.normen if n.geltung is LorenzAttraktorGeltung.LORENZATTRAHIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.lorenz_attraktor_feld_id for n in self.normen if n.geltung is LorenzAttraktorGeltung.GRUNDLEGEND_LORENZATTRAHIERT)

    @property
    def feld_signal(self):
        if any(n.geltung is LorenzAttraktorGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-gesperrt")
        elif any(n.geltung is LorenzAttraktorGeltung.LORENZATTRAHIERT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-lorenzattrahiert")
        from types import SimpleNamespace
        return SimpleNamespace(status="feld-grundlegend-lorenzattrahiert")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_lorenz_attraktor_feld(
    plasma_verfassung: PlasmaVerfassung | None = None,
    *,
    feld_id: str = "lorenz-attraktor-feld",
) -> LorenzAttraktorFeld:
    if plasma_verfassung is None:
        plasma_verfassung = build_plasma_verfassung(verfassung_id=f"{feld_id}-verfassung")

    normen: list[LorenzAttraktorNorm] = []
    for parent_norm in plasma_verfassung.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{feld_id}-{parent_norm.plasma_verfassung_id.removeprefix(f'{plasma_verfassung.verfassung_id}-')}"
        raw_weight = min(1.0, parent_norm.plasma_verfassungs_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.plasma_verfassungs_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is LorenzAttraktorGeltung.GRUNDLEGEND_LORENZATTRAHIERT)
        normen.append(
            LorenzAttraktorNorm(
                lorenz_attraktor_feld_id=new_id,
                lorenz_attraktor_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                lorenz_attraktor_weight=new_weight,
                lorenz_attraktor_tier=new_tier,
                canonical=is_canonical,
                lorenz_attraktor_ids=parent_norm.plasma_verfassungs_ids + (new_id,),
                lorenz_attraktor_tags=parent_norm.plasma_verfassungs_tags + (f"lorenz-attraktor:{new_geltung.value}",),
            )
        )
    return LorenzAttraktorFeld(
        feld_id=feld_id,
        plasma_verfassung=plasma_verfassung,
        normen=tuple(normen),
    )
