"""kosmos_verfassung — Metaphysik & Kosmologie Kronungsabschluss (#260)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .absolut_charta import (
    AbsolutCharta,
    AbsolutGeltung,
    AbsolutNorm,
    AbsolutProzedur,
    AbsolutTyp,
    build_absolut_charta,
)

__all__ = [
    "KosmosVerfassungsTyp",
    "KosmosVerfassungsProzedur",
    "KosmosVerfassungsGeltung",
    "KosmosVerfassungsNorm",
    "KosmosVerfassung",
    "build_kosmos_verfassung",
]


class KosmosVerfassungsTyp(str, Enum):
    SCHUTZ_VERFASSUNG = "schutz-verfassung"
    ORDNUNGS_VERFASSUNG = "ordnungs-verfassung"
    SOUVERAENITAETS_VERFASSUNG = "souveraenitaets-verfassung"


class KosmosVerfassungsProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KosmosVerfassungsGeltung(str, Enum):
    GESPERRT = "gesperrt"
    VERFASST = "verfasst"
    GRUNDLEGEND_VERFASST = "grundlegend-verfasst"


_TYP_MAP: dict[AbsolutGeltung, KosmosVerfassungsTyp] = {
    AbsolutGeltung.GESPERRT: KosmosVerfassungsTyp.SCHUTZ_VERFASSUNG,
    AbsolutGeltung.ABSOLUT: KosmosVerfassungsTyp.ORDNUNGS_VERFASSUNG,
    AbsolutGeltung.GRUNDLEGEND_ABSOLUT: KosmosVerfassungsTyp.SOUVERAENITAETS_VERFASSUNG,
}
_PROZEDUR_MAP: dict[AbsolutGeltung, KosmosVerfassungsProzedur] = {
    AbsolutGeltung.GESPERRT: KosmosVerfassungsProzedur.NOTPROZEDUR,
    AbsolutGeltung.ABSOLUT: KosmosVerfassungsProzedur.REGELPROTOKOLL,
    AbsolutGeltung.GRUNDLEGEND_ABSOLUT: KosmosVerfassungsProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[AbsolutGeltung, KosmosVerfassungsGeltung] = {
    AbsolutGeltung.GESPERRT: KosmosVerfassungsGeltung.GESPERRT,
    AbsolutGeltung.ABSOLUT: KosmosVerfassungsGeltung.VERFASST,
    AbsolutGeltung.GRUNDLEGEND_ABSOLUT: KosmosVerfassungsGeltung.GRUNDLEGEND_VERFASST,
}
_WEIGHT_BONUS: dict[AbsolutGeltung, float] = {
    AbsolutGeltung.GESPERRT: 0.0,
    AbsolutGeltung.ABSOLUT: 0.04,
    AbsolutGeltung.GRUNDLEGEND_ABSOLUT: 0.08,
}
_TIER_BONUS: dict[AbsolutGeltung, int] = {
    AbsolutGeltung.GESPERRT: 0,
    AbsolutGeltung.ABSOLUT: 1,
    AbsolutGeltung.GRUNDLEGEND_ABSOLUT: 2,
}


@dataclass(frozen=True)
class KosmosVerfassungsNorm:
    kosmos_verfassung_id: str
    kosmos_verfassungs_typ: KosmosVerfassungsTyp
    prozedur: KosmosVerfassungsProzedur
    geltung: KosmosVerfassungsGeltung
    kosmos_verfassungs_weight: float
    kosmos_verfassungs_tier: int
    canonical: bool
    kosmos_verfassung_ids: tuple[str, ...]
    kosmos_verfassung_tags: tuple[str, ...]


@dataclass(frozen=True)
class KosmosVerfassung:
    verfassung_id: str
    absolut_charta: AbsolutCharta
    normen: tuple[KosmosVerfassungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kosmos_verfassung_id for n in self.normen if n.geltung is KosmosVerfassungsGeltung.GESPERRT)

    @property
    def verfasst_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kosmos_verfassung_id for n in self.normen if n.geltung is KosmosVerfassungsGeltung.VERFASST)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kosmos_verfassung_id for n in self.normen if n.geltung is KosmosVerfassungsGeltung.GRUNDLEGEND_VERFASST)

    @property
    def verfassung_signal(self):
        if any(n.geltung is KosmosVerfassungsGeltung.GESPERRT for n in self.normen):
            status = "verfassung-gesperrt"
            severity = "critical"
        elif any(n.geltung is KosmosVerfassungsGeltung.VERFASST for n in self.normen):
            status = "verfassung-verfasst"
            severity = "warning"
        else:
            status = "verfassung-grundlegend-verfasst"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_kosmos_verfassung(
    absolut_charta: AbsolutCharta | None = None,
    *,
    verfassung_id: str = "kosmos-verfassung",
) -> KosmosVerfassung:
    if absolut_charta is None:
        absolut_charta = build_absolut_charta(charta_id=f"{verfassung_id}-charta")

    normen: list[KosmosVerfassungsNorm] = []
    for parent_norm in absolut_charta.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{verfassung_id}-{parent_norm.absolut_charta_id.removeprefix(f'{absolut_charta.charta_id}-')}"
        raw_weight = min(1.0, round(parent_norm.absolut_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.absolut_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KosmosVerfassungsGeltung.GRUNDLEGEND_VERFASST)
        normen.append(
            KosmosVerfassungsNorm(
                kosmos_verfassung_id=new_id,
                kosmos_verfassungs_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                kosmos_verfassungs_weight=raw_weight,
                kosmos_verfassungs_tier=new_tier,
                canonical=is_canonical,
                kosmos_verfassung_ids=parent_norm.absolut_charta_ids + (new_id,),
                kosmos_verfassung_tags=parent_norm.absolut_charta_tags + (f"kosmos-verfassung:{new_geltung.value}",),
            )
        )

    return KosmosVerfassung(
        verfassung_id=verfassung_id,
        absolut_charta=absolut_charta,
        normen=tuple(normen),
    )
