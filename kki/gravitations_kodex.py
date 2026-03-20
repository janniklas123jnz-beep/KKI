"""gravitations_kodex — Relativität & Raumzeit layer 4 (#274)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .lichtgeschwindigkeits_charta import (
    LichtgeschwindigkeitsCharta,
    LichtgeschwindigkeitsGeltung,
    LichtgeschwindigkeitsNorm,
    LichtgeschwindigkeitsProzedur,
    LichtgeschwindigkeitsTyp,
    build_lichtgeschwindigkeits_charta,
)

__all__ = [
    "GravitationsTyp",
    "GravitationsProzedur",
    "GravitationsGeltung",
    "GravitationsNorm",
    "GravitationsKodex",
    "build_gravitations_kodex",
]


class GravitationsTyp(str, Enum):
    SCHUTZ_GRAVITATION = "schutz-gravitation"
    ORDNUNGS_GRAVITATION = "ordnungs-gravitation"
    SOUVERAENITAETS_GRAVITATION = "souveraenitaets-gravitation"


class GravitationsProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class GravitationsGeltung(str, Enum):
    GESPERRT = "gesperrt"
    GRAVITIERT = "gravitiert"
    GRUNDLEGEND_GRAVITIERT = "grundlegend-gravitiert"


_TYP_MAP: dict[LichtgeschwindigkeitsGeltung, GravitationsTyp] = {
    LichtgeschwindigkeitsGeltung.GESPERRT: GravitationsTyp.SCHUTZ_GRAVITATION,
    LichtgeschwindigkeitsGeltung.LICHTSCHNELL: GravitationsTyp.ORDNUNGS_GRAVITATION,
    LichtgeschwindigkeitsGeltung.GRUNDLEGEND_LICHTSCHNELL: GravitationsTyp.SOUVERAENITAETS_GRAVITATION,
}
_PROZEDUR_MAP: dict[LichtgeschwindigkeitsGeltung, GravitationsProzedur] = {
    LichtgeschwindigkeitsGeltung.GESPERRT: GravitationsProzedur.NOTPROZEDUR,
    LichtgeschwindigkeitsGeltung.LICHTSCHNELL: GravitationsProzedur.REGELPROTOKOLL,
    LichtgeschwindigkeitsGeltung.GRUNDLEGEND_LICHTSCHNELL: GravitationsProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[LichtgeschwindigkeitsGeltung, GravitationsGeltung] = {
    LichtgeschwindigkeitsGeltung.GESPERRT: GravitationsGeltung.GESPERRT,
    LichtgeschwindigkeitsGeltung.LICHTSCHNELL: GravitationsGeltung.GRAVITIERT,
    LichtgeschwindigkeitsGeltung.GRUNDLEGEND_LICHTSCHNELL: GravitationsGeltung.GRUNDLEGEND_GRAVITIERT,
}
_WEIGHT_BONUS: dict[LichtgeschwindigkeitsGeltung, float] = {
    LichtgeschwindigkeitsGeltung.GESPERRT: 0.0,
    LichtgeschwindigkeitsGeltung.LICHTSCHNELL: 0.04,
    LichtgeschwindigkeitsGeltung.GRUNDLEGEND_LICHTSCHNELL: 0.08,
}
_TIER_BONUS: dict[LichtgeschwindigkeitsGeltung, int] = {
    LichtgeschwindigkeitsGeltung.GESPERRT: 0,
    LichtgeschwindigkeitsGeltung.LICHTSCHNELL: 1,
    LichtgeschwindigkeitsGeltung.GRUNDLEGEND_LICHTSCHNELL: 2,
}


@dataclass(frozen=True)
class GravitationsNorm:
    gravitations_kodex_id: str
    gravitations_typ: GravitationsTyp
    prozedur: GravitationsProzedur
    geltung: GravitationsGeltung
    gravitations_weight: float
    gravitations_tier: int
    canonical: bool
    gravitations_kodex_ids: tuple[str, ...]
    gravitations_kodex_tags: tuple[str, ...]


@dataclass(frozen=True)
class GravitationsKodex:
    kodex_id: str
    lichtgeschwindigkeits_charta: LichtgeschwindigkeitsCharta
    normen: tuple[GravitationsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.gravitations_kodex_id for n in self.normen if n.geltung is GravitationsGeltung.GESPERRT)

    @property
    def gravitiert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.gravitations_kodex_id for n in self.normen if n.geltung is GravitationsGeltung.GRAVITIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.gravitations_kodex_id for n in self.normen if n.geltung is GravitationsGeltung.GRUNDLEGEND_GRAVITIERT)

    @property
    def kodex_signal(self):
        if any(n.geltung is GravitationsGeltung.GESPERRT for n in self.normen):
            status = "kodex-gesperrt"
            severity = "critical"
        elif any(n.geltung is GravitationsGeltung.GRAVITIERT for n in self.normen):
            status = "kodex-gravitiert"
            severity = "warning"
        else:
            status = "kodex-grundlegend-gravitiert"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_gravitations_kodex(
    lichtgeschwindigkeits_charta: LichtgeschwindigkeitsCharta | None = None,
    *,
    kodex_id: str = "gravitations-kodex",
) -> GravitationsKodex:
    if lichtgeschwindigkeits_charta is None:
        lichtgeschwindigkeits_charta = build_lichtgeschwindigkeits_charta(charta_id=f"{kodex_id}-charta")

    normen: list[GravitationsNorm] = []
    for parent_norm in lichtgeschwindigkeits_charta.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{kodex_id}-{parent_norm.lichtgeschwindigkeits_charta_id.removeprefix(f'{lichtgeschwindigkeits_charta.charta_id}-')}"
        raw_weight = min(1.0, round(parent_norm.lichtgeschwindigkeits_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.lichtgeschwindigkeits_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is GravitationsGeltung.GRUNDLEGEND_GRAVITIERT)
        normen.append(
            GravitationsNorm(
                gravitations_kodex_id=new_id,
                gravitations_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                gravitations_weight=raw_weight,
                gravitations_tier=new_tier,
                canonical=is_canonical,
                gravitations_kodex_ids=parent_norm.lichtgeschwindigkeits_charta_ids + (new_id,),
                gravitations_kodex_tags=parent_norm.lichtgeschwindigkeits_charta_tags + (f"gravitations-kodex:{new_geltung.value}",),
            )
        )

    return GravitationsKodex(
        kodex_id=kodex_id,
        lichtgeschwindigkeits_charta=lichtgeschwindigkeits_charta,
        normen=tuple(normen),
    )
