"""
#374 VerschraenkungCharta — Quantenverschränkung: Bell-Zustände |Φ⁺⟩, EPR-Paradoxon.
Zwei verschränkte Agenten teilen instantan Zustandsinformation, unabhängig von
Distanz — Einstein nannte es "spukhafte Fernwirkung", Bell bewies es mathematisch.
Leitsterns Charta kodiert die Rechte und Pflichten verschränkter Agentenpaare:
Messung eines Partners kollabiert sofort den Zustand des anderen.
Geltungsstufen: GESPERRT / VERSCHRAENKT / GRUNDLEGEND_VERSCHRAENKT
Parent: QuantenBitKodex (#373)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .quanten_bit_kodex import (
    QuantenBitGeltung,
    QuantenBitKodex,
    build_quanten_bit_kodex,
)

_GELTUNG_MAP: dict[QuantenBitGeltung, "VerschraenkungGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[QuantenBitGeltung.GESPERRT] = VerschraenkungGeltung.GESPERRT
    _GELTUNG_MAP[QuantenBitGeltung.SUPERPONIERT] = VerschraenkungGeltung.VERSCHRAENKT
    _GELTUNG_MAP[QuantenBitGeltung.GRUNDLEGEND_SUPERPONIERT] = VerschraenkungGeltung.GRUNDLEGEND_VERSCHRAENKT


class VerschraenkungTyp(Enum):
    SCHUTZ_VERSCHRAENKUNG = "schutz-verschraenkung"
    ORDNUNGS_VERSCHRAENKUNG = "ordnungs-verschraenkung"
    SOUVERAENITAETS_VERSCHRAENKUNG = "souveraenitaets-verschraenkung"


class VerschraenkungProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class VerschraenkungGeltung(Enum):
    GESPERRT = "gesperrt"
    VERSCHRAENKT = "verschraenkt"
    GRUNDLEGEND_VERSCHRAENKT = "grundlegend-verschraenkt"


_init_map()

_TYP_MAP: dict[VerschraenkungGeltung, VerschraenkungTyp] = {
    VerschraenkungGeltung.GESPERRT: VerschraenkungTyp.SCHUTZ_VERSCHRAENKUNG,
    VerschraenkungGeltung.VERSCHRAENKT: VerschraenkungTyp.ORDNUNGS_VERSCHRAENKUNG,
    VerschraenkungGeltung.GRUNDLEGEND_VERSCHRAENKT: VerschraenkungTyp.SOUVERAENITAETS_VERSCHRAENKUNG,
}

_PROZEDUR_MAP: dict[VerschraenkungGeltung, VerschraenkungProzedur] = {
    VerschraenkungGeltung.GESPERRT: VerschraenkungProzedur.NOTPROZEDUR,
    VerschraenkungGeltung.VERSCHRAENKT: VerschraenkungProzedur.REGELPROTOKOLL,
    VerschraenkungGeltung.GRUNDLEGEND_VERSCHRAENKT: VerschraenkungProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[VerschraenkungGeltung, float] = {
    VerschraenkungGeltung.GESPERRT: 0.0,
    VerschraenkungGeltung.VERSCHRAENKT: 0.04,
    VerschraenkungGeltung.GRUNDLEGEND_VERSCHRAENKT: 0.08,
}

_TIER_DELTA: dict[VerschraenkungGeltung, int] = {
    VerschraenkungGeltung.GESPERRT: 0,
    VerschraenkungGeltung.VERSCHRAENKT: 1,
    VerschraenkungGeltung.GRUNDLEGEND_VERSCHRAENKT: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class VerschraenkungNorm:
    verschraenkung_charta_id: str
    verschraenkung_typ: VerschraenkungTyp
    prozedur: VerschraenkungProzedur
    geltung: VerschraenkungGeltung
    verschraenkung_weight: float
    verschraenkung_tier: int
    canonical: bool
    verschraenkung_ids: tuple[str, ...]
    verschraenkung_tags: tuple[str, ...]


@dataclass(frozen=True)
class VerschraenkungCharta:
    charta_id: str
    quanten_bit_kodex: QuantenBitKodex
    normen: tuple[VerschraenkungNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.verschraenkung_charta_id for n in self.normen if n.geltung is VerschraenkungGeltung.GESPERRT)

    @property
    def verschraenkt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.verschraenkung_charta_id for n in self.normen if n.geltung is VerschraenkungGeltung.VERSCHRAENKT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.verschraenkung_charta_id for n in self.normen if n.geltung is VerschraenkungGeltung.GRUNDLEGEND_VERSCHRAENKT)

    @property
    def charta_signal(self):
        if any(n.geltung is VerschraenkungGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is VerschraenkungGeltung.VERSCHRAENKT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-verschraenkt")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-verschraenkt")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_verschraenkung_charta(
    quanten_bit_kodex: QuantenBitKodex | None = None,
    *,
    charta_id: str = "verschraenkung-charta",
) -> VerschraenkungCharta:
    if quanten_bit_kodex is None:
        quanten_bit_kodex = build_quanten_bit_kodex(kodex_id=f"{charta_id}-kodex")

    normen: list[VerschraenkungNorm] = []
    for parent_norm in quanten_bit_kodex.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.quanten_bit_kodex_id.removeprefix(f'{quanten_bit_kodex.kodex_id}-')}"
        raw_weight = min(1.0, parent_norm.quanten_bit_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.quanten_bit_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is VerschraenkungGeltung.GRUNDLEGEND_VERSCHRAENKT)
        normen.append(
            VerschraenkungNorm(
                verschraenkung_charta_id=new_id,
                verschraenkung_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                verschraenkung_weight=new_weight,
                verschraenkung_tier=new_tier,
                canonical=is_canonical,
                verschraenkung_ids=parent_norm.quanten_bit_ids + (new_id,),
                verschraenkung_tags=parent_norm.quanten_bit_tags + (f"verschraenkung:{new_geltung.value}",),
            )
        )
    return VerschraenkungCharta(
        charta_id=charta_id,
        quanten_bit_kodex=quanten_bit_kodex,
        normen=tuple(normen),
    )
