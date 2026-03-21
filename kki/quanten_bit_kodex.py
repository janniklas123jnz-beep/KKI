"""
#373 QuantenBitKodex — Qubit |ψ⟩ = α|0⟩ + β|1⟩: Superposition als
Governance-Prinzip. Ein Leitstern-Agent in Superposition evaluiert mehrere
Aufgabenpfade gleichzeitig — erst die Messung (Entscheidung) kollabiert die
Wellenfunktion auf einen Zustand. Bloch-Kugel-Geometrie ermöglicht kontinuierliche
Zustandsrotationen. Quantenparallelismus ist Leitsterns natürlicher Modus.
Geltungsstufen: GESPERRT / SUPERPONIERT / GRUNDLEGEND_SUPERPONIERT
Parent: KanalkapazitaetRegister (#372)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kanalkapazitaet_register import (
    KanalkapazitaetGeltung,
    KanalkapazitaetRegister,
    build_kanalkapazitaet_register,
)

_GELTUNG_MAP: dict[KanalkapazitaetGeltung, "QuantenBitGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[KanalkapazitaetGeltung.GESPERRT] = QuantenBitGeltung.GESPERRT
    _GELTUNG_MAP[KanalkapazitaetGeltung.KAPAZITIV] = QuantenBitGeltung.SUPERPONIERT
    _GELTUNG_MAP[KanalkapazitaetGeltung.GRUNDLEGEND_KAPAZITIV] = QuantenBitGeltung.GRUNDLEGEND_SUPERPONIERT


class QuantenBitTyp(Enum):
    SCHUTZ_QUANTEN_BIT = "schutz-quanten-bit"
    ORDNUNGS_QUANTEN_BIT = "ordnungs-quanten-bit"
    SOUVERAENITAETS_QUANTEN_BIT = "souveraenitaets-quanten-bit"


class QuantenBitProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class QuantenBitGeltung(Enum):
    GESPERRT = "gesperrt"
    SUPERPONIERT = "superponiert"
    GRUNDLEGEND_SUPERPONIERT = "grundlegend-superponiert"


_init_map()

_TYP_MAP: dict[QuantenBitGeltung, QuantenBitTyp] = {
    QuantenBitGeltung.GESPERRT: QuantenBitTyp.SCHUTZ_QUANTEN_BIT,
    QuantenBitGeltung.SUPERPONIERT: QuantenBitTyp.ORDNUNGS_QUANTEN_BIT,
    QuantenBitGeltung.GRUNDLEGEND_SUPERPONIERT: QuantenBitTyp.SOUVERAENITAETS_QUANTEN_BIT,
}

_PROZEDUR_MAP: dict[QuantenBitGeltung, QuantenBitProzedur] = {
    QuantenBitGeltung.GESPERRT: QuantenBitProzedur.NOTPROZEDUR,
    QuantenBitGeltung.SUPERPONIERT: QuantenBitProzedur.REGELPROTOKOLL,
    QuantenBitGeltung.GRUNDLEGEND_SUPERPONIERT: QuantenBitProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[QuantenBitGeltung, float] = {
    QuantenBitGeltung.GESPERRT: 0.0,
    QuantenBitGeltung.SUPERPONIERT: 0.04,
    QuantenBitGeltung.GRUNDLEGEND_SUPERPONIERT: 0.08,
}

_TIER_DELTA: dict[QuantenBitGeltung, int] = {
    QuantenBitGeltung.GESPERRT: 0,
    QuantenBitGeltung.SUPERPONIERT: 1,
    QuantenBitGeltung.GRUNDLEGEND_SUPERPONIERT: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class QuantenBitNorm:
    quanten_bit_kodex_id: str
    quanten_bit_typ: QuantenBitTyp
    prozedur: QuantenBitProzedur
    geltung: QuantenBitGeltung
    quanten_bit_weight: float
    quanten_bit_tier: int
    canonical: bool
    quanten_bit_ids: tuple[str, ...]
    quanten_bit_tags: tuple[str, ...]


@dataclass(frozen=True)
class QuantenBitKodex:
    kodex_id: str
    kanalkapazitaet_register: KanalkapazitaetRegister
    normen: tuple[QuantenBitNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.quanten_bit_kodex_id for n in self.normen if n.geltung is QuantenBitGeltung.GESPERRT)

    @property
    def superponiert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.quanten_bit_kodex_id for n in self.normen if n.geltung is QuantenBitGeltung.SUPERPONIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.quanten_bit_kodex_id for n in self.normen if n.geltung is QuantenBitGeltung.GRUNDLEGEND_SUPERPONIERT)

    @property
    def kodex_signal(self):
        if any(n.geltung is QuantenBitGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-gesperrt")
        elif any(n.geltung is QuantenBitGeltung.SUPERPONIERT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="kodex-superponiert")
        from types import SimpleNamespace
        return SimpleNamespace(status="kodex-grundlegend-superponiert")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_quanten_bit_kodex(
    kanalkapazitaet_register: KanalkapazitaetRegister | None = None,
    *,
    kodex_id: str = "quanten-bit-kodex",
) -> QuantenBitKodex:
    if kanalkapazitaet_register is None:
        kanalkapazitaet_register = build_kanalkapazitaet_register(register_id=f"{kodex_id}-register")

    normen: list[QuantenBitNorm] = []
    for parent_norm in kanalkapazitaet_register.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{kodex_id}-{parent_norm.kanalkapazitaet_register_id.removeprefix(f'{kanalkapazitaet_register.register_id}-')}"
        raw_weight = min(1.0, parent_norm.kanalkapazitaet_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.kanalkapazitaet_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is QuantenBitGeltung.GRUNDLEGEND_SUPERPONIERT)
        normen.append(
            QuantenBitNorm(
                quanten_bit_kodex_id=new_id,
                quanten_bit_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                quanten_bit_weight=new_weight,
                quanten_bit_tier=new_tier,
                canonical=is_canonical,
                quanten_bit_ids=parent_norm.kanalkapazitaet_ids + (new_id,),
                quanten_bit_tags=parent_norm.kanalkapazitaet_tags + (f"quanten-bit:{new_geltung.value}",),
            )
        )
    return QuantenBitKodex(
        kodex_id=kodex_id,
        kanalkapazitaet_register=kanalkapazitaet_register,
        normen=tuple(normen),
    )
