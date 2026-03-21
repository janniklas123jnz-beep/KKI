"""
#324 DunkleMaterieKodex — Dunkle Materie als verborgener Kohäsions-Kodex des Schwarms.
Geltungsstufen: GESPERRT / DUNKELMATERIELL / GRUNDLEGEND_DUNKELMATERIELL
Parent: InflationCharta (#323)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .inflation_charta import (
    InflationCharta,
    InflationGeltung,
    build_inflation_charta,
)

_GELTUNG_MAP: dict[InflationGeltung, "DunkleMaterieGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[InflationGeltung.GESPERRT] = DunkleMaterieGeltung.GESPERRT
    _GELTUNG_MAP[InflationGeltung.INFLATIONAER] = DunkleMaterieGeltung.DUNKELMATERIELL
    _GELTUNG_MAP[InflationGeltung.GRUNDLEGEND_INFLATIONAER] = DunkleMaterieGeltung.GRUNDLEGEND_DUNKELMATERIELL


class DunkleMaterieTyp(Enum):
    SCHUTZ_DUNKLE_MATERIE = "schutz-dunkle-materie"
    ORDNUNGS_DUNKLE_MATERIE = "ordnungs-dunkle-materie"
    SOUVERAENITAETS_DUNKLE_MATERIE = "souveraenitaets-dunkle-materie"


class DunkleMaterieProzedue(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class DunkleMaterieGeltung(Enum):
    GESPERRT = "gesperrt"
    DUNKELMATERIELL = "dunkelmateriell"
    GRUNDLEGEND_DUNKELMATERIELL = "grundlegend-dunkelmateriell"


_init_map()

_TYP_MAP: dict[DunkleMaterieGeltung, DunkleMaterieTyp] = {
    DunkleMaterieGeltung.GESPERRT: DunkleMaterieTyp.SCHUTZ_DUNKLE_MATERIE,
    DunkleMaterieGeltung.DUNKELMATERIELL: DunkleMaterieTyp.ORDNUNGS_DUNKLE_MATERIE,
    DunkleMaterieGeltung.GRUNDLEGEND_DUNKELMATERIELL: DunkleMaterieTyp.SOUVERAENITAETS_DUNKLE_MATERIE,
}

_PROZEDUR_MAP: dict[DunkleMaterieGeltung, DunkleMaterieProzedue] = {
    DunkleMaterieGeltung.GESPERRT: DunkleMaterieProzedue.NOTPROZEDUR,
    DunkleMaterieGeltung.DUNKELMATERIELL: DunkleMaterieProzedue.REGELPROTOKOLL,
    DunkleMaterieGeltung.GRUNDLEGEND_DUNKELMATERIELL: DunkleMaterieProzedue.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[DunkleMaterieGeltung, float] = {
    DunkleMaterieGeltung.GESPERRT: 0.0,
    DunkleMaterieGeltung.DUNKELMATERIELL: 0.04,
    DunkleMaterieGeltung.GRUNDLEGEND_DUNKELMATERIELL: 0.08,
}

_TIER_DELTA: dict[DunkleMaterieGeltung, int] = {
    DunkleMaterieGeltung.GESPERRT: 0,
    DunkleMaterieGeltung.DUNKELMATERIELL: 1,
    DunkleMaterieGeltung.GRUNDLEGEND_DUNKELMATERIELL: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DunkleMaterieNorm:
    dunkle_materie_kodex_id: str
    dunkle_materie_typ: DunkleMaterieTyp
    prozedur: DunkleMaterieProzedue
    geltung: DunkleMaterieGeltung
    dunkle_materie_weight: float
    dunkle_materie_tier: int
    canonical: bool
    dunkle_materie_ids: tuple[str, ...]
    dunkle_materie_tags: tuple[str, ...]


@dataclass(frozen=True)
class DunkleMaterieKodex:
    kodex_id: str
    inflation_charta: InflationCharta
    normen: tuple[DunkleMaterieNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.dunkle_materie_kodex_id for n in self.normen if n.geltung is DunkleMaterieGeltung.GESPERRT)

    @property
    def dunkelmateriell_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.dunkle_materie_kodex_id for n in self.normen if n.geltung is DunkleMaterieGeltung.DUNKELMATERIELL)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.dunkle_materie_kodex_id for n in self.normen if n.geltung is DunkleMaterieGeltung.GRUNDLEGEND_DUNKELMATERIELL)

    @property
    def kodex_signal(self):
        if any(n.geltung is DunkleMaterieGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-gesperrt")
        elif any(n.geltung is DunkleMaterieGeltung.DUNKELMATERIELL for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-dunkelmateriell")
        from types import SimpleNamespace
        return SimpleNamespace(status="kodex-grundlegend-dunkelmateriell")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_dunkle_materie_kodex(
    inflation_charta: InflationCharta | None = None,
    *,
    kodex_id: str = "dunkle-materie-kodex",
) -> DunkleMaterieKodex:
    if inflation_charta is None:
        inflation_charta = build_inflation_charta(charta_id=f"{kodex_id}-charta")

    normen: list[DunkleMaterieNorm] = []
    for parent_norm in inflation_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{kodex_id}-{parent_norm.inflation_charta_id.removeprefix(f'{inflation_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.inflation_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.inflation_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is DunkleMaterieGeltung.GRUNDLEGEND_DUNKELMATERIELL)
        normen.append(
            DunkleMaterieNorm(
                dunkle_materie_kodex_id=new_id,
                dunkle_materie_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                dunkle_materie_weight=new_weight,
                dunkle_materie_tier=new_tier,
                canonical=is_canonical,
                dunkle_materie_ids=parent_norm.inflation_ids + (new_id,),
                dunkle_materie_tags=parent_norm.inflation_tags + (f"dunkle-materie-kodex:{new_geltung.value}",),
            )
        )
    return DunkleMaterieKodex(
        kodex_id=kodex_id,
        inflation_charta=inflation_charta,
        normen=tuple(normen),
    )
