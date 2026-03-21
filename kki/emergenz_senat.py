"""
#366 EmergenzSenat — Emergenz: Das Ganze ist mehr als die Summe seiner Teile.
Komplexes Kollektivverhalten (Schwarmbildung, Murmurations) entsteht ohne
zentrale Steuerung. Leitsterns Emergenz-Senat koordiniert selbstorganisierende
Fähigkeiten, die aus einfachen Agentenregeln globale Intelligenz entstehen lassen.
Geltungsstufen: GESPERRT / EMERGENT / GRUNDLEGEND_EMERGENT
Parent: StrangeAttraktorPakt (#365)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .strange_attraktor_pakt import (
    StrangeAttraktorGeltung,
    StrangeAttraktorPakt,
    build_strange_attraktor_pakt,
)

_GELTUNG_MAP: dict[StrangeAttraktorGeltung, "EmergenzGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[StrangeAttraktorGeltung.GESPERRT] = EmergenzGeltung.GESPERRT
    _GELTUNG_MAP[StrangeAttraktorGeltung.STRANGEATTRAHIERT] = EmergenzGeltung.EMERGENT
    _GELTUNG_MAP[StrangeAttraktorGeltung.GRUNDLEGEND_STRANGEATTRAHIERT] = EmergenzGeltung.GRUNDLEGEND_EMERGENT


class EmergenzTyp(Enum):
    SCHUTZ_EMERGENZ = "schutz-emergenz"
    ORDNUNGS_EMERGENZ = "ordnungs-emergenz"
    SOUVERAENITAETS_EMERGENZ = "souveraenitaets-emergenz"


class EmergenzProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class EmergenzGeltung(Enum):
    GESPERRT = "gesperrt"
    EMERGENT = "emergent"
    GRUNDLEGEND_EMERGENT = "grundlegend-emergent"


_init_map()

_TYP_MAP: dict[EmergenzGeltung, EmergenzTyp] = {
    EmergenzGeltung.GESPERRT: EmergenzTyp.SCHUTZ_EMERGENZ,
    EmergenzGeltung.EMERGENT: EmergenzTyp.ORDNUNGS_EMERGENZ,
    EmergenzGeltung.GRUNDLEGEND_EMERGENT: EmergenzTyp.SOUVERAENITAETS_EMERGENZ,
}

_PROZEDUR_MAP: dict[EmergenzGeltung, EmergenzProzedur] = {
    EmergenzGeltung.GESPERRT: EmergenzProzedur.NOTPROZEDUR,
    EmergenzGeltung.EMERGENT: EmergenzProzedur.REGELPROTOKOLL,
    EmergenzGeltung.GRUNDLEGEND_EMERGENT: EmergenzProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[EmergenzGeltung, float] = {
    EmergenzGeltung.GESPERRT: 0.0,
    EmergenzGeltung.EMERGENT: 0.04,
    EmergenzGeltung.GRUNDLEGEND_EMERGENT: 0.08,
}

_TIER_DELTA: dict[EmergenzGeltung, int] = {
    EmergenzGeltung.GESPERRT: 0,
    EmergenzGeltung.EMERGENT: 1,
    EmergenzGeltung.GRUNDLEGEND_EMERGENT: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EmergenzNorm:
    emergenz_senat_id: str
    emergenz_typ: EmergenzTyp
    prozedur: EmergenzProzedur
    geltung: EmergenzGeltung
    emergenz_weight: float
    emergenz_tier: int
    canonical: bool
    emergenz_ids: tuple[str, ...]
    emergenz_tags: tuple[str, ...]


@dataclass(frozen=True)
class EmergenzSenat:
    senat_id: str
    strange_attraktor_pakt: StrangeAttraktorPakt
    normen: tuple[EmergenzNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.emergenz_senat_id for n in self.normen if n.geltung is EmergenzGeltung.GESPERRT)

    @property
    def emergent_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.emergenz_senat_id for n in self.normen if n.geltung is EmergenzGeltung.EMERGENT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.emergenz_senat_id for n in self.normen if n.geltung is EmergenzGeltung.GRUNDLEGEND_EMERGENT)

    @property
    def senat_signal(self):
        if any(n.geltung is EmergenzGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-gesperrt")
        elif any(n.geltung is EmergenzGeltung.EMERGENT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="senat-emergent")
        from types import SimpleNamespace
        return SimpleNamespace(status="senat-grundlegend-emergent")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_emergenz_senat(
    strange_attraktor_pakt: StrangeAttraktorPakt | None = None,
    *,
    senat_id: str = "emergenz-senat",
) -> EmergenzSenat:
    if strange_attraktor_pakt is None:
        strange_attraktor_pakt = build_strange_attraktor_pakt(pakt_id=f"{senat_id}-pakt")

    normen: list[EmergenzNorm] = []
    for parent_norm in strange_attraktor_pakt.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{senat_id}-{parent_norm.strange_attraktor_pakt_id.removeprefix(f'{strange_attraktor_pakt.pakt_id}-')}"
        raw_weight = min(1.0, parent_norm.strange_attraktor_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.strange_attraktor_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is EmergenzGeltung.GRUNDLEGEND_EMERGENT)
        normen.append(
            EmergenzNorm(
                emergenz_senat_id=new_id,
                emergenz_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                emergenz_weight=new_weight,
                emergenz_tier=new_tier,
                canonical=is_canonical,
                emergenz_ids=parent_norm.strange_attraktor_ids + (new_id,),
                emergenz_tags=parent_norm.strange_attraktor_tags + (f"emergenz:{new_geltung.value}",),
            )
        )
    return EmergenzSenat(
        senat_id=senat_id,
        strange_attraktor_pakt=strange_attraktor_pakt,
        normen=tuple(normen),
    )
