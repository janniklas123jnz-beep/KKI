"""
#370 ChaosVerfassung — Block-Krone: Chaostheorie & Komplexe Systeme.
Die höchste Instanz des Chaos-Blocks vereint alle Komplexitäts-Prinzipien:
Lorenz-Attraktor, Bifurkationskaskaden, Lyapunov-Stabilität, Fraktale
Selbstähnlichkeit, Strange-Attraktoren, Schwarmemergenz, Perkolationsresilienz,
Kolmogorov-Komplexität und adaptiver Schwarmkodex. Chaos ist nicht Unordnung —
Leitsterns Chaos-Verfassung kanalisiert deterministische Komplexität in
souveräne Governance-Ordnung.
Geltungsstufen: GESPERRT / CHAOSVERFASST / GRUNDLEGEND_CHAOSVERFASST
Parent: AdaptivSchwarmKodex (#369)
Block #361–#370 Krone
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .adaptiv_schwarm_kodex import (
    AdaptivSchwarmGeltung,
    AdaptivSchwarmKodex,
    build_adaptiv_schwarm_kodex,
)

_GELTUNG_MAP: dict[AdaptivSchwarmGeltung, "ChaosVerfassungsGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[AdaptivSchwarmGeltung.GESPERRT] = ChaosVerfassungsGeltung.GESPERRT
    _GELTUNG_MAP[AdaptivSchwarmGeltung.ADAPTIV_SCHWARMEND] = ChaosVerfassungsGeltung.CHAOSVERFASST
    _GELTUNG_MAP[AdaptivSchwarmGeltung.GRUNDLEGEND_ADAPTIV_SCHWARMEND] = ChaosVerfassungsGeltung.GRUNDLEGEND_CHAOSVERFASST


class ChaosVerfassungsTyp(Enum):
    SCHUTZ_CHAOSVERFASSUNG = "schutz-chaosverfassung"
    ORDNUNGS_CHAOSVERFASSUNG = "ordnungs-chaosverfassung"
    SOUVERAENITAETS_CHAOSVERFASSUNG = "souveraenitaets-chaosverfassung"


class ChaosVerfassungsProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class ChaosVerfassungsGeltung(Enum):
    GESPERRT = "gesperrt"
    CHAOSVERFASST = "chaosverfasst"
    GRUNDLEGEND_CHAOSVERFASST = "grundlegend-chaosverfasst"


_init_map()

_TYP_MAP: dict[ChaosVerfassungsGeltung, ChaosVerfassungsTyp] = {
    ChaosVerfassungsGeltung.GESPERRT: ChaosVerfassungsTyp.SCHUTZ_CHAOSVERFASSUNG,
    ChaosVerfassungsGeltung.CHAOSVERFASST: ChaosVerfassungsTyp.ORDNUNGS_CHAOSVERFASSUNG,
    ChaosVerfassungsGeltung.GRUNDLEGEND_CHAOSVERFASST: ChaosVerfassungsTyp.SOUVERAENITAETS_CHAOSVERFASSUNG,
}

_PROZEDUR_MAP: dict[ChaosVerfassungsGeltung, ChaosVerfassungsProzedur] = {
    ChaosVerfassungsGeltung.GESPERRT: ChaosVerfassungsProzedur.NOTPROZEDUR,
    ChaosVerfassungsGeltung.CHAOSVERFASST: ChaosVerfassungsProzedur.REGELPROTOKOLL,
    ChaosVerfassungsGeltung.GRUNDLEGEND_CHAOSVERFASST: ChaosVerfassungsProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[ChaosVerfassungsGeltung, float] = {
    ChaosVerfassungsGeltung.GESPERRT: 0.0,
    ChaosVerfassungsGeltung.CHAOSVERFASST: 0.04,
    ChaosVerfassungsGeltung.GRUNDLEGEND_CHAOSVERFASST: 0.08,
}

_TIER_DELTA: dict[ChaosVerfassungsGeltung, int] = {
    ChaosVerfassungsGeltung.GESPERRT: 0,
    ChaosVerfassungsGeltung.CHAOSVERFASST: 1,
    ChaosVerfassungsGeltung.GRUNDLEGEND_CHAOSVERFASST: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ChaosVerfassungsNorm:
    chaos_verfassung_id: str
    chaos_verfassungs_typ: ChaosVerfassungsTyp
    prozedur: ChaosVerfassungsProzedur
    geltung: ChaosVerfassungsGeltung
    chaos_verfassungs_weight: float
    chaos_verfassungs_tier: int
    canonical: bool
    chaos_verfassungs_ids: tuple[str, ...]
    chaos_verfassungs_tags: tuple[str, ...]


@dataclass(frozen=True)
class ChaosVerfassung:
    verfassung_id: str
    adaptiv_schwarm_kodex: AdaptivSchwarmKodex
    normen: tuple[ChaosVerfassungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.chaos_verfassung_id for n in self.normen if n.geltung is ChaosVerfassungsGeltung.GESPERRT)

    @property
    def chaosverfasst_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.chaos_verfassung_id for n in self.normen if n.geltung is ChaosVerfassungsGeltung.CHAOSVERFASST)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.chaos_verfassung_id for n in self.normen if n.geltung is ChaosVerfassungsGeltung.GRUNDLEGEND_CHAOSVERFASST)

    @property
    def verfassung_signal(self):
        if any(n.geltung is ChaosVerfassungsGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-gesperrt")
        elif any(n.geltung is ChaosVerfassungsGeltung.CHAOSVERFASST for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="verfassung-chaosverfasst")
        from types import SimpleNamespace
        return SimpleNamespace(status="verfassung-grundlegend-chaosverfasst")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_chaos_verfassung(
    adaptiv_schwarm_kodex: AdaptivSchwarmKodex | None = None,
    *,
    verfassung_id: str = "chaos-verfassung",
) -> ChaosVerfassung:
    if adaptiv_schwarm_kodex is None:
        adaptiv_schwarm_kodex = build_adaptiv_schwarm_kodex(kodex_id=f"{verfassung_id}-kodex")

    normen: list[ChaosVerfassungsNorm] = []
    for parent_norm in adaptiv_schwarm_kodex.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{verfassung_id}-{parent_norm.adaptiv_schwarm_kodex_id.removeprefix(f'{adaptiv_schwarm_kodex.kodex_id}-')}"
        raw_weight = min(1.0, parent_norm.adaptiv_schwarm_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.adaptiv_schwarm_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is ChaosVerfassungsGeltung.GRUNDLEGEND_CHAOSVERFASST)
        normen.append(
            ChaosVerfassungsNorm(
                chaos_verfassung_id=new_id,
                chaos_verfassungs_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                chaos_verfassungs_weight=new_weight,
                chaos_verfassungs_tier=new_tier,
                canonical=is_canonical,
                chaos_verfassungs_ids=parent_norm.adaptiv_schwarm_ids + (new_id,),
                chaos_verfassungs_tags=parent_norm.adaptiv_schwarm_tags + (f"chaos-verfassung:{new_geltung.value}",),
            )
        )
    return ChaosVerfassung(
        verfassung_id=verfassung_id,
        adaptiv_schwarm_kodex=adaptiv_schwarm_kodex,
        normen=tuple(normen),
    )
