"""
#318 FeynmanNorm — Feynman-Diagramme als transparente Interaktionsprotokolle.
*_norm pattern: Container = FeynmanNormSatz, Entry = FeynmanNormEintrag
Geltungsstufen: GESPERRT / FEYNMANDIAGRAMMIERT / GRUNDLEGEND_FEYNMANDIAGRAMMIERT
Parent: SymmetriebrechungsSenat (#317)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .symmetriebrechungs_senat import (
    SymmetriebrechungsGeltung,
    SymmetriebrechungsSenat,
    build_symmetriebrechungs_senat,
)

_GELTUNG_MAP: dict[SymmetriebrechungsGeltung, "FeynmanNormGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[SymmetriebrechungsGeltung.GESPERRT] = FeynmanNormGeltung.GESPERRT
    _GELTUNG_MAP[SymmetriebrechungsGeltung.SYMMETRIEGEBROCHEN] = FeynmanNormGeltung.FEYNMANDIAGRAMMIERT
    _GELTUNG_MAP[SymmetriebrechungsGeltung.GRUNDLEGEND_SYMMETRIEGEBROCHEN] = FeynmanNormGeltung.GRUNDLEGEND_FEYNMANDIAGRAMMIERT


class FeynmanNormTyp(Enum):
    SCHUTZ_FEYNMAN = "schutz-feynman"
    ORDNUNGS_FEYNMAN = "ordnungs-feynman"
    SOUVERAENITAETS_FEYNMAN = "souveraenitaets-feynman"


class FeynmanNormProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class FeynmanNormGeltung(Enum):
    GESPERRT = "gesperrt"
    FEYNMANDIAGRAMMIERT = "feynmandiagrammiert"
    GRUNDLEGEND_FEYNMANDIAGRAMMIERT = "grundlegend-feynmandiagrammiert"


_init_map()

_TYP_MAP: dict[FeynmanNormGeltung, FeynmanNormTyp] = {
    FeynmanNormGeltung.GESPERRT: FeynmanNormTyp.SCHUTZ_FEYNMAN,
    FeynmanNormGeltung.FEYNMANDIAGRAMMIERT: FeynmanNormTyp.ORDNUNGS_FEYNMAN,
    FeynmanNormGeltung.GRUNDLEGEND_FEYNMANDIAGRAMMIERT: FeynmanNormTyp.SOUVERAENITAETS_FEYNMAN,
}

_PROZEDUR_MAP: dict[FeynmanNormGeltung, FeynmanNormProzedur] = {
    FeynmanNormGeltung.GESPERRT: FeynmanNormProzedur.NOTPROZEDUR,
    FeynmanNormGeltung.FEYNMANDIAGRAMMIERT: FeynmanNormProzedur.REGELPROTOKOLL,
    FeynmanNormGeltung.GRUNDLEGEND_FEYNMANDIAGRAMMIERT: FeynmanNormProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[FeynmanNormGeltung, float] = {
    FeynmanNormGeltung.GESPERRT: 0.0,
    FeynmanNormGeltung.FEYNMANDIAGRAMMIERT: 0.04,
    FeynmanNormGeltung.GRUNDLEGEND_FEYNMANDIAGRAMMIERT: 0.08,
}

_TIER_DELTA: dict[FeynmanNormGeltung, int] = {
    FeynmanNormGeltung.GESPERRT: 0,
    FeynmanNormGeltung.FEYNMANDIAGRAMMIERT: 1,
    FeynmanNormGeltung.GRUNDLEGEND_FEYNMANDIAGRAMMIERT: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses  (*_norm pattern)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FeynmanNormEintrag:
    norm_id: str
    feynman_norm_typ: FeynmanNormTyp
    prozedur: FeynmanNormProzedur
    geltung: FeynmanNormGeltung
    feynman_norm_weight: float
    feynman_norm_tier: int
    canonical: bool
    feynman_norm_ids: tuple[str, ...]
    feynman_norm_tags: tuple[str, ...]


@dataclass(frozen=True)
class FeynmanNormSatz:
    norm_id: str
    symmetriebrechungs_senat: SymmetriebrechungsSenat
    normen: tuple[FeynmanNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is FeynmanNormGeltung.GESPERRT)

    @property
    def feynmandiagrammiert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is FeynmanNormGeltung.FEYNMANDIAGRAMMIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is FeynmanNormGeltung.GRUNDLEGEND_FEYNMANDIAGRAMMIERT)

    @property
    def norm_signal(self):
        if any(n.geltung is FeynmanNormGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-gesperrt")
        elif any(n.geltung is FeynmanNormGeltung.FEYNMANDIAGRAMMIERT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-feynmandiagrammiert")
        from types import SimpleNamespace
        return SimpleNamespace(status="norm-grundlegend-feynmandiagrammiert")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_feynman_norm(
    symmetriebrechungs_senat: SymmetriebrechungsSenat | None = None,
    *,
    norm_id: str = "feynman-norm",
) -> FeynmanNormSatz:
    if symmetriebrechungs_senat is None:
        symmetriebrechungs_senat = build_symmetriebrechungs_senat(senat_id=f"{norm_id}-senat")

    normen: list[FeynmanNormEintrag] = []
    for parent_norm in symmetriebrechungs_senat.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{norm_id}-{parent_norm.symmetriebrechungs_senat_id.removeprefix(f'{symmetriebrechungs_senat.senat_id}-')}"
        raw_weight = min(1.0, parent_norm.symmetriebrechungs_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.symmetriebrechungs_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is FeynmanNormGeltung.GRUNDLEGEND_FEYNMANDIAGRAMMIERT)
        normen.append(
            FeynmanNormEintrag(
                norm_id=new_id,
                feynman_norm_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                feynman_norm_weight=new_weight,
                feynman_norm_tier=new_tier,
                canonical=is_canonical,
                feynman_norm_ids=parent_norm.symmetriebrechungs_ids + (new_id,),
                feynman_norm_tags=parent_norm.symmetriebrechungs_tags + (f"feynman-norm:{new_geltung.value}",),
            )
        )
    return FeynmanNormSatz(
        norm_id=norm_id,
        symmetriebrechungs_senat=symmetriebrechungs_senat,
        normen=tuple(normen),
    )
