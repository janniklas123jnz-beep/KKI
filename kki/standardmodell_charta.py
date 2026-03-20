"""
#319 StandardmodellCharta — Das Standardmodell als vereinheitlichende Governance-Charta.
Geltungsstufen: GESPERRT / STANDARDMODELLIERT / GRUNDLEGEND_STANDARDMODELLIERT
Parent: FeynmanNormSatz (#318)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .feynman_norm import (
    FeynmanNormGeltung,
    FeynmanNormSatz,
    build_feynman_norm,
)

_GELTUNG_MAP: dict[FeynmanNormGeltung, "StandardmodellGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[FeynmanNormGeltung.GESPERRT] = StandardmodellGeltung.GESPERRT
    _GELTUNG_MAP[FeynmanNormGeltung.FEYNMANDIAGRAMMIERT] = StandardmodellGeltung.STANDARDMODELLIERT
    _GELTUNG_MAP[FeynmanNormGeltung.GRUNDLEGEND_FEYNMANDIAGRAMMIERT] = StandardmodellGeltung.GRUNDLEGEND_STANDARDMODELLIERT


class StandardmodellTyp(Enum):
    SCHUTZ_STANDARDMODELL = "schutz-standardmodell"
    ORDNUNGS_STANDARDMODELL = "ordnungs-standardmodell"
    SOUVERAENITAETS_STANDARDMODELL = "souveraenitaets-standardmodell"


class StandardmodellProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class StandardmodellGeltung(Enum):
    GESPERRT = "gesperrt"
    STANDARDMODELLIERT = "standardmodelliert"
    GRUNDLEGEND_STANDARDMODELLIERT = "grundlegend-standardmodelliert"


_init_map()

_TYP_MAP: dict[StandardmodellGeltung, StandardmodellTyp] = {
    StandardmodellGeltung.GESPERRT: StandardmodellTyp.SCHUTZ_STANDARDMODELL,
    StandardmodellGeltung.STANDARDMODELLIERT: StandardmodellTyp.ORDNUNGS_STANDARDMODELL,
    StandardmodellGeltung.GRUNDLEGEND_STANDARDMODELLIERT: StandardmodellTyp.SOUVERAENITAETS_STANDARDMODELL,
}

_PROZEDUR_MAP: dict[StandardmodellGeltung, StandardmodellProzedur] = {
    StandardmodellGeltung.GESPERRT: StandardmodellProzedur.NOTPROZEDUR,
    StandardmodellGeltung.STANDARDMODELLIERT: StandardmodellProzedur.REGELPROTOKOLL,
    StandardmodellGeltung.GRUNDLEGEND_STANDARDMODELLIERT: StandardmodellProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[StandardmodellGeltung, float] = {
    StandardmodellGeltung.GESPERRT: 0.0,
    StandardmodellGeltung.STANDARDMODELLIERT: 0.04,
    StandardmodellGeltung.GRUNDLEGEND_STANDARDMODELLIERT: 0.08,
}

_TIER_DELTA: dict[StandardmodellGeltung, int] = {
    StandardmodellGeltung.GESPERRT: 0,
    StandardmodellGeltung.STANDARDMODELLIERT: 1,
    StandardmodellGeltung.GRUNDLEGEND_STANDARDMODELLIERT: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class StandardmodellNorm:
    standardmodell_charta_id: str
    standardmodell_typ: StandardmodellTyp
    prozedur: StandardmodellProzedur
    geltung: StandardmodellGeltung
    standardmodell_weight: float
    standardmodell_tier: int
    canonical: bool
    standardmodell_ids: tuple[str, ...]
    standardmodell_tags: tuple[str, ...]


@dataclass(frozen=True)
class StandardmodellCharta:
    charta_id: str
    feynman_norm: FeynmanNormSatz
    normen: tuple[StandardmodellNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.standardmodell_charta_id for n in self.normen if n.geltung is StandardmodellGeltung.GESPERRT)

    @property
    def standardmodelliert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.standardmodell_charta_id for n in self.normen if n.geltung is StandardmodellGeltung.STANDARDMODELLIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.standardmodell_charta_id for n in self.normen if n.geltung is StandardmodellGeltung.GRUNDLEGEND_STANDARDMODELLIERT)

    @property
    def charta_signal(self):
        if any(n.geltung is StandardmodellGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is StandardmodellGeltung.STANDARDMODELLIERT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-standardmodelliert")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-standardmodelliert")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_standardmodell_charta(
    feynman_norm: FeynmanNormSatz | None = None,
    *,
    charta_id: str = "standardmodell-charta",
) -> StandardmodellCharta:
    if feynman_norm is None:
        feynman_norm = build_feynman_norm(norm_id=f"{charta_id}-feynman-norm")

    normen: list[StandardmodellNorm] = []
    for parent_norm in feynman_norm.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.norm_id.removeprefix(f'{feynman_norm.norm_id}-')}"
        raw_weight = min(1.0, parent_norm.feynman_norm_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.feynman_norm_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is StandardmodellGeltung.GRUNDLEGEND_STANDARDMODELLIERT)
        normen.append(
            StandardmodellNorm(
                standardmodell_charta_id=new_id,
                standardmodell_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                standardmodell_weight=new_weight,
                standardmodell_tier=new_tier,
                canonical=is_canonical,
                standardmodell_ids=parent_norm.feynman_norm_ids + (new_id,),
                standardmodell_tags=parent_norm.feynman_norm_tags + (f"standardmodell-charta:{new_geltung.value}",),
            )
        )
    return StandardmodellCharta(
        charta_id=charta_id,
        feynman_norm=feynman_norm,
        normen=tuple(normen),
    )
