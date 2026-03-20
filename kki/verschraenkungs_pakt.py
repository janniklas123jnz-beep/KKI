"""verschraenkungs_pakt — Quantenfelder & Dimensionen layer 5 (#265)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .superpositions_kodex import (
    SuperpositionsGeltung,
    SuperpositionsKodex,
    SuperpositionsNorm,
    SuperpositionsProzedur,
    SuperpositionsTyp,
    build_superpositions_kodex,
)

__all__ = [
    "VerschraenkunsTyp",
    "VerschraenkunsProzedur",
    "VerschraenkunsGeltung",
    "VerschraenkunsNorm",
    "VerschraenkunsPakt",
    "build_verschraenkungs_pakt",
]


class VerschraenkunsTyp(str, Enum):
    SCHUTZ_VERSCHRAENKUNG = "schutz-verschraenkung"
    ORDNUNGS_VERSCHRAENKUNG = "ordnungs-verschraenkung"
    SOUVERAENITAETS_VERSCHRAENKUNG = "souveraenitaets-verschraenkung"


class VerschraenkunsProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class VerschraenkunsGeltung(str, Enum):
    GESPERRT = "gesperrt"
    VERSCHRAENKT = "verschraenkt"
    GRUNDLEGEND_VERSCHRAENKT = "grundlegend-verschraenkt"


_TYP_MAP: dict[SuperpositionsGeltung, VerschraenkunsTyp] = {
    SuperpositionsGeltung.GESPERRT: VerschraenkunsTyp.SCHUTZ_VERSCHRAENKUNG,
    SuperpositionsGeltung.SUPERPONIERT: VerschraenkunsTyp.ORDNUNGS_VERSCHRAENKUNG,
    SuperpositionsGeltung.GRUNDLEGEND_SUPERPONIERT: VerschraenkunsTyp.SOUVERAENITAETS_VERSCHRAENKUNG,
}
_PROZEDUR_MAP: dict[SuperpositionsGeltung, VerschraenkunsProzedur] = {
    SuperpositionsGeltung.GESPERRT: VerschraenkunsProzedur.NOTPROZEDUR,
    SuperpositionsGeltung.SUPERPONIERT: VerschraenkunsProzedur.REGELPROTOKOLL,
    SuperpositionsGeltung.GRUNDLEGEND_SUPERPONIERT: VerschraenkunsProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[SuperpositionsGeltung, VerschraenkunsGeltung] = {
    SuperpositionsGeltung.GESPERRT: VerschraenkunsGeltung.GESPERRT,
    SuperpositionsGeltung.SUPERPONIERT: VerschraenkunsGeltung.VERSCHRAENKT,
    SuperpositionsGeltung.GRUNDLEGEND_SUPERPONIERT: VerschraenkunsGeltung.GRUNDLEGEND_VERSCHRAENKT,
}
_WEIGHT_BONUS: dict[SuperpositionsGeltung, float] = {
    SuperpositionsGeltung.GESPERRT: 0.0,
    SuperpositionsGeltung.SUPERPONIERT: 0.04,
    SuperpositionsGeltung.GRUNDLEGEND_SUPERPONIERT: 0.08,
}
_TIER_BONUS: dict[SuperpositionsGeltung, int] = {
    SuperpositionsGeltung.GESPERRT: 0,
    SuperpositionsGeltung.SUPERPONIERT: 1,
    SuperpositionsGeltung.GRUNDLEGEND_SUPERPONIERT: 2,
}


@dataclass(frozen=True)
class VerschraenkunsNorm:
    verschraenkungs_pakt_id: str
    verschraenkungs_typ: VerschraenkunsTyp
    prozedur: VerschraenkunsProzedur
    geltung: VerschraenkunsGeltung
    verschraenkungs_weight: float
    verschraenkungs_tier: int
    canonical: bool
    verschraenkungs_pakt_ids: tuple[str, ...]
    verschraenkungs_pakt_tags: tuple[str, ...]


@dataclass(frozen=True)
class VerschraenkunsPakt:
    pakt_id: str
    superpositions_kodex: SuperpositionsKodex
    normen: tuple[VerschraenkunsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.verschraenkungs_pakt_id for n in self.normen if n.geltung is VerschraenkunsGeltung.GESPERRT)

    @property
    def verschraenkt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.verschraenkungs_pakt_id for n in self.normen if n.geltung is VerschraenkunsGeltung.VERSCHRAENKT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.verschraenkungs_pakt_id for n in self.normen if n.geltung is VerschraenkunsGeltung.GRUNDLEGEND_VERSCHRAENKT)

    @property
    def pakt_signal(self):
        if any(n.geltung is VerschraenkunsGeltung.GESPERRT for n in self.normen):
            status = "pakt-gesperrt"
            severity = "critical"
        elif any(n.geltung is VerschraenkunsGeltung.VERSCHRAENKT for n in self.normen):
            status = "pakt-verschraenkt"
            severity = "warning"
        else:
            status = "pakt-grundlegend-verschraenkt"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_verschraenkungs_pakt(
    superpositions_kodex: SuperpositionsKodex | None = None,
    *,
    pakt_id: str = "verschraenkungs-pakt",
) -> VerschraenkunsPakt:
    if superpositions_kodex is None:
        superpositions_kodex = build_superpositions_kodex(kodex_id=f"{pakt_id}-kodex")

    normen: list[VerschraenkunsNorm] = []
    for parent_norm in superpositions_kodex.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{pakt_id}-{parent_norm.superpositions_kodex_id.removeprefix(f'{superpositions_kodex.kodex_id}-')}"
        raw_weight = min(1.0, round(parent_norm.superpositions_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.superpositions_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is VerschraenkunsGeltung.GRUNDLEGEND_VERSCHRAENKT)
        normen.append(
            VerschraenkunsNorm(
                verschraenkungs_pakt_id=new_id,
                verschraenkungs_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                verschraenkungs_weight=raw_weight,
                verschraenkungs_tier=new_tier,
                canonical=is_canonical,
                verschraenkungs_pakt_ids=parent_norm.superpositions_kodex_ids + (new_id,),
                verschraenkungs_pakt_tags=parent_norm.superpositions_kodex_tags + (f"verschraenkungs-pakt:{new_geltung.value}",),
            )
        )

    return VerschraenkunsPakt(
        pakt_id=pakt_id,
        superpositions_kodex=superpositions_kodex,
        normen=tuple(normen),
    )
