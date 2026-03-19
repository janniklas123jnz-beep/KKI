"""wirklichkeits_kodex — Metaphysik & Kosmologie layer 3 (#253)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .seins_charta import (
    SeinsCharta,
    SeinsGeltung,
    SeinsNorm,
    SeinsProzedur,
    SeinsTyp,
    build_seins_charta,
)

__all__ = [
    "WirklichkeitsEbene",
    "WirklichkeitsProzedur",
    "WirklichkeitsGeltung",
    "WirklichkeitsNorm",
    "WirklichkeitsKodex",
    "build_wirklichkeits_kodex",
]


class WirklichkeitsEbene(str, Enum):
    SCHUTZ_WIRKLICHKEIT = "schutz-wirklichkeit"
    ORDNUNGS_WIRKLICHKEIT = "ordnungs-wirklichkeit"
    SOUVERAENITAETS_WIRKLICHKEIT = "souveraenitaets-wirklichkeit"


class WirklichkeitsProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class WirklichkeitsGeltung(str, Enum):
    GESPERRT = "gesperrt"
    MANIFESTIERT = "manifestiert"
    GRUNDLEGEND_MANIFESTIERT = "grundlegend-manifestiert"


_EBENE_MAP: dict[SeinsGeltung, WirklichkeitsEbene] = {
    SeinsGeltung.GESPERRT: WirklichkeitsEbene.SCHUTZ_WIRKLICHKEIT,
    SeinsGeltung.VERANKERT: WirklichkeitsEbene.ORDNUNGS_WIRKLICHKEIT,
    SeinsGeltung.GRUNDLEGEND_VERANKERT: WirklichkeitsEbene.SOUVERAENITAETS_WIRKLICHKEIT,
}
_PROZEDUR_MAP: dict[SeinsGeltung, WirklichkeitsProzedur] = {
    SeinsGeltung.GESPERRT: WirklichkeitsProzedur.NOTPROZEDUR,
    SeinsGeltung.VERANKERT: WirklichkeitsProzedur.REGELPROTOKOLL,
    SeinsGeltung.GRUNDLEGEND_VERANKERT: WirklichkeitsProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[SeinsGeltung, WirklichkeitsGeltung] = {
    SeinsGeltung.GESPERRT: WirklichkeitsGeltung.GESPERRT,
    SeinsGeltung.VERANKERT: WirklichkeitsGeltung.MANIFESTIERT,
    SeinsGeltung.GRUNDLEGEND_VERANKERT: WirklichkeitsGeltung.GRUNDLEGEND_MANIFESTIERT,
}
_WEIGHT_BONUS: dict[SeinsGeltung, float] = {
    SeinsGeltung.GESPERRT: 0.0,
    SeinsGeltung.VERANKERT: 0.04,
    SeinsGeltung.GRUNDLEGEND_VERANKERT: 0.08,
}
_TIER_BONUS: dict[SeinsGeltung, int] = {
    SeinsGeltung.GESPERRT: 0,
    SeinsGeltung.VERANKERT: 1,
    SeinsGeltung.GRUNDLEGEND_VERANKERT: 2,
}


@dataclass(frozen=True)
class WirklichkeitsNorm:
    wirklichkeits_kodex_id: str
    wirklichkeits_ebene: WirklichkeitsEbene
    prozedur: WirklichkeitsProzedur
    geltung: WirklichkeitsGeltung
    wirklichkeits_weight: float
    wirklichkeits_tier: int
    canonical: bool
    wirklichkeits_kodex_ids: tuple[str, ...]
    wirklichkeits_kodex_tags: tuple[str, ...]


@dataclass(frozen=True)
class WirklichkeitsKodex:
    kodex_id: str
    seins_charta: SeinsCharta
    normen: tuple[WirklichkeitsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.wirklichkeits_kodex_id for n in self.normen if n.geltung is WirklichkeitsGeltung.GESPERRT)

    @property
    def manifestiert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.wirklichkeits_kodex_id for n in self.normen if n.geltung is WirklichkeitsGeltung.MANIFESTIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.wirklichkeits_kodex_id for n in self.normen if n.geltung is WirklichkeitsGeltung.GRUNDLEGEND_MANIFESTIERT)

    @property
    def kodex_signal(self):
        if any(n.geltung is WirklichkeitsGeltung.GESPERRT for n in self.normen):
            status = "kodex-gesperrt"
            severity = "critical"
        elif any(n.geltung is WirklichkeitsGeltung.MANIFESTIERT for n in self.normen):
            status = "kodex-manifestiert"
            severity = "warning"
        else:
            status = "kodex-grundlegend-manifestiert"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_wirklichkeits_kodex(
    seins_charta: SeinsCharta | None = None,
    *,
    kodex_id: str = "wirklichkeits-kodex",
) -> WirklichkeitsKodex:
    if seins_charta is None:
        seins_charta = build_seins_charta(charta_id=f"{kodex_id}-charta")

    normen: list[WirklichkeitsNorm] = []
    for parent_norm in seins_charta.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{kodex_id}-{parent_norm.seins_charta_id.removeprefix(f'{seins_charta.charta_id}-')}"
        raw_weight = min(1.0, round(parent_norm.seins_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.seins_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is WirklichkeitsGeltung.GRUNDLEGEND_MANIFESTIERT)
        normen.append(
            WirklichkeitsNorm(
                wirklichkeits_kodex_id=new_id,
                wirklichkeits_ebene=_EBENE_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                wirklichkeits_weight=raw_weight,
                wirklichkeits_tier=new_tier,
                canonical=is_canonical,
                wirklichkeits_kodex_ids=parent_norm.seins_charta_ids + (new_id,),
                wirklichkeits_kodex_tags=parent_norm.seins_charta_tags + (f"wirklichkeits-kodex:{new_geltung.value}",),
            )
        )

    return WirklichkeitsKodex(
        kodex_id=kodex_id,
        seins_charta=seins_charta,
        normen=tuple(normen),
    )
