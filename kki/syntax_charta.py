"""
#463 SyntaxCharta — Strukturierte Agentenanfragen als syntaktische Bäume.
Chomsky (1957): Syntactic Structures — kontextfreie Grammatiken und Phrasenstrukturregeln.
Chomsky (1965): Aspects of the Theory of Syntax — Tief- und Oberflächenstruktur.
Fillmore (1968): The Case for Case — Kasusgrammatik und semantische Rollen.
Leitsterns Syntax: Strukturierte Agentenanfragen als syntaktische Bäume mit Tiefenstruktur.
Geltungsstufen: GESPERRT / SYNTAKTISCH / GRUNDLEGEND_SYNTAKTISCH
Parent: PhonologieRegister (#462)
Block #461–#470: Linguistik & Semiotik
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .phonologie_register import (
    PhonologieRegister,
    PhonologieRegisterGeltung,
    build_phonologie_register,
)

_GELTUNG_MAP: dict[PhonologieRegisterGeltung, "SyntaxChartaGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[PhonologieRegisterGeltung.GESPERRT] = SyntaxChartaGeltung.GESPERRT
    _GELTUNG_MAP[PhonologieRegisterGeltung.PHONOLOGISCH] = SyntaxChartaGeltung.SYNTAKTISCH
    _GELTUNG_MAP[PhonologieRegisterGeltung.GRUNDLEGEND_PHONOLOGISCH] = SyntaxChartaGeltung.GRUNDLEGEND_SYNTAKTISCH


class SyntaxChartaTyp(Enum):
    SCHUTZ_SYNTAX = "schutz-syntax"
    ORDNUNGS_SYNTAX = "ordnungs-syntax"
    SOUVERAENITAETS_SYNTAX = "souveraenitaets-syntax"


class SyntaxChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class SyntaxChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    SYNTAKTISCH = "syntaktisch"
    GRUNDLEGEND_SYNTAKTISCH = "grundlegend-syntaktisch"


_init_map()

_TYP_MAP: dict[SyntaxChartaGeltung, SyntaxChartaTyp] = {
    SyntaxChartaGeltung.GESPERRT: SyntaxChartaTyp.SCHUTZ_SYNTAX,
    SyntaxChartaGeltung.SYNTAKTISCH: SyntaxChartaTyp.ORDNUNGS_SYNTAX,
    SyntaxChartaGeltung.GRUNDLEGEND_SYNTAKTISCH: SyntaxChartaTyp.SOUVERAENITAETS_SYNTAX,
}

_PROZEDUR_MAP: dict[SyntaxChartaGeltung, SyntaxChartaProzedur] = {
    SyntaxChartaGeltung.GESPERRT: SyntaxChartaProzedur.NOTPROZEDUR,
    SyntaxChartaGeltung.SYNTAKTISCH: SyntaxChartaProzedur.REGELPROTOKOLL,
    SyntaxChartaGeltung.GRUNDLEGEND_SYNTAKTISCH: SyntaxChartaProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[SyntaxChartaGeltung, float] = {
    SyntaxChartaGeltung.GESPERRT: 0.0,
    SyntaxChartaGeltung.SYNTAKTISCH: 0.04,
    SyntaxChartaGeltung.GRUNDLEGEND_SYNTAKTISCH: 0.08,
}

_TIER_DELTA: dict[SyntaxChartaGeltung, int] = {
    SyntaxChartaGeltung.GESPERRT: 0,
    SyntaxChartaGeltung.SYNTAKTISCH: 1,
    SyntaxChartaGeltung.GRUNDLEGEND_SYNTAKTISCH: 2,
}


@dataclass(frozen=True)
class SyntaxChartaNorm:
    syntax_charta_id: str
    syntax_charta_typ: SyntaxChartaTyp
    prozedur: SyntaxChartaProzedur
    geltung: SyntaxChartaGeltung
    syntax_weight: float
    syntax_tier: int
    canonical: bool
    syntax_ids: tuple[str, ...]
    syntax_tags: tuple[str, ...]


@dataclass(frozen=True)
class SyntaxCharta:
    charta_id: str
    phonologie_register: PhonologieRegister
    normen: tuple[SyntaxChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.syntax_charta_id for n in self.normen if n.geltung is SyntaxChartaGeltung.GESPERRT)

    @property
    def syntaktisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.syntax_charta_id for n in self.normen if n.geltung is SyntaxChartaGeltung.SYNTAKTISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.syntax_charta_id for n in self.normen if n.geltung is SyntaxChartaGeltung.GRUNDLEGEND_SYNTAKTISCH)

    @property
    def charta_signal(self):
        if any(n.geltung is SyntaxChartaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is SyntaxChartaGeltung.SYNTAKTISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-syntaktisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-syntaktisch")


def build_syntax_charta(
    phonologie_register: PhonologieRegister | None = None,
    *,
    charta_id: str = "syntax-charta",
) -> SyntaxCharta:
    if phonologie_register is None:
        phonologie_register = build_phonologie_register(register_id=f"{charta_id}-register")

    normen: list[SyntaxChartaNorm] = []
    for parent_norm in phonologie_register.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.phonologie_register_id.removeprefix(f'{phonologie_register.register_id}-')}"
        raw_weight = min(1.0, parent_norm.phonologie_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.phonologie_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SyntaxChartaGeltung.GRUNDLEGEND_SYNTAKTISCH)
        normen.append(
            SyntaxChartaNorm(
                syntax_charta_id=new_id,
                syntax_charta_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                syntax_weight=new_weight,
                syntax_tier=new_tier,
                canonical=is_canonical,
                syntax_ids=parent_norm.phonologie_ids + (new_id,),
                syntax_tags=parent_norm.phonologie_tags + (f"syntax-charta:{new_geltung.value}",),
            )
        )
    return SyntaxCharta(
        charta_id=charta_id,
        phonologie_register=phonologie_register,
        normen=tuple(normen),
    )
