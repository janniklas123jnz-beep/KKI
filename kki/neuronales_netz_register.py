"""
#902 NeuronalesNetzRegister — Neuronale Netze: McCulloch-Pitts bis modernes Deep Learning.
McCulloch & Pitts (1943): Erstes formales Neuronenmodell — logische Operationen durch Neuronen.
Frank Rosenblatt (1958): Perceptron — erstes lernfähiges künstliches neuronales Netz.
Rumelhart, Hinton & Williams (1986): Backpropagation — Grundlage tiefer Netze.
LeCun et al. (1998): LeNet — erstes praktisches CNN für Bildklassifikation.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .maschinenlernen_feld import MaschinenlernenFeld, build_maschinenlernen_feld


class NeuronalesNetzRegisterTyp(Enum):
    FEEDFORWARD = auto()
    KONVOLUTIONELL = auto()
    REKURRENT = auto()
    TRANSFORMER = auto()
    AUTOENCODER = auto()


class NeuronalesNetzRegisterProzedur(Enum):
    INITIALISIERUNG = auto()
    VORWAERTS_PASS = auto()
    RUECKWAERTS_PASS = auto()
    GEWICHTS_UPDATE = auto()
    REGULARISIERUNG = auto()


_WEIGHT_DELTA = {
    NeuronalesNetzRegisterTyp.FEEDFORWARD: 0.0,
    NeuronalesNetzRegisterTyp.KONVOLUTIONELL: 1.5,
    NeuronalesNetzRegisterTyp.REKURRENT: 3.0,
    NeuronalesNetzRegisterTyp.TRANSFORMER: 4.5,
    NeuronalesNetzRegisterTyp.AUTOENCODER: 6.0,
}
_TYP_MAP = {
    NeuronalesNetzRegisterTyp.FEEDFORWARD: "feedforward",
    NeuronalesNetzRegisterTyp.KONVOLUTIONELL: "konvolutionell",
    NeuronalesNetzRegisterTyp.REKURRENT: "rekurrent",
    NeuronalesNetzRegisterTyp.TRANSFORMER: "transformer",
    NeuronalesNetzRegisterTyp.AUTOENCODER: "autoencoder",
}
_PROZEDUR_MAP = {
    NeuronalesNetzRegisterProzedur.INITIALISIERUNG: "initialisierung",
    NeuronalesNetzRegisterProzedur.VORWAERTS_PASS: "vorwaerts_pass",
    NeuronalesNetzRegisterProzedur.RUECKWAERTS_PASS: "rueckwaerts_pass",
    NeuronalesNetzRegisterProzedur.GEWICHTS_UPDATE: "gewichts_update",
    NeuronalesNetzRegisterProzedur.REGULARISIERUNG: "regularisierung",
}


@dataclass(frozen=True)
class NeuronalesNetzRegisterEintrag:
    typ: NeuronalesNetzRegisterTyp
    prozedur: NeuronalesNetzRegisterProzedur
    maschinenlernen_weight: float
    maschinenlernen_tier: int
    canonical: bool = True


@dataclass(frozen=True)
class NeuronalesNetzRegister:
    eintraege: tuple[NeuronalesNetzRegisterEintrag, ...]
    canonical: bool = True

    def aggregates_register_signal(self) -> dict:
        return {
            "register_id": "neuronales-netz-register-902",
            "eintraege_count": len(self.eintraege),
            "canonical": self.canonical,
        }


def build_neuronales_netz_register(parent: Optional[MaschinenlernenFeld] = None) -> NeuronalesNetzRegister:
    if parent is None:
        parent = build_maschinenlernen_feld()
    base = sum(n.maschinenlernen_weight for n in parent.normen)
    eintraege = tuple(
        NeuronalesNetzRegisterEintrag(
            typ=t,
            prozedur=list(NeuronalesNetzRegisterProzedur)[i],
            maschinenlernen_weight=base + _WEIGHT_DELTA[t],
            maschinenlernen_tier=i + 1,
        )
        for i, t in enumerate(NeuronalesNetzRegisterTyp)
    )
    return NeuronalesNetzRegister(eintraege=eintraege)
