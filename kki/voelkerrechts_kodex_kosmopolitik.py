"""voelkerrechts_kodex — Weltrecht & Kosmopolitik layer 2 (#232)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from .weltordnungs_prinzip import (
    WeltordnungsEbene,
    WeltordnungsGeltung,
    WeltordnungsNorm,
    WeltordnungsPrinzip,
    WeltordnungsProzedur,
    build_weltordnungs_prinzip,
)

__all__ = [
    "VoelkerrechtsKlasse",
    "VoelkerrechtsProzedur",
    "VoelkerrechtsGeltung",
    "VoelkerrechtsNorm",
    "VoelkerrechtsKodex",
    "build_voelkerrechts_kodex",
]


class VoelkerrechtsKlasse(str, Enum):
    SCHUTZ_KLASSE = "schutz-klasse"
    ORDNUNGS_KLASSE = "ordnungs-klasse"
    SOUVERAENITAETS_KLASSE = "souveraenitaets-klasse"


class VoelkerrechtsProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class VoelkerrechtsGeltung(str, Enum):
    GESPERRT = "gesperrt"
    KODIFIZIERT = "kodifiziert"
    GRUNDLEGEND_KODIFIZIERT = "grundlegend-kodifiziert"


_KLASSE_MAP: dict[WeltordnungsGeltung, VoelkerrechtsKlasse] = {
    WeltordnungsGeltung.GESPERRT: VoelkerrechtsKlasse.SCHUTZ_KLASSE,
    WeltordnungsGeltung.GEORDNET: VoelkerrechtsKlasse.ORDNUNGS_KLASSE,
    WeltordnungsGeltung.GRUNDLEGEND_GEORDNET: VoelkerrechtsKlasse.SOUVERAENITAETS_KLASSE,
}
_PROZEDUR_MAP: dict[WeltordnungsGeltung, VoelkerrechtsProzedur] = {
    WeltordnungsGeltung.GESPERRT: VoelkerrechtsProzedur.NOTPROZEDUR,
    WeltordnungsGeltung.GEORDNET: VoelkerrechtsProzedur.REGELPROTOKOLL,
    WeltordnungsGeltung.GRUNDLEGEND_GEORDNET: VoelkerrechtsProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[WeltordnungsGeltung, VoelkerrechtsGeltung] = {
    WeltordnungsGeltung.GESPERRT: VoelkerrechtsGeltung.GESPERRT,
    WeltordnungsGeltung.GEORDNET: VoelkerrechtsGeltung.KODIFIZIERT,
    WeltordnungsGeltung.GRUNDLEGEND_GEORDNET: VoelkerrechtsGeltung.GRUNDLEGEND_KODIFIZIERT,
}
_WEIGHT_BONUS: dict[WeltordnungsGeltung, float] = {
    WeltordnungsGeltung.GESPERRT: 0.0,
    WeltordnungsGeltung.GEORDNET: 0.04,
    WeltordnungsGeltung.GRUNDLEGEND_GEORDNET: 0.08,
}
_TIER_BONUS: dict[WeltordnungsGeltung, int] = {
    WeltordnungsGeltung.GESPERRT: 0,
    WeltordnungsGeltung.GEORDNET: 1,
    WeltordnungsGeltung.GRUNDLEGEND_GEORDNET: 2,
}


@dataclass(frozen=True)
class VoelkerrechtsNorm:
    voelkerrechts_kodex_id: str
    voelkerrechts_klasse: VoelkerrechtsKlasse
    prozedur: VoelkerrechtsProzedur
    geltung: VoelkerrechtsGeltung
    voelkerrechts_weight: float
    voelkerrechts_tier: int
    canonical: bool
    voelkerrechts_kodex_ids: tuple[str, ...]
    voelkerrechts_kodex_tags: tuple[str, ...]


@dataclass(frozen=True)
class VoelkerrechtsKodex:
    kodex_id: str
    weltordnungs_prinzip: WeltordnungsPrinzip
    normen: tuple[VoelkerrechtsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.voelkerrechts_kodex_id for n in self.normen if n.geltung is VoelkerrechtsGeltung.GESPERRT)

    @property
    def kodifiziert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.voelkerrechts_kodex_id for n in self.normen if n.geltung is VoelkerrechtsGeltung.KODIFIZIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.voelkerrechts_kodex_id for n in self.normen if n.geltung is VoelkerrechtsGeltung.GRUNDLEGEND_KODIFIZIERT)

    @property
    def kodex_signal(self):
        if any(n.geltung is VoelkerrechtsGeltung.GESPERRT for n in self.normen):
            status = "kodex-gesperrt"
            severity = "critical"
        elif any(n.geltung is VoelkerrechtsGeltung.KODIFIZIERT for n in self.normen):
            status = "kodex-kodifiziert"
            severity = "warning"
        else:
            status = "kodex-grundlegend-kodifiziert"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_voelkerrechts_kodex(
    weltordnungs_prinzip: WeltordnungsPrinzip | None = None,
    *,
    kodex_id: str = "voelkerrechts-kodex",
) -> VoelkerrechtsKodex:
    if weltordnungs_prinzip is None:
        weltordnungs_prinzip = build_weltordnungs_prinzip(
            prinzip_id=f"{kodex_id}-prinzip"
        )

    normen: list[VoelkerrechtsNorm] = []
    for parent_norm in weltordnungs_prinzip.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{kodex_id}-{parent_norm.weltordnungs_norm_id.removeprefix(f'{weltordnungs_prinzip.prinzip_id}-')}"
        raw_weight = min(1.0, round(parent_norm.weltordnungs_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.weltordnungs_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is VoelkerrechtsGeltung.GRUNDLEGEND_KODIFIZIERT)
        normen.append(
            VoelkerrechtsNorm(
                voelkerrechts_kodex_id=new_id,
                voelkerrechts_klasse=_KLASSE_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                voelkerrechts_weight=raw_weight,
                voelkerrechts_tier=new_tier,
                canonical=is_canonical,
                voelkerrechts_kodex_ids=parent_norm.weltordnungs_norm_ids + (new_id,),
                voelkerrechts_kodex_tags=parent_norm.weltordnungs_norm_tags + (f"voelkerrechts-kodex:{new_geltung.value}",),
            )
        )

    return VoelkerrechtsKodex(
        kodex_id=kodex_id,
        weltordnungs_prinzip=weltordnungs_prinzip,
        normen=tuple(normen),
    )
