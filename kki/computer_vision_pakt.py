"""
#906 ComputerVisionPakt — Computer Vision: Bildverstehen durch neuronale Netze.
David Hubel & Torsten Wiesel (1959): Rezeptive Felder im visuellen Kortex — biologische Basis für CNN.
LeCun et al. (1998): LeNet-5 — erstes praktisches CNN für Ziffernerkennung (MNIST).
Krizhevsky et al. (2012): AlexNet — ImageNet-Gewinner startet Deep-Learning-Revolution.
He et al. (2015): ResNet — Residual Connections ermöglichen sehr tiefe Netze (152 Schichten).
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .natural_language_manifest import NaturalLanguageManifest, build_natural_language_manifest


class ComputerVisionPaktTyp(Enum):
    KLASSIFIKATION = auto()
    DETEKTION = auto()
    SEGMENTIERUNG = auto()
    GENERIERUNG = auto()
    TRACKING = auto()


class ComputerVisionPaktProzedur(Enum):
    VORVERARBEITUNG = auto()
    MERKMALSEXTRAKTION = auto()
    KLASSIFIZIERUNG = auto()
    POSTVERARBEITUNG = auto()
    AUSWERTUNG = auto()


_WEIGHT_DELTA = {
    ComputerVisionPaktTyp.KLASSIFIKATION: 0.0,
    ComputerVisionPaktTyp.DETEKTION: 1.6,
    ComputerVisionPaktTyp.SEGMENTIERUNG: 3.2,
    ComputerVisionPaktTyp.GENERIERUNG: 4.8,
    ComputerVisionPaktTyp.TRACKING: 6.4,
}
_TYP_MAP = {
    ComputerVisionPaktTyp.KLASSIFIKATION: "klassifikation",
    ComputerVisionPaktTyp.DETEKTION: "detektion",
    ComputerVisionPaktTyp.SEGMENTIERUNG: "segmentierung",
    ComputerVisionPaktTyp.GENERIERUNG: "generierung",
    ComputerVisionPaktTyp.TRACKING: "tracking",
}
_PROZEDUR_MAP = {
    ComputerVisionPaktProzedur.VORVERARBEITUNG: "vorverarbeitung",
    ComputerVisionPaktProzedur.MERKMALSEXTRAKTION: "merkmalsextraktion",
    ComputerVisionPaktProzedur.KLASSIFIZIERUNG: "klassifizierung",
    ComputerVisionPaktProzedur.POSTVERARBEITUNG: "postverarbeitung",
    ComputerVisionPaktProzedur.AUSWERTUNG: "auswertung",
}


@dataclass(frozen=True)
class ComputerVisionPaktEintrag:
    typ: ComputerVisionPaktTyp
    prozedur: ComputerVisionPaktProzedur
    maschinenlernen_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class ComputerVisionPakt:
    eintraege: tuple[ComputerVisionPaktEintrag, ...]
    canonical: bool = True

    def aggregates_pakt_signal(self) -> dict:
        return {
            "pakt_id": "computer-vision-pakt-906",
            "eintraege_count": len(self.eintraege),
            "canonical": self.canonical,
        }


def build_computer_vision_pakt(parent: Optional[NaturalLanguageManifest] = None) -> ComputerVisionPakt:
    if parent is None:
        parent = build_natural_language_manifest()
    base = sum(n.maschinenlernen_weight for n in parent.normen)
    eintraege = tuple(
        ComputerVisionPaktEintrag(
            typ=t,
            prozedur=list(ComputerVisionPaktProzedur)[i],
            maschinenlernen_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(ComputerVisionPaktTyp)
    )
    return ComputerVisionPakt(eintraege=eintraege)
