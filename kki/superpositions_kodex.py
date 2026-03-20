"""superpositions_kodex — Quantenfelder & Dimensionen layer 4 (#264)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .wellen_charta import (
    WellenCharta,
    WellenGeltung,
    WellenNorm,
    WellenProzedur,
    WellenTyp,
    build_wellen_charta,
)

__all__ = [
    "SuperpositionsTyp",
    "SuperpositionsProzedur",
    "SuperpositionsGeltung",
    "SuperpositionsNorm",
    "SuperpositionsKodex",
    "build_superpositions_kodex",
]


class SuperpositionsTyp(str, Enum):
    SCHUTZ_SUPERPOSITION = "schutz-superposition"
    ORDNUNGS_SUPERPOSITION = "ordnungs-superposition"
    SOUVERAENITAETS_SUPERPOSITION = "souveraenitaets-superposition"


class SuperpositionsProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class SuperpositionsGeltung(str, Enum):
    GESPERRT = "gesperrt"
    SUPERPONIERT = "superponiert"
    GRUNDLEGEND_SUPERPONIERT = "grundlegend-superponiert"


_TYP_MAP: dict[WellenGeltung, SuperpositionsTyp] = {
    WellenGeltung.GESPERRT: SuperpositionsTyp.SCHUTZ_SUPERPOSITION,
    WellenGeltung.WELLEND: SuperpositionsTyp.ORDNUNGS_SUPERPOSITION,
    WellenGeltung.GRUNDLEGEND_WELLEND: SuperpositionsTyp.SOUVERAENITAETS_SUPERPOSITION,
}
_PROZEDUR_MAP: dict[WellenGeltung, SuperpositionsProzedur] = {
    WellenGeltung.GESPERRT: SuperpositionsProzedur.NOTPROZEDUR,
    WellenGeltung.WELLEND: SuperpositionsProzedur.REGELPROTOKOLL,
    WellenGeltung.GRUNDLEGEND_WELLEND: SuperpositionsProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[WellenGeltung, SuperpositionsGeltung] = {
    WellenGeltung.GESPERRT: SuperpositionsGeltung.GESPERRT,
    WellenGeltung.WELLEND: SuperpositionsGeltung.SUPERPONIERT,
    WellenGeltung.GRUNDLEGEND_WELLEND: SuperpositionsGeltung.GRUNDLEGEND_SUPERPONIERT,
}
_WEIGHT_BONUS: dict[WellenGeltung, float] = {
    WellenGeltung.GESPERRT: 0.0,
    WellenGeltung.WELLEND: 0.04,
    WellenGeltung.GRUNDLEGEND_WELLEND: 0.08,
}
_TIER_BONUS: dict[WellenGeltung, int] = {
    WellenGeltung.GESPERRT: 0,
    WellenGeltung.WELLEND: 1,
    WellenGeltung.GRUNDLEGEND_WELLEND: 2,
}


@dataclass(frozen=True)
class SuperpositionsNorm:
    superpositions_kodex_id: str
    superpositions_typ: SuperpositionsTyp
    prozedur: SuperpositionsProzedur
    geltung: SuperpositionsGeltung
    superpositions_weight: float
    superpositions_tier: int
    canonical: bool
    superpositions_kodex_ids: tuple[str, ...]
    superpositions_kodex_tags: tuple[str, ...]


@dataclass(frozen=True)
class SuperpositionsKodex:
    kodex_id: str
    wellen_charta: WellenCharta
    normen: tuple[SuperpositionsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.superpositions_kodex_id for n in self.normen if n.geltung is SuperpositionsGeltung.GESPERRT)

    @property
    def superponiert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.superpositions_kodex_id for n in self.normen if n.geltung is SuperpositionsGeltung.SUPERPONIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.superpositions_kodex_id for n in self.normen if n.geltung is SuperpositionsGeltung.GRUNDLEGEND_SUPERPONIERT)

    @property
    def kodex_signal(self):
        if any(n.geltung is SuperpositionsGeltung.GESPERRT for n in self.normen):
            status = "kodex-gesperrt"
            severity = "critical"
        elif any(n.geltung is SuperpositionsGeltung.SUPERPONIERT for n in self.normen):
            status = "kodex-superponiert"
            severity = "warning"
        else:
            status = "kodex-grundlegend-superponiert"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_superpositions_kodex(
    wellen_charta: WellenCharta | None = None,
    *,
    kodex_id: str = "superpositions-kodex",
) -> SuperpositionsKodex:
    if wellen_charta is None:
        wellen_charta = build_wellen_charta(charta_id=f"{kodex_id}-charta")

    normen: list[SuperpositionsNorm] = []
    for parent_norm in wellen_charta.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{kodex_id}-{parent_norm.wellen_charta_id.removeprefix(f'{wellen_charta.charta_id}-')}"
        raw_weight = min(1.0, round(parent_norm.wellen_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.wellen_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SuperpositionsGeltung.GRUNDLEGEND_SUPERPONIERT)
        normen.append(
            SuperpositionsNorm(
                superpositions_kodex_id=new_id,
                superpositions_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                superpositions_weight=raw_weight,
                superpositions_tier=new_tier,
                canonical=is_canonical,
                superpositions_kodex_ids=parent_norm.wellen_charta_ids + (new_id,),
                superpositions_kodex_tags=parent_norm.wellen_charta_tags + (f"superpositions-kodex:{new_geltung.value}",),
            )
        )

    return SuperpositionsKodex(
        kodex_id=kodex_id,
        wellen_charta=wellen_charta,
        normen=tuple(normen),
    )
