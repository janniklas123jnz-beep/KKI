"""
#946 BioprozesstechnikPakt — Bioprozesstechnik: Fermentation, Bioreaktor & Downstream.
Pasteur (1857): Fermentation und Mikroorganismen — Fermentation als kontrollierter
  mikrobieller Prozess; Grundlage industrieller Biotechnologie und Bierbrauerei.
Monod (1949): The Growth of Bacterial Cultures — Wachstumskinetik von Mikroorganismen;
  Monod-Gleichung als Basis für Bioreaktorkonstruktion und Prozessoptimierung.
Aiba, Humphrey & Millis (1973): Biochemical Engineering — systematische
  Bioreaktortechnik; Sauerstofftransfer, Rührtechnik und Maßstabsübertragung.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from .mrna_manifest import mRNAManifest, build_mrna_manifest


class BioprozesstechnikPaktTyp(Enum):
    FERMENTATION = auto()
    ZELLKULTUR = auto()
    DOWNSTREAM_PROCESSING = auto()
    BIOREAKTORTECHNIK = auto()
    KONTINUIERLICHER_PROZESS = auto()


class BioprozesstechnikPaktProzedur(Enum):
    ANZUCHT = auto()
    FERMENTATION = auto()
    ERNTE = auto()
    AUFREINIGUNG = auto()
    FORMULIERUNG = auto()


_WEIGHT_DELTA = {
    BioprozesstechnikPaktTyp.FERMENTATION: 0.0,
    BioprozesstechnikPaktTyp.ZELLKULTUR: 1.7,
    BioprozesstechnikPaktTyp.DOWNSTREAM_PROCESSING: 3.4,
    BioprozesstechnikPaktTyp.BIOREAKTORTECHNIK: 5.1,
    BioprozesstechnikPaktTyp.KONTINUIERLICHER_PROZESS: 6.8,
}
_TYP_MAP = {
    BioprozesstechnikPaktTyp.FERMENTATION: "fermentation",
    BioprozesstechnikPaktTyp.ZELLKULTUR: "zellkultur",
    BioprozesstechnikPaktTyp.DOWNSTREAM_PROCESSING: "downstream_processing",
    BioprozesstechnikPaktTyp.BIOREAKTORTECHNIK: "bioreaktortechnik",
    BioprozesstechnikPaktTyp.KONTINUIERLICHER_PROZESS: "kontinuierlicher_prozess",
}
_PROZEDUR_MAP = {
    BioprozesstechnikPaktProzedur.ANZUCHT: "anzucht",
    BioprozesstechnikPaktProzedur.FERMENTATION: "fermentation",
    BioprozesstechnikPaktProzedur.ERNTE: "ernte",
    BioprozesstechnikPaktProzedur.AUFREINIGUNG: "aufreinigung",
    BioprozesstechnikPaktProzedur.FORMULIERUNG: "formulierung",
}


@dataclass(frozen=True)
class BioprozesstechnikPaktEintrag:
    typ: BioprozesstechnikPaktTyp
    prozedur: BioprozesstechnikPaktProzedur
    biotech_weight: float
    tier: int
    canonical: bool = True


@dataclass(frozen=True)
class BioprozesstechnikPakt:
    eintraege: tuple[BioprozesstechnikPaktEintrag, ...]
    canonical: bool = True

    def aggregates_pakt_signal(self) -> dict:
        return {
            "pakt_id": "bioprozesstechnik-pakt-946",
            "eintraege_count": len(self.eintraege),
            "canonical": self.canonical,
        }


def build_bioprozesstechnik_pakt(parent: Optional[mRNAManifest] = None) -> BioprozesstechnikPakt:
    if parent is None:
        parent = build_mrna_manifest()
    base = sum(n.biotech_weight for n in parent.normen)
    eintraege = tuple(
        BioprozesstechnikPaktEintrag(
            typ=t,
            prozedur=list(BioprozesstechnikPaktProzedur)[i],
            biotech_weight=base + _WEIGHT_DELTA[t],
            tier=i + 1,
        )
        for i, t in enumerate(BioprozesstechnikPaktTyp)
    )
    return BioprozesstechnikPakt(eintraege=eintraege)
