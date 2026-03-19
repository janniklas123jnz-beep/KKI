"""allianz_vertrag — Weltrecht & Kosmopolitik layer 4 (#234)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .diplomatie_charta import (
    DiplomatieCharta,
    DiplomatieGeltung,
    DiplomatieNorm,
    DiplomatieProzedur,
    DiplomatieRang,
    build_diplomatie_charta,
)

__all__ = [
    "AllianzTyp",
    "AllianzProzedur",
    "AllianzGeltung",
    "AllianzNorm",
    "AllianzVertrag",
    "build_allianz_vertrag",
]


class AllianzTyp(str, Enum):
    SCHUTZ_ALLIANZ = "schutz-allianz"
    ORDNUNGS_ALLIANZ = "ordnungs-allianz"
    SOUVERAENITAETS_ALLIANZ = "souveraenitaets-allianz"


class AllianzProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class AllianzGeltung(str, Enum):
    GESPERRT = "gesperrt"
    VERBUNDEN = "verbunden"
    GRUNDLEGEND_VERBUNDEN = "grundlegend-verbunden"


_TYP_MAP: dict[DiplomatieGeltung, AllianzTyp] = {
    DiplomatieGeltung.GESPERRT: AllianzTyp.SCHUTZ_ALLIANZ,
    DiplomatieGeltung.AKKREDITIERT: AllianzTyp.ORDNUNGS_ALLIANZ,
    DiplomatieGeltung.GRUNDLEGEND_AKKREDITIERT: AllianzTyp.SOUVERAENITAETS_ALLIANZ,
}
_PROZEDUR_MAP: dict[DiplomatieGeltung, AllianzProzedur] = {
    DiplomatieGeltung.GESPERRT: AllianzProzedur.NOTPROZEDUR,
    DiplomatieGeltung.AKKREDITIERT: AllianzProzedur.REGELPROTOKOLL,
    DiplomatieGeltung.GRUNDLEGEND_AKKREDITIERT: AllianzProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[DiplomatieGeltung, AllianzGeltung] = {
    DiplomatieGeltung.GESPERRT: AllianzGeltung.GESPERRT,
    DiplomatieGeltung.AKKREDITIERT: AllianzGeltung.VERBUNDEN,
    DiplomatieGeltung.GRUNDLEGEND_AKKREDITIERT: AllianzGeltung.GRUNDLEGEND_VERBUNDEN,
}
_WEIGHT_BONUS: dict[DiplomatieGeltung, float] = {
    DiplomatieGeltung.GESPERRT: 0.0,
    DiplomatieGeltung.AKKREDITIERT: 0.04,
    DiplomatieGeltung.GRUNDLEGEND_AKKREDITIERT: 0.08,
}
_TIER_BONUS: dict[DiplomatieGeltung, int] = {
    DiplomatieGeltung.GESPERRT: 0,
    DiplomatieGeltung.AKKREDITIERT: 1,
    DiplomatieGeltung.GRUNDLEGEND_AKKREDITIERT: 2,
}


@dataclass(frozen=True)
class AllianzNorm:
    allianz_vertrag_id: str
    allianz_typ: AllianzTyp
    prozedur: AllianzProzedur
    geltung: AllianzGeltung
    allianz_weight: float
    allianz_tier: int
    canonical: bool
    allianz_vertrag_ids: tuple[str, ...]
    allianz_vertrag_tags: tuple[str, ...]


@dataclass(frozen=True)
class AllianzVertrag:
    vertrag_id: str
    diplomatie_charta: DiplomatieCharta
    normen: tuple[AllianzNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.allianz_vertrag_id for n in self.normen if n.geltung is AllianzGeltung.GESPERRT)

    @property
    def verbunden_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.allianz_vertrag_id for n in self.normen if n.geltung is AllianzGeltung.VERBUNDEN)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.allianz_vertrag_id for n in self.normen if n.geltung is AllianzGeltung.GRUNDLEGEND_VERBUNDEN)

    @property
    def vertrag_signal(self):
        if any(n.geltung is AllianzGeltung.GESPERRT for n in self.normen):
            status = "vertrag-gesperrt"
            severity = "critical"
        elif any(n.geltung is AllianzGeltung.VERBUNDEN for n in self.normen):
            status = "vertrag-verbunden"
            severity = "warning"
        else:
            status = "vertrag-grundlegend-verbunden"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_allianz_vertrag(
    diplomatie_charta: DiplomatieCharta | None = None,
    *,
    vertrag_id: str = "allianz-vertrag",
) -> AllianzVertrag:
    if diplomatie_charta is None:
        diplomatie_charta = build_diplomatie_charta(
            charta_id=f"{vertrag_id}-charta"
        )

    normen: list[AllianzNorm] = []
    for parent_norm in diplomatie_charta.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{vertrag_id}-{parent_norm.diplomatie_charta_id.removeprefix(f'{diplomatie_charta.charta_id}-')}"
        raw_weight = min(1.0, round(parent_norm.diplomatie_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.diplomatie_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is AllianzGeltung.GRUNDLEGEND_VERBUNDEN)
        normen.append(
            AllianzNorm(
                allianz_vertrag_id=new_id,
                allianz_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                allianz_weight=raw_weight,
                allianz_tier=new_tier,
                canonical=is_canonical,
                allianz_vertrag_ids=parent_norm.diplomatie_charta_ids + (new_id,),
                allianz_vertrag_tags=parent_norm.diplomatie_charta_tags + (f"allianz-vertrag:{new_geltung.value}",),
            )
        )

    return AllianzVertrag(
        vertrag_id=vertrag_id,
        diplomatie_charta=diplomatie_charta,
        normen=tuple(normen),
    )
