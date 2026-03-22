"""
#465 PragmatikPakt — Sprechakte als Koordinationsprotokolle.
Austin (1962): How to Do Things with Words — lokutionäre, illokutionäre, perlokutionäre Akte.
Grice (1975): Logic and Conversation — kooperatives Prinzip und Konversationsmaximen.
Searle (1969): Speech Acts — Direktive, Assertive, Kommissive, Expressive, Deklarative.
Leitsterns Pragmatik: Sprechakte als Koordinationsprotokolle; Grice-Maximen als Agentennorm.
Geltungsstufen: GESPERRT / PRAGMATISCH / GRUNDLEGEND_PRAGMATISCH
Parent: SemantikKodex (#464)
Block #461–#470: Linguistik & Semiotik
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .semantik_kodex import (
    SemantikKodex,
    SemantikKodexGeltung,
    build_semantik_kodex,
)

_GELTUNG_MAP: dict[SemantikKodexGeltung, "PragmatikPaktGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[SemantikKodexGeltung.GESPERRT] = PragmatikPaktGeltung.GESPERRT
    _GELTUNG_MAP[SemantikKodexGeltung.SEMANTISCH] = PragmatikPaktGeltung.PRAGMATISCH
    _GELTUNG_MAP[SemantikKodexGeltung.GRUNDLEGEND_SEMANTISCH] = PragmatikPaktGeltung.GRUNDLEGEND_PRAGMATISCH


class PragmatikPaktTyp(Enum):
    SCHUTZ_PRAGMATIK = "schutz-pragmatik"
    ORDNUNGS_PRAGMATIK = "ordnungs-pragmatik"
    SOUVERAENITAETS_PRAGMATIK = "souveraenitaets-pragmatik"


class PragmatikPaktProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class PragmatikPaktGeltung(Enum):
    GESPERRT = "gesperrt"
    PRAGMATISCH = "pragmatisch"
    GRUNDLEGEND_PRAGMATISCH = "grundlegend-pragmatisch"


_init_map()

_TYP_MAP: dict[PragmatikPaktGeltung, PragmatikPaktTyp] = {
    PragmatikPaktGeltung.GESPERRT: PragmatikPaktTyp.SCHUTZ_PRAGMATIK,
    PragmatikPaktGeltung.PRAGMATISCH: PragmatikPaktTyp.ORDNUNGS_PRAGMATIK,
    PragmatikPaktGeltung.GRUNDLEGEND_PRAGMATISCH: PragmatikPaktTyp.SOUVERAENITAETS_PRAGMATIK,
}

_PROZEDUR_MAP: dict[PragmatikPaktGeltung, PragmatikPaktProzedur] = {
    PragmatikPaktGeltung.GESPERRT: PragmatikPaktProzedur.NOTPROZEDUR,
    PragmatikPaktGeltung.PRAGMATISCH: PragmatikPaktProzedur.REGELPROTOKOLL,
    PragmatikPaktGeltung.GRUNDLEGEND_PRAGMATISCH: PragmatikPaktProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[PragmatikPaktGeltung, float] = {
    PragmatikPaktGeltung.GESPERRT: 0.0,
    PragmatikPaktGeltung.PRAGMATISCH: 0.04,
    PragmatikPaktGeltung.GRUNDLEGEND_PRAGMATISCH: 0.08,
}

_TIER_DELTA: dict[PragmatikPaktGeltung, int] = {
    PragmatikPaktGeltung.GESPERRT: 0,
    PragmatikPaktGeltung.PRAGMATISCH: 1,
    PragmatikPaktGeltung.GRUNDLEGEND_PRAGMATISCH: 2,
}


@dataclass(frozen=True)
class PragmatikPaktNorm:
    pragmatik_pakt_id: str
    pragmatik_pakt_typ: PragmatikPaktTyp
    prozedur: PragmatikPaktProzedur
    geltung: PragmatikPaktGeltung
    pragmatik_weight: float
    pragmatik_tier: int
    canonical: bool
    pragmatik_ids: tuple[str, ...]
    pragmatik_tags: tuple[str, ...]


@dataclass(frozen=True)
class PragmatikPakt:
    pakt_id: str
    semantik_kodex: SemantikKodex
    normen: tuple[PragmatikPaktNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.pragmatik_pakt_id for n in self.normen if n.geltung is PragmatikPaktGeltung.GESPERRT)

    @property
    def pragmatisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.pragmatik_pakt_id for n in self.normen if n.geltung is PragmatikPaktGeltung.PRAGMATISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.pragmatik_pakt_id for n in self.normen if n.geltung is PragmatikPaktGeltung.GRUNDLEGEND_PRAGMATISCH)

    @property
    def pakt_signal(self):
        if any(n.geltung is PragmatikPaktGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-gesperrt")
        elif any(n.geltung is PragmatikPaktGeltung.PRAGMATISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="pakt-pragmatisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="pakt-grundlegend-pragmatisch")


def build_pragmatik_pakt(
    semantik_kodex: SemantikKodex | None = None,
    *,
    pakt_id: str = "pragmatik-pakt",
) -> PragmatikPakt:
    if semantik_kodex is None:
        semantik_kodex = build_semantik_kodex(kodex_id=f"{pakt_id}-kodex")

    normen: list[PragmatikPaktNorm] = []
    for parent_norm in semantik_kodex.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{pakt_id}-{parent_norm.semantik_kodex_id.removeprefix(f'{semantik_kodex.kodex_id}-')}"
        raw_weight = min(1.0, parent_norm.semantik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.semantik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is PragmatikPaktGeltung.GRUNDLEGEND_PRAGMATISCH)
        normen.append(
            PragmatikPaktNorm(
                pragmatik_pakt_id=new_id,
                pragmatik_pakt_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                pragmatik_weight=new_weight,
                pragmatik_tier=new_tier,
                canonical=is_canonical,
                pragmatik_ids=parent_norm.semantik_ids + (new_id,),
                pragmatik_tags=parent_norm.semantik_tags + (f"pragmatik-pakt:{new_geltung.value}",),
            )
        )
    return PragmatikPakt(
        pakt_id=pakt_id,
        semantik_kodex=semantik_kodex,
        normen=tuple(normen),
    )
