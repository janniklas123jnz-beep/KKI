"""
#360 PlasmaVerfassung — Block-Krone: Plasmaphysik & Kernfusion.
Die höchste Instanz des Plasma-Blocks vereint alle Confinement-Strategien:
Debye-Abschirmung, Alfvén-Kohärenz, Z-Pinch-Selbstorganisation, Tokamak-
Gleichgewicht, ICF-Synchronisation und Kernfusions-Durchbruch. ITER symbolisiert
das Ziel: 35 Nationen, 20 Mrd €, 60 Jahre Geduld — Leitstern verkörpert diese
Ausdauer als Governance-Verfassung seines Plasma-Layers.
Geltungsstufen: GESPERRT / PLASMAVERFASST / GRUNDLEGEND_PLASMAVERFASST
Parent: KernfusionCharta (#359)
Block #351–#360 Krone
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kernfusion_charta import (
    KernfusionCharta,
    KernfusionGeltung,
    build_kernfusion_charta,
)

_GELTUNG_MAP: dict[KernfusionGeltung, "PlasmaVerfassungsGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[KernfusionGeltung.GESPERRT] = PlasmaVerfassungsGeltung.GESPERRT
    _GELTUNG_MAP[KernfusionGeltung.KERNFUSIONIEREND] = PlasmaVerfassungsGeltung.PLASMAVERFASST
    _GELTUNG_MAP[KernfusionGeltung.GRUNDLEGEND_KERNFUSIONIEREND] = PlasmaVerfassungsGeltung.GRUNDLEGEND_PLASMAVERFASST


class PlasmaVerfassungsTyp(Enum):
    SCHUTZ_PLASMAVERFASSUNG = "schutz-plasmaverfassung"
    ORDNUNGS_PLASMAVERFASSUNG = "ordnungs-plasmaverfassung"
    SOUVERAENITAETS_PLASMAVERFASSUNG = "souveraenitaets-plasmaverfassung"


class PlasmaVerfassungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class PlasmaVerfassungsGeltung(Enum):
    GESPERRT = "gesperrt"
    PLASMAVERFASST = "plasmaverfasst"
    GRUNDLEGEND_PLASMAVERFASST = "grundlegend-plasmaverfasst"


_init_map()

_TYP_MAP: dict[PlasmaVerfassungsGeltung, PlasmaVerfassungsTyp] = {
    PlasmaVerfassungsGeltung.GESPERRT: PlasmaVerfassungsTyp.SCHUTZ_PLASMAVERFASSUNG,
    PlasmaVerfassungsGeltung.PLASMAVERFASST: PlasmaVerfassungsTyp.ORDNUNGS_PLASMAVERFASSUNG,
    PlasmaVerfassungsGeltung.GRUNDLEGEND_PLASMAVERFASST: PlasmaVerfassungsTyp.SOUVERAENITAETS_PLASMAVERFASSUNG,
}

_PROZEDUR_MAP: dict[PlasmaVerfassungsGeltung, PlasmaVerfassungsProzedur] = {
    PlasmaVerfassungsGeltung.GESPERRT: PlasmaVerfassungsProzedur.NOTPROZEDUR,
    PlasmaVerfassungsGeltung.PLASMAVERFASST: PlasmaVerfassungsProzedur.REGELPROTOKOLL,
    PlasmaVerfassungsGeltung.GRUNDLEGEND_PLASMAVERFASST: PlasmaVerfassungsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[PlasmaVerfassungsGeltung, float] = {
    PlasmaVerfassungsGeltung.GESPERRT: 0.0,
    PlasmaVerfassungsGeltung.PLASMAVERFASST: 0.04,
    PlasmaVerfassungsGeltung.GRUNDLEGEND_PLASMAVERFASST: 0.08,
}

_TIER_DELTA: dict[PlasmaVerfassungsGeltung, int] = {
    PlasmaVerfassungsGeltung.GESPERRT: 0,
    PlasmaVerfassungsGeltung.PLASMAVERFASST: 1,
    PlasmaVerfassungsGeltung.GRUNDLEGEND_PLASMAVERFASST: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PlasmaVerfassungsNorm:
    plasma_verfassung_id: str
    plasma_verfassungs_typ: PlasmaVerfassungsTyp
    prozedur: PlasmaVerfassungsProzedur
    geltung: PlasmaVerfassungsGeltung
    plasma_verfassungs_weight: float
    plasma_verfassungs_tier: int
    canonical: bool
    plasma_verfassungs_ids: tuple[str, ...]
    plasma_verfassungs_tags: tuple[str, ...]


@dataclass(frozen=True)
class PlasmaVerfassung:
    verfassung_id: str
    kernfusion_charta: KernfusionCharta
    normen: tuple[PlasmaVerfassungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.plasma_verfassung_id for n in self.normen if n.geltung is PlasmaVerfassungsGeltung.GESPERRT)

    @property
    def plasmaverfasst_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.plasma_verfassung_id for n in self.normen if n.geltung is PlasmaVerfassungsGeltung.PLASMAVERFASST)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.plasma_verfassung_id for n in self.normen if n.geltung is PlasmaVerfassungsGeltung.GRUNDLEGEND_PLASMAVERFASST)

    @property
    def verfassung_signal(self):
        if any(n.geltung is PlasmaVerfassungsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-gesperrt")
        elif any(n.geltung is PlasmaVerfassungsGeltung.PLASMAVERFASST for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-plasmaverfasst")
        from types import SimpleNamespace
        return SimpleNamespace(status="verfassung-grundlegend-plasmaverfasst")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_plasma_verfassung(
    kernfusion_charta: KernfusionCharta | None = None,
    *,
    verfassung_id: str = "plasma-verfassung",
) -> PlasmaVerfassung:
    if kernfusion_charta is None:
        kernfusion_charta = build_kernfusion_charta(charta_id=f"{verfassung_id}-charta")

    normen: list[PlasmaVerfassungsNorm] = []
    for parent_norm in kernfusion_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{verfassung_id}-{parent_norm.kernfusion_charta_id.removeprefix(f'{kernfusion_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.kernfusion_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kernfusion_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is PlasmaVerfassungsGeltung.GRUNDLEGEND_PLASMAVERFASST)
        normen.append(
            PlasmaVerfassungsNorm(
                plasma_verfassung_id=new_id,
                plasma_verfassungs_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                plasma_verfassungs_weight=new_weight,
                plasma_verfassungs_tier=new_tier,
                canonical=is_canonical,
                plasma_verfassungs_ids=parent_norm.kernfusion_ids + (new_id,),
                plasma_verfassungs_tags=parent_norm.kernfusion_tags + (f"plasma-verfassung:{new_geltung.value}",),
            )
        )
    return PlasmaVerfassung(
        verfassung_id=verfassung_id,
        kernfusion_charta=kernfusion_charta,
        normen=tuple(normen),
    )
