"""
#464 SemantikKodex — Agenten operieren auf Wahrheitsbedingungen.
Frege (1892): Über Sinn und Bedeutung — Sinn (Intension) vs. Bedeutung (Extension).
Tarski (1944): The Semantic Conception of Truth — Wahrheitsbedingungen formaler Sprachen.
Kripke (1972): Naming and Necessity — starre Designatoren und mögliche Welten.
Leitsterns Semantik: Agenten operieren auf Wahrheitsbedingungen; Bedeutung ist kontextuell verankert.
Geltungsstufen: GESPERRT / SEMANTISCH / GRUNDLEGEND_SEMANTISCH
Parent: SyntaxCharta (#463)
Block #461–#470: Linguistik & Semiotik
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .syntax_charta import (
    SyntaxCharta,
    SyntaxChartaGeltung,
    build_syntax_charta,
)

_GELTUNG_MAP: dict[SyntaxChartaGeltung, "SemantikKodexGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[SyntaxChartaGeltung.GESPERRT] = SemantikKodexGeltung.GESPERRT
    _GELTUNG_MAP[SyntaxChartaGeltung.SYNTAKTISCH] = SemantikKodexGeltung.SEMANTISCH
    _GELTUNG_MAP[SyntaxChartaGeltung.GRUNDLEGEND_SYNTAKTISCH] = SemantikKodexGeltung.GRUNDLEGEND_SEMANTISCH


class SemantikKodexTyp(Enum):
    SCHUTZ_SEMANTIK = "schutz-semantik"
    ORDNUNGS_SEMANTIK = "ordnungs-semantik"
    SOUVERAENITAETS_SEMANTIK = "souveraenitaets-semantik"


class SemantikKodexProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class SemantikKodexGeltung(Enum):
    GESPERRT = "gesperrt"
    SEMANTISCH = "semantisch"
    GRUNDLEGEND_SEMANTISCH = "grundlegend-semantisch"


_init_map()

_TYP_MAP: dict[SemantikKodexGeltung, SemantikKodexTyp] = {
    SemantikKodexGeltung.GESPERRT: SemantikKodexTyp.SCHUTZ_SEMANTIK,
    SemantikKodexGeltung.SEMANTISCH: SemantikKodexTyp.ORDNUNGS_SEMANTIK,
    SemantikKodexGeltung.GRUNDLEGEND_SEMANTISCH: SemantikKodexTyp.SOUVERAENITAETS_SEMANTIK,
}

_PROZEDUR_MAP: dict[SemantikKodexGeltung, SemantikKodexProzedur] = {
    SemantikKodexGeltung.GESPERRT: SemantikKodexProzedur.NOTPROZEDUR,
    SemantikKodexGeltung.SEMANTISCH: SemantikKodexProzedur.REGELPROTOKOLL,
    SemantikKodexGeltung.GRUNDLEGEND_SEMANTISCH: SemantikKodexProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[SemantikKodexGeltung, float] = {
    SemantikKodexGeltung.GESPERRT: 0.0,
    SemantikKodexGeltung.SEMANTISCH: 0.04,
    SemantikKodexGeltung.GRUNDLEGEND_SEMANTISCH: 0.08,
}

_TIER_DELTA: dict[SemantikKodexGeltung, int] = {
    SemantikKodexGeltung.GESPERRT: 0,
    SemantikKodexGeltung.SEMANTISCH: 1,
    SemantikKodexGeltung.GRUNDLEGEND_SEMANTISCH: 2,
}


@dataclass(frozen=True)
class SemantikKodexNorm:
    semantik_kodex_id: str
    semantik_kodex_typ: SemantikKodexTyp
    prozedur: SemantikKodexProzedur
    geltung: SemantikKodexGeltung
    semantik_weight: float
    semantik_tier: int
    canonical: bool
    semantik_ids: tuple[str, ...]
    semantik_tags: tuple[str, ...]


@dataclass(frozen=True)
class SemantikKodex:
    kodex_id: str
    syntax_charta: SyntaxCharta
    normen: tuple[SemantikKodexNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.semantik_kodex_id for n in self.normen if n.geltung is SemantikKodexGeltung.GESPERRT)

    @property
    def semantisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.semantik_kodex_id for n in self.normen if n.geltung is SemantikKodexGeltung.SEMANTISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.semantik_kodex_id for n in self.normen if n.geltung is SemantikKodexGeltung.GRUNDLEGEND_SEMANTISCH)

    @property
    def kodex_signal(self):
        if any(n.geltung is SemantikKodexGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-gesperrt")
        elif any(n.geltung is SemantikKodexGeltung.SEMANTISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-semantisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="kodex-grundlegend-semantisch")


def build_semantik_kodex(
    syntax_charta: SyntaxCharta | None = None,
    *,
    kodex_id: str = "semantik-kodex",
) -> SemantikKodex:
    if syntax_charta is None:
        syntax_charta = build_syntax_charta(charta_id=f"{kodex_id}-charta")

    normen: list[SemantikKodexNorm] = []
    for parent_norm in syntax_charta.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{kodex_id}-{parent_norm.syntax_charta_id.removeprefix(f'{syntax_charta.charta_id}-')}"
        raw_weight = min(1.0, parent_norm.syntax_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.syntax_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SemantikKodexGeltung.GRUNDLEGEND_SEMANTISCH)
        normen.append(
            SemantikKodexNorm(
                semantik_kodex_id=new_id,
                semantik_kodex_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                semantik_weight=new_weight,
                semantik_tier=new_tier,
                canonical=is_canonical,
                semantik_ids=parent_norm.syntax_ids + (new_id,),
                semantik_tags=parent_norm.syntax_tags + (f"semantik-kodex:{new_geltung.value}",),
            )
        )
    return SemantikKodex(
        kodex_id=kodex_id,
        syntax_charta=syntax_charta,
        normen=tuple(normen),
    )
