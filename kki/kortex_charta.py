"""
#433 KortexCharta — Neokortex: Cortical Columns und kortikale Hierarchie.
Mountcastle (1957): Kortikale Kolumne als funktionale Grundeinheit des Neokortex.
Felleman & Van Essen (1991): Hierarchische Kortexorganisation — 32 Areale, 305 Verbindungen.
Brodmann-Areale (1909): zytoarchitektonische Karte — 52 Felder, heute Goldstandard.
Leitsterns Governance ist kortex-artig: hierarchisch, kolumnar, spezialisiert.
Geltungsstufen: GESPERRT / KORTIKAL / GRUNDLEGEND_KORTIKAL
Parent: SynaptikRegister (#432)
Block #431–#440: Neurowissenschaften & Kognition
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .synaptik_register import (
    SynaptikRegister,
    SynaptikRegisterGeltung,
    build_synaptik_register,
)

_GELTUNG_MAP: dict[SynaptikRegisterGeltung, "KortexChartaGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[SynaptikRegisterGeltung.GESPERRT] = KortexChartaGeltung.GESPERRT
    _GELTUNG_MAP[SynaptikRegisterGeltung.SYNAPTISCH] = KortexChartaGeltung.KORTIKAL
    _GELTUNG_MAP[SynaptikRegisterGeltung.GRUNDLEGEND_SYNAPTISCH] = KortexChartaGeltung.GRUNDLEGEND_KORTIKAL


class KortexChartaTyp(Enum):
    SCHUTZ_KORTEX = "schutz-kortex"
    ORDNUNGS_KORTEX = "ordnungs-kortex"
    SOUVERAENITAETS_KORTEX = "souveraenitaets-kortex"


class KortexChartaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KortexChartaGeltung(Enum):
    GESPERRT = "gesperrt"
    KORTIKAL = "kortikal"
    GRUNDLEGEND_KORTIKAL = "grundlegend-kortikal"


_init_map()

_TYP_MAP: dict[KortexChartaGeltung, KortexChartaTyp] = {
    KortexChartaGeltung.GESPERRT: KortexChartaTyp.SCHUTZ_KORTEX,
    KortexChartaGeltung.KORTIKAL: KortexChartaTyp.ORDNUNGS_KORTEX,
    KortexChartaGeltung.GRUNDLEGEND_KORTIKAL: KortexChartaTyp.SOUVERAENITAETS_KORTEX,
}

_PROZEDUR_MAP: dict[KortexChartaGeltung, KortexChartaProzedur] = {
    KortexChartaGeltung.GESPERRT: KortexChartaProzedur.NOTPROZEDUR,
    KortexChartaGeltung.KORTIKAL: KortexChartaProzedur.REGELPROTOKOLL,
    KortexChartaGeltung.GRUNDLEGEND_KORTIKAL: KortexChartaProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[KortexChartaGeltung, float] = {
    KortexChartaGeltung.GESPERRT: 0.0,
    KortexChartaGeltung.KORTIKAL: 0.04,
    KortexChartaGeltung.GRUNDLEGEND_KORTIKAL: 0.08,
}

_TIER_DELTA: dict[KortexChartaGeltung, int] = {
    KortexChartaGeltung.GESPERRT: 0,
    KortexChartaGeltung.KORTIKAL: 1,
    KortexChartaGeltung.GRUNDLEGEND_KORTIKAL: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class KortexChartaNorm:
    kortex_charta_id: str
    kortex_typ: KortexChartaTyp
    prozedur: KortexChartaProzedur
    geltung: KortexChartaGeltung
    kortex_weight: float
    kortex_tier: int
    canonical: bool
    kortex_ids: tuple[str, ...]
    kortex_tags: tuple[str, ...]


@dataclass(frozen=True)
class KortexCharta:
    charta_id: str
    synaptik_register: SynaptikRegister
    normen: tuple[KortexChartaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kortex_charta_id for n in self.normen if n.geltung is KortexChartaGeltung.GESPERRT)

    @property
    def kortikal_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kortex_charta_id for n in self.normen if n.geltung is KortexChartaGeltung.KORTIKAL)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kortex_charta_id for n in self.normen if n.geltung is KortexChartaGeltung.GRUNDLEGEND_KORTIKAL)

    @property
    def charta_signal(self):
        if any(n.geltung is KortexChartaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is KortexChartaGeltung.KORTIKAL for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-kortikal")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-kortikal")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_kortex_charta(
    synaptik_register: SynaptikRegister | None = None,
    *,
    charta_id: str = "kortex-charta",
) -> KortexCharta:
    if synaptik_register is None:
        synaptik_register = build_synaptik_register(register_id=f"{charta_id}-register")

    normen: list[KortexChartaNorm] = []
    for parent_norm in synaptik_register.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.synaptik_register_id.removeprefix(f'{synaptik_register.register_id}-')}"
        raw_weight = min(1.0, parent_norm.synaptik_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.synaptik_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KortexChartaGeltung.GRUNDLEGEND_KORTIKAL)
        normen.append(
            KortexChartaNorm(
                kortex_charta_id=new_id,
                kortex_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                kortex_weight=new_weight,
                kortex_tier=new_tier,
                canonical=is_canonical,
                kortex_ids=parent_norm.synaptik_ids + (new_id,),
                kortex_tags=parent_norm.synaptik_tags + (f"kortex-charta:{new_geltung.value}",),
            )
        )
    return KortexCharta(
        charta_id=charta_id,
        synaptik_register=synaptik_register,
        normen=tuple(normen),
    )
