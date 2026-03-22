"""
#458 EvolutionsNorm — Artbildung und Populationsgenetik: Hardy-Weinberg und Drift.
Hardy & Weinberg (1908): Gleichgewichtsgesetz — Allelfrequenzen in großen Populationen konstant.
Wright (1931): Genetischer Drift — Zufallsschwankungen in kleinen Populationen.
Mayr (1942): Allopatrische Artbildung — geografische Isolation als Artbildungsmechanismus.
Leitsterns Populations-Norm: Hardy-Weinberg-Gleichgewicht als Referenz für Schwarm-Diversität.
Geltungsstufen: GESPERRT / ARTBILDEND / GRUNDLEGEND_ARTBILDEND
Parent: OekologieSenat (#457) — *_norm-Muster
Block #451–#460: Evolutionsbiologie & Genetik
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .oekologie_senat import (
    OekologieSenat,
    OekologieSenatGeltung,
    build_oekologie_senat,
)

_GELTUNG_MAP: dict[OekologieSenatGeltung, "EvolutionsNormGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[OekologieSenatGeltung.GESPERRT] = EvolutionsNormGeltung.GESPERRT
    _GELTUNG_MAP[OekologieSenatGeltung.OEKOLOGISCH] = EvolutionsNormGeltung.ARTBILDEND
    _GELTUNG_MAP[OekologieSenatGeltung.GRUNDLEGEND_OEKOLOGISCH] = EvolutionsNormGeltung.GRUNDLEGEND_ARTBILDEND


class EvolutionsNormTyp(Enum):
    SCHUTZ_EVOLUTIONS_NORM = "schutz-evolutions-norm"
    ORDNUNGS_EVOLUTIONS_NORM = "ordnungs-evolutions-norm"
    SOUVERAENITAETS_EVOLUTIONS_NORM = "souveraenitaets-evolutions-norm"


class EvolutionsNormProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class EvolutionsNormGeltung(Enum):
    GESPERRT = "gesperrt"
    ARTBILDEND = "artbildend"
    GRUNDLEGEND_ARTBILDEND = "grundlegend-artbildend"


_init_map()

_TYP_MAP: dict[EvolutionsNormGeltung, EvolutionsNormTyp] = {
    EvolutionsNormGeltung.GESPERRT: EvolutionsNormTyp.SCHUTZ_EVOLUTIONS_NORM,
    EvolutionsNormGeltung.ARTBILDEND: EvolutionsNormTyp.ORDNUNGS_EVOLUTIONS_NORM,
    EvolutionsNormGeltung.GRUNDLEGEND_ARTBILDEND: EvolutionsNormTyp.SOUVERAENITAETS_EVOLUTIONS_NORM,
}

_PROZEDUR_MAP: dict[EvolutionsNormGeltung, EvolutionsNormProzedur] = {
    EvolutionsNormGeltung.GESPERRT: EvolutionsNormProzedur.NOTPROZEDUR,
    EvolutionsNormGeltung.ARTBILDEND: EvolutionsNormProzedur.REGELPROTOKOLL,
    EvolutionsNormGeltung.GRUNDLEGEND_ARTBILDEND: EvolutionsNormProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[EvolutionsNormGeltung, float] = {
    EvolutionsNormGeltung.GESPERRT: 0.0,
    EvolutionsNormGeltung.ARTBILDEND: 0.04,
    EvolutionsNormGeltung.GRUNDLEGEND_ARTBILDEND: 0.08,
}

_TIER_DELTA: dict[EvolutionsNormGeltung, int] = {
    EvolutionsNormGeltung.GESPERRT: 0,
    EvolutionsNormGeltung.ARTBILDEND: 1,
    EvolutionsNormGeltung.GRUNDLEGEND_ARTBILDEND: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses (*_norm pattern)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EvolutionsNormEintrag:
    norm_id: str
    evolutions_norm_typ: EvolutionsNormTyp
    prozedur: EvolutionsNormProzedur
    geltung: EvolutionsNormGeltung
    evolutions_norm_weight: float
    evolutions_norm_tier: int
    canonical: bool
    evolutions_norm_ids: tuple[str, ...]
    evolutions_norm_tags: tuple[str, ...]


@dataclass(frozen=True)
class EvolutionsNormSatz:
    norm_id: str
    oekologie_senat: OekologieSenat
    normen: tuple[EvolutionsNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is EvolutionsNormGeltung.GESPERRT)

    @property
    def artbildend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is EvolutionsNormGeltung.ARTBILDEND)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is EvolutionsNormGeltung.GRUNDLEGEND_ARTBILDEND)

    @property
    def norm_signal(self):
        if any(n.geltung is EvolutionsNormGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-gesperrt")
        elif any(n.geltung is EvolutionsNormGeltung.ARTBILDEND for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-artbildend")
        from types import SimpleNamespace
        return SimpleNamespace(status="norm-grundlegend-artbildend")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_evolutions_norm(
    oekologie_senat: OekologieSenat | None = None,
    *,
    norm_id: str = "evolutions-norm",
) -> EvolutionsNormSatz:
    if oekologie_senat is None:
        oekologie_senat = build_oekologie_senat(senat_id=f"{norm_id}-senat")

    normen: list[EvolutionsNormEintrag] = []
    for parent_norm in oekologie_senat.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{norm_id}-{parent_norm.oekologie_senat_id.removeprefix(f'{oekologie_senat.senat_id}-')}"
        raw_weight = min(1.0, parent_norm.oekologie_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.oekologie_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is EvolutionsNormGeltung.GRUNDLEGEND_ARTBILDEND)
        normen.append(
            EvolutionsNormEintrag(
                norm_id=new_id,
                evolutions_norm_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                evolutions_norm_weight=new_weight,
                evolutions_norm_tier=new_tier,
                canonical=is_canonical,
                evolutions_norm_ids=parent_norm.oekologie_ids + (new_id,),
                evolutions_norm_tags=parent_norm.oekologie_tags + (f"evolutions-norm:{new_geltung.value}",),
            )
        )
    return EvolutionsNormSatz(
        norm_id=norm_id,
        oekologie_senat=oekologie_senat,
        normen=tuple(normen),
    )
