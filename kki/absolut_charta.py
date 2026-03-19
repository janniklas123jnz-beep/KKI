"""absolut_charta — Metaphysik & Kosmologie layer 9 (#259)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kosmos_ewigkeit import (
    KosmosEwigkeit,
    KosmosEwigkeitsGeltung,
    KosmosEwigkeitsNormEintrag,
    KosmosEwigkeitsProzedur,
    KosmosEwigkeitsRang,
    build_kosmos_ewigkeit,
)

__all__ = [
    "AbsolutTyp",
    "AbsolutProzedur",
    "AbsolutGeltung",
    "AbsolutNorm",
    "AbsolutCharta",
    "build_absolut_charta",
]


class AbsolutTyp(str, Enum):
    SCHUTZ_ABSOLUT = "schutz-absolut"
    ORDNUNGS_ABSOLUT = "ordnungs-absolut"
    SOUVERAENITAETS_ABSOLUT = "souveraenitaets-absolut"


class AbsolutProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class AbsolutGeltung(str, Enum):
    GESPERRT = "gesperrt"
    ABSOLUT = "absolut"
    GRUNDLEGEND_ABSOLUT = "grundlegend-absolut"


_TYP_MAP: dict[KosmosEwigkeitsGeltung, AbsolutTyp] = {
    KosmosEwigkeitsGeltung.GESPERRT: AbsolutTyp.SCHUTZ_ABSOLUT,
    KosmosEwigkeitsGeltung.EWIG: AbsolutTyp.ORDNUNGS_ABSOLUT,
    KosmosEwigkeitsGeltung.GRUNDLEGEND_EWIG: AbsolutTyp.SOUVERAENITAETS_ABSOLUT,
}
_PROZEDUR_MAP: dict[KosmosEwigkeitsGeltung, AbsolutProzedur] = {
    KosmosEwigkeitsGeltung.GESPERRT: AbsolutProzedur.NOTPROZEDUR,
    KosmosEwigkeitsGeltung.EWIG: AbsolutProzedur.REGELPROTOKOLL,
    KosmosEwigkeitsGeltung.GRUNDLEGEND_EWIG: AbsolutProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[KosmosEwigkeitsGeltung, AbsolutGeltung] = {
    KosmosEwigkeitsGeltung.GESPERRT: AbsolutGeltung.GESPERRT,
    KosmosEwigkeitsGeltung.EWIG: AbsolutGeltung.ABSOLUT,
    KosmosEwigkeitsGeltung.GRUNDLEGEND_EWIG: AbsolutGeltung.GRUNDLEGEND_ABSOLUT,
}
_WEIGHT_BONUS: dict[KosmosEwigkeitsGeltung, float] = {
    KosmosEwigkeitsGeltung.GESPERRT: 0.0,
    KosmosEwigkeitsGeltung.EWIG: 0.04,
    KosmosEwigkeitsGeltung.GRUNDLEGEND_EWIG: 0.08,
}
_TIER_BONUS: dict[KosmosEwigkeitsGeltung, int] = {
    KosmosEwigkeitsGeltung.GESPERRT: 0,
    KosmosEwigkeitsGeltung.EWIG: 1,
    KosmosEwigkeitsGeltung.GRUNDLEGEND_EWIG: 2,
}


@dataclass(frozen=True)
class AbsolutNorm:
    absolut_charta_id: str
    absolut_typ: AbsolutTyp
    prozedur: AbsolutProzedur
    geltung: AbsolutGeltung
    absolut_weight: float
    absolut_tier: int
    canonical: bool
    absolut_charta_ids: tuple[str, ...]
    absolut_charta_tags: tuple[str, ...]


@dataclass(frozen=True)
class AbsolutCharta:
    charta_id: str
    kosmos_ewigkeit: KosmosEwigkeit
    normen: tuple[AbsolutNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.absolut_charta_id for n in self.normen if n.geltung is AbsolutGeltung.GESPERRT)

    @property
    def absolut_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.absolut_charta_id for n in self.normen if n.geltung is AbsolutGeltung.ABSOLUT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.absolut_charta_id for n in self.normen if n.geltung is AbsolutGeltung.GRUNDLEGEND_ABSOLUT)

    @property
    def charta_signal(self):
        if any(n.geltung is AbsolutGeltung.GESPERRT for n in self.normen):
            status = "charta-gesperrt"
            severity = "critical"
        elif any(n.geltung is AbsolutGeltung.ABSOLUT for n in self.normen):
            status = "charta-absolut"
            severity = "warning"
        else:
            status = "charta-grundlegend-absolut"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_absolut_charta(
    kosmos_ewigkeit: KosmosEwigkeit | None = None,
    *,
    charta_id: str = "absolut-charta",
) -> AbsolutCharta:
    if kosmos_ewigkeit is None:
        kosmos_ewigkeit = build_kosmos_ewigkeit(ewigkeit_id=f"{charta_id}-ewigkeit")

    normen: list[AbsolutNorm] = []
    for parent_norm in kosmos_ewigkeit.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{charta_id}-{parent_norm.kosmos_ewigkeit_id.removeprefix(f'{kosmos_ewigkeit.ewigkeit_id}-')}"
        raw_weight = min(1.0, round(parent_norm.kosmos_ewigkeits_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.kosmos_ewigkeits_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is AbsolutGeltung.GRUNDLEGEND_ABSOLUT)
        normen.append(
            AbsolutNorm(
                absolut_charta_id=new_id,
                absolut_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                absolut_weight=raw_weight,
                absolut_tier=new_tier,
                canonical=is_canonical,
                absolut_charta_ids=parent_norm.kosmos_ewigkeit_ids + (new_id,),
                absolut_charta_tags=parent_norm.kosmos_ewigkeit_tags + (f"absolut-charta:{new_geltung.value}",),
            )
        )

    return AbsolutCharta(
        charta_id=charta_id,
        kosmos_ewigkeit=kosmos_ewigkeit,
        normen=tuple(normen),
    )
