"""kruemmungs_pakt — Relativität & Raumzeit layer 5 (#275)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .gravitations_kodex import (
    GravitationsGeltung,
    GravitationsKodex,
    GravitationsNorm,
    GravitationsProzedur,
    GravitationsTyp,
    build_gravitations_kodex,
)

__all__ = [
    "KruemmungsTyp",
    "KruemmungsProzedur",
    "KruemmungsGeltung",
    "KruemmungsNorm",
    "KruemmungsPakt",
    "build_kruemmungs_pakt",
]


class KruemmungsTyp(str, Enum):
    SCHUTZ_KRUEMMUNG = "schutz-kruemmung"
    ORDNUNGS_KRUEMMUNG = "ordnungs-kruemmung"
    SOUVERAENITAETS_KRUEMMUNG = "souveraenitaets-kruemmung"


class KruemmungsProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KruemmungsGeltung(str, Enum):
    GESPERRT = "gesperrt"
    GEKRUEMMT = "gekruemmt"
    GRUNDLEGEND_GEKRUEMMT = "grundlegend-gekruemmt"


_TYP_MAP: dict[GravitationsGeltung, KruemmungsTyp] = {
    GravitationsGeltung.GESPERRT: KruemmungsTyp.SCHUTZ_KRUEMMUNG,
    GravitationsGeltung.GRAVITIERT: KruemmungsTyp.ORDNUNGS_KRUEMMUNG,
    GravitationsGeltung.GRUNDLEGEND_GRAVITIERT: KruemmungsTyp.SOUVERAENITAETS_KRUEMMUNG,
}
_PROZEDUR_MAP: dict[GravitationsGeltung, KruemmungsProzedur] = {
    GravitationsGeltung.GESPERRT: KruemmungsProzedur.NOTPROZEDUR,
    GravitationsGeltung.GRAVITIERT: KruemmungsProzedur.REGELPROTOKOLL,
    GravitationsGeltung.GRUNDLEGEND_GRAVITIERT: KruemmungsProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[GravitationsGeltung, KruemmungsGeltung] = {
    GravitationsGeltung.GESPERRT: KruemmungsGeltung.GESPERRT,
    GravitationsGeltung.GRAVITIERT: KruemmungsGeltung.GEKRUEMMT,
    GravitationsGeltung.GRUNDLEGEND_GRAVITIERT: KruemmungsGeltung.GRUNDLEGEND_GEKRUEMMT,
}
_WEIGHT_BONUS: dict[GravitationsGeltung, float] = {
    GravitationsGeltung.GESPERRT: 0.0,
    GravitationsGeltung.GRAVITIERT: 0.04,
    GravitationsGeltung.GRUNDLEGEND_GRAVITIERT: 0.08,
}
_TIER_BONUS: dict[GravitationsGeltung, int] = {
    GravitationsGeltung.GESPERRT: 0,
    GravitationsGeltung.GRAVITIERT: 1,
    GravitationsGeltung.GRUNDLEGEND_GRAVITIERT: 2,
}


@dataclass(frozen=True)
class KruemmungsNorm:
    kruemmungs_pakt_id: str
    kruemmungs_typ: KruemmungsTyp
    prozedur: KruemmungsProzedur
    geltung: KruemmungsGeltung
    kruemmungs_weight: float
    kruemmungs_tier: int
    canonical: bool
    kruemmungs_pakt_ids: tuple[str, ...]
    kruemmungs_pakt_tags: tuple[str, ...]


@dataclass(frozen=True)
class KruemmungsPakt:
    pakt_id: str
    gravitations_kodex: GravitationsKodex
    normen: tuple[KruemmungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kruemmungs_pakt_id for n in self.normen if n.geltung is KruemmungsGeltung.GESPERRT)

    @property
    def gekruemmt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kruemmungs_pakt_id for n in self.normen if n.geltung is KruemmungsGeltung.GEKRUEMMT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kruemmungs_pakt_id for n in self.normen if n.geltung is KruemmungsGeltung.GRUNDLEGEND_GEKRUEMMT)

    @property
    def pakt_signal(self):
        if any(n.geltung is KruemmungsGeltung.GESPERRT for n in self.normen):
            status = "pakt-gesperrt"
            severity = "critical"
        elif any(n.geltung is KruemmungsGeltung.GEKRUEMMT for n in self.normen):
            status = "pakt-gekruemmt"
            severity = "warning"
        else:
            status = "pakt-grundlegend-gekruemmt"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_kruemmungs_pakt(
    gravitations_kodex: GravitationsKodex | None = None,
    *,
    pakt_id: str = "kruemmungs-pakt",
) -> KruemmungsPakt:
    if gravitations_kodex is None:
        gravitations_kodex = build_gravitations_kodex(kodex_id=f"{pakt_id}-kodex")

    normen: list[KruemmungsNorm] = []
    for parent_norm in gravitations_kodex.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{pakt_id}-{parent_norm.gravitations_kodex_id.removeprefix(f'{gravitations_kodex.kodex_id}-')}"
        raw_weight = min(1.0, round(parent_norm.gravitations_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.gravitations_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KruemmungsGeltung.GRUNDLEGEND_GEKRUEMMT)
        normen.append(
            KruemmungsNorm(
                kruemmungs_pakt_id=new_id,
                kruemmungs_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                kruemmungs_weight=raw_weight,
                kruemmungs_tier=new_tier,
                canonical=is_canonical,
                kruemmungs_pakt_ids=parent_norm.gravitations_kodex_ids + (new_id,),
                kruemmungs_pakt_tags=parent_norm.gravitations_kodex_tags + (f"kruemmungs-pakt:{new_geltung.value}",),
            )
        )

    return KruemmungsPakt(
        pakt_id=pakt_id,
        gravitations_kodex=gravitations_kodex,
        normen=tuple(normen),
    )
