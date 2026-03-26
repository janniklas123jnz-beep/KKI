"""
#903 DeepLearningCharta — Deep Learning: Hinton, LeCun, Bengio und die KI-Revolution.
Geoffrey Hinton (2006): Deep Belief Networks — Durchbruch beim Training tiefer Netze.
Yann LeCun (2010): Convolutional Neural Networks für Bild- und Sprachverarbeitung.
Yoshua Bengio (2012): Representation Learning — tiefe Repräsentationen als Schlüssel.
Krizhevsky et al. (2012): AlexNet — ImageNet-Sieg beginnt moderne Deep-Learning-Ära.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .neuronales_netz_register import NeuronalesNetzRegister, build_neuronales_netz_register


class DeepLearningChartaTyp(Enum):
    TIEF_FEEDFORWARD = auto()
    CNN = auto()
    RNN_LSTM = auto()
    GENERATIV = auto()
    ATTENTION = auto()


class DeepLearningChartaProzedur(Enum):
    SCHICHTUNG = auto()
    AKTIVIERUNG = auto()
    NORMIERUNG = auto()
    DROPOUT = auto()
    FINE_TUNING = auto()


_WEIGHT_DELTA = {
    DeepLearningChartaTyp.TIEF_FEEDFORWARD: 0.0,
    DeepLearningChartaTyp.CNN: 1.7,
    DeepLearningChartaTyp.RNN_LSTM: 3.4,
    DeepLearningChartaTyp.GENERATIV: 5.1,
    DeepLearningChartaTyp.ATTENTION: 6.8,
}
_TYP_MAP = {
    DeepLearningChartaTyp.TIEF_FEEDFORWARD: "tief_feedforward",
    DeepLearningChartaTyp.CNN: "cnn",
    DeepLearningChartaTyp.RNN_LSTM: "rnn_lstm",
    DeepLearningChartaTyp.GENERATIV: "generativ",
    DeepLearningChartaTyp.ATTENTION: "attention",
}
_PROZEDUR_MAP = {
    DeepLearningChartaProzedur.SCHICHTUNG: "schichtung",
    DeepLearningChartaProzedur.AKTIVIERUNG: "aktivierung",
    DeepLearningChartaProzedur.NORMIERUNG: "normierung",
    DeepLearningChartaProzedur.DROPOUT: "dropout",
    DeepLearningChartaProzedur.FINE_TUNING: "fine_tuning",
}


@dataclass(frozen=True)
class DeepLearningChartaNorm:
    typ: DeepLearningChartaTyp
    prozedur: DeepLearningChartaProzedur
    maschinenlernen_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class DeepLearningCharta:
    normen: tuple[DeepLearningChartaNorm, ...]
    canonical: bool = True

    def aggregates_charta_signal(self) -> dict:
        return {
            "charta_id": "deep-learning-charta-903",
            "normen_count": len(self.normen),
            "canonical": self.canonical,
        }


def build_deep_learning_charta(parent: Optional[NeuronalesNetzRegister] = None) -> DeepLearningCharta:
    if parent is None:
        parent = build_neuronales_netz_register()
    base = sum(e.maschinenlernen_weight for e in parent.eintraege)
    normen = tuple(
        DeepLearningChartaNorm(
            typ=t,
            prozedur=list(DeepLearningChartaProzedur)[i],
            maschinenlernen_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(DeepLearningChartaTyp)
    )
    return DeepLearningCharta(normen=normen)
