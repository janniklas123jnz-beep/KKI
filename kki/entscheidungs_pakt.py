"""
#445 EntscheidungsPakt — Entscheidungstheorie: Erwartungsnutzen und Prospect Theory.
Savage (1954): Subjective Expected Utility — kohärente Präferenzen unter Unsicherheit.
Kahneman & Tversky (1979): Prospect Theory — Verlustaversion, Referenzpunkte. Nobel 2002.
Ellsberg (1961): Ellsberg-Paradoxon — Ambiguitätsaversion bei unbekannten Wahrscheinlichkeiten.
Leitsterns Agenten wissen: Verluste schmerzen stärker als gleich hohe Gewinne. Prospect-bewusst.
Geltungsstufen: GESPERRT / ENTSCHEIDEND / GRUNDLEGEND_ENTSCHEIDEND
Parent: MechanismusKodex (#444)
Block #441–#450: Spieltheorie & Entscheidungstheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .mechanismus_kodex import (
    MechanismusKodex,
    MechanismusKodexGeltung,
    build_mechanismus_kodex,
)

_GELTUNG_MAP: dict[MechanismusKodexGeltung, "EntscheidungsPaktGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[MechanismusKodexGeltung.GESPERRT] = EntscheidungsPaktGeltung.GESPERRT
    _GELTUNG_MAP[MechanismusKodexGeltung.MECHANISTISCH] = EntscheidungsPaktGeltung.ENTSCHEIDEND
    _GELTUNG_MAP[MechanismusKodexGeltung.GRUNDLEGEND_MECHANISTISCH] = EntscheidungsPaktGeltung.GRUNDLEGEND_ENTSCHEIDEND


class EntscheidungsPaktTyp(Enum):
    SCHUTZ_ENTSCHEIDUNG = "schutz-entscheidung"
    ORDNUNGS_ENTSCHEIDUNG = "ordnungs-entscheidung"
    SOUVERAENITAETS_ENTSCHEIDUNG = "souveraenitaets-entscheidung"


class EntscheidungsPaktProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class EntscheidungsPaktGeltung(Enum):
    GESPERRT = "gesperrt"
    ENTSCHEIDEND = "entscheidend"
    GRUNDLEGEND_ENTSCHEIDEND = "grundlegend-entscheidend"


_init_map()

_TYP_MAP: dict[EntscheidungsPaktGeltung, EntscheidungsPaktTyp] = {
    EntscheidungsPaktGeltung.GESPERRT: EntscheidungsPaktTyp.SCHUTZ_ENTSCHEIDUNG,
    EntscheidungsPaktGeltung.ENTSCHEIDEND: EntscheidungsPaktTyp.ORDNUNGS_ENTSCHEIDUNG,
    EntscheidungsPaktGeltung.GRUNDLEGEND_ENTSCHEIDEND: EntscheidungsPaktTyp.SOUVERAENITAETS_ENTSCHEIDUNG,
}

_PROZEDUR_MAP: dict[EntscheidungsPaktGeltung, EntscheidungsPaktProzedur] = {
    EntscheidungsPaktGeltung.GESPERRT: EntscheidungsPaktProzedur.NOTPROZEDUR,
    EntscheidungsPaktGeltung.ENTSCHEIDEND: EntscheidungsPaktProzedur.REGELPROTOKOLL,
    EntscheidungsPaktGeltung.GRUNDLEGEND_ENTSCHEIDEND: EntscheidungsPaktProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[EntscheidungsPaktGeltung, float] = {
    EntscheidungsPaktGeltung.GESPERRT: 0.0,
    EntscheidungsPaktGeltung.ENTSCHEIDEND: 0.04,
    EntscheidungsPaktGeltung.GRUNDLEGEND_ENTSCHEIDEND: 0.08,
}

_TIER_DELTA: dict[EntscheidungsPaktGeltung, int] = {
    EntscheidungsPaktGeltung.GESPERRT: 0,
    EntscheidungsPaktGeltung.ENTSCHEIDEND: 1,
    EntscheidungsPaktGeltung.GRUNDLEGEND_ENTSCHEIDEND: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EntscheidungsPaktNorm:
    entscheidungs_pakt_id: str
    entscheidungs_pakt_typ: EntscheidungsPaktTyp
    prozedur: EntscheidungsPaktProzedur
    geltung: EntscheidungsPaktGeltung
    entscheidungs_weight: float
    entscheidungs_tier: int
    canonical: bool
    entscheidungs_ids: tuple[str, ...]
    entscheidungs_tags: tuple[str, ...]


@dataclass(frozen=True)
class EntscheidungsPakt:
    pakt_id: str
    mechanismus_kodex: MechanismusKodex
    normen: tuple[EntscheidungsPaktNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.entscheidungs_pakt_id for n in self.normen if n.geltung is EntscheidungsPaktGeltung.GESPERRT)

    @property
    def entscheidend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.entscheidungs_pakt_id for n in self.normen if n.geltung is EntscheidungsPaktGeltung.ENTSCHEIDEND)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.entscheidungs_pakt_id for n in self.normen if n.geltung is EntscheidungsPaktGeltung.GRUNDLEGEND_ENTSCHEIDEND)

    @property
    def pakt_signal(self):
        if any(n.geltung is EntscheidungsPaktGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-gesperrt")
        elif any(n.geltung is EntscheidungsPaktGeltung.ENTSCHEIDEND for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-entscheidend")
        from types import SimpleNamespace
        return SimpleNamespace(status="pakt-grundlegend-entscheidend")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_entscheidungs_pakt(
    mechanismus_kodex: MechanismusKodex | None = None,
    *,
    pakt_id: str = "entscheidungs-pakt",
) -> EntscheidungsPakt:
    if mechanismus_kodex is None:
        mechanismus_kodex = build_mechanismus_kodex(kodex_id=f"{pakt_id}-kodex")

    normen: list[EntscheidungsPaktNorm] = []
    for parent_norm in mechanismus_kodex.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{pakt_id}-{parent_norm.mechanismus_kodex_id.removeprefix(f'{mechanismus_kodex.kodex_id}-')}"
        raw_weight = min(1.0, parent_norm.mechanismus_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.mechanismus_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is EntscheidungsPaktGeltung.GRUNDLEGEND_ENTSCHEIDEND)
        normen.append(
            EntscheidungsPaktNorm(
                entscheidungs_pakt_id=new_id,
                entscheidungs_pakt_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                entscheidungs_weight=new_weight,
                entscheidungs_tier=new_tier,
                canonical=is_canonical,
                entscheidungs_ids=parent_norm.mechanismus_ids + (new_id,),
                entscheidungs_tags=parent_norm.mechanismus_tags + (f"entscheidungs-pakt:{new_geltung.value}",),
            )
        )
    return EntscheidungsPakt(
        pakt_id=pakt_id,
        mechanismus_kodex=mechanismus_kodex,
        normen=tuple(normen),
    )
