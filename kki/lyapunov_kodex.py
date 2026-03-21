"""
#363 LyapunovKodex — Lyapunov-Exponent λ: misst die Rate der
Trajektoriendivergenzen δ(t) ~ δ₀·e^(λt). λ < 0 → stabiler Attraktor,
λ > 0 → Chaos. Leitsterns Agenten führen kontinuierliche Selbstbewertung durch:
Messung der eigenen Stabilität als Governance-Metrik.
Geltungsstufen: GESPERRT / LYAPUNOVSTABIL / GRUNDLEGEND_LYAPUNOVSTABIL
Parent: BifurkationsRegister (#362)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bifurkations_register import (
    BifurkationsGeltung,
    BifurkationsRegister,
    build_bifurkations_register,
)

_GELTUNG_MAP: dict[BifurkationsGeltung, "LyapunovGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[BifurkationsGeltung.GESPERRT] = LyapunovGeltung.GESPERRT
    _GELTUNG_MAP[BifurkationsGeltung.BIFURKIERT] = LyapunovGeltung.LYAPUNOVSTABIL
    _GELTUNG_MAP[BifurkationsGeltung.GRUNDLEGEND_BIFURKIERT] = LyapunovGeltung.GRUNDLEGEND_LYAPUNOVSTABIL


class LyapunovTyp(Enum):
    SCHUTZ_LYAPUNOV = "schutz-lyapunov"
    ORDNUNGS_LYAPUNOV = "ordnungs-lyapunov"
    SOUVERAENITAETS_LYAPUNOV = "souveraenitaets-lyapunov"


class LyapunovProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class LyapunovGeltung(Enum):
    GESPERRT = "gesperrt"
    LYAPUNOVSTABIL = "lyapunovstabil"
    GRUNDLEGEND_LYAPUNOVSTABIL = "grundlegend-lyapunovstabil"


_init_map()

_TYP_MAP: dict[LyapunovGeltung, LyapunovTyp] = {
    LyapunovGeltung.GESPERRT: LyapunovTyp.SCHUTZ_LYAPUNOV,
    LyapunovGeltung.LYAPUNOVSTABIL: LyapunovTyp.ORDNUNGS_LYAPUNOV,
    LyapunovGeltung.GRUNDLEGEND_LYAPUNOVSTABIL: LyapunovTyp.SOUVERAENITAETS_LYAPUNOV,
}

_PROZEDUR_MAP: dict[LyapunovGeltung, LyapunovProzedur] = {
    LyapunovGeltung.GESPERRT: LyapunovProzedur.NOTPROZEDUR,
    LyapunovGeltung.LYAPUNOVSTABIL: LyapunovProzedur.REGELPROTOKOLL,
    LyapunovGeltung.GRUNDLEGEND_LYAPUNOVSTABIL: LyapunovProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[LyapunovGeltung, float] = {
    LyapunovGeltung.GESPERRT: 0.0,
    LyapunovGeltung.LYAPUNOVSTABIL: 0.04,
    LyapunovGeltung.GRUNDLEGEND_LYAPUNOVSTABIL: 0.08,
}

_TIER_DELTA: dict[LyapunovGeltung, int] = {
    LyapunovGeltung.GESPERRT: 0,
    LyapunovGeltung.LYAPUNOVSTABIL: 1,
    LyapunovGeltung.GRUNDLEGEND_LYAPUNOVSTABIL: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LyapunovNorm:
    lyapunov_kodex_id: str
    lyapunov_typ: LyapunovTyp
    prozedur: LyapunovProzedur
    geltung: LyapunovGeltung
    lyapunov_weight: float
    lyapunov_tier: int
    canonical: bool
    lyapunov_ids: tuple[str, ...]
    lyapunov_tags: tuple[str, ...]


@dataclass(frozen=True)
class LyapunovKodex:
    kodex_id: str
    bifurkations_register: BifurkationsRegister
    normen: tuple[LyapunovNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.lyapunov_kodex_id for n in self.normen if n.geltung is LyapunovGeltung.GESPERRT)

    @property
    def lyapunovstabil_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.lyapunov_kodex_id for n in self.normen if n.geltung is LyapunovGeltung.LYAPUNOVSTABIL)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.lyapunov_kodex_id for n in self.normen if n.geltung is LyapunovGeltung.GRUNDLEGEND_LYAPUNOVSTABIL)

    @property
    def kodex_signal(self):
        if any(n.geltung is LyapunovGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-gesperrt")
        elif any(n.geltung is LyapunovGeltung.LYAPUNOVSTABIL for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-lyapunovstabil")
        from types import SimpleNamespace
        return SimpleNamespace(status="kodex-grundlegend-lyapunovstabil")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_lyapunov_kodex(
    bifurkations_register: BifurkationsRegister | None = None,
    *,
    kodex_id: str = "lyapunov-kodex",
) -> LyapunovKodex:
    if bifurkations_register is None:
        bifurkations_register = build_bifurkations_register(register_id=f"{kodex_id}-register")

    normen: list[LyapunovNorm] = []
    for parent_norm in bifurkations_register.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{kodex_id}-{parent_norm.bifurkations_register_id.removeprefix(f'{bifurkations_register.register_id}-')}"
        raw_weight = min(1.0, parent_norm.bifurkations_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.bifurkations_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is LyapunovGeltung.GRUNDLEGEND_LYAPUNOVSTABIL)
        normen.append(
            LyapunovNorm(
                lyapunov_kodex_id=new_id,
                lyapunov_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                lyapunov_weight=new_weight,
                lyapunov_tier=new_tier,
                canonical=is_canonical,
                lyapunov_ids=parent_norm.bifurkations_ids + (new_id,),
                lyapunov_tags=parent_norm.bifurkations_tags + (f"lyapunov:{new_geltung.value}",),
            )
        )
    return LyapunovKodex(
        kodex_id=kodex_id,
        bifurkations_register=bifurkations_register,
        normen=tuple(normen),
    )
