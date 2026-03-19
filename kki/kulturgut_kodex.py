"""kulturgut_kodex — Zivilisation & Transzendenz layer 5 (#245)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .zivilisations_pakt import (
    ZivilisationsGeltung,
    ZivilisationsNorm,
    ZivilisationsPakt,
    ZivilisationsProzedur,
    ZivilisationsTyp,
    build_zivilisations_pakt,
)

__all__ = [
    "KulturgutRang",
    "KulturgutProzedur",
    "KulturgutGeltung",
    "KulturgutNorm",
    "KulturgutKodex",
    "build_kulturgut_kodex",
]


class KulturgutRang(str, Enum):
    SCHUTZ_KULTURGUT = "schutz-kulturgut"
    ORDNUNGS_KULTURGUT = "ordnungs-kulturgut"
    SOUVERAENITAETS_KULTURGUT = "souveraenitaets-kulturgut"


class KulturgutProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class KulturgutGeltung(str, Enum):
    GESPERRT = "gesperrt"
    BEWAHRT = "bewahrt"
    GRUNDLEGEND_BEWAHRT = "grundlegend-bewahrt"


_RANG_MAP: dict[ZivilisationsGeltung, KulturgutRang] = {
    ZivilisationsGeltung.GESPERRT: KulturgutRang.SCHUTZ_KULTURGUT,
    ZivilisationsGeltung.GESCHLOSSEN: KulturgutRang.ORDNUNGS_KULTURGUT,
    ZivilisationsGeltung.GRUNDLEGEND_GESCHLOSSEN: KulturgutRang.SOUVERAENITAETS_KULTURGUT,
}
_PROZEDUR_MAP: dict[ZivilisationsGeltung, KulturgutProzedur] = {
    ZivilisationsGeltung.GESPERRT: KulturgutProzedur.NOTPROZEDUR,
    ZivilisationsGeltung.GESCHLOSSEN: KulturgutProzedur.REGELPROTOKOLL,
    ZivilisationsGeltung.GRUNDLEGEND_GESCHLOSSEN: KulturgutProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[ZivilisationsGeltung, KulturgutGeltung] = {
    ZivilisationsGeltung.GESPERRT: KulturgutGeltung.GESPERRT,
    ZivilisationsGeltung.GESCHLOSSEN: KulturgutGeltung.BEWAHRT,
    ZivilisationsGeltung.GRUNDLEGEND_GESCHLOSSEN: KulturgutGeltung.GRUNDLEGEND_BEWAHRT,
}
_WEIGHT_BONUS: dict[ZivilisationsGeltung, float] = {
    ZivilisationsGeltung.GESPERRT: 0.0,
    ZivilisationsGeltung.GESCHLOSSEN: 0.04,
    ZivilisationsGeltung.GRUNDLEGEND_GESCHLOSSEN: 0.08,
}
_TIER_BONUS: dict[ZivilisationsGeltung, int] = {
    ZivilisationsGeltung.GESPERRT: 0,
    ZivilisationsGeltung.GESCHLOSSEN: 1,
    ZivilisationsGeltung.GRUNDLEGEND_GESCHLOSSEN: 2,
}


@dataclass(frozen=True)
class KulturgutNorm:
    kulturgut_kodex_id: str
    kulturgut_rang: KulturgutRang
    prozedur: KulturgutProzedur
    geltung: KulturgutGeltung
    kulturgut_weight: float
    kulturgut_tier: int
    canonical: bool
    kulturgut_kodex_ids: tuple[str, ...]
    kulturgut_kodex_tags: tuple[str, ...]


@dataclass(frozen=True)
class KulturgutKodex:
    kodex_id: str
    zivilisations_pakt: ZivilisationsPakt
    normen: tuple[KulturgutNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kulturgut_kodex_id for n in self.normen if n.geltung is KulturgutGeltung.GESPERRT)

    @property
    def bewahrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kulturgut_kodex_id for n in self.normen if n.geltung is KulturgutGeltung.BEWAHRT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.kulturgut_kodex_id for n in self.normen if n.geltung is KulturgutGeltung.GRUNDLEGEND_BEWAHRT)

    @property
    def kodex_signal(self):
        if any(n.geltung is KulturgutGeltung.GESPERRT for n in self.normen):
            status = "kodex-gesperrt"
            severity = "critical"
        elif any(n.geltung is KulturgutGeltung.BEWAHRT for n in self.normen):
            status = "kodex-bewahrt"
            severity = "warning"
        else:
            status = "kodex-grundlegend-bewahrt"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_kulturgut_kodex(
    zivilisations_pakt: ZivilisationsPakt | None = None,
    *,
    kodex_id: str = "kulturgut-kodex",
) -> KulturgutKodex:
    if zivilisations_pakt is None:
        zivilisations_pakt = build_zivilisations_pakt(pakt_id=f"{kodex_id}-pakt")

    normen: list[KulturgutNorm] = []
    for parent_norm in zivilisations_pakt.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{kodex_id}-{parent_norm.zivilisations_pakt_id.removeprefix(f'{zivilisations_pakt.pakt_id}-')}"
        raw_weight = min(1.0, round(parent_norm.zivilisations_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.zivilisations_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is KulturgutGeltung.GRUNDLEGEND_BEWAHRT)
        normen.append(
            KulturgutNorm(
                kulturgut_kodex_id=new_id,
                kulturgut_rang=_RANG_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                kulturgut_weight=raw_weight,
                kulturgut_tier=new_tier,
                canonical=is_canonical,
                kulturgut_kodex_ids=parent_norm.zivilisations_pakt_ids + (new_id,),
                kulturgut_kodex_tags=parent_norm.zivilisations_pakt_tags + (f"kulturgut-kodex:{new_geltung.value}",),
            )
        )

    return KulturgutKodex(
        kodex_id=kodex_id,
        zivilisations_pakt=zivilisations_pakt,
        normen=tuple(normen),
    )
