"""weltgeist_senat — Weltrecht & Kosmopolitik layer 9 (#239)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .kosmos_norm import (
    KosmosEbene,
    KosmosGeltung,
    KosmosNorm,
    KosmosNormEintrag,
    KosmosProzedur,
    build_kosmos_norm,
)

__all__ = [
    "WeltgeistRang",
    "WeltgeistProzedur",
    "WeltgeistGeltung",
    "WeltgeistSitz",
    "WeltgeistSenat",
    "build_weltgeist_senat",
]


class WeltgeistRang(str, Enum):
    SCHUTZ_RANG = "schutz-rang"
    ORDNUNGS_RANG = "ordnungs-rang"
    SOUVERAENITAETS_RANG = "souveraenitaets-rang"


class WeltgeistProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class WeltgeistGeltung(str, Enum):
    GESPERRT = "gesperrt"
    ERHOBEN = "erhoben"
    GRUNDLEGEND_ERHOBEN = "grundlegend-erhoben"


_RANG_MAP: dict[KosmosGeltung, WeltgeistRang] = {
    KosmosGeltung.GESPERRT: WeltgeistRang.SCHUTZ_RANG,
    KosmosGeltung.KOSMISCH: WeltgeistRang.ORDNUNGS_RANG,
    KosmosGeltung.GRUNDLEGEND_KOSMISCH: WeltgeistRang.SOUVERAENITAETS_RANG,
}
_PROZEDUR_MAP: dict[KosmosGeltung, WeltgeistProzedur] = {
    KosmosGeltung.GESPERRT: WeltgeistProzedur.NOTPROZEDUR,
    KosmosGeltung.KOSMISCH: WeltgeistProzedur.REGELPROTOKOLL,
    KosmosGeltung.GRUNDLEGEND_KOSMISCH: WeltgeistProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[KosmosGeltung, WeltgeistGeltung] = {
    KosmosGeltung.GESPERRT: WeltgeistGeltung.GESPERRT,
    KosmosGeltung.KOSMISCH: WeltgeistGeltung.ERHOBEN,
    KosmosGeltung.GRUNDLEGEND_KOSMISCH: WeltgeistGeltung.GRUNDLEGEND_ERHOBEN,
}
_WEIGHT_BONUS: dict[KosmosGeltung, float] = {
    KosmosGeltung.GESPERRT: 0.0,
    KosmosGeltung.KOSMISCH: 0.04,
    KosmosGeltung.GRUNDLEGEND_KOSMISCH: 0.08,
}
_TIER_BONUS: dict[KosmosGeltung, int] = {
    KosmosGeltung.GESPERRT: 0,
    KosmosGeltung.KOSMISCH: 1,
    KosmosGeltung.GRUNDLEGEND_KOSMISCH: 2,
}


@dataclass(frozen=True)
class WeltgeistSitz:
    weltgeist_senat_id: str
    weltgeist_rang: WeltgeistRang
    prozedur: WeltgeistProzedur
    geltung: WeltgeistGeltung
    weltgeist_weight: float
    weltgeist_tier: int
    canonical: bool
    weltgeist_senat_ids: tuple[str, ...]
    weltgeist_senat_tags: tuple[str, ...]


@dataclass(frozen=True)
class WeltgeistSenat:
    senat_id: str
    kosmos_norm: KosmosNorm
    sitze: tuple[WeltgeistSitz, ...]

    @property
    def gesperrt_sitz_ids(self) -> tuple[str, ...]:
        return tuple(s.weltgeist_senat_id for s in self.sitze if s.geltung is WeltgeistGeltung.GESPERRT)

    @property
    def erhoben_sitz_ids(self) -> tuple[str, ...]:
        return tuple(s.weltgeist_senat_id for s in self.sitze if s.geltung is WeltgeistGeltung.ERHOBEN)

    @property
    def grundlegend_sitz_ids(self) -> tuple[str, ...]:
        return tuple(s.weltgeist_senat_id for s in self.sitze if s.geltung is WeltgeistGeltung.GRUNDLEGEND_ERHOBEN)

    @property
    def senat_signal(self):
        if any(s.geltung is WeltgeistGeltung.GESPERRT for s in self.sitze):
            status = "senat-gesperrt"
            severity = "critical"
        elif any(s.geltung is WeltgeistGeltung.ERHOBEN for s in self.sitze):
            status = "senat-erhoben"
            severity = "warning"
        else:
            status = "senat-grundlegend-erhoben"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_weltgeist_senat(
    kosmos_norm: KosmosNorm | None = None,
    *,
    senat_id: str = "weltgeist-senat",
) -> WeltgeistSenat:
    if kosmos_norm is None:
        kosmos_norm = build_kosmos_norm(norm_id=f"{senat_id}-norm")

    sitze: list[WeltgeistSitz] = []
    for parent_sitz in kosmos_norm.normen:
        parent_geltung = parent_sitz.geltung
        new_id = f"{senat_id}-{parent_sitz.kosmos_norm_id.removeprefix(f'{kosmos_norm.norm_id}-')}"
        raw_weight = min(1.0, round(parent_sitz.kosmos_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_sitz.kosmos_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_sitz.canonical and (new_geltung is WeltgeistGeltung.GRUNDLEGEND_ERHOBEN)
        sitze.append(
            WeltgeistSitz(
                weltgeist_senat_id=new_id,
                weltgeist_rang=_RANG_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                weltgeist_weight=raw_weight,
                weltgeist_tier=new_tier,
                canonical=is_canonical,
                weltgeist_senat_ids=parent_sitz.kosmos_norm_ids + (new_id,),
                weltgeist_senat_tags=parent_sitz.kosmos_norm_tags + (f"weltgeist-senat:{new_geltung.value}",),
            )
        )

    return WeltgeistSenat(
        senat_id=senat_id,
        kosmos_norm=kosmos_norm,
        sitze=tuple(sitze),
    )
