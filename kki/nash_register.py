"""
#442 NashRegister — Nash-Gleichgewicht: Strategische Stabilität im Schwarm.
Nash (1950): Gleichgewichtskonzept für N-Personen-Spiele — kein Spieler profitiert vom Abweichen.
Gefangenendilemma: individuelle Rationalität führt zu kollektiv suboptimalem Ergebnis.
Nash-Bargaining: axiomatische Lösung kooperativer Verhandlungsprobleme (1950).
Leitsterns Agenten suchen Nash-stabile Interaktionsmuster für robuste Schwarmdynamik.
Geltungsstufen: GESPERRT / NASH / GRUNDLEGEND_NASH
Parent: SpieltheorieFeld (#441)
Block #441–#450: Spieltheorie & Entscheidungstheorie
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .spieltheorie_feld import (
    SpieltheorieFeld,
    SpieltheorieFeldGeltung,
    build_spieltheorie_feld,
)

_GELTUNG_MAP: dict[SpieltheorieFeldGeltung, "NashRegisterGeltung"] = {}


def _init_map() -> None:
    _GELTUNG_MAP[SpieltheorieFeldGeltung.GESPERRT] = NashRegisterGeltung.GESPERRT
    _GELTUNG_MAP[SpieltheorieFeldGeltung.SPIELTHEORETISCH] = NashRegisterGeltung.NASH
    _GELTUNG_MAP[SpieltheorieFeldGeltung.GRUNDLEGEND_SPIELTHEORETISCH] = NashRegisterGeltung.GRUNDLEGEND_NASH


class NashRegisterTyp(Enum):
    SCHUTZ_NASH = "schutz-nash"
    ORDNUNGS_NASH = "ordnungs-nash"
    SOUVERAENITAETS_NASH = "souveraenitaets-nash"


class NashRegisterProzedur(Enum):
    NOTPROZEDUR = "notprozedur"
    REGELPROTOKOLL = "regelprotokoll"
    PLENARPROTOKOLL = "plenarprotokoll"


class NashRegisterGeltung(Enum):
    GESPERRT = "gesperrt"
    NASH = "nash"
    GRUNDLEGEND_NASH = "grundlegend-nash"


_init_map()

_TYP_MAP: dict[NashRegisterGeltung, NashRegisterTyp] = {
    NashRegisterGeltung.GESPERRT: NashRegisterTyp.SCHUTZ_NASH,
    NashRegisterGeltung.NASH: NashRegisterTyp.ORDNUNGS_NASH,
    NashRegisterGeltung.GRUNDLEGEND_NASH: NashRegisterTyp.SOUVERAENITAETS_NASH,
}

_PROZEDUR_MAP: dict[NashRegisterGeltung, NashRegisterProzedur] = {
    NashRegisterGeltung.GESPERRT: NashRegisterProzedur.NOTPROZEDUR,
    NashRegisterGeltung.NASH: NashRegisterProzedur.REGELPROTOKOLL,
    NashRegisterGeltung.GRUNDLEGEND_NASH: NashRegisterProzedur.PLENARPROTOKOLL,
}

_WEIGHT_DELTA: dict[NashRegisterGeltung, float] = {
    NashRegisterGeltung.GESPERRT: 0.0,
    NashRegisterGeltung.NASH: 0.04,
    NashRegisterGeltung.GRUNDLEGEND_NASH: 0.08,
}

_TIER_DELTA: dict[NashRegisterGeltung, int] = {
    NashRegisterGeltung.GESPERRT: 0,
    NashRegisterGeltung.NASH: 1,
    NashRegisterGeltung.GRUNDLEGEND_NASH: 2,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class NashRegisterNorm:
    nash_register_id: str
    nash_register_typ: NashRegisterTyp
    prozedur: NashRegisterProzedur
    geltung: NashRegisterGeltung
    nash_weight: float
    nash_tier: int
    canonical: bool
    nash_ids: tuple[str, ...]
    nash_tags: tuple[str, ...]


@dataclass(frozen=True)
class NashRegister:
    register_id: str
    spieltheorie_feld: SpieltheorieFeld
    normen: tuple[NashRegisterNorm, ...]

    @property
    def gesperrt_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.nash_register_id for n in self.normen if n.geltung is NashRegisterGeltung.GESPERRT)

    @property
    def nash_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.nash_register_id for n in self.normen if n.geltung is NashRegisterGeltung.NASH)

    @property
    def grundlegend_norm_ids(self) -> tuple[str, ...]:
        return tuple(n.nash_register_id for n in self.normen if n.geltung is NashRegisterGeltung.GRUNDLEGEND_NASH)

    @property
    def register_signal(self):
        if any(n.geltung is NashRegisterGeltung.GESPERRT for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-gesperrt")
        elif any(n.geltung is NashRegisterGeltung.NASH for n in self.normen):
            from types import SimpleNamespace
            return SimpleNamespace(status="register-nash")
        from types import SimpleNamespace
        return SimpleNamespace(status="register-grundlegend-nash")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_nash_register(
    spieltheorie_feld: SpieltheorieFeld | None = None,
    *,
    register_id: str = "nash-register",
) -> NashRegister:
    if spieltheorie_feld is None:
        spieltheorie_feld = build_spieltheorie_feld(feld_id=f"{register_id}-feld")

    normen: list[NashRegisterNorm] = []
    for parent_norm in spieltheorie_feld.normen:
        new_geltung = _GELTUNG_MAP[parent_norm.geltung]
        new_id = f"{register_id}-{parent_norm.spieltheorie_feld_id.removeprefix(f'{spieltheorie_feld.feld_id}-')}"
        raw_weight = min(1.0, parent_norm.spieltheorie_weight + _WEIGHT_DELTA[new_geltung])
        new_weight = round(raw_weight, 3)
        new_tier = parent_norm.spieltheorie_tier + _TIER_DELTA[new_geltung]
        is_canonical = parent_norm.canonical and (new_geltung is NashRegisterGeltung.GRUNDLEGEND_NASH)
        normen.append(
            NashRegisterNorm(
                nash_register_id=new_id,
                nash_register_typ=_TYP_MAP[new_geltung],
                prozedur=_PROZEDUR_MAP[new_geltung],
                geltung=new_geltung,
                nash_weight=new_weight,
                nash_tier=new_tier,
                canonical=is_canonical,
                nash_ids=parent_norm.spieltheorie_ids + (new_id,),
                nash_tags=parent_norm.spieltheorie_tags + (f"nash-register:{new_geltung.value}",),
            )
        )
    return NashRegister(
        register_id=register_id,
        spieltheorie_feld=spieltheorie_feld,
        normen=tuple(normen),
    )
