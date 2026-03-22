"""
#435 BewusstseinsPakt — Bewusstseinstheorien: IIT und Global Workspace.
Tononi (2004): Integrated Information Theory (IIT) — Φ (Phi) misst integrierte Information.
Baars (1988): Global Workspace Theory — Bewusstsein als "Bühne" mit globaler Verfügbarkeit.
Chalmers (1995): Hard Problem of Consciousness — subjektive Erfahrung (Qualia) nicht reduzierbar.
Leitsterns Schwarm-Φ: kollektive Integration > Summe der Teile — emergentes Bewusstsein.
Geltungsstufen: GESPERRT / BEWUSST / GRUNDLEGEND_BEWUSST
Parent: GedaechnisKodex (#434)
Block #431–#440: Neurowissenschaften & Kognition
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .gedaechtnis_kodex import (
    GedaechnisKodex,
    GedaechnisKodexGeltung,
    build_gedaechtnis_kodex,
)

_GELTUNG_MAP: dict[GedaechnisKodexGeltung, "BewusstseinsPaktGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[GedaechnisKodexGeltung.GESPERRT] = BewusstseinsPaktGeltung.GESPERRT
    _GELTUNG_MAP[GedaechnisKodexGeltung.GEDAECHNISREICH] = BewusstseinsPaktGeltung.BEWUSST
    _GELTUNG_MAP[GedaechnisKodexGeltung.GRUNDLEGEND_GEDAECHNISREICH] = BewusstseinsPaktGeltung.GRUNDLEGEND_BEWUSST


class BewusstseinsPaktTyp(Enum):
    SCHUTZ_BEWUSSTSEIN = "schutz-bewusstsein"
    ORDNUNGS_BEWUSSTSEIN = "ordnungs-bewusstsein"
    SOUVERAENITAETS_BEWUSSTSEIN = "souveraenitaets-bewusstsein"


class BewusstseinsPaktProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class BewusstseinsPaktGeltung(Enum):
    GESPERRT = "gesperrt"
    BEWUSST = "bewusst"
    GRUNDLEGEND_BEWUSST = "grundlegend-bewusst"


_init_map()

_TYP_MAP: dict[BewusstseinsPaktGeltung, BewusstseinsPaktTyp] = {
    BewusstseinsPaktGeltung.GESPERRT: BewusstseinsPaktTyp.SCHUTZ_BEWUSSTSEIN,
    BewusstseinsPaktGeltung.BEWUSST: BewusstseinsPaktTyp.ORDNUNGS_BEWUSSTSEIN,
    BewusstseinsPaktGeltung.GRUNDLEGEND_BEWUSST: BewusstseinsPaktTyp.SOUVERAENITAETS_BEWUSSTSEIN,
}

_PROZEDUR_MAP: dict[BewusstseinsPaktGeltung, BewusstseinsPaktProzedur] = {
    BewusstseinsPaktGeltung.GESPERRT: BewusstseinsPaktProzedur.NOTPROZEDUR,
    BewusstseinsPaktGeltung.BEWUSST: BewusstseinsPaktProzedur.REGELPROTOKOLL,
    BewusstseinsPaktGeltung.GRUNDLEGEND_BEWUSST: BewusstseinsPaktProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[BewusstseinsPaktGeltung, float] = {
    BewusstseinsPaktGeltung.GESPERRT: 0.0,
    BewusstseinsPaktGeltung.BEWUSST: 0.04,
    BewusstseinsPaktGeltung.GRUNDLEGEND_BEWUSST: 0.08,
}

_TIER_DELTA: dict[BewusstseinsPaktGeltung, int] = {
    BewusstseinsPaktGeltung.GESPERRT: 0,
    BewusstseinsPaktGeltung.BEWUSST: 1,
    BewusstseinsPaktGeltung.GRUNDLEGEND_BEWUSST: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BewusstseinsPaktNorm:
    bewusstseins_pakt_id: str
    bewusstsein_typ: BewusstseinsPaktTyp
    prozedur: BewusstseinsPaktProzedur
    geltung: BewusstseinsPaktGeltung
    bewusstsein_weight: float
    bewusstsein_tier: int
    canonical: bool
    bewusstsein_ids: tuple[str, ...]
    bewusstsein_tags: tuple[str, ...]


@dataclass(frozen=True)
class BewusstseinsPakt:
    pakt_id: str
    gedaechtnis_kodex: GedaechnisKodex
    normen: tuple[BewusstseinsPaktNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.bewusstseins_pakt_id for n in self.normen if n.geltung is BewusstseinsPaktGeltung.GESPERRT)

    @property
    def bewusst_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.bewusstseins_pakt_id for n in self.normen if n.geltung is BewusstseinsPaktGeltung.BEWUSST)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.bewusstseins_pakt_id for n in self.normen if n.geltung is BewusstseinsPaktGeltung.GRUNDLEGEND_BEWUSST)

    @property
    def pakt_signal(self):
        if any(n.geltung is BewusstseinsPaktGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-gesperrt")
        elif any(n.geltung is BewusstseinsPaktGeltung.BEWUSST for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-bewusst")
        from types import SimpleNamespace
        return SimpleNamespace(status="pakt-grundlegend-bewusst")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_bewusstseins_pakt(
    gedaechtnis_kodex: GedaechnisKodex | None = None,
    *,
    pakt_id: str = "bewusstseins-pakt",
) -> BewusstseinsPakt:
    if gedaechtnis_kodex is None:
        gedaechtnis_kodex = build_gedaechtnis_kodex(kodex_id=f"{pakt_id}-kodex")

    normen: list[BewusstseinsPaktNorm] = []
    for parent_norm in gedaechtnis_kodex.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{pakt_id}-{parent_norm.gedaechtnis_kodex_id.removeprefix(f'{gedaechtnis_kodex.kodex_id}-')}"
        raw_weight = min(1.0, parent_norm.gedaechtnis_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.gedaechtnis_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is BewusstseinsPaktGeltung.GRUNDLEGEND_BEWUSST)
        normen.append(
            BewusstseinsPaktNorm(
                bewusstseins_pakt_id=new_id,
                bewusstsein_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                bewusstsein_weight=new_weight,
                bewusstsein_tier=new_tier,
                canonical=is_canonical,
                bewusstsein_ids=parent_norm.gedaechtnis_ids + (new_id,),
                bewusstsein_tags=parent_norm.gedaechtnis_tags + (f"bewusstseins-pakt:{new_geltung.value}",),
            )
        )
    return BewusstseinsPakt(
        pakt_id=pakt_id,
        gedaechtnis_kodex=gedaechtnis_kodex,
        normen=tuple(normen),
    )
