"""
#364 FraktalCharta — Fraktale Selbstähnlichkeit: Mandelbrot-Menge, Hausdorff-
Dimension D_H > topologische Dimension. Governance-Regeln skalieren identisch
auf allen Ebenen — von der Einzelagenten-Interaktion bis zur Terra-Schwarm-
Koordination. Das Selbstähnlichkeitsprinzip ist Leitsterns Skalierbarkeitsgarantie.
Geltungsstufen: GESPERRT / FRAKTAL / GRUNDLEGEND_FRAKTAL
Parent: LyapunovKodex (#363)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .lyapunov_kodex import (
    LyapunovGeltung,
    LyapunovKodex,
    build_lyapunov_kodex,
)

_GELTUNG_MAP: dict[LyapunovGeltung, "FraktalGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[LyapunovGeltung.GESPERRT] = FraktalGeltung.GESPERRT
    _GELTUNG_MAP[LyapunovGeltung.LYAPUNOVSTABIL] = FraktalGeltung.FRAKTAL
    _GELTUNG_MAP[LyapunovGeltung.GRUNDLEGEND_LYAPUNOVSTABIL] = FraktalGeltung.GRUNDLEGEND_FRAKTAL


class FraktalTyp(Enum):
    SCHUTZ_FRAKTAL = "schutz-fraktal"
    ORDNUNGS_FRAKTAL = "ordnungs-fraktal"
    SOUVERAENITAETS_FRAKTAL = "souveraenitaets-fraktal"


class FraktalProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class FraktalGeltung(Enum):
    GESPERRT = "gesperrt"
    FRAKTAL = "fraktal"
    GRUNDLEGEND_FRAKTAL = "grundlegend-fraktal"


_init_map()

_TYP_MAP: dict[FraktalGeltung, FraktalTyp] = {
    FraktalGeltung.GESPERRT: FraktalTyp.SCHUTZ_FRAKTAL,
    FraktalGeltung.FRAKTAL: FraktalTyp.ORDNUNGS_FRAKTAL,
    FraktalGeltung.GRUNDLEGEND_FRAKTAL: FraktalTyp.SOUVERAENITAETS_FRAKTAL,
}

_PROZEDUR_MAP: dict[FraktalGeltung, FraktalProzedur] = {
    FraktalGeltung.GESPERRT: FraktalProzedur.NOTPROZEDUR,
    FraktalGeltung.FRAKTAL: FraktalProzedur.REGELPROTOKOLL,
    FraktalGeltung.GRUNDLEGEND_FRAKTAL: FraktalProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[FraktalGeltung, float] = {
    FraktalGeltung.GESPERRT: 0.0,
    FraktalGeltung.FRAKTAL: 0.04,
    FraktalGeltung.GRUNDLEGEND_FRAKTAL: 0.08,
}

_TIER_DELTA: dict[FraktalGeltung, int] = {
    FraktalGeltung.GESPERRT: 0,
    FraktalGeltung.FRAKTAL: 1,
    FraktalGeltung.GRUNDLEGEND_FRAKTAL: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FraktalNorm:
    fraktal_charta_id: str
    fraktal_typ: FraktalTyp
    prozedur: FraktalProzedur
    geltung: FraktalGeltung
    fraktal_weight: float
    fraktal_tier: int
    canonical: bool
    fraktal_ids: tuple[str, ...]
    fraktal_tags: tuple[str, ...]


@dataclass(frozen=True)
class FraktalCharta:
    charta_id: str
    lyapunov_kodex: LyapunovKodex
    normen: tuple[FraktalNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.fraktal_charta_id for n in self.normen if n.geltung is FraktalGeltung.GESPERRT)

    @property
    def fraktal_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.fraktal_charta_id for n in self.normen if n.geltung is FraktalGeltung.FRAKTAL)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.fraktal_charta_id for n in self.normen if n.geltung is FraktalGeltung.GRUNDLEGEND_FRAKTAL)

    @property
    def charta_signal(self):
        if any(n.geltung is FraktalGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is FraktalGeltung.FRAKTAL for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-fraktal")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-fraktal")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_fraktal_charta(
    lyapunov_kodex: LyapunovKodex | None = None,
    *,
    charta_id: str = "fraktal-charta",
) -> FraktalCharta:
    if lyapunov_kodex is None:
        lyapunov_kodex = build_lyapunov_kodex(kodex_id=f"{charta_id}-kodex")

    normen: list[FraktalNorm] = []
    for parent_norm in lyapunov_kodex.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.lyapunov_kodex_id.removeprefix(f'{lyapunov_kodex.kodex_id}-')}"
        raw_weight = min(1.0, parent_norm.lyapunov_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.lyapunov_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is FraktalGeltung.GRUNDLEGEND_FRAKTAL)
        normen.append(
            FraktalNorm(
                fraktal_charta_id=new_id,
                fraktal_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                fraktal_weight=new_weight,
                fraktal_tier=new_tier,
                canonical=is_canonical,
                fraktal_ids=parent_norm.lyapunov_ids + (new_id,),
                fraktal_tags=parent_norm.lyapunov_tags + (f"fraktal:{new_geltung.value}",),
            )
        )
    return FraktalCharta(
        charta_id=charta_id,
        lyapunov_kodex=lyapunov_kodex,
        normen=tuple(normen),
    )
