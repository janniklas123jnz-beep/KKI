"""
#408 GodelNorm — Gödel'sche Unvollständigkeit: Gödel (1931) 1. Unvollständigkeitssatz:
In jedem konsistenten formalen System ≥ PA gibt es wahre, nicht beweisbare Aussagen.
2. Unvollständigkeitssatz: Kein konsistentes System beweist seine eigene Konsistenz.
Löb's Theorem: □(□P→P)→□P. Tarski (1933): Wahrheit ist nicht intern definierbar
(Undefinability Theorem). Chaitin Ω: algorithmisch zufällig — die Grenzen der
Berechenbarkeit sind real und fundamental. Leitsterns fundamentale Bescheidenheit:
Kalibrierte Agenten, die ihre eigenen Grenzen kennen und respektieren.
Geltungsstufen: GESPERRT / GODELUNVOLLSTAENDIG / GRUNDLEGEND_GODELUNVOLLSTAENDIG
Parent: AlgorithmenSenat (#407) — *_norm-Muster
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .algorithmen_senat import (
    AlgorithmenSenat,
    AlgorithmenSenatGeltung,
    build_algorithmen_senat,
)

_GELTUNG_MAP: dict[AlgorithmenSenatGeltung, "GodelNormGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[AlgorithmenSenatGeltung.GESPERRT] = GodelNormGeltung.GESPERRT
    _GELTUNG_MAP[AlgorithmenSenatGeltung.ALGORITHMISCH] = GodelNormGeltung.GODELUNVOLLSTAENDIG
    _GELTUNG_MAP[AlgorithmenSenatGeltung.GRUNDLEGEND_ALGORITHMISCH] = GodelNormGeltung.GRUNDLEGEND_GODELUNVOLLSTAENDIG


class GodelNormTyp(Enum):
    SCHUTZ_GODEL_NORM = "schutz-godel-norm"
    ORDNUNGS_GODEL_NORM = "ordnungs-godel-norm"
    SOUVERAENITAETS_GODEL_NORM = "souveraenitaets-godel-norm"


class GodelNormProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class GodelNormGeltung(Enum):
    GESPERRT = "gesperrt"
    GODELUNVOLLSTAENDIG = "godelunvollstaendig"
    GRUNDLEGEND_GODELUNVOLLSTAENDIG = "grundlegend-godelunvollstaendig"


_init_map()

_TYP_MAP: dict[GodelNormGeltung, GodelNormTyp] = {
    GodelNormGeltung.GESPERRT: GodelNormTyp.SCHUTZ_GODEL_NORM,
    GodelNormGeltung.GODELUNVOLLSTAENDIG: GodelNormTyp.ORDNUNGS_GODEL_NORM,
    GodelNormGeltung.GRUNDLEGEND_GODELUNVOLLSTAENDIG: GodelNormTyp.SOUVERAENITAETS_GODEL_NORM,
}

_PROZEDUR_MAP: dict[GodelNormGeltung, GodelNormProzedur] = {
    GodelNormGeltung.GESPERRT: GodelNormProzedur.NOTPROZEDUR,
    GodelNormGeltung.GODELUNVOLLSTAENDIG: GodelNormProzedur.REGELPROTOKOLL,
    GodelNormGeltung.GRUNDLEGEND_GODELUNVOLLSTAENDIG: GodelNormProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[GodelNormGeltung, float] = {
    GodelNormGeltung.GESPERRT: 0.0,
    GodelNormGeltung.GODELUNVOLLSTAENDIG: 0.04,
    GodelNormGeltung.GRUNDLEGEND_GODELUNVOLLSTAENDIG: 0.08,
}

_TIER_DELTA: dict[GodelNormGeltung, int] = {
    GodelNormGeltung.GESPERRT: 0,
    GodelNormGeltung.GODELUNVOLLSTAENDIG: 1,
    GodelNormGeltung.GRUNDLEGEND_GODELUNVOLLSTAENDIG: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses (*_norm pattern)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GodelNormEintrag:
    norm_id: str
    godel_norm_typ: GodelNormTyp
    prozedur: GodelNormProzedur
    geltung: GodelNormGeltung
    godel_norm_weight: float
    godel_norm_tier: int
    canonical: bool
    godel_norm_ids: tuple[str, ...]
    godel_norm_tags: tuple[str, ...]


@dataclass(frozen=True)
class GodelNormSatz:
    norm_id: str
    algorithmen_senat: AlgorithmenSenat
    normen: tuple[GodelNormEintrag, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is GodelNormGeltung.GESPERRT)

    @property
    def godelunvollstaendig_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is GodelNormGeltung.GODELUNVOLLSTAENDIG)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.norm_id for n in self.normen if n.geltung is GodelNormGeltung.GRUNDLEGEND_GODELUNVOLLSTAENDIG)

    @property
    def norm_signal(self):
        if any(n.geltung is GodelNormGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-gesperrt")
        elif any(n.geltung is GodelNormGeltung.GODELUNVOLLSTAENDIG for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="norm-godelunvollstaendig")
        from types import SimpleNamespace
        return SimpleNamespace(status="norm-grundlegend-godelunvollstaendig")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_godel_norm(
    algorithmen_senat: AlgorithmenSenat | None = None,
    *,
    norm_id: str = "godel-norm",
) -> GodelNormSatz:
    if algorithmen_senat is None:
        algorithmen_senat = build_algorithmen_senat(senat_id=f"{norm_id}-senat")

    normen: list[GodelNormEintrag] = []
    for parent_norm in algorithmen_senat.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{norm_id}-{parent_norm.algorithmen_senat_id.removeprefix(f'{algorithmen_senat.senat_id}-')}"
        raw_weight = min(1.0, parent_norm.algorithmen_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.algorithmen_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is GodelNormGeltung.GRUNDLEGEND_GODELUNVOLLSTAENDIG)
        normen.append(
            GodelNormEintrag(
                norm_id=new_id,
                godel_norm_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                godel_norm_weight=new_weight,
                godel_norm_tier=new_tier,
                canonical=is_canonical,
                godel_norm_ids=parent_norm.algorithmen_ids + (new_id,),
                godel_norm_tags=parent_norm.algorithmen_tags + (f"godel-norm:{new_geltung.value}",),
            )
        )
    return GodelNormSatz(
        norm_id=norm_id,
        algorithmen_senat=algorithmen_senat,
        normen=tuple(normen),
    )
