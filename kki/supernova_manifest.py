"""
#336 SupernovaManifest — Supernova als transformatives Schwarmereignis-Manifest:
alte Governance-Strukturen explodieren und befruchten als Saatgut die nächste Generation.
Geltungsstufen: GESPERRT / SUPERNOVAEXPLOSIV / GRUNDLEGEND_SUPERNOVAEXPLOSIV
Parent: RoterRiesePakt (#335)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .roter_riese_pakt import (
    RoterRieseGeltung,
    RoterRiesePakt,
    build_roter_riese_pakt,
)

_GELTUNG_MAP: dict[RoterRieseGeltung, "SupernovaGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[RoterRieseGeltung.GESPERRT] = SupernovaGeltung.GESPERRT
    _GELTUNG_MAP[RoterRieseGeltung.RIESENPHASIG] = SupernovaGeltung.SUPERNOVAEXPLOSIV
    _GELTUNG_MAP[RoterRieseGeltung.GRUNDLEGEND_RIESENPHASIG] = SupernovaGeltung.GRUNDLEGEND_SUPERNOVAEXPLOSIV


class SupernovaTyp(Enum):
    SCHUTZ_SUPERNOVA = "schutz-supernova"
    ORDNUNGS_SUPERNOVA = "ordnungs-supernova"
    SOUVERAENITAETS_SUPERNOVA = "souveraenitaets-supernova"


class SupernovaProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class SupernovaGeltung(Enum):
    GESPERRT = "gesperrt"
    SUPERNOVAEXPLOSIV = "supernovaexplosiv"
    GRUNDLEGEND_SUPERNOVAEXPLOSIV = "grundlegend-supernovaexplosiv"


_init_map()

_TYP_MAP: dict[SupernovaGeltung, SupernovaTyp] = {
    SupernovaGeltung.GESPERRT: SupernovaTyp.SCHUTZ_SUPERNOVA,
    SupernovaGeltung.SUPERNOVAEXPLOSIV: SupernovaTyp.ORDNUNGS_SUPERNOVA,
    SupernovaGeltung.GRUNDLEGEND_SUPERNOVAEXPLOSIV: SupernovaTyp.SOUVERAENITAETS_SUPERNOVA,
}

_PROZEDUR_MAP: dict[SupernovaGeltung, SupernovaProzedur] = {
    SupernovaGeltung.GESPERRT: SupernovaProzedur.NOTPROZEDUR,
    SupernovaGeltung.SUPERNOVAEXPLOSIV: SupernovaProzedur.REGELPROTOKOLL,
    SupernovaGeltung.GRUNDLEGEND_SUPERNOVAEXPLOSIV: SupernovaProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[SupernovaGeltung, float] = {
    SupernovaGeltung.GESPERRT: 0.0,
    SupernovaGeltung.SUPERNOVAEXPLOSIV: 0.04,
    SupernovaGeltung.GRUNDLEGEND_SUPERNOVAEXPLOSIV: 0.08,
}

_TIER_DELTA: dict[SupernovaGeltung, int] = {
    SupernovaGeltung.GESPERRT: 0,
    SupernovaGeltung.SUPERNOVAEXPLOSIV: 1,
    SupernovaGeltung.GRUNDLEGEND_SUPERNOVAEXPLOSIV: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SupernovaNorm:
    supernova_manifest_id: str
    supernova_typ: SupernovaTyp
    prozedur: SupernovaProzedur
    geltung: SupernovaGeltung
    supernova_weight: float
    supernova_tier: int
    canonical: bool
    supernova_ids: tuple[str, ...]
    supernova_tags: tuple[str, ...]


@dataclass(frozen=True)
class SupernovaManifest:
    manifest_id: str
    roter_riese_pakt: RoterRiesePakt
    normen: tuple[SupernovaNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.supernova_manifest_id for n in self.normen if n.geltung is SupernovaGeltung.GESPERRT)

    @property
    def supernovaexplosiv_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.supernova_manifest_id for n in self.normen if n.geltung is SupernovaGeltung.SUPERNOVAEXPLOSIV)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.supernova_manifest_id for n in self.normen if n.geltung is SupernovaGeltung.GRUNDLEGEND_SUPERNOVAEXPLOSIV)

    @property
    def manifest_signal(self):
        if any(n.geltung is SupernovaGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-gesperrt")
        elif any(n.geltung is SupernovaGeltung.SUPERNOVAEXPLOSIV for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="manifest-supernovaexplosiv")
        from types import SimpleNamespace
        return SimpleNamespace(status="manifest-grundlegend-supernovaexplosiv")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_supernova_manifest(
    roter_riese_pakt: RoterRiesePakt | None = None,
    *,
    manifest_id: str = "supernova-manifest",
) -> SupernovaManifest:
    if roter_riese_pakt is None:
        roter_riese_pakt = build_roter_riese_pakt(pakt_id=f"{manifest_id}-pakt")

    normen: list[SupernovaNorm] = []
    for parent_norm in roter_riese_pakt.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{manifest_id}-{parent_norm.roter_riese_pakt_id.removeprefix(f'{roter_riese_pakt.pakt_id}-')}"
        raw_weight = min(1.0, parent_norm.roter_riese_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.roter_riese_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SupernovaGeltung.GRUNDLEGEND_SUPERNOVAEXPLOSIV)
        normen.append(
            SupernovaNorm(
                supernova_manifest_id=new_id,
                supernova_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                supernova_weight=new_weight,
                supernova_tier=new_tier,
                canonical=is_canonical,
                supernova_ids=parent_norm.roter_riese_ids + (new_id,),
                supernova_tags=parent_norm.roter_riese_tags + (f"supernova:{new_geltung.value}",),
            )
        )
    return SupernovaManifest(
        manifest_id=manifest_id,
        roter_riese_pakt=roter_riese_pakt,
        normen=tuple(normen),
    )
