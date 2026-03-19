"""universal_kodex — Weltrecht & Kosmopolitik layer 10 / Block Crown (#240)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .weltgeist_senat import (
    WeltgeistGeltung,
    WeltgeistProzedur,
    WeltgeistRang,
    WeltgeistSenat,
    WeltgeistSitz,
    build_weltgeist_senat,
)

__all__ = [
    "UniversalKodexKlasse",
    "UniversalKodexProzedur",
    "UniversalKodexGeltung",
    "UniversalKodexNorm",
    "UniversalKodex",
    "build_universal_kodex",
]


class UniversalKodexKlasse(str, Enum):
    SCHUTZ_KLASSE = "schutz-klasse"
    ORDNUNGS_KLASSE = "ordnungs-klasse"
    SOUVERAENITAETS_KLASSE = "souveraenitaets-klasse"


class UniversalKodexProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class UniversalKodexGeltung(str, Enum):
    GESPERRT = "gesperrt"
    UNIVERSELL = "universell"
    GRUNDLEGEND_UNIVERSELL = "grundlegend-universell"


_KLASSE_MAP: dict[WeltgeistGeltung, UniversalKodexKlasse] = {
    WeltgeistGeltung.GESPERRT: UniversalKodexKlasse.SCHUTZ_KLASSE,
    WeltgeistGeltung.ERHOBEN: UniversalKodexKlasse.ORDNUNGS_KLASSE,
    WeltgeistGeltung.GRUNDLEGEND_ERHOBEN: UniversalKodexKlasse.SOUVERAENITAETS_KLASSE,
}
_PROZEDUR_MAP: dict[WeltgeistGeltung, UniversalKodexProzedur] = {
    WeltgeistGeltung.GESPERRT: UniversalKodexProzedur.NOTPROZEDUR,
    WeltgeistGeltung.ERHOBEN: UniversalKodexProzedur.REGELPROTOKOLL,
    WeltgeistGeltung.GRUNDLEGEND_ERHOBEN: UniversalKodexProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[WeltgeistGeltung, UniversalKodexGeltung] = {
    WeltgeistGeltung.GESPERRT: UniversalKodexGeltung.GESPERRT,
    WeltgeistGeltung.ERHOBEN: UniversalKodexGeltung.UNIVERSELL,
    WeltgeistGeltung.GRUNDLEGEND_ERHOBEN: UniversalKodexGeltung.GRUNDLEGEND_UNIVERSELL,
}
_WEIGHT_BONUS: dict[WeltgeistGeltung, float] = {
    WeltgeistGeltung.GESPERRT: 0.0,
    WeltgeistGeltung.ERHOBEN: 0.04,
    WeltgeistGeltung.GRUNDLEGEND_ERHOBEN: 0.08,
}
_TIER_BONUS: dict[WeltgeistGeltung, int] = {
    WeltgeistGeltung.GESPERRT: 0,
    WeltgeistGeltung.ERHOBEN: 1,
    WeltgeistGeltung.GRUNDLEGEND_ERHOBEN: 2,
}


@dataclass(frozen=True)
class UniversalKodexNorm:
    universal_kodex_id: str
    universal_kodex_klasse: UniversalKodexKlasse
    prozedur: UniversalKodexProzedur
    geltung: UniversalKodexGeltung
    universal_weight: float
    universal_tier: int
    canonical: bool
    universal_kodex_ids: tuple[str, ...]
    universal_kodex_tags: tuple[str, ...]


@dataclass(frozen=True)
class UniversalKodex:
    kodex_id: str
    weltgeist_senat: WeltgeistSenat
    normen: tuple[UniversalKodexNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.universal_kodex_id for n in self.normen if n.geltung is UniversalKodexGeltung.GESPERRT)

    @property
    def universell_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.universal_kodex_id for n in self.normen if n.geltung is UniversalKodexGeltung.UNIVERSELL)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.universal_kodex_id for n in self.normen if n.geltung is UniversalKodexGeltung.GRUNDLEGEND_UNIVERSELL)

    @property
    def kodex_signal(self):
        if any(n.geltung is UniversalKodexGeltung.GESPERRT for n in self.normen):
            status = "kodex-gesperrt"
            severity = "critical"
        elif any(n.geltung is UniversalKodexGeltung.UNIVERSELL for n in self.normen):
            status = "kodex-universell"
            severity = "warning"
        else:
            status = "kodex-grundlegend-universell"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_universal_kodex(
    weltgeist_senat: WeltgeistSenat | None = None,
    *,
    kodex_id: str = "universal-kodex",
) -> UniversalKodex:
    if weltgeist_senat is None:
        weltgeist_senat = build_weltgeist_senat(senat_id=f"{kodex_id}-senat")

    normen: list[UniversalKodexNorm] = []
    for parent_norm in weltgeist_senat.sitze:
        parent_geltung = parent_norm.geltung
        new_id = f"{kodex_id}-{parent_norm.weltgeist_senat_id.removeprefix(f'{weltgeist_senat.senat_id}-')}"
        raw_weight = min(1.0, round(parent_norm.weltgeist_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.weltgeist_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is UniversalKodexGeltung.GRUNDLEGEND_UNIVERSELL)
        normen.append(
            UniversalKodexNorm(
                universal_kodex_id=new_id,
                universal_kodex_klasse=_KLASSE_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                universal_weight=raw_weight,
                universal_tier=new_tier,
                canonical=is_canonical,
                universal_kodex_ids=parent_norm.weltgeist_senat_ids + (new_id,),
                universal_kodex_tags=parent_norm.weltgeist_senat_tags + (f"universal-kodex:{new_geltung.value}",),
            )
        )

    return UniversalKodex(
        kodex_id=kodex_id,
        weltgeist_senat=weltgeist_senat,
        normen=tuple(normen),
    )
