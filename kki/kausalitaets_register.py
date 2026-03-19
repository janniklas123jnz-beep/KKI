"""kausalitaets_register — Metaphysik & Kosmologie layer 4 (#254)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .wirklichkeits_kodex import (
    WirklichkeitsEbene,
    WirklichkeitsGeltung,
    WirklichkeitsKodex,
    WirklichkeitsNorm,
    WirklichkeitsProzedur,
    build_wirklichkeits_kodex,
)

__all__ = [
    "KausalitaetsRang",
    "KausalitaetsProzedur",
    "KausalitaetsGeltung",
    "KausalitaetsNorm",
    "KausalitaetsRegister",
    "build_kausalitaets_register",
]


class KausalitaetsRang(str, Enum):
    SCHUTZ_KAUSALITAET = "schutz-kausalitaet"
    ORDNUNGS_KAUSALITAET = "ordnungs-kausalitaet"
    SOUVERAENITAETS_KAUSALITAET = "souveraenitaets-kausalitaet"


class KausalitaetsProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KausalitaetsGeltung(str, Enum):
    GESPERRT = "gesperrt"
    KAUSAL = "kausal"
    GRUNDLEGEND_KAUSAL = "grundlegend-kausal"


_RANG_MAP: dict[WirklichkeitsGeltung, KausalitaetsRang] = {
    WirklichkeitsGeltung.GESPERRT: KausalitaetsRang.SCHUTZ_KAUSALITAET,
    WirklichkeitsGeltung.MANIFESTIERT: KausalitaetsRang.ORDNUNGS_KAUSALITAET,
    WirklichkeitsGeltung.GRUNDLEGEND_MANIFESTIERT: KausalitaetsRang.SOUVERAENITAETS_KAUSALITAET,
}
_PROZEDUR_MAP: dict[WirklichkeitsGeltung, KausalitaetsProzedur] = {
    WirklichkeitsGeltung.GESPERRT: KausalitaetsProzedur.NOTPROZEDUR,
    WirklichkeitsGeltung.MANIFESTIERT: KausalitaetsProzedur.REGELPROTOKOLL,
    WirklichkeitsGeltung.GRUNDLEGEND_MANIFESTIERT: KausalitaetsProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[WirklichkeitsGeltung, KausalitaetsGeltung] = {
    WirklichkeitsGeltung.GESPERRT: KausalitaetsGeltung.GESPERRT,
    WirklichkeitsGeltung.MANIFESTIERT: KausalitaetsGeltung.KAUSAL,
    WirklichkeitsGeltung.GRUNDLEGEND_MANIFESTIERT: KausalitaetsGeltung.GRUNDLEGEND_KAUSAL,
}
_WEIGHT_BONUS: dict[WirklichkeitsGeltung, float] = {
    WirklichkeitsGeltung.GESPERRT: 0.0,
    WirklichkeitsGeltung.MANIFESTIERT: 0.04,
    WirklichkeitsGeltung.GRUNDLEGEND_MANIFESTIERT: 0.08,
}
_TIER_BONUS: dict[WirklichkeitsGeltung, int] = {
    WirklichkeitsGeltung.GESPERRT: 0,
    WirklichkeitsGeltung.MANIFESTIERT: 1,
    WirklichkeitsGeltung.GRUNDLEGEND_MANIFESTIERT: 2,
}


@dataclass(frozen=True)
class KausalitaetsNorm:
    kausalitaets_register_id: str
    kausalitaets_rang: KausalitaetsRang
    prozedur: KausalitaetsProzedur
    geltung: KausalitaetsGeltung
    kausalitaets_weight: float
    kausalitaets_tier: int
    canonical: bool
    kausalitaets_register_ids: tuple[str, ...]
    kausalitaets_register_tags: tuple[str, ...]


@dataclass(frozen=True)
class KausalitaetsRegister:
    register_id: str
    wirklichkeits_kodex: WirklichkeitsKodex
    normen: tuple[KausalitaetsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kausalitaets_register_id for n in self.normen if n.geltung is KausalitaetsGeltung.GESPERRT)

    @property
    def kausal_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kausalitaets_register_id for n in self.normen if n.geltung is KausalitaetsGeltung.KAUSAL)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kausalitaets_register_id for n in self.normen if n.geltung is KausalitaetsGeltung.GRUNDLEGEND_KAUSAL)

    @property
    def register_signal(self):
        if any(n.geltung is KausalitaetsGeltung.GESPERRT for n in self.normen):
            status = "register-gesperrt"
            severity = "critical"
        elif any(n.geltung is KausalitaetsGeltung.KAUSAL for n in self.normen):
            status = "register-kausal"
            severity = "warning"
        else:
            status = "register-grundlegend-kausal"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_kausalitaets_register(
    wirklichkeits_kodex: WirklichkeitsKodex | None = None,
    *,
    register_id: str = "kausalitaets-register",
) -> KausalitaetsRegister:
    if wirklichkeits_kodex is None:
        wirklichkeits_kodex = build_wirklichkeits_kodex(kodex_id=f"{register_id}-kodex")

    normen: list[KausalitaetsNorm] = []
    for parent_norm in wirklichkeits_kodex.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{register_id}-{parent_norm.wirklichkeits_kodex_id.removeprefix(f'{wirklichkeits_kodex.kodex_id}-')}"
        raw_weight = min(1.0, round(parent_norm.wirklichkeits_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.wirklichkeits_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KausalitaetsGeltung.GRUNDLEGEND_KAUSAL)
        normen.append(
            KausalitaetsNorm(
                kausalitaets_register_id=new_id,
                kausalitaets_rang=_RANG_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                kausalitaets_weight=raw_weight,
                kausalitaets_tier=new_tier,
                canonical=is_canonical,
                kausalitaets_register_ids=parent_norm.wirklichkeits_kodex_ids + (new_id,),
                kausalitaets_register_tags=parent_norm.wirklichkeits_kodex_tags + (f"kausalitaets-register:{new_geltung.value}",),
            )
        )

    return KausalitaetsRegister(
        register_id=register_id,
        wirklichkeits_kodex=wirklichkeits_kodex,
        normen=tuple(normen),
    )
