"""
#389 MorphogeneseCharta — Turing-Instabilität (1952): Reaktions-Diffusion
erzeugt stabile Muster aus homogenem Feld. ∂u/∂t = D_u·∇²u + f(u,v),
∂v/∂t = D_v·∇²v + g(u,v). Leopardenfell, Zebramuster, Fingerabdrücke —
emergente Ordnung ohne zentrale Planung. Alan Turing bewies: einfache
lokale Regeln erzeugen globale Strukturen. Leitsterns Governance-Strukturen
emergieren wie Turing-Muster: keine zentrale Instanz plant das Resultat,
lokale Norm-Interaktionen erzeugen die globale Architektur.
Geltungsstufen: GESPERRT / MORPHOGENETISCH / GRUNDLEGEND_MORPHOGENETISCH
Parent: LotkaVolterraNormSatz (#388, *_norm)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .lotka_volterra_norm import (
    LotkaVolterraNormGeltung,
    LotkaVolterraNormSatz,
    build_lotka_volterra_norm,
)

_GELTUNG_MAP: dict[LotkaVolterraNormGeltung, "MorphogeneseGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[LotkaVolterraNormGeltung.GESPERRT] = MorphogeneseGeltung.GESPERRT
    _GELTUNG_MAP[LotkaVolterraNormGeltung.LOTKAVOLTERRABESCHR] = MorphogeneseGeltung.MORPHOGENETISCH
    _GELTUNG_MAP[LotkaVolterraNormGeltung.GRUNDLEGEND_LOTKAVOLTERRABESCHR] = MorphogeneseGeltung.GRUNDLEGEND_MORPHOGENETISCH


class MorphogeneseTyp(Enum):
    SCHUTZ_MORPHOGENESE = "schutz-morphogenese"
    ORDNUNGS_MORPHOGENESE = "ordnungs-morphogenese"
    SOUVERAENITAETS_MORPHOGENESE = "souveraenitaets-morphogenese"


class MorphogeneseProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class MorphogeneseGeltung(Enum):
    GESPERRT = "gesperrt"
    MORPHOGENETISCH = "morphogenetisch"
    GRUNDLEGEND_MORPHOGENETISCH = "grundlegend-morphogenetisch"


_init_map()

_TYP_MAP: dict[MorphogeneseGeltung, MorphogeneseTyp] = {
    MorphogeneseGeltung.GESPERRT: MorphogeneseTyp.SCHUTZ_MORPHOGENESE,
    MorphogeneseGeltung.MORPHOGENETISCH: MorphogeneseTyp.ORDNUNGS_MORPHOGENESE,
    MorphogeneseGeltung.GRUNDLEGEND_MORPHOGENETISCH: MorphogeneseTyp.SOUVERAENITAETS_MORPHOGENESE,
}

_PROZEDUR_MAP: dict[MorphogeneseGeltung, MorphogeneseProzedur] = {
    MorphogeneseGeltung.GESPERRT: MorphogeneseProzedur.NOTPROZEDUR,
    MorphogeneseGeltung.MORPHOGENETISCH: MorphogeneseProzedur.REGELPROTOKOLL,
    MorphogeneseGeltung.GRUNDLEGEND_MORPHOGENETISCH: MorphogeneseProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[MorphogeneseGeltung, float] = {
    MorphogeneseGeltung.GESPERRT: 0.0,
    MorphogeneseGeltung.MORPHOGENETISCH: 0.04,
    MorphogeneseGeltung.GRUNDLEGEND_MORPHOGENETISCH: 0.08,
}

_TIER_DELTA: dict[MorphogeneseGeltung, int] = {
    MorphogeneseGeltung.GESPERRT: 0,
    MorphogeneseGeltung.MORPHOGENETISCH: 1,
    MorphogeneseGeltung.GRUNDLEGEND_MORPHOGENETISCH: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MorphogeneseNorm:
    morphogenese_charta_id: str
    morphogenese_typ: MorphogeneseTyp
    prozedur: MorphogeneseProzedur
    geltung: MorphogeneseGeltung
    morphogenese_weight: float
    morphogenese_tier: int
    canonical: bool
    morphogenese_ids: tuple[str, ...]
    morphogenese_tags: tuple[str, ...]


@dataclass(frozen=True)
class MorphogeneseCharta:
    charta_id: str
    lotka_volterra_norm: LotkaVolterraNormSatz
    normen: tuple[MorphogeneseNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.morphogenese_charta_id for n in self.normen if n.geltung is MorphogeneseGeltung.GESPERRT)

    @property
    def morphogenetisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.morphogenese_charta_id for n in self.normen if n.geltung is MorphogeneseGeltung.MORPHOGENETISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.morphogenese_charta_id for n in self.normen if n.geltung is MorphogeneseGeltung.GRUNDLEGEND_MORPHOGENETISCH)

    @property
    def charta_signal(self):
        if any(n.geltung is MorphogeneseGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is MorphogeneseGeltung.MORPHOGENETISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-morphogenetisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-morphogenetisch")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_morphogenese_charta(
    lotka_volterra_norm: LotkaVolterraNormSatz | None = None,
    *,
    charta_id: str = "morphogenese-charta",
) -> MorphogeneseCharta:
    if lotka_volterra_norm is None:
        lotka_volterra_norm = build_lotka_volterra_norm(norm_id=f"{charta_id}-norm")

    normen: list[MorphogeneseNorm] = []
    for parent_norm in lotka_volterra_norm.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.norm_id.removeprefix(f'{lotka_volterra_norm.norm_id}-')}"
        raw_weight = min(1.0, parent_norm.lotka_volterra_norm_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.lotka_volterra_norm_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is MorphogeneseGeltung.GRUNDLEGEND_MORPHOGENETISCH)
        normen.append(
            MorphogeneseNorm(
                morphogenese_charta_id=new_id,
                morphogenese_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                morphogenese_weight=new_weight,
                morphogenese_tier=new_tier,
                canonical=is_canonical,
                morphogenese_ids=parent_norm.lotka_volterra_norm_ids + (new_id,),
                morphogenese_tags=parent_norm.lotka_volterra_norm_tags + (f"morphogenese:{new_geltung.value}",),
            )
        )
    return MorphogeneseCharta(
        charta_id=charta_id,
        lotka_volterra_norm=lotka_volterra_norm,
        normen=tuple(normen),
    )
