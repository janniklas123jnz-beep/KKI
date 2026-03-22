"""
#462 PhonologieRegister — Distinktive Merkmale als binäre Codes.
Troubetzkoy (1939): Grundzüge der Phonologie — phonologische Oppositionen und distinktive Merkmale.
Jakobson (1941): Kindersprache, Aphasie und allgemeine Lautgesetze — Merkmaltheorie.
Chomsky & Halle (1968): The Sound Pattern of English — Generative Phonologie.
Leitsterns Phonologie: Distinktive Merkmale als binäre Codes im Agent-Kommunikationsprotokoll.
Geltungsstufen: GESPERRT / PHONOLOGISCH / GRUNDLEGEND_PHONOLOGISCH
Parent: SprachFeld (#461)
Block #461–#470: Linguistik & Semiotik
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .sprach_feld import (
    SprachFeld,
    SprachFeldGeltung,
    build_sprach_feld,
)

_GELTUNG_MAP: dict[SprachFeldGeltung, "PhonologieRegisterGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[SprachFeldGeltung.GESPERRT] = PhonologieRegisterGeltung.GESPERRT
    _GELTUNG_MAP[SprachFeldGeltung.SPRACHLICH] = PhonologieRegisterGeltung.PHONOLOGISCH
    _GELTUNG_MAP[SprachFeldGeltung.GRUNDLEGEND_SPRACHLICH] = PhonologieRegisterGeltung.GRUNDLEGEND_PHONOLOGISCH


class PhonologieRegisterTyp(Enum):
    SCHUTZ_PHONOLOGIE = "schutz-phonologie"
    ORDNUNGS_PHONOLOGIE = "ordnungs-phonologie"
    SOUVERAENITAETS_PHONOLOGIE = "souveraenitaets-phonologie"


class PhonologieRegisterProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class PhonologieRegisterGeltung(Enum):
    GESPERRT = "gesperrt"
    PHONOLOGISCH = "phonologisch"
    GRUNDLEGEND_PHONOLOGISCH = "grundlegend-phonologisch"


_init_map()

_TYP_MAP: dict[PhonologieRegisterGeltung, PhonologieRegisterTyp] = {
    PhonologieRegisterGeltung.GESPERRT: PhonologieRegisterTyp.SCHUTZ_PHONOLOGIE,
    PhonologieRegisterGeltung.PHONOLOGISCH: PhonologieRegisterTyp.ORDNUNGS_PHONOLOGIE,
    PhonologieRegisterGeltung.GRUNDLEGEND_PHONOLOGISCH: PhonologieRegisterTyp.SOUVERAENITAETS_PHONOLOGIE,
}

_PROZEDUR_MAP: dict[PhonologieRegisterGeltung, PhonologieRegisterProzedur] = {
    PhonologieRegisterGeltung.GESPERRT: PhonologieRegisterProzedur.NOTPROZEDUR,
    PhonologieRegisterGeltung.PHONOLOGISCH: PhonologieRegisterProzedur.REGELPROTOKOLL,
    PhonologieRegisterGeltung.GRUNDLEGEND_PHONOLOGISCH: PhonologieRegisterProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[PhonologieRegisterGeltung, float] = {
    PhonologieRegisterGeltung.GESPERRT: 0.0,
    PhonologieRegisterGeltung.PHONOLOGISCH: 0.04,
    PhonologieRegisterGeltung.GRUNDLEGEND_PHONOLOGISCH: 0.08,
}

_TIER_DELTA: dict[PhonologieRegisterGeltung, int] = {
    PhonologieRegisterGeltung.GESPERRT: 0,
    PhonologieRegisterGeltung.PHONOLOGISCH: 1,
    PhonologieRegisterGeltung.GRUNDLEGEND_PHONOLOGISCH: 2,
}


@dataclass(frozen=True)
class PhonologieRegisterNorm:
    phonologie_register_id: str
    phonologie_register_typ: PhonologieRegisterTyp
    prozedur: PhonologieRegisterProzedur
    geltung: PhonologieRegisterGeltung
    phonologie_weight: float
    phonologie_tier: int
    canonical: bool
    phonologie_ids: tuple[str, ...]
    phonologie_tags: tuple[str, ...]


@dataclass(frozen=True)
class PhonologieRegister:
    register_id: str
    sprach_feld: SprachFeld
    normen: tuple[PhonologieRegisterNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.phonologie_register_id for n in self.normen if n.geltung is PhonologieRegisterGeltung.GESPERRT)

    @property
    def phonologisch_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.phonologie_register_id for n in self.normen if n.geltung is PhonologieRegisterGeltung.PHONOLOGISCH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.phonologie_register_id for n in self.normen if n.geltung is PhonologieRegisterGeltung.GRUNDLEGEND_PHONOLOGISCH)

    @property
    def register_signal(self):
        if any(n.geltung is PhonologieRegisterGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-gesperrt")
        elif any(n.geltung is PhonologieRegisterGeltung.PHONOLOGISCH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-phonologisch")
        from types import SimpleNamespace
        return SimpleNamespace(status="register-grundlegend-phonologisch")


def build_phonologie_register(
    sprach_feld: SprachFeld | None = None,
    *,
    register_id: str = "phonologie-register",
) -> PhonologieRegister:
    if sprach_feld is None:
        sprach_feld = build_sprach_feld(feld_id=f"{register_id}-feld")

    normen: list[PhonologieRegisterNorm] = []
    for parent_norm in sprach_feld.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{register_id}-{parent_norm.sprach_feld_id.removeprefix(f'{sprach_feld.feld_id}-')}"
        raw_weight = min(1.0, parent_norm.sprach_feld_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.sprach_feld_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is PhonologieRegisterGeltung.GRUNDLEGEND_PHONOLOGISCH)
        normen.append(
            PhonologieRegisterNorm(
                phonologie_register_id=new_id,
                phonologie_register_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                phonologie_weight=new_weight,
                phonologie_tier=new_tier,
                canonical=is_canonical,
                phonologie_ids=parent_norm.sprach_feld_ids + (new_id,),
                phonologie_tags=parent_norm.sprach_feld_tags + (f"phonologie-register:{new_geltung.value}",),
            )
        )
    return PhonologieRegister(
        register_id=register_id,
        sprach_feld=sprach_feld,
        normen=tuple(normen),
    )
