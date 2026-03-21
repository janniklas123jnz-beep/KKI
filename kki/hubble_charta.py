"""
#329 HubbleCharta — Hubble-Expansion als kosmologische Rechts-Charta des Schwarms.
Geltungsstufen: GESPERRT / HUBBLEGEBUNDEN / GRUNDLEGEND_HUBBLEGEBUNDEN
Parent: ExpansionNormSatz (#328)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .expansion_norm import (
    ExpansionNormGeltung,
    ExpansionNormSatz,
    build_expansion_norm,
)

_GELTUNG_MAP: dict[ExpansionNormGeltung, "HubbleGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[ExpansionNormGeltung.GESPERRT] = HubbleGeltung.GESPERRT
    _GELTUNG_MAP[ExpansionNormGeltung.EXPANSIONSNORMIERT] = HubbleGeltung.HUBBLEGEBUNDEN
    _GELTUNG_MAP[ExpansionNormGeltung.GRUNDLEGEND_EXPANSIONSNORMIERT] = HubbleGeltung.GRUNDLEGEND_HUBBLEGEBUNDEN


class HubbleTyp(Enum):
    SCHUTZ_HUBBLE = "schutz-hubble"
    ORDNUNGS_HUBBLE = "ordnungs-hubble"
    SOUVERAENITAETS_HUBBLE = "souveraenitaets-hubble"


class HubbleProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class HubbleGeltung(Enum):
    GESPERRT = "gesperrt"
    HUBBLEGEBUNDEN = "hubblegebunden"
    GRUNDLEGEND_HUBBLEGEBUNDEN = "grundlegend-hubblegebunden"


_init_map()

_TYP_MAP: dict[HubbleGeltung, HubbleTyp] = {
    HubbleGeltung.GESPERRT: HubbleTyp.SCHUTZ_HUBBLE,
    HubbleGeltung.HUBBLEGEBUNDEN: HubbleTyp.ORDNUNGS_HUBBLE,
    HubbleGeltung.GRUNDLEGEND_HUBBLEGEBUNDEN: HubbleTyp.SOUVERAENITAETS_HUBBLE,
}

_PROZEDUR_MAP: dict[HubbleGeltung, HubbleProzedur] = {
    HubbleGeltung.GESPERRT: HubbleProzedur.NOTPROZEDUR,
    HubbleGeltung.HUBBLEGEBUNDEN: HubbleProzedur.REGELPROTOKOLL,
    HubbleGeltung.GRUNDLEGEND_HUBBLEGEBUNDEN: HubbleProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[HubbleGeltung, float] = {
    HubbleGeltung.GESPERRT: 0.0,
    HubbleGeltung.HUBBLEGEBUNDEN: 0.04,
    HubbleGeltung.GRUNDLEGEND_HUBBLEGEBUNDEN: 0.08,
}

_TIER_DELTA: dict[HubbleGeltung, int] = {
    HubbleGeltung.GESPERRT: 0,
    HubbleGeltung.HUBBLEGEBUNDEN: 1,
    HubbleGeltung.GRUNDLEGEND_HUBBLEGEBUNDEN: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class HubbleNorm:
    hubble_charta_id: str
    hubble_typ: HubbleTyp
    prozedur: HubbleProzedur
    geltung: HubbleGeltung
    hubble_weight: float
    hubble_tier: int
    canonical: bool
    hubble_ids: tuple[str, ...]
    hubble_tags: tuple[str, ...]


@dataclass(frozen=True)
class HubbleCharta:
    charta_id: str
    expansion_norm: ExpansionNormSatz
    normen: tuple[HubbleNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.hubble_charta_id for n in self.normen if n.geltung is HubbleGeltung.GESPERRT)

    @property
    def hubblegebunden_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.hubble_charta_id for n in self.normen if n.geltung is HubbleGeltung.HUBBLEGEBUNDEN)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.hubble_charta_id for n in self.normen if n.geltung is HubbleGeltung.GRUNDLEGEND_HUBBLEGEBUNDEN)

    @property
    def charta_signal(self):
        if any(n.geltung is HubbleGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is HubbleGeltung.HUBBLEGEBUNDEN for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-hubblegebunden")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-hubblegebunden")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_hubble_charta(
    expansion_norm: ExpansionNormSatz | None = None,
    *,
    charta_id: str = "hubble-charta",
) -> HubbleCharta:
    if expansion_norm is None:
        expansion_norm = build_expansion_norm(norm_id=f"{charta_id}-expansion-norm")

    normen: list[HubbleNorm] = []
    for parent_norm in expansion_norm.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.norm_id.removeprefix(f'{expansion_norm.norm_id}-')}"
        raw_weight = min(1.0, parent_norm.expansion_norm_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.expansion_norm_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is HubbleGeltung.GRUNDLEGEND_HUBBLEGEBUNDEN)
        normen.append(
            HubbleNorm(
                hubble_charta_id=new_id,
                hubble_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                hubble_weight=new_weight,
                hubble_tier=new_tier,
                canonical=is_canonical,
                hubble_ids=parent_norm.expansion_norm_ids + (new_id,),
                hubble_tags=parent_norm.expansion_norm_tags + (f"hubble-charta:{new_geltung.value}",),
            )
        )
    return HubbleCharta(
        charta_id=charta_id,
        expansion_norm=expansion_norm,
        normen=tuple(normen),
    )
