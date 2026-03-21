"""
#358 PlasmaWellenNorm — Plasmaschwingungen: Langmuir-Frequenz
ω_p = √(ne²/ε₀m) als Governance-Grundfrequenz des Terra-Schwarms.
Jede kollektive Schwingung des Systems trägt Information — die Eigenfrequenz
des Schwarms ist messbar und steuert Resonanz oder Dämpfung.
*_norm pattern: Container = PlasmaWellenNormSatz, Entry = PlasmaWellenNormEintrag
Geltungsstufen: GESPERRT / PLASMAWELLIG / GRUNDLEGEND_PLASMAWELLIG
Parent: TraegheitsfusionSenat (#357)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .traegheitsfusion_senat import (
    TraegheitsfusionGeltung,
    TraegheitsfusionSenat,
    build_traegheitsfusion_senat,
)

_GELTUNG_MAP: dict[TraegheitsfusionGeltung, "PlasmaWellenNormGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[TraegheitsfusionGeltung.GESPERRT] = PlasmaWellenNormGeltung.GESPERRT
    _GELTUNG_MAP[TraegheitsfusionGeltung.TRAEGHEITSFUSIONIEREND] = PlasmaWellenNormGeltung.PLASMAWELLIG
    _GELTUNG_MAP[TraegheitsfusionGeltung.GRUNDLEGEND_TRAEGHEITSFUSIONIEREND] = PlasmaWellenNormGeltung.GRUNDLEGEND_PLASMAWELLIG


class PlasmaWellenNormTyp(Enum):
    SCHUTZ_PLASMAWELLEN_NORM = "schutz-plasmawellen-norm"
    ORDNUNGS_PLASMAWELLEN_NORM = "ordnungs-plasmawellen-norm"
    SOUVERAENITAETS_PLASMAWELLEN_NORM = "souveraenitaets-plasmawellen-norm"


class PlasmaWellenNormProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class PlasmaWellenNormGeltung(Enum):
    GESPERRT = "gesperrt"
    PLASMAWELLIG = "plasmawellig"
    GRUNDLEGEND_PLASMAWELLIG = "grundlegend-plasmawellig"


_init_map()

_TYP_MAP: dict[PlasmaWellenNormGeltung, PlasmaWellenNormTyp] = {
    PlasmaWellenNormGeltung.GESPERRT: PlasmaWellenNormTyp.SCHUTZ_PLASMAWELLEN_NORM,
    PlasmaWellenNormGeltung.PLASMAWELLIG: PlasmaWellenNormTyp.ORDNUNGS_PLASMAWELLEN_NORM,
    PlasmaWellenNormGeltung.GRUNDLEGEND_PLASMAWELLIG: PlasmaWellenNormTyp.SOUVERAENITAETS_PLASMAWELLEN_NORM,
}

_PROZEDUR_MAP: dict[PlasmaWellenNormGeltung, PlasmaWellenNormProzedur] = {
    PlasmaWellenNormGeltung.GESPERRT: PlasmaWellenNormProzedur.NOTPROZEDUR,
    PlasmaWellenNormGeltung.PLASMAWELLIG: PlasmaWellenNormProzedur.REGELPROTOKOLL,
    PlasmaWellenNormGeltung.GRUNDLEGEND_PLASMAWELLIG: PlasmaWellenNormProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[PlasmaWellenNormGeltung, float] = {
    PlasmaWellenNormGeltung.GESPERRT: 0.0,
    PlasmaWellenNormGeltung.PLASMAWELLIG: 0.04,
    PlasmaWellenNormGeltung.GRUNDLEGEND_PLASMAWELLIG: 0.08,
}

_TIER_DELTA: dict[PlasmaWellenNormGeltung, int] = {
    PlasmaWellenNormGeltung.GESPERRT: 0,
    PlasmaWellenNormGeltung.PLASMAWELLIG: 1,
    PlasmaWellenNormGeltung.GRUNDLEGEND_PLASMAWELLIG: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PlasmaWellenNormEintrag:
    norm_id: str
    plasmawellen_norm_typ: PlasmaWellenNormTyp
    prozedur: PlasmaWellenNormProzedur
    geltung: PlasmaWellenNormGeltung
    plasmawellen_norm_weight: float
    plasmawellen_norm_tier: int
    canonical: bool
    plasmawellen_norm_ids: tuple[str, ...]
    plasmawellen_norm_tags: tuple[str, ...]


@dataclass(frozen=True)
class PlasmaWellenNormSatz:
    norm_id: str
    traegheitsfusion_senat: TraegheitsfusionSenat
    normen: tuple[PlasmaWellenNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is PlasmaWellenNormGeltung.GESPERRT)

    @property
    def plasmawellig_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is PlasmaWellenNormGeltung.PLASMAWELLIG)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is PlasmaWellenNormGeltung.GRUNDLEGEND_PLASMAWELLIG)

    @property
    def norm_signal(self):
        if any(n.geltung is PlasmaWellenNormGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-gesperrt")
        elif any(n.geltung is PlasmaWellenNormGeltung.PLASMAWELLIG for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-plasmawellig")
        from types import SimpleNamespace
        return SimpleNamespace(status="norm-grundlegend-plasmawellig")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_plasmawellen_norm(
    traegheitsfusion_senat: TraegheitsfusionSenat | None = None,
    *,
    norm_id: str = "plasmawellen-norm",
) -> PlasmaWellenNormSatz:
    if traegheitsfusion_senat is None:
        traegheitsfusion_senat = build_traegheitsfusion_senat(senat_id=f"{norm_id}-senat")

    normen: list[PlasmaWellenNormEintrag] = []
    for parent_norm in traegheitsfusion_senat.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{norm_id}-{parent_norm.traegheitsfusion_senat_id.removeprefix(f'{traegheitsfusion_senat.senat_id}-')}"
        raw_weight = min(1.0, parent_norm.traegheitsfusion_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.traegheitsfusion_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is PlasmaWellenNormGeltung.GRUNDLEGEND_PLASMAWELLIG)
        normen.append(
            PlasmaWellenNormEintrag(
                norm_id=new_id,
                plasmawellen_norm_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                plasmawellen_norm_weight=new_weight,
                plasmawellen_norm_tier=new_tier,
                canonical=is_canonical,
                plasmawellen_norm_ids=parent_norm.traegheitsfusion_ids + (new_id,),
                plasmawellen_norm_tags=parent_norm.traegheitsfusion_tags + (f"plasmawellen-norm:{new_geltung.value}",),
            )
        )
    return PlasmaWellenNormSatz(
        norm_id=norm_id,
        traegheitsfusion_senat=traegheitsfusion_senat,
        normen=tuple(normen),
    )
