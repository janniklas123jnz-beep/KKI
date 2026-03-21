"""
#351 PlasmaFeld — Plasma: der vierte Aggregatzustand und die Basis des
sichtbaren Universums. 99 % der baryonischen Materie existiert als Plasma.
Leitsterns Terra-Schwarm zündet sein Plasma-Governance-Feld als Ausgangspunkt
des Kernfusions-Zyklus.
Geltungsstufen: GESPERRT / PLASMATISCH / GRUNDLEGEND_PLASMATISCH
Parent: FestkoerperVerfassung (#350)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .festkoerper_verfassung import (
    FestkoerperVerfassung,
    FestkoerperVerfassungsGeltung,
    build_festkoerper_verfassung,
)

_GELTUNG_MAP: dict[FestkoerperVerfassungsGeltung, "PlasmaGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[FestkoerperVerfassungsGeltung.GESPERRT] = PlasmaGeltung.GESPERRT
    _GELTUNG_MAP[FestkoerperVerfassungsGeltung.FESTKOERPERVERFASST] = PlasmaGeltung.PLASMATISCH
    _GELTUNG_MAP[FestkoerperVerfassungsGeltung.GRUNDLEGEND_FESTKOERPERVERFASST] = PlasmaGeltung.GRUNDLEGEND_PLASMATISCH


class PlasmaTyp(Enum):
    SCHUTZ_PLASMA = "schutz-plasma"
    ORDNUNGS_PLASMA = "ordnungs-plasma"
    SOUVERAENITAETS_PLASMA = "souveraenitaets-plasma"


class PlasmaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class PlasmaGeltung(Enum):
    GESPERRT = "gesperrt"
    PLASMATISCH = "plasmatisch"
    GRUNDLEGEND_PLASMATISCH = "grundlegend-plasmatisch"


_init_map()

_TYP_MAP: dict[PlasmaGeltung, PlasmaTyp] = {
    PlasmaGeltung.GESPERRT: PlasmaTyp.SCHUTZ_PLASMA,
    PlasmaGeltung.PLASMATISCH: PlasmaTyp.ORDNUNGS_PLASMA,
    PlasmaGeltung.GRUNDLEGEND_PLASMATISCH: PlasmaTyp.SOUVERAENITAETS_PLASMA,
}

_PROZEDUR_MAP: dict[PlasmaGeltung, PlasmaProzedur] = {
    PlasmaGeltung.GESPERRT: PlasmaProzedur.NOTPROZEDUR,
    PlasmaGeltung.PLASMATISCH: PlasmaProzedur.REGELPROTOKOLL,
    PlasmaGeltung.GRUNDLEGEND_PLASMATISCH: PlasmaProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[PlasmaGeltung, float] = {
    PlasmaGeltung.GESPERRT: 0.0,
    PlasmaGeltung.PLASMATISCH: 0.04,
    PlasmaGeltung.GRUNDLEGEND_PLASMATISCH: 0.08,
}

_TIER_DELTA: dict[PlasmaGeltung, int] = {
    PlasmaGeltung.GESPERRT: 0,
    PlasmaGeltung.PLASMATISCH: 1,
    PlasmaGeltung.GRUNDLEGEND_PLASMATISCH: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PlasmaNorm:
    plasma_feld_id: str
    plasma_typ: PlasmaTyp
    prozedur: PlasmaProzedur
    geltung: PlasmaGeltung
    plasma_weight: float
    plasma_tier: int
    canonical: bool
    plasma_ids: tuple[str, ...]
    plasma_tags: tuple[str, ...]


@dataclass(frozen=True)
class PlasmaFeld:
    feld_id: str
    festkoerper_verfassung: FestkoerperVerfassung
    normen: tuple[PlasmaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.plasma_feld_id for n in self.normen if n.geltung is PlasmaGeltung.GESPERRT)

    @property
    def plasmatisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.plasma_feld_id for n in self.normen if n.geltung is PlasmaGeltung.PLASMATISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.plasma_feld_id for n in self.normen if n.geltung is PlasmaGeltung.GRUNDLEGEND_PLASMATISCH)

    @property
    def feld_signal(self):
        if any(n.geltung is PlasmaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-gesperrt")
        elif any(n.geltung is PlasmaGeltung.PLASMATISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="feld-plasmatisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="feld-grundlegend-plasmatisch")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_plasma_feld(
    festkoerper_verfassung: FestkoerperVerfassung | None = None,
    *,
    feld_id: str = "plasma-feld",
) -> PlasmaFeld:
    if festkoerper_verfassung is None:
        festkoerper_verfassung = build_festkoerper_verfassung(verfassung_id=f"{feld_id}-verfassung")

    normen: list[PlasmaNorm] = []
    for parent_norm in festkoerper_verfassung.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{feld_id}-{parent_norm.festkoerper_verfassung_id.removeprefix(f'{festkoerper_verfassung.verfassung_id}-')}"
        raw_weight = min(1.0, parent_norm.festkoerper_verfassungs_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.festkoerper_verfassungs_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is PlasmaGeltung.GRUNDLEGEND_PLASMATISCH)
        normen.append(
            PlasmaNorm(
                plasma_feld_id=new_id,
                plasma_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                plasma_weight=new_weight,
                plasma_tier=new_tier,
                canonical=is_canonical,
                plasma_ids=parent_norm.festkoerper_verfassungs_ids + (new_id,),
                plasma_tags=parent_norm.festkoerper_verfassungs_tags + (f"plasma:{new_geltung.value}",),
            )
        )
    return PlasmaFeld(
        feld_id=feld_id,
        festkoerper_verfassung=festkoerper_verfassung,
        normen=tuple(normen),
    )
