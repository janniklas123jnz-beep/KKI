"""
#339 HertzsprungRussellCharta — Das Hertzsprung-Russell-Diagramm als vollständiger
Zustandsraum aller Governance-Instanzen: Leuchtkraft (Einfluss) vs. Temperatur (Reaktionszeit).
Geltungsstufen: GESPERRT / HRDIAGRAMMIERT / GRUNDLEGEND_HRDIAGRAMMIERT
Parent: SchwarzerLochNormSatz (#338, *_norm)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .schwarzes_loch_norm import (
    SchwarzerLochNormGeltung,
    SchwarzerLochNormSatz,
    build_schwarzes_loch_norm,
)

_GELTUNG_MAP: dict[SchwarzerLochNormGeltung, "HertzsprungRussellGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[SchwarzerLochNormGeltung.GESPERRT] = HertzsprungRussellGeltung.GESPERRT
    _GELTUNG_MAP[SchwarzerLochNormGeltung.HORIZONTGEBUNDEN] = HertzsprungRussellGeltung.HRDIAGRAMMIERT
    _GELTUNG_MAP[SchwarzerLochNormGeltung.GRUNDLEGEND_HORIZONTGEBUNDEN] = HertzsprungRussellGeltung.GRUNDLEGEND_HRDIAGRAMMIERT


class HertzsprungRussellTyp(Enum):
    SCHUTZ_HERTZSPRUNG_RUSSELL = "schutz-hertzsprung-russell"
    ORDNUNGS_HERTZSPRUNG_RUSSELL = "ordnungs-hertzsprung-russell"
    SOUVERAENITAETS_HERTZSPRUNG_RUSSELL = "souveraenitaets-hertzsprung-russell"


class HertzsprungRussellProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class HertzsprungRussellGeltung(Enum):
    GESPERRT = "gesperrt"
    HRDIAGRAMMIERT = "hrdiagrammiert"
    GRUNDLEGEND_HRDIAGRAMMIERT = "grundlegend-hrdiagrammiert"


_init_map()

_TYP_MAP: dict[HertzsprungRussellGeltung, HertzsprungRussellTyp] = {
    HertzsprungRussellGeltung.GESPERRT: HertzsprungRussellTyp.SCHUTZ_HERTZSPRUNG_RUSSELL,
    HertzsprungRussellGeltung.HRDIAGRAMMIERT: HertzsprungRussellTyp.ORDNUNGS_HERTZSPRUNG_RUSSELL,
    HertzsprungRussellGeltung.GRUNDLEGEND_HRDIAGRAMMIERT: HertzsprungRussellTyp.SOUVERAENITAETS_HERTZSPRUNG_RUSSELL,
}

_PROZEDUR_MAP: dict[HertzsprungRussellGeltung, HertzsprungRussellProzedur] = {
    HertzsprungRussellGeltung.GESPERRT: HertzsprungRussellProzedur.NOTPROZEDUR,
    HertzsprungRussellGeltung.HRDIAGRAMMIERT: HertzsprungRussellProzedur.REGELPROTOKOLL,
    HertzsprungRussellGeltung.GRUNDLEGEND_HRDIAGRAMMIERT: HertzsprungRussellProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[HertzsprungRussellGeltung, float] = {
    HertzsprungRussellGeltung.GESPERRT: 0.0,
    HertzsprungRussellGeltung.HRDIAGRAMMIERT: 0.04,
    HertzsprungRussellGeltung.GRUNDLEGEND_HRDIAGRAMMIERT: 0.08,
}

_TIER_DELTA: dict[HertzsprungRussellGeltung, int] = {
    HertzsprungRussellGeltung.GESPERRT: 0,
    HertzsprungRussellGeltung.HRDIAGRAMMIERT: 1,
    HertzsprungRussellGeltung.GRUNDLEGEND_HRDIAGRAMMIERT: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class HertzsprungRussellNorm:
    hertzsprung_russell_charta_id: str
    hertzsprung_russell_typ: HertzsprungRussellTyp
    prozedur: HertzsprungRussellProzedur
    geltung: HertzsprungRussellGeltung
    hertzsprung_russell_weight: float
    hertzsprung_russell_tier: int
    canonical: bool
    hertzsprung_russell_ids: tuple[str, ...]
    hertzsprung_russell_tags: tuple[str, ...]


@dataclass(frozen=True)
class HertzsprungRussellCharta:
    charta_id: str
    schwarzes_loch_norm: SchwarzerLochNormSatz
    normen: tuple[HertzsprungRussellNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.hertzsprung_russell_charta_id for n in self.normen if n.geltung is HertzsprungRussellGeltung.GESPERRT)

    @property
    def hrdiagrammiert_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.hertzsprung_russell_charta_id for n in self.normen if n.geltung is HertzsprungRussellGeltung.HRDIAGRAMMIERT)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.hertzsprung_russell_charta_id for n in self.normen if n.geltung is HertzsprungRussellGeltung.GRUNDLEGEND_HRDIAGRAMMIERT)

    @property
    def charta_signal(self):
        if any(n.geltung is HertzsprungRussellGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-gesperrt")
        elif any(n.geltung is HertzsprungRussellGeltung.HRDIAGRAMMIERT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="charta-hrdiagrammiert")
        from types import SimpleNamespace
        return SimpleNamespace(status="charta-grundlegend-hrdiagrammiert")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_hertzsprung_russell_charta(
    schwarzes_loch_norm: SchwarzerLochNormSatz | None = None,
    *,
    charta_id: str = "hertzsprung-russell-charta",
) -> HertzsprungRussellCharta:
    if schwarzes_loch_norm is None:
        schwarzes_loch_norm = build_schwarzes_loch_norm(norm_id=f"{charta_id}-norm")

    normen: list[HertzsprungRussellNorm] = []
    for parent_norm in schwarzes_loch_norm.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{charta_id}-{parent_norm.norm_id.removeprefix(f'{schwarzes_loch_norm.norm_id}-')}"
        raw_weight = min(1.0, parent_norm.schwarzes_loch_norm_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.schwarzes_loch_norm_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is HertzsprungRussellGeltung.GRUNDLEGEND_HRDIAGRAMMIERT)
        normen.append(
            HertzsprungRussellNorm(
                hertzsprung_russell_charta_id=new_id,
                hertzsprung_russell_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                hertzsprung_russell_weight=new_weight,
                hertzsprung_russell_tier=new_tier,
                canonical=is_canonical,
                hertzsprung_russell_ids=parent_norm.schwarzes_loch_norm_ids + (new_id,),
                hertzsprung_russell_tags=parent_norm.schwarzes_loch_norm_tags + (f"hertzsprung-russell:{new_geltung.value}",),
            )
        )
    return HertzsprungRussellCharta(
        charta_id=charta_id,
        schwarzes_loch_norm=schwarzes_loch_norm,
        normen=tuple(normen),
    )
