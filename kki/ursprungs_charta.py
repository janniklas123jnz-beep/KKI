"""ursprungs_charta — Zivilisation & Transzendenz layer 1 (#241)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .universal_kodex import (
    UniversalKodex,
    UniversalKodexGeltung,
    UniversalKodexKlasse,
    UniversalKodexNorm,
    UniversalKodexProzedur,
    build_universal_kodex,
)

__all__ = [
    "UrsprungsTyp",
    "UrsprungsProzedur",
    "UrsprungsGeltung",
    "UrsprungsNorm",
    "UrsprungsCharta",
    "build_ursprungs_charta",
]


class UrsprungsTyp(str, Enum):
    SCHUTZ_URSPRUNG = "schutz-ursprung"
    ORDNUNGS_URSPRUNG = "ordnungs-ursprung"
    SOUVERAENITAETS_URSPRUNG = "souveraenitaets-ursprung"


class UrsprungsProzedur(str, Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class UrsprungsGeltung(str, Enum):
    GESPERRT = "gesperrt"
    VERBRIEFT = "verbrieft"
    GRUNDLEGEND_VERBRIEFT = "grundlegend-verbrieft"


_TYP_MAP: dict[UniversalKodexGeltung, UrsprungsTyp] = {
    UniversalKodexGeltung.GESPERRT: UrsprungsTyp.SCHUTZ_URSPRUNG,
    UniversalKodexGeltung.UNIVERSELL: UrsprungsTyp.ORDNUNGS_URSPRUNG,
    UniversalKodexGeltung.GRUNDLEGEND_UNIVERSELL: UrsprungsTyp.SOUVERAENITAETS_URSPRUNG,
}
_PROZEDUR_MAP: dict[UniversalKodexGeltung, UrsprungsProzedur] = {
    UniversalKodexGeltung.GESPERRT: UrsprungsProzedur.NOTPROZEDUR,
    UniversalKodexGeltung.UNIVERSELL: UrsprungsProzedur.REGELPROTOKOLL,
    UniversalKodexGeltung.GRUNDLEGEND_UNIVERSELL: UrsprungsProzedur.PLENARPROTOKOLL,
}
_GELTUNG_MAP: dict[UniversalKodexGeltung, UrsprungsGeltung] = {
    UniversalKodexGeltung.GESPERRT: UrsprungsGeltung.GESPERRT,
    UniversalKodexGeltung.UNIVERSELL: UrsprungsGeltung.VERBRIEFT,
    UniversalKodexGeltung.GRUNDLEGEND_UNIVERSELL: UrsprungsGeltung.GRUNDLEGEND_VERBRIEFT,
}
_WEIGHT_BONUS: dict[UniversalKodexGeltung, float] = {
    UniversalKodexGeltung.GESPERRT: 0.0,
    UniversalKodexGeltung.UNIVERSELL: 0.04,
    UniversalKodexGeltung.GRUNDLEGEND_UNIVERSELL: 0.08,
}
_TIER_BONUS: dict[UniversalKodexGeltung, int] = {
    UniversalKodexGeltung.GESPERRT: 0,
    UniversalKodexGeltung.UNIVERSELL: 1,
    UniversalKodexGeltung.GRUNDLEGEND_UNIVERSELL: 2,
}


@dataclass(frozen=True)
class UrsprungsNorm:
    ursprungs_charta_id: str
    ursprungs_typ: UrsprungsTyp
    prozedur: UrsprungsProzedur
    geltung: UrsprungsGeltung
    ursprungs_weight: float
    ursprungs_tier: int
    canonical: bool
    ursprungs_charta_ids: tuple[str, ...]
    ursprungs_charta_tags: tuple[str, ...]


@dataclass(frozen=True)
class UrsprungsCharta:
    charta_id: str
    universal_kodex: UniversalKodex
    normen: tuple[UrsprungsNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.ursprungs_charta_id for n in self.normen if n.geltung is UrsprungsGeltung.GESPERRT)

    @property
    def verbrieft_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.ursprungs_charta_id for n in self.normen if n.geltung is UrsprungsGeltung.VERBRIEFT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.ursprungs_charta_id for n in self.normen if n.geltung is UrsprungsGeltung.GRUNDLEGEND_VERBRIEFT)

    @property
    def charta_signal(self):
        if any(n.geltung is UrsprungsGeltung.GESPERRT for n in self.normen):
            status = "charta-gesperrt"
            severity = "critical"
        elif any(n.geltung is UrsprungsGeltung.VERBRIEFT for n in self.normen):
            status = "charta-verbrieft"
            severity = "warning"
        else:
            status = "charta-grundlegend-verbrieft"
            severity = "info"

        @dataclass(frozen=True)
        class _Signal:
            status: str
            severity: str

        return _Signal(status=status, severity=severity)


def build_ursprungs_charta(
    universal_kodex: UniversalKodex | None = None,
    *,
    charta_id: str = "ursprungs-charta",
) -> UrsprungsCharta:
    if universal_kodex is None:
        universal_kodex = build_universal_kodex(kodex_id=f"{charta_id}-kodex")

    normen: list[UrsprungsNorm] = []
    for parent_norm in universal_kodex.normen:
        parent_geltung = parent_norm.geltung
        new_id = f"{charta_id}-{parent_norm.universal_kodex_id.removeprefix(f'{universal_kodex.kodex_id}-')}"
        raw_weight = min(1.0, round(parent_norm.universal_weight + _WEIGHT_BONUS[parent_geltung], 3))
        new_tier = parent_norm.universal_tier + _TIER_BONUS[parent_geltung]
        new_geltung = _GELTUNG_MAP[parent_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is UrsprungsGeltung.GRUNDLEGEND_VERBRIEFT)
        normen.append(
            UrsprungsNorm(
                ursprungs_charta_id=new_id,
                ursprungs_typ=_TYP_MAP[parent_geltung],
                prozedur=_PROZEDUR_MAP[parent_geltung],
                geltung=new_geltung,
                ursprungs_weight=raw_weight,
                ursprungs_tier=new_tier,
                canonical=is_canonical,
                ursprungs_charta_ids=parent_norm.universal_kodex_ids + (new_id,),
                ursprungs_charta_tags=parent_norm.universal_kodex_tags + (f"ursprungs-charta:{new_geltung.value}",),
            )
        )

    return UrsprungsCharta(
        charta_id=charta_id,
        universal_kodex=universal_kodex,
        normen=tuple(normen),
    )
