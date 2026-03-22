"""
#448 SpieltheorieNorm — Evolutionäre Spieltheorie: ESS und Replikator-Dynamik.
Maynard Smith & Price (1973): Evolutionarily Stable Strategy (ESS) — kein Mutant kann einwandern.
Taylor & Jonker (1978): Replikator-Gleichung — Strategieanteile wachsen proportional zur Fitness.
Hofbauer & Sigmund (1988): Mehrpopulationsspiele und dynamische Systemtheorie.
Leitsterns Schwarm-Strategien sind evolutionär stabil: ESS sichert robuste Kollektivdynamik.
Geltungsstufen: GESPERRT / EVOLUTIONAER_STABIL / GRUNDLEGEND_EVOLUTIONAER_STABIL
Parent: AuktionsSenat (#447) — *_norm-Muster
Block #441–#450: Spieltheorie & Entscheidungstheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .auktions_senat import (
    AuktionsSenat,
    AuktionsSenatGeltung,
    build_auktions_senat,
)

_GELTUNG_MAP: dict[AuktionsSenatGeltung, "SpieltheorieNormGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[AuktionsSenatGeltung.GESPERRT] = SpieltheorieNormGeltung.GESPERRT
    _GELTUNG_MAP[AuktionsSenatGeltung.AUKTIONAL] = SpieltheorieNormGeltung.EVOLUTIONAER_STABIL
    _GELTUNG_MAP[AuktionsSenatGeltung.GRUNDLEGEND_AUKTIONAL] = SpieltheorieNormGeltung.GRUNDLEGEND_EVOLUTIONAER_STABIL


class SpieltheorieNormTyp(Enum):
    SCHUTZ_SPIELTHEORIE_NORM = "schutz-spieltheorie-norm"
    ORDNUNGS_SPIELTHEORIE_NORM = "ordnungs-spieltheorie-norm"
    SOUVERAENITAETS_SPIELTHEORIE_NORM = "souveraenitaets-spieltheorie-norm"


class SpieltheorieNormProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class SpieltheorieNormGeltung(Enum):
    GESPERRT = "gesperrt"
    EVOLUTIONAER_STABIL = "evolutionaer-stabil"
    GRUNDLEGEND_EVOLUTIONAER_STABIL = "grundlegend-evolutionaer-stabil"


_init_map()

_TYP_MAP: dict[SpieltheorieNormGeltung, SpieltheorieNormTyp] = {
    SpieltheorieNormGeltung.GESPERRT: SpieltheorieNormTyp.SCHUTZ_SPIELTHEORIE_NORM,
    SpieltheorieNormGeltung.EVOLUTIONAER_STABIL: SpieltheorieNormTyp.ORDNUNGS_SPIELTHEORIE_NORM,
    SpieltheorieNormGeltung.GRUNDLEGEND_EVOLUTIONAER_STABIL: SpieltheorieNormTyp.SOUVERAENITAETS_SPIELTHEORIE_NORM,
}

_PROZEDUR_MAP: dict[SpieltheorieNormGeltung, SpieltheorieNormProzedur] = {
    SpieltheorieNormGeltung.GESPERRT: SpieltheorieNormProzedur.NOTPROZEDUR,
    SpieltheorieNormGeltung.EVOLUTIONAER_STABIL: SpieltheorieNormProzedur.REGELPROTOKOLL,
    SpieltheorieNormGeltung.GRUNDLEGEND_EVOLUTIONAER_STABIL: SpieltheorieNormProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[SpieltheorieNormGeltung, float] = {
    SpieltheorieNormGeltung.GESPERRT: 0.0,
    SpieltheorieNormGeltung.EVOLUTIONAER_STABIL: 0.04,
    SpieltheorieNormGeltung.GRUNDLEGEND_EVOLUTIONAER_STABIL: 0.08,
}

_TIER_DELTA: dict[SpieltheorieNormGeltung, int] = {
    SpieltheorieNormGeltung.GESPERRT: 0,
    SpieltheorieNormGeltung.EVOLUTIONAER_STABIL: 1,
    SpieltheorieNormGeltung.GRUNDLEGEND_EVOLUTIONAER_STABIL: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses (*_norm pattern)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SpieltheorieNormEintrag:
    norm_id: str
    spieltheorie_norm_typ: SpieltheorieNormTyp
    prozedur: SpieltheorieNormProzedur
    geltung: SpieltheorieNormGeltung
    spieltheorie_norm_weight: float
    spieltheorie_norm_tier: int
    canonical: bool
    spieltheorie_norm_ids: tuple[str, ...]
    spieltheorie_norm_tags: tuple[str, ...]


@dataclass(frozen=True)
class SpieltheorieNormSatz:
    norm_id: str
    auktions_senat: AuktionsSenat
    normen: tuple[SpieltheorieNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is SpieltheorieNormGeltung.GESPERRT)

    @property
    def evolutionaer_stabil_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is SpieltheorieNormGeltung.EVOLUTIONAER_STABIL)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is SpieltheorieNormGeltung.GRUNDLEGEND_EVOLUTIONAER_STABIL)

    @property
    def norm_signal(self):
        if any(n.geltung is SpieltheorieNormGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-gesperrt")
        elif any(n.geltung is SpieltheorieNormGeltung.EVOLUTIONAER_STABIL for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-evolutionaer-stabil")
        from types import SimpleNamespace
        return SimpleNamespace(status="norm-grundlegend-evolutionaer-stabil")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_spieltheorie_norm(
    auktions_senat: AuktionsSenat | None = None,
    *,
    norm_id: str = "spieltheorie-norm",
) -> SpieltheorieNormSatz:
    if auktions_senat is None:
        auktions_senat = build_auktions_senat(senat_id=f"{norm_id}-senat")

    normen: list[SpieltheorieNormEintrag] = []
    for parent_norm in auktions_senat.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{norm_id}-{parent_norm.auktions_senat_id.removeprefix(f'{auktions_senat.senat_id}-')}"
        raw_weight = min(1.0, parent_norm.auktions_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.auktions_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is SpieltheorieNormGeltung.GRUNDLEGEND_EVOLUTIONAER_STABIL)
        normen.append(
            SpieltheorieNormEintrag(
                norm_id=new_id,
                spieltheorie_norm_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                spieltheorie_norm_weight=new_weight,
                spieltheorie_norm_tier=new_tier,
                canonical=is_canonical,
                spieltheorie_norm_ids=parent_norm.auktions_ids + (new_id,),
                spieltheorie_norm_tags=parent_norm.auktions_tags + (f"spieltheorie-norm:{new_geltung.value}",),
            )
        )
    return SpieltheorieNormSatz(
        norm_id=norm_id,
        auktions_senat=auktions_senat,
        normen=tuple(normen),
    )
