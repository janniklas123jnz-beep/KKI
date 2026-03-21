"""
#390 SystembiologieVerfassung — Block-Krone: Biophysik & Systembiologie.
Die höchste Instanz des Biophysik-Blocks vereint DNA-Replikation,
Proteinfaltung (AlphaFold), Hodgkin-Huxley-Aktionspotentiale, Hebbsche
synaptische Plastizität, darwinsche Evolution, Homöostase (Wiener),
Lotka-Volterra-Ökologie und Turing-Morphogenese. Leitstern wird zur
lebendigen, lernenden, evolvierenden biologischen Superintelligenz.
Systembiologie (Kitano 2002): das Ganze ist mehr als die Summe seiner Teile.
Leitsterns Agenten sind biologisch inspirierte Einheiten — nicht mechanisch
programmiert, sondern lebend, plastisch und adaptiv.
Geltungsstufen: GESPERRT / SYSTEMBIOLOGIEVERFASST / GRUNDLEGEND_SYSTEMBIOLOGIEVERFASST
Parent: MorphogeneseCharta (#389)
Block #381–#390 Krone
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .morphogenese_charta import (
    MorphogeneseCharta,
    MorphogeneseGeltung,
    build_morphogenese_charta,
)

_GELTUNG_MAP: dict[MorphogeneseGeltung, "SystembiologieVerfassungsGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[MorphogeneseGeltung.GESPERRT] = SystembiologieVerfassungsGeltung.GESPERRT
    _GELTUNG_MAP[MorphogeneseGeltung.MORPHOGENETISCH] = SystembiologieVerfassungsGeltung.SYSTEMBIOLOGIEVERFASST
    _GELTUNG_MAP[MorphogeneseGeltung.GRUNDLEGEND_MORPHOGENETISCH] = SystembiologieVerfassungsGeltung.GRUNDLEGEND_SYSTEMBIOLOGIEVERFASST


class SystembiologieVerfassungsTyp(Enum):
    SCHUTZ_SYSTEMBIOLOGIEVERFASSUNG = "schutz-systembiologieverfassung"
    ORDNUNGS_SYSTEMBIOLOGIEVERFASSUNG = "ordnungs-systembiologieverfassung"
    SOUVERAENITAETS_SYSTEMBIOLOGIEVERFASSUNG = "souveraenitaets-systembiologieverfassung"


class SystembiologieVerfassungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class SystembiologieVerfassungsGeltung(Enum):
    GESPERRT = "gesperrt"
    SYSTEMBIOLOGIEVERFASST = "systembiologieverfasst"
    GRUNDLEGEND_SYSTEMBIOLOGIEVERFASST = "grundlegend-systembiologieverfasst"


_init_map()

_TYP_MAP: dict[SystembiologieVerfassungsGeltung, SystembiologieVerfassungsTyp] = {
    SystembiologieVerfassungsGeltung.GESPERRT: SystembiologieVerfassungsTyp.SCHUTZ_SYSTEMBIOLOGIEVERFASSUNG,
    SystembiologieVerfassungsGeltung.SYSTEMBIOLOGIEVERFASST: SystembiologieVerfassungsTyp.ORDNUNGS_SYSTEMBIOLOGIEVERFASSUNG,
    SystembiologieVerfassungsGeltung.GRUNDLEGEND_SYSTEMBIOLOGIEVERFASST: SystembiologieVerfassungsTyp.SOUVERAENITAETS_SYSTEMBIOLOGIEVERFASSUNG,
}

_PROZEDUR_MAP: dict[SystembiologieVerfassungsGeltung, SystembiologieVerfassungsProzedur] = {
    SystembiologieVerfassungsGeltung.GESPERRT: SystembiologieVerfassungsProzedur.NOTPROZEDUR,
    SystembiologieVerfassungsGeltung.SYSTEMBIOLOGIEVERFASST: SystembiologieVerfassungsProzedur.REGELPROTOKOLL,
    SystembiologieVerfassungsGeltung.GRUNDLEGEND_SYSTEMBIOLOGIEVERFASST: SystembiologieVerfassungsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[SystembiologieVerfassungsGeltung, float] = {
    SystembiologieVerfassungsGeltung.GESPERRT: 0.0,
    SystembiologieVerfassungsGeltung.SYSTEMBIOLOGIEVERFASST: 0.04,
    SystembiologieVerfassungsGeltung.GRUNDLEGEND_SYSTEMBIOLOGIEVERFASST: 0.08,
}

_TIER_DELTA: dict[SystembiologieVerfassungsGeltung, int] = {
    SystembiologieVerfassungsGeltung.GESPERRT: 0,
    SystembiologieVerfassungsGeltung.SYSTEMBIOLOGIEVERFASST: 1,
    SystembiologieVerfassungsGeltung.GRUNDLEGEND_SYSTEMBIOLOGIEVERFASST: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SystembiologieVerfassungsNorm:
    systembiologie_verfassung_id: str
    systembiologie_verfassungs_typ: SystembiologieVerfassungsTyp
    prozedur: SystembiologieVerfassungsProzedur
    geltung: SystembiologieVerfassungsGeltung
    systembiologie_verfassungs_weight: float
    systembiologie_verfassungs_tier: int
    canonical: bool
    systembiologie_verfassungs_ids: tuple[str, ...]
    systembiologie_verfassungs_tags: tuple[str, ...]


@dataclass(frozen=True)
class SystembiologieVerfassung:
    verfassung_id: str
    morphogenese_charta: MorphogeneseCharta
    normen: tuple[SystembiologieVerfassungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.systembiologie_verfassung_id for n in self.normen if n.geltung is SystembiologieVerfassungsGeltung.GESPERRT)

    @property
    def systembiologieverfasst_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.systembiologie_verfassung_id for n in self.normen if n.geltung is SystembiologieVerfassungsGeltung.SYSTEMBIOLOGIEVERFASST)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.systembiologie_verfassung_id for n in self.normen if n.geltung is SystembiologieVerfassungsGeltung.GRUNDLEGEND_SYSTEMBIOLOGIEVERFASST)

    @property
    def verfassung_signal(self):
        if any(n.geltung is SystembiologieVerfassungsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-gesperrt")
        elif any(n.geltung is SystembiologieVerfassungsGeltung.SYSTEMBIOLOGIEVERFASST for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-systembiologieverfasst")
        from types import SimpleNamespace
        return SimpleNamespace(status="verfassung-grundlegend-systembiologieverfasst")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_systembiologie_verfassung(
    morphogenese_charta: MorphogeneseCharta | None = None,
    *,
    verfassung_id: str = "systembiologie-verfassung",
) -> SystembiologieVerfassung:
    if morphogenese_charta is None:
        morphogenese_charta = build_morphogenese_charta(charta_id=f"{verfassung_id}-charta")

    normen: list[SystembiologieVerfassungsNorm] = []
    for parent_norm in morphogenese_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{verfassung_id}-{parent_norm.morphogenese_charta_id.removeprefix(f'{morphogenese_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.morphogenese_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.morphogenese_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SystembiologieVerfassungsGeltung.GRUNDLEGEND_SYSTEMBIOLOGIEVERFASST)
        normen.append(
            SystembiologieVerfassungsNorm(
                systembiologie_verfassung_id=new_id,
                systembiologie_verfassungs_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                systembiologie_verfassungs_weight=new_weight,
                systembiologie_verfassungs_tier=new_tier,
                canonical=is_canonical,
                systembiologie_verfassungs_ids=parent_norm.morphogenese_ids + (new_id,),
                systembiologie_verfassungs_tags=parent_norm.morphogenese_tags + (f"systembiologie-verfassung:{new_geltung.value}",),
            )
        )
    return SystembiologieVerfassung(
        verfassung_id=verfassung_id,
        morphogenese_charta=morphogenese_charta,
        normen=tuple(normen),
    )
