"""
#904 VerstaerkungslernenKodex — Reinforcement Learning: Bellman bis AlphaGo.
Richard Bellman (1957): Bellman-Gleichung — optimale Entscheidungsfolgen durch dynamisches Programmieren.
Sutton & Barto (1988): Temporal Difference Learning — TD(λ) als universelles RL-Paradigma.
Watkins (1989): Q-Learning — modellfreies RL mit Aktions-Wert-Funktionen.
DeepMind (2015): DQN — Deep Q-Networks bezwingen Atari-Spiele auf Menschenniveau.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .deep_learning_charta import DeepLearningCharta, build_deep_learning_charta


class VerstaerkungslernenKodexTyp(Enum):
    MODELL_FREI = auto()
    MODELL_BASIERT = auto()
    POLICY_GRADIENT = auto()
    WERT_BASIERT = auto()
    AKTEUR_KRITIKER = auto()


class VerstaerkungslernenKodexProzedur(Enum):
    EXPLORATION = auto()
    EXPLOITATION = auto()
    REWARD_SHAPING = auto()
    POLICY_UPDATE = auto()
    EVALUATION = auto()


_WEIGHT_DELTA = {
    VerstaerkungslernenKodexTyp.MODELL_FREI: 0.0,
    VerstaerkungslernenKodexTyp.MODELL_BASIERT: 1.8,
    VerstaerkungslernenKodexTyp.POLICY_GRADIENT: 3.6,
    VerstaerkungslernenKodexTyp.WERT_BASIERT: 5.4,
    VerstaerkungslernenKodexTyp.AKTEUR_KRITIKER: 7.2,
}
_TYP_MAP = {
    VerstaerkungslernenKodexTyp.MODELL_FREI: "modell_frei",
    VerstaerkungslernenKodexTyp.MODELL_BASIERT: "modell_basiert",
    VerstaerkungslernenKodexTyp.POLICY_GRADIENT: "policy_gradient",
    VerstaerkungslernenKodexTyp.WERT_BASIERT: "wert_basiert",
    VerstaerkungslernenKodexTyp.AKTEUR_KRITIKER: "akteur_kritiker",
}
_PROZEDUR_MAP = {
    VerstaerkungslernenKodexProzedur.EXPLORATION: "exploration",
    VerstaerkungslernenKodexProzedur.EXPLOITATION: "exploitation",
    VerstaerkungslernenKodexProzedur.REWARD_SHAPING: "reward_shaping",
    VerstaerkungslernenKodexProzedur.POLICY_UPDATE: "policy_update",
    VerstaerkungslernenKodexProzedur.EVALUATION: "evaluation",
}


@dataclass(frozen=True)
class VerstaerkungslernenKodexEintrag:
    typ: VerstaerkungslernenKodexTyp
    prozedur: VerstaerkungslernenKodexProzedur
    maschinenlernen_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class VerstaerkungslernenKodex:
    eintraege: tuple[VerstaerkungslernenKodexEintrag, ...]
    canonical: bool = True

    def aggregates_kodex_signal(self) -> dict:
        return {
            "kodex_id": "verstaerkungslernen-kodex-904",
            "eintraege_count": len(self.eintraege),
            "canonical": self.canonical,
        }


def build_verstaerkungslernen_kodex(parent: Optional[DeepLearningCharta] = None) -> VerstaerkungslernenKodex:
    if parent is None:
        parent = build_deep_learning_charta()
    base = sum(n.maschinenlernen_weight for n in parent.normen)
    eintraege = tuple(
        VerstaerkungslernenKodexEintrag(
            typ=t,
            prozedur=list(VerstaerkungslernenKodexProzedur)[i],
            maschinenlernen_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(VerstaerkungslernenKodexTyp)
    )
    return VerstaerkungslernenKodex(eintraege=eintraege)
