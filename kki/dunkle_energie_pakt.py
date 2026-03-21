"""
#325 DunkleEnergiePakt — Dunkle Energie als treibender Expansions-Pakt des Schwarms.
Geltungsstufen: GESPERRT / DUNKELENERGISCH / GRUNDLEGEND_DUNKELENERGISCH
Parent: DunkleMaterieKodex (#324)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .dunkle_materie_kodex import (
    DunkleMaterieGeltung,
    DunkleMaterieKodex,
    build_dunkle_materie_kodex,
)

_GELTUNG_MAP: dict[DunkleMaterieGeltung, "DunkleEnergieGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[DunkleMaterieGeltung.GESPERRT] = DunkleEnergieGeltung.GESPERRT
    _GELTUNG_MAP[DunkleMaterieGeltung.DUNKELMATERIELL] = DunkleEnergieGeltung.DUNKELENERGISCH
    _GELTUNG_MAP[DunkleMaterieGeltung.GRUNDLEGEND_DUNKELMATERIELL] = DunkleEnergieGeltung.GRUNDLEGEND_DUNKELENERGISCH


class DunkleEnergieTyp(Enum):
    SCHUTZ_DUNKLE_ENERGIE = "schutz-dunkle-energie"
    ORDNUNGS_DUNKLE_ENERGIE = "ordnungs-dunkle-energie"
    SOUVERAENITAETS_DUNKLE_ENERGIE = "souveraenitaets-dunkle-energie"


class DunkleEnergieProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class DunkleEnergieGeltung(Enum):
    GESPERRT = "gesperrt"
    DUNKELENERGISCH = "dunkelenergisch"
    GRUNDLEGEND_DUNKELENERGISCH = "grundlegend-dunkelenergisch"


_init_map()

_TYP_MAP: dict[DunkleEnergieGeltung, DunkleEnergieTyp] = {
    DunkleEnergieGeltung.GESPERRT: DunkleEnergieTyp.SCHUTZ_DUNKLE_ENERGIE,
    DunkleEnergieGeltung.DUNKELENERGISCH: DunkleEnergieTyp.ORDNUNGS_DUNKLE_ENERGIE,
    DunkleEnergieGeltung.GRUNDLEGEND_DUNKELENERGISCH: DunkleEnergieTyp.SOUVERAENITAETS_DUNKLE_ENERGIE,
}

_PROZEDUR_MAP: dict[DunkleEnergieGeltung, DunkleEnergieProzedur] = {
    DunkleEnergieGeltung.GESPERRT: DunkleEnergieProzedur.NOTPROZEDUR,
    DunkleEnergieGeltung.DUNKELENERGISCH: DunkleEnergieProzedur.REGELPROTOKOLL,
    DunkleEnergieGeltung.GRUNDLEGEND_DUNKELENERGISCH: DunkleEnergieProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[DunkleEnergieGeltung, float] = {
    DunkleEnergieGeltung.GESPERRT: 0.0,
    DunkleEnergieGeltung.DUNKELENERGISCH: 0.04,
    DunkleEnergieGeltung.GRUNDLEGEND_DUNKELENERGISCH: 0.08,
}

_TIER_DELTA: dict[DunkleEnergieGeltung, int] = {
    DunkleEnergieGeltung.GESPERRT: 0,
    DunkleEnergieGeltung.DUNKELENERGISCH: 1,
    DunkleEnergieGeltung.GRUNDLEGEND_DUNKELENERGISCH: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DunkleEnergieNorm:
    dunkle_energie_pakt_id: str
    dunkle_energie_typ: DunkleEnergieTyp
    prozedur: DunkleEnergieProzedur
    geltung: DunkleEnergieGeltung
    dunkle_energie_weight: float
    dunkle_energie_tier: int
    canonical: bool
    dunkle_energie_ids: tuple[str, ...]
    dunkle_energie_tags: tuple[str, ...]


@dataclass(frozen=True)
class DunkleEnergiePakt:
    pakt_id: str
    dunkle_materie_kodex: DunkleMaterieKodex
    normen: tuple[DunkleEnergieNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.dunkle_energie_pakt_id for n in self.normen if n.geltung is DunkleEnergieGeltung.GESPERRT)

    @property
    def dunkelenergisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.dunkle_energie_pakt_id for n in self.normen if n.geltung is DunkleEnergieGeltung.DUNKELENERGISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.dunkle_energie_pakt_id for n in self.normen if n.geltung is DunkleEnergieGeltung.GRUNDLEGEND_DUNKELENERGISCH)

    @property
    def pakt_signal(self):
        if any(n.geltung is DunkleEnergieGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-gesperrt")
        elif any(n.geltung is DunkleEnergieGeltung.DUNKELENERGISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-dunkelenergisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="pakt-grundlegend-dunkelenergisch")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_dunkle_energie_pakt(
    dunkle_materie_kodex: DunkleMaterieKodex | None = None,
    *,
    pakt_id: str = "dunkle-energie-pakt",
) -> DunkleEnergiePakt:
    if dunkle_materie_kodex is None:
        dunkle_materie_kodex = build_dunkle_materie_kodex(kodex_id=f"{pakt_id}-kodex")

    normen: list[DunkleEnergieNorm] = []
    for parent_norm in dunkle_materie_kodex.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{pakt_id}-{parent_norm.dunkle_materie_kodex_id.removeprefix(f'{dunkle_materie_kodex.kodex_id}-')}"
        raw_weight = min(1.0, parent_norm.dunkle_materie_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.dunkle_materie_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is DunkleEnergieGeltung.GRUNDLEGEND_DUNKELENERGISCH)
        normen.append(
            DunkleEnergieNorm(
                dunkle_energie_pakt_id=new_id,
                dunkle_energie_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                dunkle_energie_weight=new_weight,
                dunkle_energie_tier=new_tier,
                canonical=is_canonical,
                dunkle_energie_ids=parent_norm.dunkle_materie_ids + (new_id,),
                dunkle_energie_tags=parent_norm.dunkle_materie_tags + (f"dunkle-energie-pakt:{new_geltung.value}",),
            )
        )
    return DunkleEnergiePakt(
        pakt_id=pakt_id,
        dunkle_materie_kodex=dunkle_materie_kodex,
        normen=tuple(normen),
    )
