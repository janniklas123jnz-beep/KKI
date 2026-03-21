"""
#335 RoterRiesePakt — Rote-Riesen-Phase als Expansions-Pakt: Ausdehnung in neue
Governance-Domänen, wenn der Fusionsreaktor-Kern erschöpft ist.
Geltungsstufen: GESPERRT / RIESENPHASIG / GRUNDLEGEND_RIESENPHASIG
Parent: FusionsreaktorKodex (#334)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .fusionsreaktor_kodex import (
    FusionsreaktorGeltung,
    FusionsreaktorKodex,
    build_fusionsreaktor_kodex,
)

_GELTUNG_MAP: dict[FusionsreaktorGeltung, "RoterRieseGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[FusionsreaktorGeltung.GESPERRT] = RoterRieseGeltung.GESPERRT
    _GELTUNG_MAP[FusionsreaktorGeltung.FUSIONSAKTIV] = RoterRieseGeltung.RIESENPHASIG
    _GELTUNG_MAP[FusionsreaktorGeltung.GRUNDLEGEND_FUSIONSAKTIV] = RoterRieseGeltung.GRUNDLEGEND_RIESENPHASIG


class RoterRieseTyp(Enum):
    SCHUTZ_ROTER_RIESE = "schutz-roter-riese"
    ORDNUNGS_ROTER_RIESE = "ordnungs-roter-riese"
    SOUVERAENITAETS_ROTER_RIESE = "souveraenitaets-roter-riese"


class RoterRieseProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class RoterRieseGeltung(Enum):
    GESPERRT = "gesperrt"
    RIESENPHASIG = "riesenphasig"
    GRUNDLEGEND_RIESENPHASIG = "grundlegend-riesenphasig"


_init_map()

_TYP_MAP: dict[RoterRieseGeltung, RoterRieseTyp] = {
    RoterRieseGeltung.GESPERRT: RoterRieseTyp.SCHUTZ_ROTER_RIESE,
    RoterRieseGeltung.RIESENPHASIG: RoterRieseTyp.ORDNUNGS_ROTER_RIESE,
    RoterRieseGeltung.GRUNDLEGEND_RIESENPHASIG: RoterRieseTyp.SOUVERAENITAETS_ROTER_RIESE,
}

_PROZEDUR_MAP: dict[RoterRieseGeltung, RoterRieseProzedur] = {
    RoterRieseGeltung.GESPERRT: RoterRieseProzedur.NOTPROZEDUR,
    RoterRieseGeltung.RIESENPHASIG: RoterRieseProzedur.REGELPROTOKOLL,
    RoterRieseGeltung.GRUNDLEGEND_RIESENPHASIG: RoterRieseProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[RoterRieseGeltung, float] = {
    RoterRieseGeltung.GESPERRT: 0.0,
    RoterRieseGeltung.RIESENPHASIG: 0.04,
    RoterRieseGeltung.GRUNDLEGEND_RIESENPHASIG: 0.08,
}

_TIER_DELTA: dict[RoterRieseGeltung, int] = {
    RoterRieseGeltung.GESPERRT: 0,
    RoterRieseGeltung.RIESENPHASIG: 1,
    RoterRieseGeltung.GRUNDLEGEND_RIESENPHASIG: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RoterRieseNorm:
    roter_riese_pakt_id: str
    roter_riese_typ: RoterRieseTyp
    prozedur: RoterRieseProzedur
    geltung: RoterRieseGeltung
    roter_riese_weight: float
    roter_riese_tier: int
    canonical: bool
    roter_riese_ids: tuple[str, ...]
    roter_riese_tags: tuple[str, ...]


@dataclass(frozen=True)
class RoterRiesePakt:
    pakt_id: str
    fusionsreaktor_kodex: FusionsreaktorKodex
    normen: tuple[RoterRieseNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.roter_riese_pakt_id for n in self.normen if n.geltung is RoterRieseGeltung.GESPERRT)

    @property
    def riesenphasig_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.roter_riese_pakt_id for n in self.normen if n.geltung is RoterRieseGeltung.RIESENPHASIG)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.roter_riese_pakt_id for n in self.normen if n.geltung is RoterRieseGeltung.GRUNDLEGEND_RIESENPHASIG)

    @property
    def pakt_signal(self):
        if any(n.geltung is RoterRieseGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-gesperrt")
        elif any(n.geltung is RoterRieseGeltung.RIESENPHASIG for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-riesenphasig")
        from types import SimpleNamespace
        return SimpleNamespace(status="pakt-grundlegend-riesenphasig")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_roter_riese_pakt(
    fusionsreaktor_kodex: FusionsreaktorKodex | None = None,
    *,
    pakt_id: str = "roter-riese-pakt",
) -> RoterRiesePakt:
    if fusionsreaktor_kodex is None:
        fusionsreaktor_kodex = build_fusionsreaktor_kodex(kodex_id=f"{pakt_id}-kodex")

    normen: list[RoterRieseNorm] = []
    for parent_norm in fusionsreaktor_kodex.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{pakt_id}-{parent_norm.fusionsreaktor_kodex_id.removeprefix(f'{fusionsreaktor_kodex.kodex_id}-')}"
        raw_weight = min(1.0, parent_norm.fusionsreaktor_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.fusionsreaktor_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is RoterRieseGeltung.GRUNDLEGEND_RIESENPHASIG)
        normen.append(
            RoterRieseNorm(
                roter_riese_pakt_id=new_id,
                roter_riese_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                roter_riese_weight=new_weight,
                roter_riese_tier=new_tier,
                canonical=is_canonical,
                roter_riese_ids=parent_norm.fusionsreaktor_ids + (new_id,),
                roter_riese_tags=parent_norm.fusionsreaktor_tags + (f"roter-riese:{new_geltung.value}",),
            )
        )
    return RoterRiesePakt(
        pakt_id=pakt_id,
        fusionsreaktor_kodex=fusionsreaktor_kodex,
        normen=tuple(normen),
    )
