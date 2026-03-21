"""
#367 PerkolationsNorm — Perkolationstheorie: Phasenübergänge in vernetzten Systemen.
Kritische Perkolationsschwelle p_c bestimmt, wann Informationsfluss den gesamten
Schwarm durchdringt. Leitsterns Resilienz beruht auf Überperkolation: Redundante
Pfade garantieren, dass kein Teilausfall den Gesamtverbund isoliert.
*_norm pattern: Container = PerkolationsNormSatz, Entry = PerkolationsNormEintrag
Geltungsstufen: GESPERRT / PERKOLIEREND / GRUNDLEGEND_PERKOLIEREND
Parent: EmergenzSenat (#366)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .emergenz_senat import (
    EmergenzGeltung,
    EmergenzSenat,
    build_emergenz_senat,
)

_GELTUNG_MAP: dict[EmergenzGeltung, "PerkolationsNormGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[EmergenzGeltung.GESPERRT] = PerkolationsNormGeltung.GESPERRT
    _GELTUNG_MAP[EmergenzGeltung.EMERGENT] = PerkolationsNormGeltung.PERKOLIEREND
    _GELTUNG_MAP[EmergenzGeltung.GRUNDLEGEND_EMERGENT] = PerkolationsNormGeltung.GRUNDLEGEND_PERKOLIEREND


class PerkolationsNormTyp(Enum):
    SCHUTZ_PERKOLATIONS_NORM = "schutz-perkolations-norm"
    ORDNUNGS_PERKOLATIONS_NORM = "ordnungs-perkolations-norm"
    SOUVERAENITAETS_PERKOLATIONS_NORM = "souveraenitaets-perkolations-norm"


class PerkolationsNormProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class PerkolationsNormGeltung(Enum):
    GESPERRT = "gesperrt"
    PERKOLIEREND = "perkolierend"
    GRUNDLEGEND_PERKOLIEREND = "grundlegend-perkolierend"


_init_map()

_TYP_MAP: dict[PerkolationsNormGeltung, PerkolationsNormTyp] = {
    PerkolationsNormGeltung.GESPERRT: PerkolationsNormTyp.SCHUTZ_PERKOLATIONS_NORM,
    PerkolationsNormGeltung.PERKOLIEREND: PerkolationsNormTyp.ORDNUNGS_PERKOLATIONS_NORM,
    PerkolationsNormGeltung.GRUNDLEGEND_PERKOLIEREND: PerkolationsNormTyp.SOUVERAENITAETS_PERKOLATIONS_NORM,
}

_PROZEDUR_MAP: dict[PerkolationsNormGeltung, PerkolationsNormProzedur] = {
    PerkolationsNormGeltung.GESPERRT: PerkolationsNormProzedur.NOTPROZEDUR,
    PerkolationsNormGeltung.PERKOLIEREND: PerkolationsNormProzedur.REGELPROTOKOLL,
    PerkolationsNormGeltung.GRUNDLEGEND_PERKOLIEREND: PerkolationsNormProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[PerkolationsNormGeltung, float] = {
    PerkolationsNormGeltung.GESPERRT: 0.0,
    PerkolationsNormGeltung.PERKOLIEREND: 0.04,
    PerkolationsNormGeltung.GRUNDLEGEND_PERKOLIEREND: 0.08,
}

_TIER_DELTA: dict[PerkolationsNormGeltung, int] = {
    PerkolationsNormGeltung.GESPERRT: 0,
    PerkolationsNormGeltung.PERKOLIEREND: 1,
    PerkolationsNormGeltung.GRUNDLEGEND_PERKOLIEREND: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PerkolationsNormEintrag:
    norm_id: str
    perkolations_norm_typ: PerkolationsNormTyp
    prozedur: PerkolationsNormProzedur
    geltung: PerkolationsNormGeltung
    perkolations_norm_weight: float
    perkolations_norm_tier: int
    canonical: bool
    perkolations_norm_ids: tuple[str, ...]
    perkolations_norm_tags: tuple[str, ...]


@dataclass(frozen=True)
class PerkolationsNormSatz:
    norm_id: str
    emergenz_senat: EmergenzSenat
    normen: tuple[PerkolationsNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is PerkolationsNormGeltung.GESPERRT)

    @property
    def perkolierend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is PerkolationsNormGeltung.PERKOLIEREND)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is PerkolationsNormGeltung.GRUNDLEGEND_PERKOLIEREND)

    @property
    def norm_signal(self):
        if any(n.geltung is PerkolationsNormGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-gesperrt")
        elif any(n.geltung is PerkolationsNormGeltung.PERKOLIEREND for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-perkolierend")
        from types import SimpleNamespace
        return SimpleNamespace(status="norm-grundlegend-perkolierend")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_perkolations_norm(
    emergenz_senat: EmergenzSenat | None = None,
    *,
    norm_id: str = "perkolations-norm",
) -> PerkolationsNormSatz:
    if emergenz_senat is None:
        emergenz_senat = build_emergenz_senat(senat_id=f"{norm_id}-senat")

    normen: list[PerkolationsNormEintrag] = []
    for parent_norm in emergenz_senat.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{norm_id}-{parent_norm.emergenz_senat_id.removeprefix(f'{emergenz_senat.senat_id}-')}"
        raw_weight = min(1.0, parent_norm.emergenz_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.emergenz_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is PerkolationsNormGeltung.GRUNDLEGEND_PERKOLIEREND)
        normen.append(
            PerkolationsNormEintrag(
                norm_id=new_id,
                perkolations_norm_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                perkolations_norm_weight=new_weight,
                perkolations_norm_tier=new_tier,
                canonical=is_canonical,
                perkolations_norm_ids=parent_norm.emergenz_ids + (new_id,),
                perkolations_norm_tags=parent_norm.emergenz_tags + (f"perkolations-norm:{new_geltung.value}",),
            )
        )
    return PerkolationsNormSatz(
        norm_id=norm_id,
        emergenz_senat=emergenz_senat,
        normen=tuple(normen),
    )
