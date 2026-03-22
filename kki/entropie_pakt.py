"""
#425 EntropiePakt — Entropie: Thermodynamik und Informationsphysik.
Boltzmann (1877): S = k·ln(W) — thermodynamische Entropie als Maß der Mikrozustände.
2. Hauptsatz: ΔS ≥ 0. Maxwell's Dämon (1867): Informationsgewinn ↔ Entropiekosten.
Landauer-Prinzip (1961): Löschen von 1 Bit erzeugt mindestens k_B·T·ln(2) Wärme.
Physik der KI: Information ist physikalisch.
Geltungsstufen: GESPERRT / ENTROPISCH / GRUNDLEGEND_ENTROPISCH
Parent: RegelkreisKodex (#424)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .regelkreis_kodex import (
    RegelkreisKodex,
    RegelkreisKodexGeltung,
    build_regelkreis_kodex,
)

_GELTUNG_MAP: dict[RegelkreisKodexGeltung, "EntropiePaktGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[RegelkreisKodexGeltung.GESPERRT] = EntropiePaktGeltung.GESPERRT
    _GELTUNG_MAP[RegelkreisKodexGeltung.GEREGELT] = EntropiePaktGeltung.ENTROPISCH
    _GELTUNG_MAP[RegelkreisKodexGeltung.GRUNDLEGEND_GEREGELT] = EntropiePaktGeltung.GRUNDLEGEND_ENTROPISCH


class EntropiePaktTyp(Enum):
    SCHUTZ_ENTROPIE = "schutz-entropie"
    ORDNUNGS_ENTROPIE = "ordnungs-entropie"
    SOUVERAENITAETS_ENTROPIE = "souveraenitaets-entropie"


class EntropiePaktProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class EntropiePaktGeltung(Enum):
    GESPERRT = "gesperrt"
    ENTROPISCH = "entropisch"
    GRUNDLEGEND_ENTROPISCH = "grundlegend-entropisch"


_init_map()

_TYP_MAP: dict[EntropiePaktGeltung, EntropiePaktTyp] = {
    EntropiePaktGeltung.GESPERRT: EntropiePaktTyp.SCHUTZ_ENTROPIE,
    EntropiePaktGeltung.ENTROPISCH: EntropiePaktTyp.ORDNUNGS_ENTROPIE,
    EntropiePaktGeltung.GRUNDLEGEND_ENTROPISCH: EntropiePaktTyp.SOUVERAENITAETS_ENTROPIE,
}

_PROZEDUR_MAP: dict[EntropiePaktGeltung, EntropiePaktProzedur] = {
    EntropiePaktGeltung.GESPERRT: EntropiePaktProzedur.NOTPROZEDUR,
    EntropiePaktGeltung.ENTROPISCH: EntropiePaktProzedur.REGELPROTOKOLL,
    EntropiePaktGeltung.GRUNDLEGEND_ENTROPISCH: EntropiePaktProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[EntropiePaktGeltung, float] = {
    EntropiePaktGeltung.GESPERRT: 0.0,
    EntropiePaktGeltung.ENTROPISCH: 0.04,
    EntropiePaktGeltung.GRUNDLEGEND_ENTROPISCH: 0.08,
}

_TIER_DELTA: dict[EntropiePaktGeltung, int] = {
    EntropiePaktGeltung.GESPERRT: 0,
    EntropiePaktGeltung.ENTROPISCH: 1,
    EntropiePaktGeltung.GRUNDLEGEND_ENTROPISCH: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EntropiePaktNorm:
    entropie_pakt_id: str
    entropie_typ: EntropiePaktTyp
    prozedur: EntropiePaktProzedur
    geltung: EntropiePaktGeltung
    entropie_weight: float
    entropie_tier: int
    canonical: bool
    entropie_ids: tuple[str, ...]
    entropie_tags: tuple[str, ...]


@dataclass(frozen=True)
class EntropiePakt:
    pakt_id: str
    regelkreis_kodex: RegelkreisKodex
    normen: tuple[EntropiePaktNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.entropie_pakt_id for n in self.normen if n.geltung is EntropiePaktGeltung.GESPERRT)

    @property
    def entropisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.entropie_pakt_id for n in self.normen if n.geltung is EntropiePaktGeltung.ENTROPISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.entropie_pakt_id for n in self.normen if n.geltung is EntropiePaktGeltung.GRUNDLEGEND_ENTROPISCH)

    @property
    def pakt_signal(self):
        if any(n.geltung is EntropiePaktGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-gesperrt")
        elif any(n.geltung is EntropiePaktGeltung.ENTROPISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-entropisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="pakt-grundlegend-entropisch")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_entropie_pakt(
    regelkreis_kodex: RegelkreisKodex | None = None,
    *,
    pakt_id: str = "entropie-pakt",
) -> EntropiePakt:
    if regelkreis_kodex is None:
        regelkreis_kodex = build_regelkreis_kodex(kodex_id=f"{pakt_id}-kodex")

    normen: list[EntropiePaktNorm] = []
    for parent_norm in regelkreis_kodex.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{pakt_id}-{parent_norm.regelkreis_kodex_id.removeprefix(f'{regelkreis_kodex.kodex_id}-')}"
        raw_weight = min(1.0, parent_norm.regelkreis_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.regelkreis_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is EntropiePaktGeltung.GRUNDLEGEND_ENTROPISCH)
        normen.append(
            EntropiePaktNorm(
                entropie_pakt_id=new_id,
                entropie_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                entropie_weight=new_weight,
                entropie_tier=new_tier,
                canonical=is_canonical,
                entropie_ids=parent_norm.regelkreis_ids + (new_id,),
                entropie_tags=parent_norm.regelkreis_tags + (f"entropie-pakt:{new_geltung.value}",),
            )
        )
    return EntropiePakt(
        pakt_id=pakt_id,
        regelkreis_kodex=regelkreis_kodex,
        normen=tuple(normen),
    )
